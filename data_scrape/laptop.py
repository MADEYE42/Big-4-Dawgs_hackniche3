import requests
from bs4 import BeautifulSoup
import csv
import time
import random

def get_user_agent():
    """Return a random user agent from a predefined list to help avoid detection."""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62"
    ]
    return random.choice(user_agents)

def scrape_amazon_products(url, num_pages=1):
    """
    Scrape Amazon product listings based on the provided URL and number of pages.
    
    Args:
        url (str): The Amazon search URL to scrape
        num_pages (int): Number of pages to scrape
        
    Returns:
        list: List of dictionaries containing product information
    """
    all_products = []
    
    for page in range(1, num_pages + 1):
        if page > 1:
            # For pagination
            if '?' in url:
                current_url = f"{url}&page={page}"
            else:
                current_url = f"{url}?page={page}"
        else:
            current_url = url
        
        print(f"Scraping page {page}: {current_url}")
        
        headers = {
            "User-Agent": get_user_agent(),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Referer": "https://www.amazon.in/",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "max-age=0"
        }
        
        try:
            # Add a delay before each request to appear more human-like
            time.sleep(random.uniform(2, 5))
            
            response = requests.get(current_url, headers=headers)
            if response.status_code != 200:
                print(f"Failed to retrieve the page. Status code: {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get all product containers - updated selector for laptop search page
            product_containers = soup.select('div[data-component-type="s-search-result"]')
            
            print(f"Found {len(product_containers)} product containers on page {page}.")
            
            for container in product_containers:
                try:
                    product = {}
                    
                    # Extract ASIN (Amazon Standard Identification Number)
                    product['asin'] = container.get('data-asin', 'N/A')
                    
                    # Extract product title
                    # First check for the h2 that contains the title (based on the sample HTML)
                    title_elem = container.select_one('h2')
                    if title_elem:
                        # Look for aria-label attribute which often contains the full title
                        if 'aria-label' in title_elem.attrs:
                            product['title'] = title_elem['aria-label']
                        else:
                            # Otherwise try to find the span or a-text-normal inside h2
                            title_text_elem = title_elem.select_one('span, .a-text-normal')
                            if title_text_elem:
                                product['title'] = title_text_elem.text.strip()
                            else:
                                product['title'] = title_elem.text.strip()
                    else:
                        # Fallback methods if h2 not found
                        title_elem = container.select_one('.a-size-medium.a-color-base.a-text-normal, .a-size-base-plus.a-color-base.a-text-normal')
                        product['title'] = title_elem.text.strip() if title_elem else 'N/A'
                    
                    # Extract product URL
                    url_elem = container.select_one('h2 a')
                    if not url_elem:
                        url_elem = container.select_one('a.a-link-normal.s-no-outline')
                    
                    if url_elem and 'href' in url_elem.attrs:
                        href = url_elem['href']
                        # Handle both relative and absolute URLs
                        if href.startswith('/'):
                            product['url'] = f"https://www.amazon.in{href}"
                        else:
                            product['url'] = href
                    else:
                        product['url'] = 'N/A'
                    
                    # Extract product image URL
                    img_elem = container.select_one('img.s-image')
                    product['image_url'] = img_elem['src'] if img_elem and 'src' in img_elem.attrs else 'N/A'
                    
                    # Extract ratings - updated selector based on the sample HTML
                    rating_elem = container.select_one('i[class*="a-icon-star"], i[class*="a-star"]')
                    if rating_elem:
                        # Try to extract rating from aria-label
                        if 'aria-label' in rating_elem.attrs:
                            rating_text = rating_elem['aria-label']
                            # Extract just the number from text like "4.5 out of 5 stars"
                            product['rating'] = rating_text.split(' ')[0] if rating_text else 'N/A'
                        else:
                            # Try to extract from span with class a-icon-alt
                            rating_text = rating_elem.select_one('span.a-icon-alt')
                            product['rating'] = rating_text.text.split(' ')[0] if rating_text else 'N/A'
                    else:
                        product['rating'] = 'N/A'
                    
                    # Extract number of reviews - updated selector based on the sample HTML
                    reviews_elem = container.select_one('a span.s-underline-text')
                    if not reviews_elem:
                        reviews_elem = container.select_one('span.a-size-base.s-underline-text')
                    product['reviews_count'] = reviews_elem.text.strip() if reviews_elem else '0'
                    
                    # Extract current price - updated for laptop page format
                    price_elem = container.select_one('span.a-price span.a-offscreen')
                    if price_elem:
                        product['price'] = price_elem.text.strip()
                    else:
                        # Fallback price extractors
                        price_elem = container.select_one('.a-price .a-price-whole')
                        if price_elem:
                            product['price'] = price_elem.text.strip()
                        else:
                            product['price'] = 'N/A'
                    
                    # Extract original price (if discounted)
                    original_price_elem = container.select_one('span.a-price.a-text-price span.a-offscreen')
                    product['original_price'] = original_price_elem.text.strip() if original_price_elem else product['price']
                    
                    # Extract discount percentage - updated for laptop page
                    discount_elem = container.select_one('span.a-letter-space + span')
                    if discount_elem and '(' in discount_elem.text and ')' in discount_elem.text:
                        product['discount'] = discount_elem.text.strip()
                    else:
                        # Try alternative discount selector
                        discount_elem = container.select_one('.a-row span:contains("%")')
                        product['discount'] = discount_elem.text.strip() if discount_elem else 'N/A'
                    
                    # Check if Prime delivery is available
                    prime_elem = container.select_one('i.a-icon-prime, span.aok-relative.s-icon-text-medium.s-prime')
                    product['prime'] = 'Yes' if prime_elem else 'No'
                    
                    # Extract delivery date information - updated based on sample HTML
                    delivery_elem = container.select_one('span.a-color-base.a-text-bold')
                    if not delivery_elem:
                        delivery_elem = container.select_one('span[aria-label*="delivery"]')
                    product['delivery'] = delivery_elem.text.strip() if delivery_elem else 'N/A'
                    
                    # Extract if product is sponsored
                    sponsored_elem = container.select_one('span.a-color-secondary:contains("Sponsored")')
                    product['sponsored'] = 'Yes' if sponsored_elem else 'No'
                    
                    # Print for debugging - truncate long titles
                    print(f"Extracted product: {product['title'][:50]}..." if product['title'] != 'N/A' else "Failed to extract title")
                    
                    all_products.append(product)
                    
                except Exception as e:
                    print(f"Error parsing product: {e}")
                    continue
            
        except Exception as e:
            print(f"Error scraping page {page}: {e}")
    
    return all_products

def save_to_csv(products, filename='amazon_laptops.csv'):
    """
    Save the scraped products to a CSV file.
    
    Args:
        products (list): List of product dictionaries
        filename (str): Name of the CSV file to save
    """
    if not products:
        print("No products to save.")
        return
    
    # Get all possible keys from all products
    fieldnames = set()
    for product in products:
        fieldnames.update(product.keys())
    
    fieldnames = sorted(list(fieldnames))
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for product in products:
            writer.writerow(product)
    
    print(f"Saved {len(products)} products to {filename}")

def test_extraction_with_sample(html_content):
    """
    Test extraction with provided HTML sample.
    
    Args:
        html_content (str): HTML content to test extraction on
    """
    print("Testing extraction with provided HTML sample...")
    
    soup = BeautifulSoup(html_content, 'html.parser')
    container = soup.select_one('div[data-component-type="s-search-result"]')
    
    if not container:
        print("No product container found in the sample HTML")
        return
    
    print("\nContainer found! Testing selectors:")
    
    # Test ASIN extraction
    asin = container.get('data-asin', 'Not found')
    print(f"ASIN: {asin}")
    
    # Test title extraction
    title_elem = container.select_one('h2')
    title = "Not found"
    if title_elem:
        if 'aria-label' in title_elem.attrs:
            title = title_elem['aria-label']
        else:
            title_span = title_elem.select_one('span')
            if title_span:
                title = title_span.text.strip()
            else:
                title = title_elem.text.strip()
    print(f"Title: {title}")
    
    # Test price extraction
    price_elem = container.select_one('span.a-price span.a-offscreen')
    price = price_elem.text.strip() if price_elem else "Not found"
    print(f"Price: {price}")
    
    # Test original price extraction
    original_price_elem = container.select_one('span.a-price.a-text-price span.a-offscreen')
    original_price = original_price_elem.text.strip() if original_price_elem else "Not found"
    print(f"Original price: {original_price}")
    
    # Test rating extraction
    rating_elem = container.select_one('i[class*="a-icon-star"]')
    rating = "Not found"
    if rating_elem:
        if 'aria-label' in rating_elem.attrs:
            rating = rating_elem['aria-label']
        else:
            rating_text = rating_elem.select_one('span.a-icon-alt')
            if rating_text:
                rating = rating_text.text
    print(f"Rating: {rating}")
    
    # Test reviews count extraction
    reviews_elem = container.select_one('a span.s-underline-text')
    reviews = reviews_elem.text.strip() if reviews_elem else "Not found"
    print(f"Reviews count: {reviews}")
    
    # Test delivery extraction
    delivery_elem = container.select_one('span[aria-label*="delivery"], span.a-text-bold')
    delivery = delivery_elem.text.strip() if delivery_elem else "Not found"
    print(f"Delivery info: {delivery}")
    
    # Test prime badge
    prime_elem = container.select_one('i.a-icon-prime, span.s-prime')
    prime = "Yes" if prime_elem else "No"
    print(f"Prime: {prime}")
    
    print("\nExtraction test complete!")

if __name__ == "__main__":
    # URL to scrape - laptops search page
    url = "https://www.amazon.in/s?k=laptops&crid=1WDCNLG2RPSXG&sprefix=laptops%2Caps%2C211&ref=nb_sb_noss_2"
    
    # Number of pages to scrape
    num_pages = 2
    
    # Sample HTML for testing - use document_content from paste-2.txt
    sample_html = """
    <!-- Paste the sample HTML here -->
    """
    
    # If you have the HTML sample for testing
    test_html = """<div role="listitem" data-asin="B0DTYZ2CG8" data-component-type="s-search-result">...</div>"""
    
    if len(sample_html.strip()) > 100:  # If sample HTML is provided
        test_extraction_with_sample(sample_html)
    
    # Ask for confirmation before starting the scrape
    confirm = input("Do you want to start scraping Amazon? (y/n): ")
    if confirm.lower() == 'y':
        # Scrape the products
        products = scrape_amazon_products(url, num_pages)
        
        # Save to CSV
        if products:
            save_to_csv(products, 'amazon_laptops.csv')
    else:
        print("Scraping canceled.")