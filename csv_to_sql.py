import csv
import os
import re


def clean_column_name(name):
    """Clean column names to make them SQL-friendly"""
    # Replace special characters with underscores
    return re.sub(r"[^a-zA-Z0-9_]", "_", name.lower())


def detect_data_type(value):
    """Simple data type detection for SQL columns"""
    if value is None or value == "":
        return "TEXT"

    # Try to convert to integer
    try:
        int(value)
        return "INTEGER"
    except ValueError:
        pass

    # Try to convert to float
    try:
        float(value)
        return "REAL"
    except ValueError:
        pass

    # Check if it might be a date (simple check)
    if re.match(r"\d{4}-\d{2}-\d{2}", value):
        return "DATE"

    # Default to TEXT
    return "TEXT"


def csv_to_sql(csv_file, output_sql_file="output.sql", table_name="amazon_products"):
    """
    Convert CSV file to SQL commands and save to an .sql file
    """
    # Read CSV file
    with open(csv_file, "r", encoding="utf-8") as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader)  # Get column names from first row

        # Clean column names
        clean_headers = [clean_column_name(header) for header in headers]

        # Read first row to determine data types
        try:
            first_row = next(csv_reader)
            file.seek(0)  # Reset file pointer
            next(csv_reader)  # Skip header row again
        except StopIteration:
            first_row = [""] * len(headers)

        # Determine column types based on first row
        column_types = [detect_data_type(value) for value in first_row]

        # Create SQL file
        with open(output_sql_file, "w", encoding="utf-8") as sql_file:
            # Write DROP TABLE IF EXISTS statement
            sql_file.write(f"DROP TABLE IF EXISTS {table_name};\n\n")

            # Write CREATE TABLE statement
            sql_file.write(f"CREATE TABLE {table_name} (\n")

            # Add id column as primary key
            sql_file.write("    id INTEGER PRIMARY KEY AUTOINCREMENT,\n")

            # Add columns with detected data types
            for i, (header, data_type) in enumerate(zip(clean_headers, column_types)):
                sql_file.write(f"    {header} {data_type}")
                if i < len(headers) - 1:
                    sql_file.write(",")
                sql_file.write("\n")

            sql_file.write(");\n\n")

            # Write INSERT statements for each row
            for row in csv_reader:
                # Clean data values and handle quotes for SQL
                values = []
                for val in row:
                    # Replace single quotes with two single quotes for SQL
                    val = val.replace("'", "''")
                    values.append(f"'{val}'")

                sql_file.write(
                    f"INSERT INTO {table_name} ({', '.join(clean_headers)}) VALUES ({', '.join(values)});\n"
                )

    print(f"SQL file created successfully: {output_sql_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert CSV file to SQL commands")
    parser.add_argument("csv_file", help="Input CSV file")
    parser.add_argument(
        "--output",
        "-o",
        default="output.sql",
        help="Output SQL file (default: output.sql)",
    )
    parser.add_argument(
        "--table",
        "-t",
        default="amazon_products",
        help="Table name (default: amazon_products)",
    )

    args = parser.parse_args()

    if not os.path.exists(args.csv_file):
        print(f"Error: CSV file '{args.csv_file}' not found")
    else:
        csv_to_sql(args.csv_file, args.output, args.table)
