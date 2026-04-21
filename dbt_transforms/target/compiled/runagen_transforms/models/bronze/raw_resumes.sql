

-- Create empty table with schema (no resumes in MongoDB yet)
SELECT
    CAST(NULL AS STRING) as resume_id,
    CAST(NULL AS STRING) as user_id,
    CAST(NULL AS STRING) as raw_text,
    CAST(NULL AS STRING) as file_name,
    CAST(NULL AS INT64) as file_size,
    CAST(NULL AS TIMESTAMP) as uploaded_at,
    CAST(NULL AS STRING) as processing_status
LIMIT 0