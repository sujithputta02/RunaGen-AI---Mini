
  
    

    create or replace table `runagen-ai`.`runagen_silver_silver`.`jobs_cleaned`
      
    
    

    OPTIONS()
    as (
      

WITH cleaned_jobs AS (
    SELECT
        job_id,
        source,
        -- Clean and standardize title
        TRIM(UPPER(REGEXP_REPLACE(title, r'[^\w\s]', ''))) as title_clean,
        title as title_original,
        
        -- Clean company name
        TRIM(company) as company,
        
        -- Standardize location
        CASE
            WHEN LOWER(location) LIKE '%remote%' THEN 'Remote'
            WHEN LOWER(location) LIKE '%india%' THEN 'India'
            WHEN LOWER(location) LIKE '%usa%' OR LOWER(location) LIKE '%united states%' THEN 'United States'
            WHEN LOWER(location) LIKE '%uk%' OR LOWER(location) LIKE '%united kingdom%' THEN 'United Kingdom'
            ELSE TRIM(location)
        END as location_standardized,
        
        -- Clean description
        REGEXP_REPLACE(description, r'<[^>]*>', '') as description_clean,
        
        -- Extract skills from requirements
        requirements,
        
        -- Standardize salary
        CASE
            WHEN currency = 'USD' THEN salary_min
            WHEN currency = 'INR' THEN salary_min / 83.0  -- Convert to USD
            WHEN currency = 'GBP' THEN salary_min * 1.27
            ELSE salary_min
        END as salary_min_usd,
        
        CASE
            WHEN currency = 'USD' THEN salary_max
            WHEN currency = 'INR' THEN salary_max / 83.0
            WHEN currency = 'GBP' THEN salary_max * 1.27
            ELSE salary_max
        END as salary_max_usd,
        
        -- Standardize employment type
        CASE
            WHEN LOWER(employment_type) LIKE '%full%time%' THEN 'Full-time'
            WHEN LOWER(employment_type) LIKE '%part%time%' THEN 'Part-time'
            WHEN LOWER(employment_type) LIKE '%contract%' THEN 'Contract'
            WHEN LOWER(employment_type) LIKE '%intern%' THEN 'Internship'
            ELSE 'Other'
        END as employment_type_standardized,
        
        -- Standardize experience level
        CASE
            WHEN LOWER(experience_level) LIKE '%entry%' OR LOWER(experience_level) LIKE '%junior%' THEN 'Entry'
            WHEN LOWER(experience_level) LIKE '%mid%' OR LOWER(experience_level) LIKE '%intermediate%' THEN 'Mid'
            WHEN LOWER(experience_level) LIKE '%senior%' THEN 'Senior'
            WHEN LOWER(experience_level) LIKE '%lead%' OR LOWER(experience_level) LIKE '%principal%' THEN 'Lead'
            ELSE 'Not Specified'
        END as experience_level_standardized,
        
        posted_date,
        scraped_at,
        url,
        
        -- Data quality flags
        CASE WHEN salary_min IS NULL OR salary_max IS NULL THEN TRUE ELSE FALSE END as missing_salary,
        CASE WHEN LENGTH(description) < 100 THEN TRUE ELSE FALSE END as short_description,
        CASE WHEN SAFE.PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', posted_date) > CURRENT_TIMESTAMP() THEN TRUE ELSE FALSE END as invalid_date
        
    FROM `runagen-ai`.`runagen_silver_bronze`.`raw_jobs`
    WHERE job_id IS NOT NULL
)

SELECT *
FROM cleaned_jobs
WHERE NOT invalid_date  -- Filter out invalid records
    );
  