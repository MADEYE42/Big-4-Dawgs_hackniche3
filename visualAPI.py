import os
import sys
import numpy as np
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import uuid
from PIL import Image
import base64
from io import BytesIO

# Import the ProductVisualSearch class
from product_visual_search import ProductVisualSearch

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
UPLOAD_FOLDER = 'temp_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MODEL_DIRECTORY = 'visual_search_model'
PRODUCT_DATA_PATH = 'data_scrape/merged_data.csv'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load the visual search model
try:
    visual_search = ProductVisualSearch.load_model(MODEL_DIRECTORY, PRODUCT_DATA_PATH)
    print("Visual search model loaded successfully")
except Exception as e:
    print(f"Error loading visual search model: {e}")
    sys.exit(1)

def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_image_base64(image_path):
    """Convert image to base64 string for frontend display"""
    with open(image_path, "rb") as img_file:
        img_data = img_file.read()
        return base64.b64encode(img_data).decode('utf-8')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': True,
        'indexed_images': len(visual_search.features)
    })

@app.route('/api/search', methods=['POST'])
def search():
    """
    Search for similar products based on uploaded image
    
    Accepts:
    - 'image': File upload
    - 'top_k': Number of results to return (optional, default=5)
    
    Returns:
    - JSON with search results including product info and base64 images
    """
    # Check if the post request has the file part
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
        
    file = request.files['image']
    
    # If user submits an empty file input
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    # Get number of results to return
    top_k = int(request.form.get('top_k', 5))
    
    if file and allowed_file(file.filename):
        # Generate a unique filename to avoid conflicts
        filename = str(uuid.uuid4()) + secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Perform the search
            results = visual_search.search(filepath, top_k=top_k)
            
            # Format results for JSON response
            formatted_results = []
            for i, (img_path, asin, product_info, score) in enumerate(results):
                # Get base64 of the result image
                try:
                    image_base64 = get_image_base64(img_path)
                except Exception as e:
                    image_base64 = ""
                    print(f"Error loading image {img_path}: {e}")
                
                # Add to results
                formatted_results.append({
                    'rank': i + 1,
                    'asin': asin,
                    'title': product_info['title'],
                    'price': product_info['price'],
                    'rating': product_info['rating'],
                    'category': product_info['category'],
                    'similarity_score': float(score),
                    'image_path': img_path,
                    'image_base64': image_base64
                })
            
            # Clean up the uploaded file
            try:
                os.remove(filepath)
            except:
                pass
                
            return jsonify({
                'status': 'success',
                'query_image': filename,
                'results': formatted_results
            })
            
        except Exception as e:
            # Clean up on error
            try:
                os.remove(filepath)
            except:
                pass
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file format. Allowed formats: png, jpg, jpeg'}), 400

@app.route('/api/search_by_base64', methods=['POST'])
def search_by_base64():
    """
    Search for similar products based on base64 encoded image
    
    Accepts:
    - 'image_base64': Base64 encoded image string
    - 'top_k': Number of results to return (optional, default=5)
    
    Returns:
    - JSON with search results including product info and base64 images
    """
    # Get JSON data
    data = request.get_json()
    
    if not data or 'image_base64' not in data:
        return jsonify({'error': 'No base64 image provided'}), 400
    
    # Get base64 string and remove header if present
    base64_str = data['image_base64']
    if ',' in base64_str:
        base64_str = base64_str.split(',', 1)[1]
    
    # Get number of results
    top_k = int(data.get('top_k', 5))
    
    try:
        # Decode base64 image
        img_data = base64.b64decode(base64_str)
        temp_img = BytesIO(img_data)
        
        # Save to temporary file
        filename = f"{uuid.uuid4()}.jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Convert image and save
        with Image.open(temp_img) as img:
            img.save(filepath)
        
        # Perform the search
        results = visual_search.search(filepath, top_k=top_k)
        
        # Format results for JSON response (same as in /search endpoint)
        formatted_results = []
        for i, (img_path, asin, product_info, score) in enumerate(results):
            try:
                image_base64 = get_image_base64(img_path)
            except Exception as e:
                image_base64 = ""
                print(f"Error loading image {img_path}: {e}")
            
            formatted_results.append({
                'rank': i + 1,
                'asin': asin,
                'title': product_info['title'],
                'price': product_info['price'],
                'rating': product_info['rating'],
                'category': product_info['category'],
                'similarity_score': float(score),
                'image_path': img_path,
                'image_base64': image_base64
            })
        
        # Clean up the uploaded file
        try:
            os.remove(filepath)
        except:
            pass
            
        return jsonify({
            'status': 'success',
            'results': formatted_results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    """
    Get list of all indexed products
    
    Optional query parameters:
    - page: Page number (default=1)
    - limit: Results per page (default=20)
    
    Returns:
    - JSON with paginated product list and total count
    """
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    
    # Calculate indices for pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    
    # Get subset of products
    total_products = len(visual_search.asins)
    
    # Paginate ASINs
    paginated_asins = visual_search.asins[start_idx:min(end_idx, total_products)]
    
    # Get product info for each ASIN
    products = []
    for asin in paginated_asins:
        # Find corresponding image path
        idx = visual_search.asins.index(asin)
        img_path = visual_search.image_paths[idx] if idx < len(visual_search.image_paths) else None
        
        # Get product info
        product_info = visual_search.get_product_info(asin)
        
        # Add image base64 if available
        image_base64 = ""
        if img_path and os.path.exists(img_path):
            try:
                image_base64 = get_image_base64(img_path)
            except:
                pass
        
        products.append({
            'asin': asin,
            'title': product_info['title'],
            'price': product_info['price'],
            'rating': product_info['rating'],
            'category': product_info['category'],
            'image_path': img_path,
            'image_base64': image_base64
        })
    
    return jsonify({
        'status': 'success',
        'page': page,
        'limit': limit,
        'total': total_products,
        'total_pages': (total_products + limit - 1) // limit,
        'products': products
    })

@app.route('/api/product/<asin>', methods=['GET'])
def get_product(asin):
    """
    Get detailed information about a specific product
    
    Returns:
    - JSON with product details and image
    """
    if asin not in visual_search.asins:
        return jsonify({'error': 'Product not found'}), 404
    
    # Find image path for this ASIN
    idx = visual_search.asins.index(asin)
    img_path = visual_search.image_paths[idx] if idx < len(visual_search.image_paths) else None
    
    # Get product info
    product_info = visual_search.get_product_info(asin)
    
    # Add image base64 if available
    image_base64 = ""
    if img_path and os.path.exists(img_path):
        try:
            image_base64 = get_image_base64(img_path)
        except:
            pass
    
    return jsonify({
        'status': 'success',
        'product': {
            'asin': asin,
            'title': product_info['title'],
            'price': product_info['price'],
            'rating': product_info['rating'],
            'category': product_info['category'],
            'image_path': img_path,
            'image_base64': image_base64
        }
    })

if __name__ == '__main__':
    # Create a separate file for the ProductVisualSearch class if it doesn't exist
    with open('product_visual_search.py', 'w') as f:
        print("Creating product_visual_search.py...")
        # Here you would put the original ProductVisualSearch class code
        # For brevity, it's not included here
    
    print(f"API server starting. Model loaded with {len(visual_search.features)} indexed images.")
    app.run(host='0.0.0.0', port=5000, debug=True)