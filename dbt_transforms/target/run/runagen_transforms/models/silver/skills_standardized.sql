
  
    

    create or replace table `runagen-ai`.`runagen_silver_silver`.`skills_standardized`
      
    
    

    OPTIONS()
    as (
      

WITH skill_mapping AS (
    -- Standardize skill names
    SELECT
        skill_id,
        CASE
            -- Programming Languages
            WHEN LOWER(skill_name) IN ('py', 'python3') THEN 'Python'
            WHEN LOWER(skill_name) IN ('js', 'javascript', 'ecmascript') THEN 'JavaScript'
            WHEN LOWER(skill_name) IN ('ts', 'typescript') THEN 'TypeScript'
            WHEN LOWER(skill_name) IN ('java', 'java8', 'java11') THEN 'Java'
            
            -- Frameworks
            WHEN LOWER(skill_name) IN ('reactjs', 'react.js') THEN 'React'
            WHEN LOWER(skill_name) IN ('nodejs', 'node.js') THEN 'Node.js'
            WHEN LOWER(skill_name) IN ('django', 'django-rest-framework') THEN 'Django'
            
            -- Databases
            WHEN LOWER(skill_name) IN ('postgres', 'postgresql', 'psql') THEN 'PostgreSQL'
            WHEN LOWER(skill_name) IN ('mongo', 'mongodb') THEN 'MongoDB'
            WHEN LOWER(skill_name) IN ('mysql', 'mariadb') THEN 'MySQL'
            
            -- Cloud
            WHEN LOWER(skill_name) IN ('aws', 'amazon web services') THEN 'AWS'
            WHEN LOWER(skill_name) IN ('gcp', 'google cloud platform', 'google cloud') THEN 'Google Cloud'
            WHEN LOWER(skill_name) IN ('azure', 'microsoft azure') THEN 'Azure'
            
            -- ML/AI
            WHEN LOWER(skill_name) IN ('ml', 'machine learning') THEN 'Machine Learning'
            WHEN LOWER(skill_name) IN ('dl', 'deep learning') THEN 'Deep Learning'
            WHEN LOWER(skill_name) IN ('nlp', 'natural language processing') THEN 'NLP'
            
            -- Tools
            WHEN LOWER(skill_name) IN ('git', 'github', 'gitlab') THEN 'Git'
            WHEN LOWER(skill_name) IN ('docker', 'containerization') THEN 'Docker'
            WHEN LOWER(skill_name) IN ('k8s', 'kubernetes') THEN 'Kubernetes'
            
            ELSE INITCAP(TRIM(skill_name))
        END as skill_name_standardized,
        
        -- Categorize skills
        CASE
            WHEN LOWER(skill_name) IN ('python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'ruby', 'php', 'swift', 'kotlin', 'scala', 'r') 
                THEN 'Programming Language'
            WHEN LOWER(skill_name) IN ('react', 'angular', 'vue', 'django', 'flask', 'fastapi', 'spring', 'express', 'node.js', 'next.js', 'laravel')
                THEN 'Framework'
            WHEN LOWER(skill_name) IN ('postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'cassandra', 'dynamodb', 'oracle', 'sql server')
                THEN 'Database'
            WHEN LOWER(skill_name) IN ('aws', 'azure', 'gcp', 'google cloud', 'heroku', 'digitalocean', 'linode')
                THEN 'Cloud Platform'
            WHEN LOWER(skill_name) IN ('machine learning', 'deep learning', 'nlp', 'computer vision', 'tensorflow', 'pytorch', 'scikit-learn', 'keras')
                THEN 'AI/ML'
            WHEN LOWER(skill_name) IN ('docker', 'kubernetes', 'jenkins', 'gitlab ci', 'github actions', 'terraform', 'ansible', 'circleci')
                THEN 'DevOps'
            WHEN LOWER(skill_name) IN ('git', 'jira', 'confluence', 'slack', 'trello', 'asana')
                THEN 'Tools'
            WHEN LOWER(skill_name) IN ('html', 'css', 'sass', 'tailwind', 'bootstrap', 'material-ui')
                THEN 'Frontend'
            WHEN LOWER(skill_name) IN ('rest api', 'graphql', 'grpc', 'websocket', 'microservices')
                THEN 'API/Architecture'
            WHEN LOWER(skill_name) IN ('spark', 'hadoop', 'airflow', 'kafka', 'flink', 'etl', 'data pipeline')
                THEN 'Data Engineering'
            ELSE 'Other'
        END as skill_category_standardized,
        
        source,
        extracted_at
        
    FROM `runagen-ai`.`runagen_silver_bronze`.`raw_skills`
    WHERE skill_name IS NOT NULL
),

deduplicated AS (
    -- Remove duplicates, keep most recent
    SELECT
        skill_name_standardized as skill_name,
        skill_category_standardized as skill_category,
        COUNT(DISTINCT source) as source_count,
        MAX(extracted_at) as last_seen,
        MIN(extracted_at) as first_seen
    FROM skill_mapping
    GROUP BY skill_name_standardized, skill_category_standardized
)

SELECT
    GENERATE_UUID() as skill_id,
    skill_name,
    skill_category,
    source_count,
    first_seen,
    last_seen,
    DATE_DIFF(CURRENT_DATE(), DATE(last_seen), DAY) as days_since_last_seen
FROM deduplicated
ORDER BY skill_name
    );
  