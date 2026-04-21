{{
    config(
        materialized='table',
        description='Raw skills extracted from various sources',
        schema='bronze'
    )
}}

-- Reference the raw_skills table loaded by ETL pipeline
SELECT
    skill_id,
    skill_name,
    skill_category,
    source,
    extracted_at
FROM `{{ env_var('GCP_PROJECT_ID', 'runagen-ai') }}.runagen_bronze.raw_skills`
