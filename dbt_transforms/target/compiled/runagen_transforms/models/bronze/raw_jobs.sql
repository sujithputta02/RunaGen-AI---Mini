

-- Reference the raw_jobs table loaded by ETL pipeline
SELECT
    job_id,
    source,
    title,
    company,
    location,
    description,
    requirements,
    salary_min,
    salary_max,
    currency,
    employment_type,
    experience_level,
    posted_date,
    scraped_at,
    url
FROM `runagen-ai.runagen_bronze.raw_jobs`