import requests
from bs4 import BeautifulSoup
import json
import time
import random
import re
from urllib.parse import urljoin

class AmazonBackCoverScraper:
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
        self.skipped_pages = []

    def get_user_agent(self):
        """Return a random user agent to help avoid detection"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62"
        ]
        return random.choice(user_agents)

    def get_page(self, url):
        """Make a request to Amazon with appropriate headers and delays"""
        try:
            # Random delay to avoid being blocked (2-5 seconds)
            time.sleep(random.uniform(2, 5))
            
            # Update headers with a random user agent
            self.headers['User-Agent'] = self.get_user_agent()
            
            response = self.session.get(url, headers=self.headers)
            
            if response.status_code == 503:
                print(f"Error: Received status code 503 (Service Unavailable). Skipping this page.")
                self.skipped_pages.append(url)
                return None
            
            if response.status_code == 200:
                return response.text
            else:
                print(f"Error: Received status code {response.status_code}. Skipping this page.")
                self.skipped_pages.append(url)
                return None
                
        except Exception as e:
            print(f"Error fetching URL {url}: {e}. Skipping this page.")
            self.skipped_pages.append(url)
            return None

    def extract_asin(self, product):
        """Extract ASIN from product element"""
        try:
            # Direct method - get data-asin attribute
            data_asin = product.get('data-asin')
            if data_asin:
                return data_asin
                
            # Alternative method - find ASIN in URL patterns
            links = product.select('a.a-link-normal[href*="/dp/"]')
            for link in links:
                if 'href' in link.attrs:
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
            # Primary method - h2 with title
            title_elem = product.select_one('h2 a span')
            if title_elem:
                return title_elem.text.strip()
                
            # Backup method - look for title in other elements
            title_elem = product.select_one('h2 span.a-text-normal')
            if title_elem:
                return title_elem.text.strip()
                
            # Last resort - try any span with title-related classes
            title_elem = product.select_one('.a-size-medium.a-color-base.a-text-normal, .a-size-base-plus.a-color-base.a-text-normal')
            if title_elem:
                return title_elem.text.strip()
                
            return None
        except Exception as e:
            print(f"Error extracting title: {e}")
            return None

    def extract_price(self, product):
        """Extract current price"""
        try:
            # Primary selector for current price
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
                    
            # Alternative selector for price
            price_elem = product.select_one('.a-price-whole')
            if price_elem:
                price_text = price_elem.text.strip().replace(',', '')
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
            # Look for the original price (often displayed with strikethrough)
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

    def extract_discount(self, product):
        """Extract discount percentage"""
        try:
            # Direct method - look for discount percentage on the page
            discount_elem = product.select_one('.a-color-price span, .a-color-base span:contains("off"), .s-color-discount')
            if discount_elem:
                discount_text = discount_elem.text.strip()
                # Extract percentage value
                discount_match = re.search(r'(\d+)%', discount_text)
                if discount_match:
                    return int(discount_match.group(1))
                    
            # Alternative method - calculate from original and current price
            original = self.extract_original_price(product)
            current = self.extract_price(product)
            if original and current and original > current:
                return round(((original - current) / original) * 100)
                
            return None
        except Exception as e:
            print(f"Error extracting discount: {e}")
            return None

    def extract_rating(self, product):
        """Extract product rating"""
        try:
            # Primary method - look for rating in aria-label
            rating_elem = product.select_one('.a-icon-star-small, .a-icon-star')
            if rating_elem:
                aria_label = rating_elem.get('aria-label', '')
                if aria_label:
                    rating_match = re.search(r'([0-9.]+) out of', aria_label)
                    if rating_match:
                        return float(rating_match.group(1))
                else:
                    # Try text content if aria-label not available
                    rating_text = rating_elem.get_text().strip()
                    rating_match = re.search(r'([0-9.]+) out of', rating_text)
                    if rating_match:
                        return float(rating_match.group(1))
            
            # Alternative method - look for rating in alt text
            rating_elem = product.select_one('.a-icon-alt')
            if rating_elem:
                rating_text = rating_elem.text.strip()
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
            # Primary method - look for review count link
            reviews_elem = product.select_one('a[href*="customerReviews"] span.a-size-base')
            if reviews_elem:
                reviews_text = reviews_elem.text.strip().replace(',', '')
                if reviews_text.isdigit():
                    return int(reviews_text)
            
            # Alternative method - try different selectors for review count
            reviews_elem = product.select_one('a span.s-underline-text, span.a-size-base.s-underline-text')
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
            # Primary method - look for s-image class
            img_elem = product.select_one('.s-image')
            if img_elem and 'src' in img_elem.attrs:
                return img_elem['src']
                
            # Alternative method - try any img tag
            img_elem = product.select_one('img[src*="images/I"]')
            if img_elem and 'src' in img_elem.attrs:
                return img_elem['src']
                
            return None
        except Exception as e:
            print(f"Error extracting image URL: {e}")
            return None

    def extract_url(self, product):
        """Extract product detail URL"""
        try:
            # Primary method - look for link in h2
            link_elem = product.select_one('h2 a.a-link-normal')
            if link_elem and 'href' in link_elem.attrs:
                return urljoin(self.base_url, link_elem['href'])
                
            # Alternative method - look for any link with dp in it
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
            # Look for Prime badge
            prime_elem = product.select_one('.a-icon-prime, span.s-prime')
            return prime_elem is not None
        except Exception as e:
            print(f"Error checking Prime status: {e}")
            return None

    def extract_delivery(self, product):
        """Extract delivery information"""
        try:
            # Look for delivery information
            delivery_elem = product.select_one('span[aria-label*="delivery"], span.a-color-base:contains("delivery"), span.a-text-bold:contains("delivery")')
            if delivery_elem:
                return delivery_elem.get_text().strip()
                
            # Alternative - look for any delivery text
            delivery_text = product.find(string=re.compile(r'delivery|Delivery|Get it by'))
            if delivery_text:
                # Try to get the parent element text
                if hasattr(delivery_text, 'parent'):
                    return delivery_text.parent.get_text().strip()
                return delivery_text.strip()
                
            return None
        except Exception as e:
            print(f"Error extracting delivery info: {e}")
            return None

    def check_sponsored(self, product):
        """Check if product is sponsored"""
        try:
            # Look for sponsored tag
            sponsored_elem = product.select_one('.puis-sponsored-label-text, .s-sponsored-label-text, span.a-color-secondary:contains("Sponsored")')
            return sponsored_elem is not None
        except Exception as e:
            print(f"Error checking sponsored status: {e}")
            return None

    def extract_product_data(self, product):
        """Extract all required data for a single product"""
        asin = self.extract_asin(product)
        title = self.extract_title(product)
        
        # Skip invalid products
        if not asin or not title:
            return None
            
        product_data = {
            'asin': asin,
            'title': title,
            'price': self.extract_price(product),
            'original_price': self.extract_original_price(product),
            'discount': self.extract_discount(product),
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
            # Look for next page button that's not disabled
            next_page = soup.select_one('.s-pagination-next:not(.s-pagination-disabled)')
            if next_page and 'href' in next_page.attrs:
                return urljoin(self.base_url, next_page['href'])
            return None
        except Exception as e:
            print(f"Error getting next page URL: {e}")
            return None

    def scrape_search_results(self, search_url, max_pages=15):
        """Scrape multiple pages of search results"""
        current_url = search_url
        page_count = 0
        success_count = 0
        valid_products_count = 0
        
        while current_url and page_count < max_pages:
            page_count += 1
            print(f"Scraping page {page_count}: {current_url}")
            
            html = self.get_page(current_url)
            
            if not html:
                print(f"Skipping page {page_count} due to error. Attempting to continue to next page.")
                
                # Try to construct next page URL manually
                if page_count < max_pages:
                    page_param_match = re.search(r'page=(\d+)', current_url)
                    if page_param_match:
                        current_page = int(page_param_match.group(1))
                        current_url = re.sub(r'page=\d+', f'page={current_page+1}', current_url)
                    else:
                        if '?' in current_url:
                            current_url += f'&page={page_count+1}'
                        else:
                            current_url += f'?page={page_count+1}'
                    
                    print(f"Attempting to access next page: {current_url}")
                    continue
                else:
                    break
            
            success_count += 1
            soup = BeautifulSoup(html, 'html.parser')
            
            # Look for all product containers
            products = soup.select('div[data-component-type="s-search-result"], div.s-result-item')
            print(f"Found {len(products)} product containers on this page")
            
            page_products_count = 0
            for product in products:
                product_data = self.extract_product_data(product)
                if product_data and product_data['asin']:  # Only add if we have valid data
                    self.results.append(product_data)
                    page_products_count += 1
                    valid_products_count += 1
            
            print(f"Successfully extracted data for {page_products_count} products from page {page_count}")
            
            # Get URL for next page
            next_url = self.get_next_page_url(soup)
            if not next_url:
                print("No more pages available.")
                break
                
            current_url = next_url
            
            # Optional delay between pages (in addition to the delay in get_page)
            time.sleep(random.uniform(1, 3))
        
        print(f"\nScraping summary:")
        print(f"Attempted to scrape {page_count} pages")
        print(f"Successfully scraped {success_count} pages")
        print(f"Collected data for {valid_products_count} products")
        if self.skipped_pages:
            print(f"Skipped {len(self.skipped_pages)} pages due to errors")
            
        return self.results

    def save_to_json(self, filename='amazon_mobile_back_covers.json'):
        """Save scraped data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {filename}")

    def save_to_csv(self, filename='amazon_mobile_back_covers.csv'):
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


if __name__ == "__main__":
    # Initialize the scraper
    scraper = AmazonBackCoverScraper()
    
    # URL for mobile back covers search
    search_url = "https://www.amazon.in/s?k=mobile+back+cover&crid=25XU9TQTOELDW&sprefix=mobile+back+cover%2Caps%2C256&ref=nb_sb_noss_2"
    
    # Scrape with a high max_pages value to get as many pages as possible
    # Amazon typically allows up to 15-20 pages of results for most searches
    products = scraper.scrape_search_results(search_url, max_pages=15)
    
    # Save the results to both JSON and CSV
    scraper.save_to_json('amazon_mobile_back_covers.json')
    scraper.save_to_csv('amazon_mobile_back_covers.csv')