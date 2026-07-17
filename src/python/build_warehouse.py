import os
import sqlite3
import pandas as pd

# Dynamically locate the database and schema files relative to this script
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB_PATH = os.path.join(BASE_DIR, "data", "warehouse", "ecommerce_warehouse.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "src", "sql", "schema.sql")

def build_warehouse():
    # Connect to the existing SQLite database file
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Execute schema.sql to build the empty star schema tables
    print("Creating empty Star Schema tables from schema.sql.")
    with open(SCHEMA_PATH, 'r') as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    conn.commit()
    
    # Read our raw staged data out of the database into pandas
    print("Loading raw staging data for transformation.")
    raw_df = pd.read_sql_query("SELECT * FROM raw_transactions", conn)
    
    # Data Cleaning: Drop entries missing vital identifiers that link tables
    raw_df = raw_df.dropna(subset=['CustomerID', 'StockCode', 'InvoiceDate'])
    
    # Clean up Customer IDs: Convert float decimals (12345.0) to clean integers, then strings ("12345")
    raw_df['CustomerID'] = raw_df['CustomerID'].astype(int).astype(str)
    raw_df['StockCode'] = raw_df['StockCode'].astype(str)
    
    # Standardize our timestamp format and generate a clean YYYYMMDD date key
    raw_df['InvoiceDatetime'] = pd.to_datetime(raw_df['InvoiceDate'])
    raw_df['date_id'] = raw_df['InvoiceDatetime'].dt.strftime('%Y%m%d')
    
    # Populate dim_customers (Extract only unique customer profiles)
    print("Extracting and populating dim_customers.")
    customers = raw_df[['CustomerID', 'Country']].drop_duplicates(subset=['CustomerID']).copy()
    customers.columns = ['customer_id', 'country']
    customers.to_sql('dim_customers', conn, if_exists='replace', index=False)
    
    # Populate dim_products (Extract only unique catalog items)
    print("Extracting and populating dim_products.")
    products = raw_df[['StockCode', 'Description']].drop_duplicates(subset=['StockCode']).copy()
    products.columns = ['product_id', 'description']
    products.to_sql('dim_products', conn, if_exists='replace', index=False)
    
    # Populate dim_date (Deconstruct timestamps into explicit dimensional rows)
    print("Deconstructing and populating dim_date.")
    dates = pd.DataFrame()
    dates['date_id'] = raw_df['date_id']
    dates['full_date'] = raw_df['InvoiceDatetime'].dt.date
    dates['day'] = raw_df['InvoiceDatetime'].dt.day
    dates['month'] = raw_df['InvoiceDatetime'].dt.month
    dates['year'] = raw_df['InvoiceDatetime'].dt.year
    dates['quarter'] = raw_df['InvoiceDatetime'].dt.quarter
    dates = dates.drop_duplicates(subset=['date_id'])
    dates.to_sql('dim_date', conn, if_exists='replace', index=False)
    
    # Populate fact_retail_sales (Perform business calculations inline)
    print("Computing metrics and populating fact_retail_sales.")
    fact_sales = pd.DataFrame()
    fact_sales['invoice_no'] = raw_df['InvoiceNo'].astype(str)
    fact_sales['customer_id'] = raw_df['CustomerID']
    fact_sales['product_id'] = raw_df['StockCode']
    fact_sales['date_id'] = raw_df['date_id']
    fact_sales['quantity'] = raw_df['Quantity'].astype(int)
    fact_sales['unit_price'] = raw_df['UnitPrice'].astype(float)
    # The actual business value addition: calculating total sales revenue row-by-row
    fact_sales['total_revenue'] = fact_sales['quantity'] * fact_sales['unit_price']
    
    fact_sales.to_sql('fact_retail_sales', conn, if_exists='replace', index=False)
    
    # Commit changes and safely close the warehouse connection
    conn.commit()
    conn.close()
    print("The Star Schema Warehouse is fully built and populated.")

if __name__ == "__main__":
    build_warehouse()