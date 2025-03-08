import os
import pandas as pd

# Folder containing CSV files (Set this to your actual directory)
folder_path = "data_scrape"  # Change this to your actual path
output_file = "merged_data.csv"  # Final merged file

# List all CSV files in the folder
csv_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]

# List to store dataframes
dfs = []

# Process each CSV file
for file in csv_files:
    file_path = os.path.join(folder_path, file)
    
    # Read CSV
    df = pd.read_csv(file_path)

    # Extract category from filename (e.g., 'amazon_phones.csv' → 'phones')
    category = file.replace("amazon_", "").replace(".csv", "")

    # Add category column
    df["category"] = category

    # Append to list
    dfs.append(df)

# Merge all DataFrames
merged_df = pd.concat(dfs, ignore_index=True)

# Save to a new CSV file
merged_df.to_csv(output_file, index=False)

print(f"✅ Merged {len(csv_files)} CSV files into {output_file} successfully!")
