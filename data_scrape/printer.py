import csv
import random
import time
import re

import requests
from bs4 import BeautifulSoup


def get_user_agent():
    # Rotating user agents to avoid detection
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    ]
    return random.choice(user_agents)


def scrape_amazon_products(url, max_pages=15):
    all_products = []
    page = 1
    
    while page <= max_pages:
        # For pagination
        if page > 1:
            if "?" in url:
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
        }

        try:
            response = requests.get(current_url, headers=headers)
            if response.status_code != 200:
                print(f"Failed to retrieve the page. Status code: {response.status_code}")
                break

            soup = BeautifulSoup(response.content, "html.parser")

            # Check if we've reached the end of results
            if soup.select_one(".s-no-outline") is None and page > 1:
                print("No more results found. Stopping.")
                break

            # Get all product containers
            product_containers = soup.select('div[data-component-type="s-search-result"]')
            
            if not product_containers:
                print("No product containers found on this page. Stopping.")
                break

            for container in product_containers:
                try:
                    product = {}

                    # Extract ASIN (Amazon Standard Identification Number)
                    product["asin"] = container.get("data-asin", "N/A")

                    # Check if the product is sponsored
                    sponsored_elem = container.select_one(".puis-sponsored-label-text")
                    product["sponsored"] = "Yes" if sponsored_elem else "No"

                    # Extract product title
                    title_elem = container.select_one("h2 a span") or container.select_one("h2 span")
                    if not title_elem:
                        title_elem = container.select_one(".a-size-medium.a-color-base.a-text-normal")
                    if not title_elem:
                        title_elem = container.select_one("h2")
                    
                    product["title"] = title_elem.text.strip() if title_elem else "N/A"

                    # Extract product URL
                    url_elem = container.select_one("h2 a") or container.select_one("a.a-link-normal.s-no-outline")
                    if url_elem and 'href' in url_elem.attrs:
                        # Handle both relative and absolute URLs
                        href = url_elem['href']
                        if href.startswith('/'):
                            product["url"] = f"https://www.amazon.in{href}"
                        else:
                            product["url"] = href
                    else:
                        product["url"] = "N/A"

                    # Extract product image URL
                    img_elem = container.select_one("img.s-image")
                    product["image_url"] = img_elem["src"] if img_elem and "src" in img_elem.attrs else "N/A"

                    # Extract ratings
                    rating_elem = container.select_one('i[class*="a-icon-star"], i[class*="a-star"]')
                    if rating_elem:
                        rating_text = rating_elem.find("span", class_="a-icon-alt")
                        if rating_text:
                            # Extract just the number from "4.5 out of 5 stars"
                            rating_match = re.search(r"([0-9.]+)", rating_text.text)
                            product["rating"] = rating_match.group(1) if rating_match else "N/A"
                        else:
                            product["rating"] = "N/A"
                    else:
                        product["rating"] = "N/A"

                    # Extract number of reviews
                    reviews_elem = container.select_one("a span.s-underline-text")
                    product["reviews_count"] = reviews_elem.text.strip().replace(",", "") if reviews_elem else "0"

                    # Extract current price
                    price_elem = container.select_one("span.a-price span.a-offscreen")
                    if price_elem:
                        product["price"] = price_elem.text.strip()
                    else:
                        # Try alternative price selector
                        price_elem = container.select_one(".a-price .a-price-whole")
                        product["price"] = f"₹{price_elem.text.strip()}" if price_elem else "N/A"

                    # Extract original price (if discounted)
                    original_price_elem = container.select_one("span.a-price.a-text-price span.a-offscreen")
                    product["original_price"] = original_price_elem.text.strip() if original_price_elem else product["price"]

                    # Extract discount percentage
                    discount_elem = container.select_one("span.a-letter-space + span")
                    if discount_elem and "(" in discount_elem.text and ")" in discount_elem.text:
                        product["discount"] = discount_elem.text.strip()
                    else:
                        # Try another method to find discount
                        discount_elem = container.select_one("span:-soup-contains('% off')")
                        product["discount"] = discount_elem.text.strip() if discount_elem else "N/A"

                    # Check if Prime delivery is available
                    prime_elem = container.select_one("i.a-icon-prime")
                    product["prime"] = "Yes" if prime_elem else "No"

                    # Extract delivery date
                    delivery_elem = container.select_one("span.a-color-base.a-text-bold")
                    if delivery_elem:
                        product["delivery"] = delivery_elem.text.strip()
                    else:
                        # Try another selector for delivery info
                        delivery_elem = container.select_one("span:-soup-contains('FREE delivery')")
                        delivery_text = ""
                        if delivery_elem:
                            # Get the entire delivery text including the date
                            for elem in delivery_elem.parent.children:
                                delivery_text += elem.text.strip() + " " if hasattr(elem, 'text') else ""
                            product["delivery"] = delivery_text.strip()
                        else:
                            product["delivery"] = "N/A"

                    # Print for debugging
                    print(f"Extracted product: {product['title'][:50]}..." if product["title"] != "N/A" else "Failed to extract title")

                    all_products.append(product)

                except Exception as e:
                    print(f"Error parsing product: {e}")
                    continue

            # Check if there's a next page
            next_page = soup.select_one(".s-pagination-next:not(.s-pagination-disabled)")
            if not next_page:
                print("No more pages available.")
                break

            # Add a delay between requests to avoid being blocked
            time.sleep(random.uniform(2, 5))
            page += 1

        except Exception as e:
            print(f"Error scraping page {page}: {e}")
            break

    return all_products


def save_to_csv(products, filename="amazon_printers.csv"):
    if not products:
        print("No products to save.")
        return

    # Get all possible keys from all products
    fieldnames = set()
    for product in products:
        fieldnames.update(product.keys())

    fieldnames = sorted(list(fieldnames))

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for product in products:
            writer.writerow(product)

    print(f"Saved {len(products)} products to {filename}")


if __name__ == "__main__":
    # URL to scrape - printer search page
    url = "https://www.amazon.in/s?k=printer&crid=TINXTBF0YKTM&sprefix=printer%2Caps%2C240&ref=nb_sb_noss_2"

    # Number of pages to scrape (will stop automatically if no more pages are found)
    max_pages = 15

    # Scrape the products
    products = scrape_amazon_products(url, max_pages)

    # Save to CSV
    save_to_csv(products)