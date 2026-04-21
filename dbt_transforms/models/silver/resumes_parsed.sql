{{
    config(
        materialized='table',
        description='Parsed and structured resume data'
    )
}}

WITH parsed_resumes AS (
    SELECT
        resume_id,
        user_id,
        
        -- Extract email (if present)
        REGEXP_EXTRACT(raw_text, r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}') as email,
        
        -- Extract phone (if present)
        REGEXP_EXTRACT(raw_text, r'\+?[\d\s\-\(\)]{10,}') as phone,
        
        -- Extract education level
        CASE
            WHEN REGEXP_CONTAINS(LOWER(raw_text), r'\b(phd|ph\.d|doctorate)\b') THEN 'PhD'
            WHEN REGEXP_CONTAINS(LOWER(raw_text), r'\b(master|msc|m\.sc|mba|m\.b\.a)\b') THEN 'Masters'
            WHEN REGEXP_CONTAINS(LOWER(raw_text), r'\b(bachelor|bsc|b\.sc|btech|b\.tech|be|b\.e)\b') THEN 'Bachelors'
            WHEN REGEXP_CONTAINS(LOWER(raw_text), r'\b(diploma|associate)\b') THEN 'Diploma'
            ELSE 'Not Specified'
        END as education_level,
        
        -- Extract years of experience (approximate)
        CASE
            WHEN REGEXP_CONTAINS(raw_text, r'(\d+)\+?\s*years?\s*(of)?\s*experience') THEN
                CAST(REGEXP_EXTRACT(raw_text, r'(\d+)\+?\s*years?\s*(of)?\s*experience') AS INT64)
            ELSE NULL
        END as years_of_experience,
        
        -- Clean text
        REGEXP_REPLACE(
            REGEXP_REPLACE(raw_text, r'[^\w\s\.\,\-]', ''),
            r'\s+', ' '
        ) as text_cleaned,
        
        -- Metadata
        file_name,
        file_size,
        uploaded_at,
        processing_status,
        
        -- Data quality
        LENGTH(raw_text) as text_length,
        CASE WHEN LENGTH(raw_text) < 200 THEN TRUE ELSE FALSE END as too_short,
        CASE WHEN LENGTH(raw_text) > 50000 THEN TRUE ELSE FALSE END as too_long
        
    FROM {{ ref('raw_resumes') }}
    WHERE resume_id IS NOT NULL
)

SELECT *
FROM parsed_resumes
WHERE NOT too_short AND NOT too_long  -- Filter quality issues
