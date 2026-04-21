

WITH job_stats AS (
    SELECT
        DATE_TRUNC(SAFE.PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', posted_date), MONTH) as month,
        title_clean as role,
        location_standardized as location,
        experience_level_standardized as experience_level,
        
        COUNT(*) as job_count,
        AVG(salary_min_usd) as avg_salary_min,
        AVG(salary_max_usd) as avg_salary_max,
        AVG((salary_min_usd + salary_max_usd) / 2) as avg_salary_mid,
        
        COUNT(DISTINCT company) as unique_companies,
        COUNT(DISTINCT source) as data_sources
        
    FROM `runagen-ai`.`runagen_silver_silver`.`jobs_cleaned`
    WHERE CAST(SAFE.PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', posted_date) AS DATE) >= DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH)
    GROUP BY month, role, location, experience_level
),

growth_calculation AS (
    SELECT
        *,
        LAG(job_count) OVER (PARTITION BY role, location ORDER BY month) as prev_month_count,
        
        CASE
            WHEN LAG(job_count) OVER (PARTITION BY role, location ORDER BY month) > 0 THEN
                ((job_count - LAG(job_count) OVER (PARTITION BY role, location ORDER BY month)) / 
                 LAG(job_count) OVER (PARTITION BY role, location ORDER BY month)) * 100
            ELSE NULL
        END as month_over_month_growth
        
    FROM job_stats
)

SELECT
    month,
    role,
    location,
    experience_level,
    job_count,
    prev_month_count,
    month_over_month_growth,
    avg_salary_min,
    avg_salary_max,
    avg_salary_mid,
    unique_companies,
    data_sources,
    
    -- Trend indicators
    CASE
        WHEN month_over_month_growth > 10 THEN 'High Growth'
        WHEN month_over_month_growth > 0 THEN 'Growing'
        WHEN month_over_month_growth < -10 THEN 'Declining'
        WHEN month_over_month_growth < 0 THEN 'Slight Decline'
        ELSE 'Stable'
    END as trend_indicator,
    
    -- Market health score (0-100)
    LEAST(100, GREATEST(0,
        (job_count / 100.0 * 30) +  -- Volume score (30%)
        (COALESCE(month_over_month_growth, 0) + 20) +  -- Growth score (20%)
        (unique_companies / 10.0 * 25) +  -- Company diversity (25%)
        (CASE WHEN avg_salary_mid > 50000 THEN 25 ELSE avg_salary_mid / 2000 END)  -- Salary score (25%)
    )) as market_health_score
    
FROM growth_calculation
ORDER BY month DESC, job_count DESC