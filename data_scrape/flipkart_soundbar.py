import random
import re
import sys
import time
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_user_agent():
    """Return a random user agent to avoid detection."""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    ]
    return random.choice(user_agents)


def fetch_html(url):
    """Fetch HTML content from the given URL."""
    headers = {
        "User-Agent": get_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.flipkart.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()  # Raise an exception for 4xx/5xx status codes
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {str(e)}")
        return None


def extract_next_page_url(html_content, base_url):
    """Extract the URL for the next page from the pagination section."""
    if not html_content:
        return None

    soup = BeautifulSoup(html_content, "html.parser")

    # Try to find the "Next" button
    next_link = soup.find("a", {"class": "_9QVEpD"})
    if next_link and "href" in next_link.attrs:
        return "https://www.flipkart.com" + next_link["href"]

    # Alternative: Find all page links and get the one after the current active page
    pagination_nav = soup.find("nav", {"class": "WSL9JP"})
    if pagination_nav:
        active_page = pagination_nav.find("a", {"class": "A1msZJ"})
        if (
            active_page
            and active_page.next_sibling
            and "href" in active_page.next_sibling.attrs
        ):
            return "https://www.flipkart.com" + active_page.next_sibling["href"]

    # If we can't find the next page using the above methods,
    # try extracting the current page number and construct the next page URL
    try:
        page_info = soup.find("div", {"class": "_1G0WLw"})
        if page_info:
            page_text = page_info.get_text()
            current_page_match = re.search(r"Page (\d+)", page_text)
            total_pages_match = re.search(r"of (\d+)", page_text)

            if current_page_match and total_pages_match:
                current_page = int(current_page_match.group(1))
                total_pages = int(total_pages_match.group(1))

                if current_page < total_pages:
                    # Extract the base URL and append the next page number
                    base_url_match = re.match(r"(.*?)(?:&page=\d+|$)", base_url)
                    if base_url_match:
                        base_url_without_page = base_url_match.group(1)
                        if "?" in base_url_without_page:
                            return f"{base_url_without_page}&page={current_page + 1}"
                        else:
                            return f"{base_url_without_page}?page={current_page + 1}"
    except Exception as e:
        print(f"Error extracting pagination info: {str(e)}")

    return None


def clean_title(title):
    """Clean the title by removing the last word if it ends with '...'"""
    if title and "..." in title:
        # Split the title into words
        words = title.split()

        # If the title ends with "...", remove the last word
        if words[-1] == "...":
            return " ".join(words[:-2])  # Remove last word and "..."

        # If "..." is part of the last word, remove that word
        if "..." in words[-1]:
            return " ".join(words[:-1])

        # If "..." is in the middle, keep the title as is
        return title

    return title


def extract_product_details(html_content):
    """Extract product details from the HTML content based on the new structure."""
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, "html.parser")
    products = []

    # Find all product containers with data-id attribute
    product_divs = soup.find_all("div", {"data-id": True})

    # If no product divs found, try with the slAVV4 class directly
    if not product_divs:
        product_divs = soup.find_all("div", {"class": "slAVV4"})

    for product_div in product_divs:
        try:
            product = {
                "asin": None,  # Flipkart's product ID
                "delivery": None,
                "discount": None,
                "image_url": None,
                "original_price": None,
                "price": None,
                "prime": False,  # Flipkart doesn't have Prime
                "rating": None,
                "reviews_count": None,
                "sponsored": False,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "title": None,
                "url": None,
            }

            # Extract product ID (Flipkart's equivalent of ASIN)
            if "data-id" in product_div.attrs:
                product["asin"] = product_div["data-id"]
            elif product_div.parent and "data-id" in product_div.parent.attrs:
                product["asin"] = product_div.parent["data-id"]

            # Find all anchor tags (links) within the product div
            links = product_div.find_all("a")

            # Extract product URL from the first link
            if links and "href" in links[0].attrs:
                product["url"] = "https://www.flipkart.com" + links[0]["href"]

            # Extract image URL
            img_tag = product_div.find("img", {"class": "DByuf4"})
            if img_tag and "src" in img_tag.attrs:
                product["image_url"] = img_tag["src"]

            # Extract product title
            title_tag = product_div.find("a", {"class": "wjcEIp"})
            if title_tag:
                raw_title = title_tag.get_text().strip()

                # Get the full title from the title attribute if available
                full_title = title_tag.get("title")

                # Use the full title if available, otherwise use the cleaned truncated title
                if full_title:
                    product["title"] = full_title
                else:
                    product["title"] = clean_title(raw_title)

            # Extract rating information
            rating_div = product_div.find("div", {"class": "XQDdHH"})
            if rating_div:
                rating_text = rating_div.get_text().strip()
                # Extract the numeric rating
                rating_match = re.search(r"(\d+\.?\d*)", rating_text)
                if rating_match:
                    product["rating"] = float(rating_match.group(1))

            # Extract review count
            review_span = product_div.find("span", {"class": "Wphh3N"})
            if review_span:
                review_text = review_span.text.strip()
                # Extract the review count (remove parentheses)
                review_count_match = re.search(r"(\d+(?:,\d+)*)", review_text)
                if review_count_match:
                    product["reviews_count"] = int(
                        review_count_match.group(1).replace(",", "")
                    )

            # Extract price information from the hl05eU container
            price_container = product_div.find("div", {"class": "hl05eU"})
            if price_container:
                # Current price
                current_price_div = price_container.find("div", {"class": "Nx9bqj"})
                if current_price_div:
                    price_text = current_price_div.text.strip()
                    # Remove the rupee symbol and commas
                    price_value = re.sub(r"[^\d.]", "", price_text)
                    if price_value:
                        product["price"] = float(price_value)

                # Original price
                original_price_div = price_container.find("div", {"class": "yRaY8j"})
                if original_price_div:
                    original_price_text = original_price_div.text.strip()
                    original_price_value = re.sub(r"[^\d.]", "", original_price_text)
                    if original_price_value:
                        product["original_price"] = float(original_price_value)

                # Discount
                discount_div = price_container.find("div", {"class": "UkUFwK"})
                if discount_div:
                    discount_text = discount_div.text.strip()
                    product["discount"] = discount_text

            # Extract delivery or offer information
            delivery_div = product_div.find("div", {"class": "yiggsN"})
            if delivery_div:
                product["delivery"] = delivery_div.text.strip()

            # Only add product if we have at least a title or price
            if product["title"] or product["price"]:
                products.append(product)

        except Exception as e:
            print(f"Error processing a product: {str(e)}")
            continue

    return products


