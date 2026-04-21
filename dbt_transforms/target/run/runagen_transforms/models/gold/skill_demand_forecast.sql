
  
    

    create or replace table `runagen-ai`.`runagen_silver_gold`.`skill_demand_forecast`
      
    
    

    OPTIONS()
    as (
      

WITH skill_extraction AS (
    -- Extract skills mentioned in job descriptions
    SELECT
        j.job_id,
        j.posted_date,
        j.title_clean as role,
        j.location_standardized as location,
        s.skill_name,
        s.skill_category
    FROM `runagen-ai`.`runagen_silver_silver`.`jobs_cleaned` j
    CROSS JOIN `runagen-ai`.`runagen_silver_silver`.`skills_standardized` s
    WHERE REGEXP_CONTAINS(LOWER(j.description_clean), LOWER(s.skill_name))
        OR REGEXP_CONTAINS(LOWER(j.requirements), LOWER(s.skill_name))
),

monthly_demand AS (
    SELECT
        DATE_TRUNC(SAFE.PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', posted_date), MONTH) as month,
        skill_name,
        skill_category,
        role,
        location,
        
        COUNT(DISTINCT job_id) as job_mentions
        
    FROM skill_extraction se
    WHERE CAST(SAFE.PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', posted_date) AS DATE) >= DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH)
    GROUP BY month, skill_name, skill_category, role, location
),

monthly_demand_with_percentage AS (
    SELECT
        md.*,
        md.job_mentions * 1.0 / (
            SELECT COUNT(DISTINCT job_id)
            FROM `runagen-ai`.`runagen_silver_silver`.`jobs_cleaned`
            WHERE DATE_TRUNC(SAFE.PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', posted_date), MONTH) = md.month
        ) * 100 as demand_percentage
    FROM monthly_demand md
),

trend_analysis AS (
    SELECT
        *,
        LAG(demand_percentage, 1) OVER (PARTITION BY skill_name ORDER BY month) as prev_month_demand,
        LAG(demand_percentage, 3) OVER (PARTITION BY skill_name ORDER BY month) as three_months_ago_demand,
        LAG(demand_percentage, 6) OVER (PARTITION BY skill_name ORDER BY month) as six_months_ago_demand,
        
        AVG(demand_percentage) OVER (
            PARTITION BY skill_name 
            ORDER BY month 
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) as moving_avg_3month,
        
        AVG(demand_percentage) OVER (
            PARTITION BY skill_name 
            ORDER BY month 
            ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
        ) as moving_avg_6month
        
    FROM monthly_demand_with_percentage
),

growth_metrics AS (
    SELECT
        *,
        
        -- Month-over-month growth
        CASE
            WHEN prev_month_demand > 0 THEN
                ((demand_percentage - prev_month_demand) / prev_month_demand) * 100
            ELSE NULL
        END as mom_growth,
        
        -- 3-month growth
        CASE
            WHEN three_months_ago_demand > 0 THEN
                ((demand_percentage - three_months_ago_demand) / three_months_ago_demand) * 100
            ELSE NULL
        END as three_month_growth,
        
        -- 6-month growth
        CASE
            WHEN six_months_ago_demand > 0 THEN
                ((demand_percentage - six_months_ago_demand) / six_months_ago_demand) * 100
            ELSE NULL
        END as six_month_growth,
        
        -- Trend direction
        CASE
            WHEN moving_avg_3month > moving_avg_6month THEN 'Accelerating'
            WHEN moving_avg_3month < moving_avg_6month THEN 'Decelerating'
            ELSE 'Stable'
        END as trend_direction
        
    FROM trend_analysis
)

SELECT
    month,
    skill_name,
    skill_category,
    role,
    location,
    job_mentions,
    demand_percentage,
    moving_avg_3month,
    moving_avg_6month,
    mom_growth,
    three_month_growth,
    six_month_growth,
    trend_direction,
    
    -- Classify skill status
    CASE
        WHEN six_month_growth > 50 THEN 'Emerging'
        WHEN six_month_growth > 20 THEN 'Growing'
        WHEN six_month_growth > -10 THEN 'Stable'
        WHEN six_month_growth > -30 THEN 'Declining'
        ELSE 'Obsolete'
    END as skill_status,
    
    -- Demand level
    CASE
        WHEN demand_percentage > 50 THEN 'Very High'
        WHEN demand_percentage > 30 THEN 'High'
        WHEN demand_percentage > 15 THEN 'Medium'
        WHEN demand_percentage > 5 THEN 'Low'
        ELSE 'Very Low'
    END as demand_level,
    
    -- Priority score for learning (0-100)
    LEAST(100, GREATEST(0,
        (demand_percentage * 0.4) +  -- Current demand (40%)
        (COALESCE(six_month_growth, 0) * 0.3) +  -- Growth trend (30%)
        (job_mentions / 10.0 * 0.3)  -- Absolute mentions (30%)
    )) as learning_priority_score
    
FROM growth_metrics
WHERE month = (SELECT MAX(month) FROM growth_metrics)  -- Latest month only
ORDER BY learning_priority_score DESC, demand_percentage DESC
    );
  