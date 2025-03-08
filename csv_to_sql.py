import codecs
import csv
import os
import re
import sqlite3
import sys


def clean_price(price_str):
    """Extract and clean price values"""
    if not price_str or price_str == "N/A":
        return "NULL"
    
    # Extract the numeric part using regex
    price_match = re.search(r'₹([\d,]+\.?\d*)', price_str)
    if price_match:
        # Remove commas and convert to float
        return price_match.group(1).replace(',', '')
    return "NULL"

def clean_discount(discount_str):
    """Extract discount percentage"""
    if not discount_str or discount_str == "N/A":
        return "NULL"
    
    # Extract percentage using regex
    discount_match = re.search(r'(\d+)%', discount_str)
    if discount_match:
        return discount_match.group(1)
    return "NULL"

def clean_rating(rating_str):
    """Extract rating value"""
    if not rating_str or rating_str == "N/A":
        return "NULL"
    
    # Extract the numeric part using regex
    rating_match = re.search(r'(\d+\.?\d*)', rating_str)
    if rating_match:
        return rating_match.group(1)
    return "NULL"

def clean_text(text):
    """Clean and escape text for SQL insertion"""
    if not text or text == "N/A":
        return "NULL"
    
    # Escape single quotes for SQL
    return f"'{text.replace('\'', '\'\'')}'"

def create_amazon_products_table(conn):
    """Create the products table with proper structure"""
    cursor = conn.cursor()
    
    create_table_sql = '''
    CREATE TABLE IF NOT EXISTS amazon_products (
        asin TEXT PRIMARY KEY,
        title TEXT,
        price REAL,
        original_price REAL,
        discount REAL,
        rating REAL,
        reviews_count INTEGER,
        prime BOOLEAN,
        sponsored BOOLEAN,
        delivery TEXT,
        image_url TEXT,
        url TEXT,
        category TEXT
    )
    '''
    
    cursor.execute(create_table_sql)
    
    # Create indexes for better query performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_title ON amazon_products (title)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_price ON amazon_products (price)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_rating ON amazon_products (rating)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON amazon_products (category)")
    
    conn.commit()

def process_csv_file(csv_file, db_file):
    """Process the CSV file and insert records into SQLite database"""
    # Create database connection
    conn = sqlite3.connect(db_file)
    create_amazon_products_table(conn)
    cursor = conn.cursor()
    
    # Try different encoding options
    encodings = ['utf-8', 'latin-1', 'cp1252']
    csv_reader = None
    
    for encoding in encodings:
        try:
            with open(csv_file, 'r', encoding=encoding) as f:
                csv_reader = csv.reader(f)
                headers = next(csv_reader)  # Read header to test encoding
                break
        except UnicodeDecodeError:
            continue
    
    if not csv_reader:
        print(f"Error: Could not decode the CSV file with any of the attempted encodings.")
        return
    
    # Reopen the file with the successful encoding
    with open(csv_file, 'r', encoding=encoding) as f:
        csv_reader = csv.reader(f)
        headers = next(csv_reader)  # Skip header row
        
        # Map the column indices based on the headers
        try:
            asin_idx = headers.index('asin')
            delivery_idx = headers.index('delivery') if 'delivery' in headers else -1
            discount_idx = headers.index('discount') if 'discount' in headers else -1
            image_url_idx = headers.index('image_url') if 'image_url' in headers else -1
            original_price_idx = headers.index('original_price') if 'original_price' in headers else -1
            price_idx = headers.index('price') if 'price' in headers else -1
            prime_idx = headers.index('prime') if 'prime' in headers else -1
            rating_idx = headers.index('rating') if 'rating' in headers else -1
            reviews_count_idx = headers.index('reviews_count') if 'reviews_count' in headers else -1
            sponsored_idx = headers.index('sponsored') if 'sponsored' in headers else -1
            title_idx = headers.index('title') if 'title' in headers else -1
            url_idx = headers.index('url') if 'url' in headers else -1
            category_idx = headers.index('category') if 'category' in headers else -1
        except ValueError as e:
            print(f"Error: Required column not found in CSV: {e}")
            print(f"Available columns: {headers}")
            return
        
        row_count = 0
        skipped_count = 0
        
        for row in csv_reader:
            try:
                # Skip rows that don't have enough fields
                if len(row) <= asin_idx:
                    skipped_count += 1
                    continue
                
                # Extract fields from the row
                asin = clean_text(row[asin_idx]) if asin_idx >= 0 and asin_idx < len(row) else "NULL"
                delivery = clean_text(row[delivery_idx]) if delivery_idx >= 0 and delivery_idx < len(row) else "NULL"
                discount = clean_discount(row[discount_idx]) if discount_idx >= 0 and discount_idx < len(row) else "NULL"
                image_url = clean_text(row[image_url_idx]) if image_url_idx >= 0 and image_url_idx < len(row) else "NULL"
                original_price = clean_price(row[original_price_idx]) if original_price_idx >= 0 and original_price_idx < len(row) else "NULL"
                price = clean_price(row[price_idx]) if price_idx >= 0 and price_idx < len(row) else "NULL"
                prime = "1" if prime_idx >= 0 and prime_idx < len(row) and row[prime_idx].lower() == "yes" else "0"
                rating = clean_rating(row[rating_idx]) if rating_idx >= 0 and rating_idx < len(row) else "NULL"
                reviews_count = row[reviews_count_idx] if reviews_count_idx >= 0 and reviews_count_idx < len(row) and row[reviews_count_idx].isdigit() else "0"
                sponsored = "1" if sponsored_idx >= 0 and sponsored_idx < len(row) and row[sponsored_idx].lower() == "yes" else "0"
                title = clean_text(row[title_idx]) if title_idx >= 0 and title_idx < len(row) else "NULL"
                url = clean_text(row[url_idx]) if url_idx >= 0 and url_idx < len(row) else "NULL"
                category = clean_text(row[category_idx]) if category_idx >= 0 and category_idx < len(row) else "NULL"
                
                # Skip rows with invalid ASIN (our primary key)
                if asin == "NULL":
                    skipped_count += 1
                    continue
                
                # Insert data into database
                insert_sql = f'''
                INSERT OR REPLACE INTO amazon_products (
                    asin, title, price, original_price, discount, rating, 
                    reviews_count, prime, sponsored, delivery, image_url, url, category
                ) VALUES (
                    {asin}, {title}, {price}, {original_price}, {discount}, {rating},
                    {reviews_count}, {prime}, {sponsored}, {delivery}, {image_url}, {url}, {category}
                )
                '''
                
                cursor.execute(insert_sql)
                row_count += 1
                
                if row_count % 100 == 0:
                    conn.commit()
                    print(f"Processed {row_count} rows...")
                
            except Exception as e:
                print(f"Error processing row: {e}")
                skipped_count += 1
                continue
    
    # Final commit and close connection
    conn.commit()
    
    print(f"Successfully imported {row_count} records into amazon_products table")
    print(f"Skipped {skipped_count} invalid records")
    
    # Verify the database was created correctly
    verify_database(conn)
    
    conn.close()

