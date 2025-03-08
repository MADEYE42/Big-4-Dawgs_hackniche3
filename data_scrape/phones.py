import csv
import random
import time

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


def scrape_amazon_products(url, num_pages=1):
    all_products = []

    for page in range(1, num_pages + 1):
        if page > 1:
            # For pagination
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
                print(
                    f"Failed to retrieve the page. Status code: {response.status_code}"
                )
                continue

            soup = BeautifulSoup(response.content, "html.parser")

            # Get all product containers
            product_containers = soup.select(
                'div[data-component-type="s-search-result"]'
            )

            for container in product_containers:
                try:
                    product = {}

                    # Extract ASIN (Amazon Standard Identification Number)
                    product["asin"] = container.get("data-asin", "N/A")

                    # Extract product title - FIXED SELECTOR
                    # Try multiple possible selectors for the title
                    title_elem = None
                    # First attempt - look for h2 with the product title
                    title_elem = container.select_one("h2")
                    if title_elem:
                        # Look for the span that contains the actual text
                        span_elem = title_elem.select_one("span")
                        if span_elem:
                            product["title"] = span_elem.text.strip()
                        else:
                            # If no span, try getting text directly from h2
                            product["title"] = title_elem.text.strip()
                    else:
                        # Second attempt - different structure
                        title_elem = container.select_one(
                            ".a-size-medium.a-color-base.a-text-normal"
                        )
                        if title_elem:
                            product["title"] = title_elem.text.strip()
                        else:
                            # Third attempt - try finding any element with title-like class names
                            title_elem = container.select_one(
                                "a-size-base-plus, .a-text-normal, .s-title"
                            )
                            product["title"] = (
                                title_elem.text.strip() if title_elem else "N/A"
                            )

                    # Extract product URL
                    url_elem = container.select_one("h2 a")
                    if not url_elem:
                        url_elem = container.select_one("a.a-link-normal.s-no-outline")
                    product["url"] = (
                        f"https://www.amazon.in{url_elem['href']}"
                        if url_elem and "href" in url_elem.attrs
                        else "N/A"
                    )

                    # Extract product image URL
                    img_elem = container.select_one("img.s-image")
                    product["image_url"] = (
                        img_elem["src"]
                        if img_elem and "src" in img_elem.attrs
                        else "N/A"
                    )

                    # Extract ratings
                    rating_elem = container.select_one(
                        'i[class*="a-icon-star"], i[class*="a-star"]'
                    )
                    if rating_elem:
                        rating_text = rating_elem.find("span", class_="a-icon-alt")
                        product["rating"] = (
                            rating_text.text.split(" ")[0] if rating_text else "N/A"
                        )
                    else:
                        product["rating"] = "N/A"

                    # Extract number of reviews
                    reviews_elem = container.select_one("a span.s-underline-text")
                    product["reviews_count"] = (
                        reviews_elem.text.strip() if reviews_elem else "0"
                    )

                    # Extract current price
                    price_elem = container.select_one("span.a-price span.a-offscreen")
                    product["price"] = price_elem.text.strip() if price_elem else "N/A"

                    # Extract original price (if discounted)
                    original_price_elem = container.select_one(
                        "span.a-price.a-text-price span.a-offscreen"
                    )
                    product["original_price"] = (
                        original_price_elem.text.strip()
                        if original_price_elem
                        else product["price"]
                    )

                    # Extract discount percentage
                    discount_elem = container.select_one("span.a-letter-space + span")
                    product["discount"] = (
                        discount_elem.text.strip()
                        if discount_elem
                        and "(" in discount_elem.text
                        and ")" in discount_elem.text
                        else "N/A"
                    )

                    # Check if Prime delivery is available
                    prime_elem = container.select_one("i.a-icon-prime")
                    product["prime"] = "Yes" if prime_elem else "No"

                    # Extract delivery date
                    delivery_elem = container.select_one(
                        "span.a-color-base.a-text-bold"
                    )
                    product["delivery"] = (
                        delivery_elem.text.strip() if delivery_elem else "N/A"
                    )

                    # Print for debugging
                    print(
                        f"Extracted product: {product['title'][:50]}..."
                        if product["title"] != "N/A"
                        else "Failed to extract title"
                    )

                    all_products.append(product)

                except Exception as e:
                    print(f"Error parsing product: {e}")
                    continue

            # Add a delay between requests to avoid being blocked
            time.sleep(random.uniform(2, 5))

        except Exception as e:
            print(f"Error scraping page {page}: {e}")

    return all_products


def save_to_csv(products, filename="amazon_products.csv"):
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


def test_with_sample_html(html_content):
    """
    Test the extraction with the provided HTML sample
    """
    soup = BeautifulSoup(html_content, "html.parser")
    container = soup.select_one('div[data-component-type="s-search-result"]')

    if not container:
        print("No product container found in the sample HTML")
        return

    print("Testing title extraction with sample HTML...")

    # Try multiple approaches to extract the title
    # Approach 1: Direct h2 > span
    title_elem1 = container.select_one("h2 span")
    print(
        f"Approach 1 (h2 > span): {title_elem1.text.strip() if title_elem1 else 'Not found'}"
    )

    # Approach 2: Look for specific class
    title_elem2 = container.select_one(".a-size-medium.a-color-base.a-text-normal")
    print(
        f"Approach 2 (class): {title_elem2.text.strip() if title_elem2 else 'Not found'}"
    )

    # Approach 3: Direct from h2
    title_elem3 = container.select_one("h2")
    print(
        f"Approach 3 (h2): {title_elem3.text.strip() if title_elem3 else 'Not found'}"
    )

    # Approach 4: Find aria-label in h2
    title_elem4 = container.select_one("h2[aria-label]")
    print(
        f"Approach 4 (aria-label): {title_elem4['aria-label'] if title_elem4 and 'aria-label' in title_elem4.attrs else 'Not found'}"
    )


if __name__ == "__main__":
    # URL to scrape - smartphones search page
    url = "https://www.amazon.in/s?k=smartphones&i=electronics&crid=MU2BOMQCUT3U&sprefix=smartphone%2Celectronics%2C194&ref=nb_sb_noss_2"

    # Number of pages to scrape
    num_pages = 2

    # If you have sample HTML for testing
    sample_html = """
    <!-- Your pasted HTML here -->
    """

    if len(sample_html.strip()) > 100:  # If sample HTML is provided
        test_with_sample_html(sample_html)

    # Scrape the products
    products = scrape_amazon_products(url, num_pages)

    # Save to CSV
    save_to_csv(products)
