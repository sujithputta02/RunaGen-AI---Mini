

-- Reference the raw_skills table loaded by ETL pipeline
SELECT
    skill_id,
    skill_name,
    skill_category,
    source,
    extracted_at
FROM `runagen-ai.runagen_bronze.raw_skills`