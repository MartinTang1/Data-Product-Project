-- Dimension Table: Customers WHO and WHERE
CREATE TABLE IF NOT EXISTS dim_customers (
    customer_id TEXT PRIMARY KEY,
    country TEXT
);

-- Dimension Table: Products WHAT
CREATE TABLE IF NOT EXISTS dim_products (
    product_id TEXT PRIMARY KEY,
    description TEXT
);

-- Dimension Table: Date WHEN
CREATE TABLE IF NOT EXISTS dim_date (
    date_id TEXT PRIMARY KEY,       -- Format: YYYYMMDD
    full_date TEXT,
    day INTEGER,
    month INTEGER,
    year INTEGER,
    quarter INTEGER
);

-- Central Fact Table: Sales Transactions
CREATE TABLE IF NOT EXISTS fact_retail_sales (
    sales_id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_no TEXT,
    customer_id TEXT,
    product_id TEXT,
    date_id TEXT,
    quantity INTEGER,
    unit_price REAL,
    total_revenue REAL,
    FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES dim_products(product_id),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id)
);