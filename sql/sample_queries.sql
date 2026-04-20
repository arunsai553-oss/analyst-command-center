-- 1. Identify Top 3 Sectors by Total Revenue
SELECT 
    sector, 
    SUM(revenue) as total_revenue
FROM 
    financials
WHERE 
    date >= '2023-01-01'
GROUP BY 
    sector
ORDER BY 
    total_revenue DESC
LIMIT 3;

-- 2. Calculate average LTV to CAC per region
SELECT 
    region,
    AVG((arpu * (gross_profit / revenue)) / cac) as avg_ltv_to_cac_ratio
FROM 
    financials
GROUP BY 
    region;

-- 3. Monthly YoY Growth for a specific Company
WITH monthly_rev AS (
    SELECT 
        company, 
        EXTRACT(YEAR from date) as yr, 
        EXTRACT(MONTH from date) as mth,
        revenue
    FROM financials
)
SELECT 
    curr.company,
    curr.yr,
    curr.mth,
    curr.revenue as current_revenue,
    prev.revenue as prev_year_revenue,
    (curr.revenue - prev.revenue) / prev.revenue as yoy_growth
FROM monthly_rev curr
JOIN monthly_rev prev 
  ON curr.company = prev.company 
  AND curr.mth = prev.mth 
  AND curr.yr = prev.yr + 1;
