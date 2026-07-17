import os
import sqlite3
import pandas as pd

# Define paths dynamically relative to this script
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
DB_DIR = os.path.join(BASE_DIR, "data", "warehouse")
DB_PATH = os.path.join(DB_DIR, "ecommerce_warehouse.db")

# Look for raw dataset CSV file
csv_path = os.path.join(RAW_DATA_DIR, "raw_dataset.csv")

if not os.path.exists(csv_path):
    print(f"Error: Could not find 'raw_dataset.csv' in {RAW_DATA_DIR}")
    exit()

print("Found raw dataset. Reading into Python.")

# Read the CSV using pandas
df = pd.read_csv(csv_path)

# Connect to SQLite (Creates the database file automatically if it's missing)
print(f"Connecting to local database at: {DB_PATH}")
conn = sqlite3.connect(DB_PATH)

# Load the dataframe into a raw staging table
print("Loading data into 'raw_transactions' table...")
df.to_sql("raw_transactions", conn, if_exists="replace", index=False)

# Close connection
conn.close()
print("Raw data successfully staged inside the database.")