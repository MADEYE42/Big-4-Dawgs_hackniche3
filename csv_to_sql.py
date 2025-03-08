import csv
import re

# Define table name
TABLE_NAME = "amazon_products"

# Define column names and data types (excluding dropped columns)
COLUMN_TYPES = {
    "asin": "VARCHAR(20) PRIMARY KEY",
    "delivery": "TEXT",
    "discount": "VARCHAR(50)",
    "image_url": "TEXT",
    "original_price": "DECIMAL(10,2)",
    "price": "DECIMAL(10,2)",
    "rating": "DECIMAL(3,2)",
    "sponsored": "BOOLEAN",
    "title": "TEXT",
    "url": "TEXT",
    "category": "TEXT",
}


def preprocess_value(column_name, value):
    """Process values before insertion to handle special cases"""
    value = value.strip() if isinstance(value, str) else value

    # Convert 'Yes'/'No' values to 1/0 for the sponsored column
    if column_name == "sponsored":
        return "1" if str(value).lower() in ["yes", "true", "1"] else "0"

    # Remove currency symbols and commas for decimal columns
    if column_name in ["original_price", "price"]:
        value = re.sub(r"[^\d.]", "", value)  # Remove non-numeric characters except '.'
        return f"{float(value):.2f}" if value else "NULL"  # Convert to float and format

    # Escape single quotes in text fields
    if isinstance(value, str):
        value = value.replace("'", "''")  # Escape single quotes for MySQL

    return f"'{value}'" if value else "NULL"


def generate_sql(csv_filename, sql_filename):
    """Generate SQL file from CSV, removing duplicate ASINs"""

    unique_asins = set()  # Track unique ASINs to remove duplicates

    with open(csv_filename, newline="", encoding="utf-8") as csvfile, open(
        sql_filename, "w", encoding="utf-8"
    ) as sqlfile:
        reader = csv.DictReader(csvfile)

        # Create table SQL
        sqlfile.write(f"DROP TABLE IF EXISTS {TABLE_NAME};\n")
        sqlfile.write(f"CREATE TABLE {TABLE_NAME} (\n")
        sqlfile.write(
            ",\n".join([f"  {col} {dtype}" for col, dtype in COLUMN_TYPES.items()])
        )
        sqlfile.write("\n);\n\n")

        # Insert data
        for row in reader:
            asin = row["asin"].strip()  # Get ASIN and remove spaces
            if asin in unique_asins:
                continue  # Skip duplicate ASINs
            unique_asins.add(asin)

            values = [preprocess_value(col, row[col]) for col in COLUMN_TYPES.keys()]
            sqlfile.write(
                f"INSERT INTO {TABLE_NAME} ({', '.join(COLUMN_TYPES.keys())}) VALUES ({', '.join(values)});\n"
            )


# Usage
generate_sql("./data_scrape/merged_data.csv", "amazon_products.sql")
