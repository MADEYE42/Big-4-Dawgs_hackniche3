import sys
import json
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import string
import psycopg2
from elasticsearch import Elasticsearch

# PostgreSQL connection parameters
DB_PARAMS = {
    "host": "localhost",
    "database": "your_database",
    "user": "your_username",
    "password": "your_password",
    "port": "5432"
}

# Elasticsearch connection
ES_CLIENT = Elasticsearch("http://localhost:9200")

def get_db_connection():
    return psycopg2.connect(**DB_PARAMS)

def load_data_from_postgres():
    conn = get_db_connection()
    query = """
        SELECT asin, title, price, rating, category, discount, reviews_count, prime
        FROM amazon_products
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def preprocess_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = ' '.join(text.split())
    simple_stopwords = {
        'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while',
    }
    text = ' '.join([word for word in text.split() if word not in simple_stopwords])
    return text

def preprocess_data(df):
    df = df.copy()
    df['discount'] = df['discount'].replace("No Discount", 0)
    df['discount'] = pd.to_numeric(df['discount'], errors='coerce')
    df['discount'] = df['discount'].fillna(0)
    if df['price'].dtype == object:
        df['price'] = df['price'].replace('[\₹,$,£,€,]', '', regex=True).astype(str).str.replace(',', '')
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['price'] = df['price'].fillna(df['price'].median())
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df['rating'] = df['rating'].fillna(df['rating'].median())
    df['reviews_count'] = pd.to_numeric(df['reviews_count'], errors='coerce')
    df['reviews_count'] = df['reviews_count'].fillna(0)
    df['processed_title'] = df['title'].apply(preprocess_text)
    return df

def create_content_representation(df):
    def create_feature_soup(row):
        features = []
        prime_status = 'prime' if row.get('prime') == 1 else 'not_prime'
        features.append(prime_status)
        if isinstance(row.get('category'), str):
            category = row.get('category').lower().replace(' ', '_')
            features.append(f"category_{category}")
        if row['price'] < 500:
            price_range = 'budget_price'
        elif row['price'] < 2000:
            price_range = 'mid_price'
        else:
            price_range = 'premium_price'
        features.append(price_range)
        if row['rating'] >= 4.5:
            rating_range = 'top_rated'
        elif row['rating'] >= 4.0:
            rating_range = 'highly_rated'
        elif row['rating'] >= 3.0:
            rating_range = 'average_rated'
        else:
            rating_range = 'low_rated'
        features.append(rating_range)
        if row['discount'] >= 30:
            discount_range = 'high_discount'
        elif row['discount'] >= 10:
            discount_range = 'medium_discount'
        else:
            discount_range = 'low_discount'
        features.append(discount_range)
        if row['reviews_count'] > 1000:
            popularity = 'very_popular'
        elif row['reviews_count'] > 100:
            popularity = 'popular'
        else:
            popularity = 'less_popular'
        features.append(popularity)
        return ' '.join(features)
    df['feature_soup'] = df.apply(create_feature_soup, axis=1)
    return df

def extract_camera_terms(title):
    if not isinstance(title, str):
        return ""
    camera_terms = [
        'dslr', 'mirrorless', 'canon', 'nikon', 'sony', 'fujifilm', 'olympus', 'panasonic',
    ]
    title_lower = title.lower()
    found_terms = []
    for term in camera_terms:
        if term in title_lower:
            found_terms.append(term)
    model_patterns = [
        r'\b[a-z]+\d+[a-z]*\b',
        r'\b\d+[a-z]+\b',
        r'\bmark\s+[ivx]+\b',
    ]
    for pattern in model_patterns:
        matches = re.findall(pattern, title_lower)
        found_terms.extend(matches)
    return ' '.join(found_terms)

def build_recommendation_model(df):
    if 'processed_title' not in df.columns:
        df['processed_title'] = df['title'].apply(preprocess_text)
    df['camera_terms'] = df['title'].apply(extract_camera_terms)
    title_tfidf = TfidfVectorizer(
        max_features=5000,
        stop_words='english',
        ngram_range=(1, 2)
    )
    title_tfidf_matrix = title_tfidf.fit_transform(df['processed_title'])
    camera_tfidf = TfidfVectorizer(stop_words='english')
    if df['camera_terms'].str.strip().str.len().sum() > 0:
        camera_tfidf_matrix = camera_tfidf.fit_transform(df['camera_terms'])
        has_camera_terms = True
    else:
        camera_tfidf_matrix = title_tfidf_matrix.copy()
        has_camera_terms = False
    feature_tfidf = TfidfVectorizer(stop_words='english')
    feature_tfidf_matrix = feature_tfidf.fit_transform(df['feature_soup'])
    title_sim = cosine_similarity(title_tfidf_matrix, title_tfidf_matrix)
    feature_sim = cosine_similarity(feature_tfidf_matrix, feature_tfidf_matrix)
    if has_camera_terms:
        camera_sim = cosine_similarity(camera_tfidf_matrix, camera_tfidf_matrix)
        combined_sim = 0.5 * title_sim + 0.3 * camera_sim + 0.2 * feature_sim
    else:
        combined_sim = 0.7 * title_sim + 0.3 * feature_sim
    return combined_sim

def get_recommendations(product_idx, cosine_sim, df, top_n=5):
    try:
        if product_idx < 0 or product_idx >= len(df):
            print(f"Product index {product_idx} is out of range (0-{len(df)-1}).")
            return pd.DataFrame()
        sim_scores = list(enumerate(cosine_sim[product_idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:top_n+1]
        product_indices = [i[0] for i in sim_scores]
        columns_to_include = ['asin', 'title', 'price', 'rating', 'category', 'discount', 'reviews_count']
        available_columns = [col for col in columns_to_include if col in df.columns]
        recommendations = df.iloc[product_indices][available_columns].copy()
        recommendations['similarity_score'] = [score for _, score in sim_scores]
        return recommendations
    except Exception as e:
        print(f"Error getting recommendations: {e}")
        return pd.DataFrame()

def get_recommendations_from_history(user_history, df, top_n=9):
    if not user_history or len(user_history) == 0:
        return pd.DataFrame()
    processed_df = preprocess_data(df)
    content_df = create_content_representation(processed_df)
    combined_sim = build_recommendation_model(content_df)
    history_indices = []
    for asin in user_history:
        indices = content_df.index[content_df['asin'] == asin].tolist()
        if indices:
            history_indices.append(indices[0])
    if not history_indices:
        return pd.DataFrame()
    all_recommendations = pd.DataFrame()
    for idx in history_indices:
        recommendations = get_recommendations(idx, combined_sim, content_df, top_n)
        if all_recommendations.empty:
            all_recommendations = recommendations
        else:
            all_recommendations = pd.concat([all_recommendations, recommendations])
    all_recommendations = all_recommendations.sort_values('similarity_score', ascending=False)
    all_recommendations = all_recommendations.drop_duplicates(subset='asin')
    return all_recommendations.head(top_n)

def get_user_history_from_elasticsearch(user_id):
    query = {
        "query": {
            "term": {
                "user_id": user_id
            }
        }
    }
    response = ES_CLIENT.search(index="user_history", body=query)
    history = [hit["_source"]["product_asin"] for hit in response["hits"]["hits"]]
    return history

def main():
    if len(sys.argv) < 2:
        print(json.dumps([]))
        return
    command = sys.argv[1]
    df = load_data_from_postgres()

    if command == "get_product_recommendations":
        asin = sys.argv[2]
        top_n = int(sys.argv[3]) if len(sys.argv) > 3 else 9
        product_idx = df.index[df['asin'] == asin].tolist()
        if not product_idx:
            print(json.dumps([]))
            return
        processed_df = preprocess_data(df)
        content_df = create_content_representation(processed_df)
        combined_sim = build_recommendation_model(content_df)
        recommendations = get_recommendations(product_idx[0], combined_sim, content_df, top_n)
        print(json.dumps(recommendations.to_dict(orient='records')))
    
    elif command == "get_history_recommendations":
        user_id = sys.argv[2]
        top_n = int(sys.argv[3]) if len(sys.argv) > 3 else 9
        user_history = get_user_history_from_elasticsearch(user_id)
        recommendations = get_recommendations_from_history(user_history, df, top_n)
        print(json.dumps(recommendations.to_dict(orient='records')))
    
    else:
        print(json.dumps([]))

if _name_ == "_main_":
    main()