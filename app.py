from bs4 import BeautifulSoup
import json

# Read index.html file (Flipkart page source)
with open("index.html", "r", encoding="utf-8") as file:
    content = file.read()

# Parse with BeautifulSoup
soup = BeautifulSoup(content, "html.parser")

# Find all product divs
divs = soup.find_all("div", class_="cPHDOP col-12-12")

data_list = []

for index, div in enumerate(divs):
    # Extract image link
    try:
        img = div.find("img", class_="DByuf4")
        link = img["src"] if img else ""
    except:
        link = ""

    # Extract title
    try:
        title_div = div.find("div", class_="KzDlHZ")
        title = title_div.text.strip() if title_div else ""
    except:
        title = ""

    # Extract rating
    try:
        rating_div = div.find("div", class_="_5OesEi")
        rating = rating_div.text.strip() if rating_div else ""
    except:
        rating = ""

    # Extract description
    try:
        desc_div = div.find("div", class_="_6NESgJ")
        description = desc_div.text.strip() if desc_div else ""
    except:
        description = ""

    # Extract price
    try:
        price_div = div.find("div", class_="Nx9bqj _4b5DiR")
        price = price_div.text.strip() if price_div else ""
    except:
        price = ""

    # Store data
    data_list.append({
        "link": link,
        "title": title,
        "rating": rating,
        "description": description,
        "price": price
    })

# Write to data.json
with open("data.json", "w", encoding="utf-8") as json_file:
    json.dump(data_list, json_file, indent=4, ensure_ascii=False)

print(f"Extracted {len(data_list)} products. Data successfully written to data.json.")