def main():
    try:
        # Base URL to start scraping - updated for soundbars based on the HTML sample
        base_url = "https://www.flipkart.com/search?q=soundbar&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off"
        current_url = base_url

        all_products = []
        max_pages = 10  # Set a limit on the number of pages to scrape
        page_num = 1

        # Add command line argument support for max pages
        if len(sys.argv) > 1:
            try:
                max_pages = int(sys.argv[1])
                print(f"Will scrape up to {max_pages} pages")
            except ValueError:
                print(
                    f"Invalid max_pages value: {sys.argv[1]}. Using default: {max_pages}"
                )

        # Increased delay range between requests (5-10 seconds)
        min_delay = 5.0
        max_delay = 10.0

        while current_url and page_num <= max_pages:
            print(f"\nScraping page {page_num}: {current_url}")

            # Add a longer delay before making the first request
            if page_num > 1:
                delay = random.uniform(min_delay, max_delay)
                print(f"Waiting {delay:.2f} seconds before making request...")
                time.sleep(delay)

            html_content = fetch_html(current_url)

            if not html_content:
                print(
                    f"Failed to fetch HTML content for page {page_num}. Trying next page."
                )
                # Try to construct the next page URL if fetch failed
                page_num += 1
                current_url = f"{base_url}&page={page_num}"
                continue

            products = extract_product_details(html_content)

            if not products:
                print(
                    f"No products found on page {page_num}. The page structure might have changed or there might be anti-scraping protections."
                )
                # Still try to get the next page URL
            else:
                print(f"Found {len(products)} products on page {page_num}")
                all_products.extend(products)

            # Get the URL for the next page
            next_page_url = extract_next_page_url(html_content, current_url)

            if next_page_url == current_url:
                print(
                    "Next page URL is the same as current. Breaking loop to avoid infinite scraping."
                )
                break

            current_url = next_page_url
            page_num += 1

        print(f"\nFinished scraping {page_num-1} pages.")

        if not all_products:
            print("No products were found across all pages. Exiting.")
            return

        print(f"Found a total of {len(all_products)} products. Processing data...")

        # Save to CSV without removing any data
        csv_filename = "soundbar_products.csv"
        df = pd.DataFrame(all_products)
        df.to_csv(csv_filename, index=False)
        print(f"Successfully extracted {len(all_products)} products to {csv_filename}")

    except Exception as e:
        print(f"Error in main function: {str(e)}")
        # Save any products we've collected so far
        if "all_products" in locals() and all_products:
            print(
                f"Saving {len(all_products)} products collected before error occurred..."
            )
            try:
                df = pd.DataFrame(all_products)
                df.to_csv("soundbar_products_partial.csv", index=False)
                print("Saved partial results to soundbar_products_partial.csv")
            except Exception as save_error:
                print(f"Error saving partial results: {str(save_error)}")


# For testing with the provided HTML sample
def test_with_sample(html_content):
    """Test the extraction function with the provided HTML sample."""
    products = extract_product_details(html_content)
    if products:
        print(f"Found {len(products)} products in the sample:")
        for product in products:
            print("\n" + "-" * 80)
            for key, value in product.items():
                print(f"{key}: {value}")
    else:
        print(
            "No products found in the sample. Check if the HTML structure has changed."
        )


if __name__ == "__main__":
    main()
