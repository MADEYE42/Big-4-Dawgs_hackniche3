import requests
from bs4 import BeautifulSoup
import json
import time
import random
import re
from urllib.parse import urljoin

class AmazonScraper:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Referer': 'https://www.amazon.in/'
        }
        self.base_url = "https://www.amazon.in"
        self.results = []

    def get_page(self, url):
        """Make a request to Amazon with appropriate headers and delays"""
        try:
            # Random delay to avoid being blocked
            time.sleep(random.uniform(2, 5))
            response = self.session.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Error: Received status code {response.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching URL {url}: {e}")
            return None

    def extract_asin(self, product):
        """Extract ASIN from product element"""
        try:
            data_asin = product.get('data-asin')
            if data_asin:
                return data_asin
            
            # Alternative: try to get from the product URL
            link = product.select_one('a.a-link-normal[href*="/dp/"]')
            if link and 'href' in link.attrs:
                href = link['href']
                asin_match = re.search(r'/dp/([A-Z0-9]{10})/', href)
                if asin_match:
                    return asin_match.group(1)
            
            return None
        except Exception as e:
            print(f"Error extracting ASIN: {e}")
            return None

    def extract_title(self, product):
        """Extract product title"""
        try:
            title_elem = product.select_one('h2 a span, h2 span')
            if title_elem:
                return title_elem.text.strip()
            return None
        except Exception as e:
            print(f"Error extracting title: {e}")
            return None

    def extract_price(self, product):
        """Extract current price"""
        try:
            price_elem = product.select_one('.a-price .a-offscreen')
            if price_elem:
                price_text = price_elem.text.strip()
                # Remove currency symbol and commas
                price_text = price_text.replace('₹', '').replace(',', '')
                # Try to convert to float
                try:
                    return float(price_text)
                except ValueError:
                    return price_text
            return None
        except Exception as e:
            print(f"Error extracting price: {e}")
            return None

    def extract_original_price(self, product):
        """Extract original price (before discount)"""
        try:
            orig_price_elem = product.select_one('.a-price.a-text-price .a-offscreen')
            if orig_price_elem:
                price_text = orig_price_elem.text.strip()
                # Remove currency symbol and commas
                price_text = price_text.replace('₹', '').replace(',', '')
                # Try to convert to float
                try:
                    return float(price_text)
                except ValueError:
                    return price_text
            return None
        except Exception as e:
            print(f"Error extracting original price: {e}")
            return None

    def calculate_discount(self, original, current):
        """Calculate discount percentage"""
        if original and current and original > current:
            return round(((original - current) / original) * 100)
        return None

    def extract_rating(self, product):
        """Extract product rating"""
        try:
            rating_elem = product.select_one('.a-icon-star-small, .a-icon-star')
            if rating_elem:
                rating_text = rating_elem.get_text().strip()
                rating_match = re.search(r'([0-9.]+) out of', rating_text)
                if rating_match:
                    return float(rating_match.group(1))
            return None
        except Exception as e:
            print(f"Error extracting rating: {e}")
            return None

    def extract_reviews_count(self, product):
        """Extract number of reviews"""
        try:
            reviews_elem = product.select_one('a[href*="customerReviews"] span, .a-size-base:not(.a-color-secondary)')
            if reviews_elem:
                reviews_text = reviews_elem.text.strip().replace(',', '')
                if reviews_text.isdigit():
                    return int(reviews_text)
            return None
        except Exception as e:
            print(f"Error extracting reviews count: {e}")
            return None

    def extract_image_url(self, product):
        """Extract product image URL"""
        try:
            img_elem = product.select_one('.s-image')
            if img_elem and 'src' in img_elem.attrs:
                return img_elem['src']
            return None
        except Exception as e:
            print(f"Error extracting image URL: {e}")
            return None

    def extract_url(self, product):
        """Extract product detail URL"""
        try:
            link_elem = product.select_one('a.a-link-normal[href*="/dp/"]')
            if link_elem and 'href' in link_elem.attrs:
                return urljoin(self.base_url, link_elem['href'])
            return None
        except Exception as e:
            print(f"Error extracting URL: {e}")
            return None

    def check_prime(self, product):
        """Check if product has Prime delivery"""
        try:
            prime_elem = product.select_one('.a-icon-prime')
            return prime_elem is not None
        except Exception as e:
            print(f"Error checking Prime status: {e}")
            return None

    def extract_delivery(self, product):
        """Extract delivery information"""
        try:
            delivery_elem = product.select_one('.a-color-base:contains("delivery")')
            if delivery_elem:
                return delivery_elem.get_text().strip()
            return None
        except Exception as e:
            print(f"Error extracting delivery info: {e}")
            return None

    def check_sponsored(self, product):
        """Check if product is sponsored"""
        try:
            sponsored_elem = product.select_one('.puis-sponsored-label-text, .s-sponsored-label-text')
            return sponsored_elem is not None
        except Exception as e:
            print(f"Error checking sponsored status: {e}")
            return None

    def extract_product_data(self, product):
        """Extract all required data for a single product"""
        asin = self.extract_asin(product)
        title = self.extract_title(product)
        price = self.extract_price(product)
        original_price = self.extract_original_price(product)
        
        product_data = {
            'asin': asin,
            'title': title,
            'price': price,
            'original_price': original_price,
            'discount': self.calculate_discount(original_price, price),
            'rating': self.extract_rating(product),
            'reviews_count': self.extract_reviews_count(product),
            'image_url': self.extract_image_url(product),
            'url': self.extract_url(product),
            'prime': self.check_prime(product),
            'delivery': self.extract_delivery(product),
            'sponsored': self.check_sponsored(product)
        }
        
        return product_data

    def get_next_page_url(self, soup):
        """Get URL for the next page"""
        try:
            next_page = soup.select_one('.s-pagination-next:not(.s-pagination-disabled)')
            if next_page and 'href' in next_page.attrs:
                return urljoin(self.base_url, next_page['href'])
            return None
        except Exception as e:
            print(f"Error getting next page URL: {e}")
            return None

    def scrape_search_results(self, search_url, max_pages=5):
        """Scrape multiple pages of search results"""
        current_url = search_url
        page_count = 0
        
        while current_url and page_count < max_pages:
            print(f"Scraping page {page_count + 1}: {current_url}")
            html = self.get_page(current_url)
            
            if not html:
                print("Failed to fetch page. Stopping.")
                break
                
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find all product containers
            products = soup.select('div[data-component-type="s-search-result"]')
            print(f"Found {len(products)} products on this page")
            
            for product in products:
                product_data = self.extract_product_data(product)
                if product_data['asin']:  # Only add if we have a valid ASIN
                    self.results.append(product_data)
            
            # Get URL for next page
            current_url = self.get_next_page_url(soup)
            page_count += 1
            
            if not current_url:
                print("No more pages available.")
                break
        
        print(f"Scraped a total of {len(self.results)} products across {page_count} pages")
        return self.results

    def save_to_json(self, filename='amazon_products.json'):
        """Save scraped data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {filename}")

    def save_to_csv(self, filename='amazon_products.csv'):
        """Save scraped data to CSV file"""
        if not self.results:
            print("No data to save")
            return
        
        import csv
        
        keys = self.results[0].keys()
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f, keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.results)
        
        print(f"Data saved to {filename}")


# Example usage
if __name__ == "__main__":
    # Initialize the scraper
    scraper = AmazonScraper()
    
    # URL for television search results
    search_url = "https://www.amazon.in/s?k=television&crid=34918QN5GMRH4&sprefix=televisio%2Caps%2C330&ref=nb_sb_noss_2"
    
    # Scrape multiple pages (adjust max_pages as needed)
    products = scraper.scrape_search_results(search_url, max_pages=5)
    
    # Save the results
    scraper.save_to_json()
    scraper.save_to_csv()