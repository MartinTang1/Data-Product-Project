-- =====================================================================
-- BUSINESS ANALYTICS QUERIES (STAR SCHEMA)
-- =====================================================================

-- 1. TOP 10 REVENUE-GENERATING CUSTOMERS
-- Explores customer value by joining our fact table to the customer dimension.
SELECT 
    f.customer_id,
    c.country,
    COUNT(DISTINCT f.invoice_no) as total_orders,
    SUM(f.quantity) as total_items_bought,
    ROUND(SUM(f.total_revenue), 2) as total_spend
FROM fact_retail_sales f
JOIN dim_customers c ON f.customer_id = c.customer_id
GROUP BY f.customer_id, c.country
ORDER BY total_spend DESC
LIMIT 10;


-- 2. MONTH-OVER-MONTH REVENUE GROWTH TRENDS
-- Uses a Common Table Expression (CTE) and a Window Function (LAG) 
-- to calculate financial performance over time.
WITH monthly_sales AS (    
    SELECT 
        d.year,
        d.month,
        ROUND(SUM(f.total_revenue), 2) as current_month_revenue
    FROM fact_retail_sales f
    JOIN dim_date d ON f.date_id = d.date_id
    GROUP BY d.year, d.month
)
SELECT 
    year,
    month,
    current_month_revenue,
    LAG(current_month_revenue, 1) OVER (ORDER BY year, month) as previous_month_revenue,
    ROUND(
        ((current_month_revenue - LAG(current_month_revenue, 1) OVER (ORDER BY year, month)) 
        / LAG(current_month_revenue, 1) OVER (ORDER BY year, month)) * 100, 
        2
    ) as revenue_growth_percentage
FROM monthly_sales;


-- 3. MOST POPULAR PRODUCTS BY COHORT QUARTER
-- Uses a Window Function (DENSE_RANK) to rank products by item popularity per quarter.
WITH ranked_products AS (
    SELECT 
        d.year,
        d.quarter,
        p.product_id,
        p.description,
        SUM(f.quantity) as total_quantity_sold,
        DENSE_RANK() OVER (
            PARTITION BY d.year, d.quarter 
            ORDER BY SUM(f.quantity) DESC
        ) as product_rank
    FROM fact_retail_sales f
    JOIN dim_products p ON f.product_id = p.product_id
    JOIN dim_date d ON f.date_id = d.date_id
    GROUP BY d.year, d.quarter, p.product_id, p.description
)
SELECT 
    year,
    quarter,
    product_rank,
    product_id,
    description,
    total_quantity_sold
FROM ranked_products
WHERE product_rank <= 3
ORDER BY year, quarter, product_rank;