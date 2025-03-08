import csv
import random
import time

import requests
from bs4 import BeautifulSoup

# List of different User-Agent headers to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/537.36",
]


def scrape_amazon_products(base_url, num_pages=1):
    all_products = []

    for page in range(1, num_pages + 1):
        # Handle pagination
        if "?" in base_url:
            current_url = f"{base_url}&page={page}"
        else:
            current_url = f"{base_url}?page={page}"

        headers = {
            "User-Agent": random.choice(USER_AGENTS),  # Rotate User-Agent
            "Accept-Language": "en-US,en;q=0.9",
        }

        print(f"Scraping page {page}: {current_url}")

        try:
            response = requests.get(current_url, headers=headers, timeout=10)

            if response.status_code == 503:
                print(
                    f"⚠️  Amazon blocked the request (503). Retrying with a new User-Agent..."
                )
                time.sleep(random.uniform(5, 10))
                continue  # Skip this page and try again in the next iteration

            if response.status_code != 200:
                print(
                    f"Failed to retrieve the page. Status code: {response.status_code}"
                )
                continue

            soup = BeautifulSoup(response.content, "html.parser")
            product_containers = soup.select(
                'div[data-component-type="s-search-result"]'
            )

            for container in product_containers:
                try:
                    product = {}

                    # ASIN
                    product["asin"] = container.get("data-asin", "N/A").strip()

                    # Title - Try multiple selectors and approaches
                    # Approach 1: Using multiple potential class combinations
                    title_selectors = [
                        "h2 a span",  # Most common structure
                        "h2 span",
                        ".a-size-medium.a-color-base.a-text-normal",
                        ".a-size-base-plus.a-color-base.a-text-normal",
                        ".a-size-mini.a-spacing-none.a-color-base.s-line-clamp-2",
                        ".a-size-mini span",
                        ".a-link-normal .a-text-normal",
                    ]

                    # Try each selector until we find one that works
                    title_elem = None
                    for selector in title_selectors:
                        title_elem = container.select_one(selector)
                        if title_elem and title_elem.text.strip():
                            product["title"] = title_elem.text.strip()
                            break

                    # Approach 2: If all selectors fail, try getting it from h2 directly
                    if "title" not in product or not product["title"]:
                        h2_elem = container.select_one("h2")
                        if h2_elem:
                            product["title"] = h2_elem.text.strip()

                    # Approach 3: If still no title, try aria-label attribute
                    if "title" not in product or not product["title"]:
                        link_with_aria = container.select_one("a[aria-label]")
                        if link_with_aria and "aria-label" in link_with_aria.attrs:
                            product["title"] = link_with_aria["aria-label"].strip()

                    # Final fallback
                    if "title" not in product or not product["title"]:
                        product["title"] = "N/A"

                    # Debug the title extraction
                    print(
                        f"Title found: {product['title'][:50]}..."
                        if product["title"] != "N/A"
                        else "No title found!"
                    )

                    # URL
                    url_elem = container.select_one("h2 a")
                    if not url_elem:
                        url_elem = container.select_one("a.a-link-normal.s-no-outline")
                    product["url"] = (
                        f"https://www.amazon.in{url_elem['href']}"
                        if url_elem and "href" in url_elem.attrs
                        else "N/A"
                    )

                    # Image URL
                    img_elem = container.select_one("img.s-image")
                    product["image_url"] = (
                        img_elem["src"]
                        if img_elem and "src" in img_elem.attrs
                        else "N/A"
                    )

                    # Price
                    price_elem = container.select_one("span.a-price > span.a-offscreen")
                    product["price"] = price_elem.text.strip() if price_elem else "N/A"

                    # Original Price
                    original_price_elem = container.select_one(
                        "span.a-text-price > span.a-offscreen"
                    )
                    product["original_price"] = (
                        original_price_elem.text.strip()
                        if original_price_elem
                        else product["price"]
                    )

                    # Discount Calculation
                    if product["original_price"] != "N/A" and product["price"] != "N/A":
                        try:
                            orig_price = float(
                                product["original_price"]
                                .replace("₹", "")
                                .replace(",", "")
                                .strip()
                            )
                            current_price = float(
                                product["price"]
                                .replace("₹", "")
                                .replace(",", "")
                                .strip()
                            )
                            discount = round(
                                ((orig_price - current_price) / orig_price) * 100, 2
                            )
                            product["discount"] = f"{discount}%"
                        except ValueError:
                            product["discount"] = "N/A"
                    else:
                        product["discount"] = "N/A"

                    # Rating
                    rating_elem = container.select_one("span.a-icon-alt")
                    if not rating_elem:
                        rating_elem = container.select_one(
                            'i[class*="a-icon-star"] span'
                        )
                    product["rating"] = (
                        rating_elem.text.split()[0] if rating_elem else "N/A"
                    )

                    # Reviews Count
                    reviews_elem = container.select_one("span.s-underline-text")
                    product["reviews_count"] = (
                        reviews_elem.text.strip().replace(",", "")
                        if reviews_elem
                        else "0"
                    )

                    # Prime Eligibility
                    prime_elem = container.select_one("i.a-icon-prime")
                    product["prime"] = "Yes" if prime_elem else "No"

                    # Delivery Information
                    delivery_elem = container.select_one(
                        "span.a-color-base.a-text-bold"
                    )
                    product["delivery"] = (
                        delivery_elem.text.strip() if delivery_elem else "N/A"
                    )

                    all_products.append(product)

                except Exception as e:
                    print(f"Error parsing product: {e}")
                    continue

            # Random delay to avoid getting blocked
            time.sleep(random.uniform(3, 8))

        except Exception as e:
            print(f"Error scraping page {page}: {e}")

    return all_products


def save_to_csv(products, filename="amazon_products.csv"):
    if not products:
        print("No products to save.")
        return

    fieldnames = sorted(
        list(set(key for product in products for key in product.keys()))
    )

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products)

    print(f"✅ Saved {len(products)} products to {filename}")


if __name__ == "__main__":
    search_url = "https://www.amazon.in/s?k=bluetooth+headphones&i=computers&crid=1ZIPJ3QI2RUNW&sprefix=bluetooth+headphone%2Ccomputers%2C231&ref=nb_sb_noss_2"
    num_pages = 15

    products = scrape_amazon_products(search_url, num_pages)
    save_to_csv(products, filename="amazon_bluetooth_headphones.csv")
