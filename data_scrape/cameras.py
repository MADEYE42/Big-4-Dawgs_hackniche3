import csv
import logging
import random
import time
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent  # pip install fake-useragent

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("amazon_scraper.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class AmazonScraper:
    def __init__(self, proxies=None):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.proxies = proxies or []
        self.current_proxy_index = 0
        self.max_retries = 3
        self.success_count = 0

    def get_headers(self):
        """Generate realistic browser headers"""
        return {
            "User-Agent": self.ua.random,
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.amazon.in/",
            "sec-ch-ua": '"Google Chrome";v="113", "Chromium";v="113"',
            "sec-ch-ua-platform": "Windows",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
        }

    def get_current_proxy(self):
        """Get the current proxy from the rotation list"""
        if not self.proxies:
            return None

        proxy = self.proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        return proxy

    def make_request(self, url, retry=0):
        """Make a request with retry logic and proxy rotation"""
        if retry >= self.max_retries:
            logger.error(f"Max retries reached for URL: {url}")
            return None

        # Add a variable delay between requests
        delay = random.uniform(5, 15)  # Increased delay
        time.sleep(delay)

        proxy = self.get_current_proxy()
        proxies = {"http": proxy, "https": proxy} if proxy else None

        try:
            logger.info(
                f"Requesting {url} with {'proxy: ' + proxy if proxy else 'no proxy'}"
            )

            response = self.session.get(
                url, headers=self.get_headers(), proxies=proxies, timeout=30
            )

            if response.status_code == 200:
                self.success_count += 1
                if self.success_count % 5 == 0:
                    logger.info(f"Successfully completed {self.success_count} requests")
                return response
            elif response.status_code == 503:
                logger.warning(
                    f"Service unavailable (503). Retrying with different proxy and longer delay..."
                )
                time.sleep(random.uniform(20, 40))  # Much longer delay on 503
                return self.make_request(url, retry + 1)
            elif response.status_code == 403:
                logger.warning(
                    f"Forbidden (403). Retrying with different proxy and headers..."
                )
                self.session = requests.Session()  # Reset session
                time.sleep(random.uniform(30, 60))  # Even longer delay on 403
                return self.make_request(url, retry + 1)
            else:
                logger.error(f"Unexpected status code: {response.status_code}")
                return None

        except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
            logger.error(f"Request failed: {e}")
            time.sleep(random.uniform(10, 20))
            return self.make_request(url, retry + 1)

    def scrape_amazon_products(self, url, num_pages=1):
        all_products = []
        base_url = self._normalize_url(url)

        for page in range(1, num_pages + 1):
            current_url = self._get_page_url(base_url, page)
            logger.info(f"Scraping page {page}: {current_url}")

            response = self.make_request(current_url)
            if not response:
                logger.error(f"Failed to retrieve page {page}")
                continue

            soup = BeautifulSoup(response.content, "html.parser")

            # Check for CAPTCHA
            if "captcha" in response.text.lower() or "puzzle" in response.text.lower():
                logger.error("CAPTCHA detected! Amazon is blocking our requests.")
                logger.info("Waiting for a longer period before continuing...")
                time.sleep(random.uniform(60, 120))  # Long wait on CAPTCHA
                continue

            # Get all product containers
            product_containers = soup.select(
                'div[data-component-type="s-search-result"]'
            )
            logger.info(
                f"Found {len(product_containers)} product containers on page {page}"
            )

            if not product_containers:
                logger.warning(
                    "No product containers found. The page structure might have changed."
                )

            for container in product_containers:
                try:
                    product = self._parse_product(container)
                    if product:
                        all_products.append(product)
                except Exception as e:
                    logger.error(f"Error parsing product: {e}")
                    continue

            # Longer delay between pages
            page_delay = random.uniform(10, 20)
            logger.info(
                f"Finished page {page}. Waiting {page_delay:.2f} seconds before next page..."
            )
            time.sleep(page_delay)

        return all_products

    def _normalize_url(self, url):
        """Normalize the URL to handle pagination properly"""
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        # Remove any existing page parameter
        if "page" in query_params:
            del query_params["page"]

        normalized_query = urlencode(query_params, doseq=True)
        return urlunparse(
            (
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                parsed_url.params,
                normalized_query,
                "",
            )
        )

    def _get_page_url(self, base_url, page):
        """Construct the proper pagination URL"""
        if page == 1:
            return base_url

        parsed_url = urlparse(base_url)
        query_params = parse_qs(parsed_url.query)
        query_params["page"] = [str(page)]

        new_query = urlencode(query_params, doseq=True)
        return urlunparse(
            (
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                parsed_url.params,
                new_query,
                "",
            )
        )

    def _parse_product(self, container):
        """Extract product information from a container"""
        product = {}

        # Extract ASIN
        product["asin"] = container.get("data-asin", "N/A")
        if product["asin"] == "N/A":
            logger.warning("Could not find ASIN, skipping product")
            return None

        # Extract product title with multiple fallbacks
        title = None
        title_selectors = [
            # First try h2 > a with aria-label
            lambda c: c.select_one("h2 a[aria-label]"),
            # Then h2 with aria-label
            lambda c: c.select_one("h2[aria-label]"),
            # Then try h2 > a > span
            lambda c: c.select_one("h2 a span"),
            # Then try common class names
            lambda c: c.select_one(
                ".a-size-medium.a-color-base.a-text-normal, .a-size-base-plus.a-color-base.a-text-normal"
            ),
        ]

        for selector in title_selectors:
            element = selector(container)
            if element:
                if "aria-label" in element.attrs:
                    title = element["aria-label"].strip()
                else:
                    title = element.text.strip()
                if title:
                    break

        product["title"] = title if title else "N/A"

        # Extract product URL
        url_elem = container.select_one("h2 a, a.a-link-normal.s-no-outline")
        product["url"] = (
            f"https://www.amazon.in{url_elem['href']}"
            if url_elem and "href" in url_elem.attrs
            else "N/A"
        )

        # Extract product image URL
        img_elem = container.select_one("img.s-image")
        product["image_url"] = (
            img_elem["src"] if img_elem and "src" in img_elem.attrs else "N/A"
        )

        # Extract ratings with fallbacks
        rating_selectors = [
            # Try icon with aria-label first
            lambda c: c.select_one(
                'i[class*="a-icon-star"][aria-label], span[class*="a-icon-star"][aria-label]'
            ),
            # Then try icon with alt text
            lambda c: c.select_one(
                'i[class*="a-icon-star"] span.a-icon-alt, span[class*="a-icon-star"] span.a-icon-alt'
            ),
        ]

        rating = "N/A"
        for selector in rating_selectors:
            element = selector(container)
            if element:
                if "aria-label" in element.attrs:
                    rating_text = element["aria-label"]
                    # Extract just the number from text like "4.5 out of 5 stars"
                    rating = rating_text.split(" ")[0] if rating_text else "N/A"
                else:
                    rating_text = element.text
                    rating = rating_text.split(" ")[0] if rating_text else "N/A"
                break

        product["rating"] = rating

        # Extract reviews count
        reviews_elem = container.select_one(
            "a span.s-underline-text, a[href*='customerReviews'] span"
        )
        product["reviews_count"] = reviews_elem.text.strip() if reviews_elem else "0"

        # Extract current price with fallbacks
        price_elem = container.select_one(
            "span.a-price span.a-offscreen, .a-price .a-offscreen"
        )
        product["price"] = price_elem.text.strip() if price_elem else "N/A"

        # Extract original price
        original_price_elem = container.select_one(
            "span.a-price.a-text-price span.a-offscreen, .a-price.a-text-price .a-offscreen"
        )
        product["original_price"] = (
            original_price_elem.text.strip()
            if original_price_elem
            else product["price"]
        )

        # Extract discount percentage
        discount = "N/A"
        discount_elem = container.select_one("span.a-letter-space + span")
        if discount_elem and "(" in discount_elem.text and ")" in discount_elem.text:
            discount = discount_elem.text.strip()
        else:
            # Try alternative approach
            for span in container.select("span"):
                if "(" in span.text and "%)" in span.text:
                    discount = span.text.strip()
                    break

        product["discount"] = discount

        # Check if Prime delivery is available
        prime_elem = container.select_one(
            "i.a-icon-prime, span.aok-relative.s-icon-text-medium.s-prime"
        )
        product["prime"] = "Yes" if prime_elem else "No"

        # Extract delivery date with multiple approaches
        delivery = "N/A"
        # Try different text patterns
        for text in ["Get it by", "delivery", "Delivery by"]:
            for span in container.select("span"):
                if text.lower() in span.text.lower():
                    delivery = span.text.strip()
                    break
            if delivery != "N/A":
                break

        # Try parent container
        if delivery == "N/A":
            delivery_div = container.select_one("div[data-cy='delivery-recipe']")
            if delivery_div:
                bold_text = delivery_div.select_one("span.a-color-base.a-text-bold")
                if bold_text:
                    delivery = bold_text.text.strip()

        product["delivery"] = delivery

        # Check if sponsored
        sponsored_elem = container.select_one(
            "span:contains('Sponsored'), span.puis-sponsored-label-text"
        )
        product["sponsored"] = (
            "Yes"
            if sponsored_elem and "sponsored" in sponsored_elem.text.lower()
            else "No"
        )

        # Add timestamp for when this data was collected
        product["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")

        logger.info(
            f"Extracted product: {product['title'][:50]}..."
            if product["title"] != "N/A"
            else "Failed to extract title"
        )
        return product


def save_to_csv(products, filename="amazon_products.csv"):
    if not products:
        logger.warning("No products to save.")
        return False

    # Get all possible keys from all products
    fieldnames = set()
    for product in products:
        fieldnames.update(product.keys())

    fieldnames = sorted(list(fieldnames))

    try:
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for product in products:
                writer.writerow(product)

        logger.info(f"Saved {len(products)} products to {filename}")
        return True
    except Exception as e:
        logger.error(f"Error saving to CSV: {e}")
        return False


if __name__ == "__main__":
    # Example proxy list - replace with your own proxies
    # Format: "http://username:password@ip:port" or "http://ip:port"
    proxy_list = [
        # Add your proxies here, or leave empty to use direct connection
        # "http://user:pass@proxy1.example.com:8080",
        # "http://user:pass@proxy2.example.com:8080",
    ]

    # URL to scrape - camera search page
    url = "https://www.amazon.in/s?k=cameras&rh=n%3A3404636031&ref=nb_sb_noss"

    # Number of pages to scrape
    num_pages = 5

    logger.info("Starting Amazon scraper")
    scraper = AmazonScraper(proxies=proxy_list)

    try:
        products = scraper.scrape_amazon_products(url, num_pages)
        if products:
            save_to_csv(products, "amazon_cameras.csv")
        else:
            logger.warning("No products were scraped.")
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user. Saving any collected data...")
        # Try to save whatever data we have
        save_to_csv(products, "amazon_cameras_partial.csv")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
