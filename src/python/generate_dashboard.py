import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Define paths dynamically
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB_PATH = os.path.join(BASE_DIR, "data", "warehouse", "ecommerce_warehouse.db")
OUTPUT_DIR = os.path.join(BASE_DIR, "reports", "figures")

def create_visualizations():
    
    # Create the folders, just in case
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Connect to the data warehouse
    conn = sqlite3.connect(DB_PATH)
    
    print("Fetching data and generating charts.")
    
    # -----------------------------------------------------------------
    # CHART 1: Top 10 Revenue-Generating Countries
    # -----------------------------------------------------------------
    country_query = """
        SELECT c.country, SUM(f.total_revenue) as total_sales
        FROM fact_retail_sales f
        JOIN dim_customers c ON f.customer_id = c.customer_id
        GROUP BY c.country
        ORDER BY total_sales DESC
        LIMIT 5;
    """
    country_df = pd.read_sql_query(country_query, conn)
    
    plt.figure(figsize=(8, 5))
    plt.bar(country_df['country'], country_df['total_sales'])
    plt.title('Top 5 Markets by Total Revenue')
    plt.xlabel('Country')
    plt.ylabel('Total Sales ($)')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "top_markets.png"))
    plt.close()

    # -----------------------------------------------------------------
    # CHART 2: Month-over-Month Revenue Trend
    # -----------------------------------------------------------------
    trend_query = """
        SELECT d.year || '-' || printf('%02d', d.month) as year_month,
               SUM(f.total_revenue) as monthly_revenue
        FROM fact_retail_sales f
        JOIN dim_date d ON f.date_id = d.date_id
        GROUP BY d.year, d.month
        ORDER BY d.year, d.month;
    """
    trend_df = pd.read_sql_query(trend_query, conn)
    
    plt.figure(figsize=(10, 5))
    plt.plot(trend_df['year_month'], trend_df['monthly_revenue'], marker='o', linewidth=2)
    plt.title('Month-over-Month Revenue Trend')
    plt.xlabel('Timeline (Year-Month)')
    plt.ylabel('Revenue ($)')
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "revenue_trend.png"))
    plt.close()

    conn.close()
    print(f"Charts saved safely to: {OUTPUT_DIR}")

if __name__ == "__main__":
    create_visualizations()