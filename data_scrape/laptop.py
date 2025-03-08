import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import os
from datetime import datetime

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

def scrape_amazon_products(url, num_pages=15, max_retries=3, checkpoint_interval=5):
    """
    Scrape Amazon product listings based on the provided URL and number of pages.
    
    Args:
        url (str): The Amazon search URL to scrape
        num_pages (int): Number of pages to scrape
        max_retries (int): Maximum number of retries for failed requests
        checkpoint_interval (int): Save intermediate results every N pages
        
    Returns:
        list: List of dictionaries containing product information
    """
    all_products = []
    checkpoint_file = f"amazon_products_checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    for page in range(1, num_pages + 1):
        if page > 1:
            # For pagination
            if '?' in url:
                current_url = f"{url}&page={page}"
            else:
                current_url = f"{url}?page={page}"
        else:
            current_url = url
        
        print(f"Scraping page {page} of {num_pages}: {current_url}")
        
        headers = {
            "User-Agent": get_user_agent(),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Referer": "https://www.amazon.in/",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "max-age=0"
        }
        
        retry_count = 0
        success = False
        
        while retry_count < max_retries and not success:
            try:
                # Add a varying delay between requests to appear more human-like
                # Longer delays for Amazon to reduce chance of being blocked
                delay = random.uniform(5, 10)
                print(f"Waiting {delay:.2f} seconds before request...")
                time.sleep(delay)
                
                response = requests.get(current_url, headers=headers)
                
                if response.status_code == 200:
                    success = True
                    print(f"Successfully retrieved page {page}")
                elif response.status_code == 503 or response.status_code == 429:
                    # Service unavailable or too many requests - longer wait
                    retry_count += 1
                    wait_time = 60 * retry_count  # Increase wait time with each retry
                    print(f"Rate limited (status {response.status_code}). Waiting {wait_time} seconds before retry {retry_count}/{max_retries}...")
                    time.sleep(wait_time)
                else:
                    print(f"Failed to retrieve page. Status code: {response.status_code}")
                    retry_count += 1
                    time.sleep(10)
            except Exception as e:
                print(f"Error during request: {e}")
                retry_count += 1
                time.sleep(10)
        
        if not success:
            print(f"Failed to retrieve page {page} after {max_retries} retries. Skipping.")
            continue
        
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get all product containers
            product_containers = soup.select('div[data-component-type="s-search-result"]')
            
            print(f"Found {len(product_containers)} product containers on page {page}.")
            
            for container in product_containers:
                try:
                    product = {}
                    
                    # Extract ASIN (Amazon Standard Identification Number)
                    product['asin'] = container.get('data-asin', 'N/A')
                    
                    # Extract product title
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
                    
                    # Extract ratings
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
                    
                    # Extract number of reviews
                    reviews_elem = container.select_one('a span.s-underline-text')
                    if not reviews_elem:
                        reviews_elem = container.select_one('span.a-size-base.s-underline-text')
                    product['reviews_count'] = reviews_elem.text.strip() if reviews_elem else '0'
                    
                    # Extract current price
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
                    
                    # Extract discount percentage
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
                    
                    # Extract delivery date information
                    delivery_elem = container.select_one('span.a-color-base.a-text-bold')
                    if not delivery_elem:
                        delivery_elem = container.select_one('span[aria-label*="delivery"]')
                    product['delivery'] = delivery_elem.text.strip() if delivery_elem else 'N/A'
                    
                    # Extract if product is sponsored
                    sponsored_elem = container.select_one('span.a-color-secondary:contains("Sponsored")')
                    product['sponsored'] = 'Yes' if sponsored_elem else 'No'
                    
                    # Add page number information
                    product['page'] = page
                    
                    # Print shortened title for debugging
                    title_preview = (product['title'][:47] + '...') if len(product['title']) > 50 else product['title']
                    print(f"Extracted: {title_preview}")
                    
                    all_products.append(product)
                    
                except Exception as e:
                    print(f"Error parsing product: {e}")
                    continue
        
        except Exception as e:
            print(f"Error scraping page {page}: {e}")
        
        # Save checkpoint data periodically
        if page % checkpoint_interval == 0:
            print(f"Creating checkpoint after page {page}...")
            save_to_csv(all_products, f"checkpoint_page_{page}_{checkpoint_file}")
    
    return all_products

def save_to_csv(products, filename='amazon_laptops_15pages.csv'):
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

if __name__ == "__main__":
    # URL to scrape - laptops search page
    url = "https://www.amazon.in/s?k=laptops&crid=1WDCNLG2RPSXG&sprefix=laptops%2Caps%2C211&ref=nb_sb_noss_2"
    
    # Number of pages to scrape - now set to 15
    num_pages = 15
    
    # Ask for confirmation before starting the scrape
    print(f"This script will scrape {num_pages} pages from Amazon.")
    print("WARNING: Scraping too many pages too quickly may get your IP temporarily blocked.")
    confirm = input("Do you want to start scraping Amazon? (y/n): ")
    
    if confirm.lower() == 'y':
        # Create a timestamp for the filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"amazon_laptops_{timestamp}.csv"
        
        # Scrape the products
        products = scrape_amazon_products(url, num_pages, max_retries=3, checkpoint_interval=5)
        
        # Save to CSV
        if products:
            save_to_csv(products, filename)
            print(f"Scraping complete! Found {len(products)} products across {num_pages} pages.")
    else:
        print("Scraping canceled.")