def verify_database(conn):
    """Verify the database was created correctly by running some test queries"""
    cursor = conn.cursor()
    
    print("\n=== Database Verification ===")
    
    # Check table structure
    cursor.execute("PRAGMA table_info(amazon_products)")
    columns = cursor.fetchall()
    print(f"\nTable Structure (amazon_products):")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Count total records
    cursor.execute("SELECT COUNT(*) FROM amazon_products")
    count = cursor.fetchone()[0]
    print(f"\nTotal Records: {count}")
    
    # Check for null ASINs (should be none since it's a primary key)
    cursor.execute("SELECT COUNT(*) FROM amazon_products WHERE asin IS NULL")
    null_asins = cursor.fetchone()[0]
    print(f"Records with NULL ASIN: {null_asins} (should be 0)")
    
    # Get price range
    cursor.execute("SELECT MIN(price), MAX(price), AVG(price) FROM amazon_products")
    price_stats = cursor.fetchone()
    print(f"Price Range: Min={price_stats[0]}, Max={price_stats[1]}, Avg={price_stats[2]:.2f}")
    
    # Get rating distribution
    cursor.execute("""
    SELECT 
        CASE 
            WHEN rating < 1 THEN '0-1'
            WHEN rating >= 1 AND rating < 2 THEN '1-2'
            WHEN rating >= 2 AND rating < 3 THEN '2-3'
            WHEN rating >= 3 AND rating < 4 THEN '3-4'
            WHEN rating >= 4 AND rating <= 5 THEN '4-5'
            ELSE 'Unknown'
        END as rating_range,
        COUNT(*) as count
    FROM amazon_products
    GROUP BY rating_range
    ORDER BY rating_range
    """)
    rating_dist = cursor.fetchall()
    print("\nRating Distribution:")
    for rating_range, count in rating_dist:
        print(f"  {rating_range}: {count}")
    
    # Sample data
    cursor.execute("SELECT asin, title, price, rating FROM amazon_products LIMIT 5")
    sample_data = cursor.fetchall()
    print("\nSample Data (first 5 records):")
    for record in sample_data:
        print(f"  {record[0]}: {record[1][:30]}... | Price: {record[2]} | Rating: {record[3]}")
    
    print("\nDatabase verification complete!")

def main():
    if len(sys.argv) < 2:
        print("Usage: python csv_to_sql.py <csv_file> [database_file]")
        return
    
    csv_file = sys.argv[1]
    db_file = sys.argv[2] if len(sys.argv) > 2 else "amazon_products.db"
    
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found")
        return
    
    process_csv_file(csv_file, db_file)
    
    print(f"\nDatabase created at: {os.path.abspath(db_file)}")
    print("\nTo query the database using SQLite command line:")
    print(f"  sqlite3 {db_file}")
    print("  SELECT * FROM amazon_products LIMIT 10;")

if __name__ == "__main__":
    main()
