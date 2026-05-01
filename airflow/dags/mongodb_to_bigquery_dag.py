"""
Airflow DAG: MongoDB → BigQuery ETL Pipeline
Runs daily to sync data from MongoDB to BigQuery
"""
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.bash import BashOperator
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.etl.mongodb_to_bigquery import MongoDBToBigQueryETL


# Default arguments
default_args = {
    'owner': 'runagen',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email': ['alerts@runagen.ai'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

# Create DAG
dag = DAG(
    'mongodb_to_bigquery_etl',
    default_args=default_args,
    description='ETL pipeline from MongoDB to BigQuery',
    schedule_interval='0 2 * * *',  # Run daily at 2 AM
    catchup=False,
    tags=['etl', 'mongodb', 'bigquery'],
)


def extract_and_load_jobs(**context):
    """Extract jobs from MongoDB and load to BigQuery"""
    etl = MongoDBToBigQueryETL()
    jobs_df = etl.extract_jobs_from_mongodb()
    
    if not jobs_df.empty:
        etl.load_to_bigquery(jobs_df, 'raw_jobs', etl.dataset_bronze)
        return len(jobs_df)
    return 0


def extract_and_load_skills(**context):
    """Extract skills from MongoDB and load to BigQuery"""
    etl = MongoDBToBigQueryETL()
    skills_df = etl.extract_skills_from_mongodb()
    
    if not skills_df.empty:
        etl.load_to_bigquery(skills_df, 'raw_skills', etl.dataset_bronze)
        return len(skills_df)
    return 0


def extract_and_load_resumes(**context):
    """Extract resumes from MongoDB and load to BigQuery"""
    etl = MongoDBToBigQueryETL()
    resumes_df = etl.extract_resumes_from_mongodb()
    
    if not resumes_df.empty:
        etl.load_to_bigquery(resumes_df, 'raw_resumes', etl.dataset_bronze)
        return len(resumes_df)
    return 0


def validate_data_quality(**context):
    """Validate data quality after load"""
    etl = MongoDBToBigQueryETL()
    
    # Get stats
    mongo_stats = etl.get_mongodb_stats()
    bq_stats = etl.get_bigquery_stats()
    
    # Check if data was loaded
    for collection in ['jobs', 'skills']:
        mongo_count = mongo_stats.get(collection, 0)
        bq_count = bq_stats.get(f'raw_{collection}', 0)
        
        if mongo_count > 0 and bq_count == 0:
            raise ValueError(f"Data quality check failed: {collection} not loaded to BigQuery")
    
    print("✅ Data quality validation passed!")
    return True


# Task 1: Extract and load jobs
extract_load_jobs = PythonOperator(
    task_id='extract_load_jobs',
    python_callable=extract_and_load_jobs,
    dag=dag,
)

# Task 2: Extract and load skills
extract_load_skills = PythonOperator(
    task_id='extract_load_skills',
    python_callable=extract_and_load_skills,
    dag=dag,
)

# Task 3: Extract and load resumes
extract_load_resumes = PythonOperator(
    task_id='extract_load_resumes',
    python_callable=extract_and_load_resumes,
    dag=dag,
)

# Task 4: Run dbt transformations (Silver layer)
dbt_run_silver = BashOperator(
    task_id='dbt_run_silver',
    bash_command='cd dbt_transforms && dbt run --models silver.*',
    dag=dag,
)

# Task 5: Run dbt transformations (Gold layer)
dbt_run_gold = BashOperator(
    task_id='dbt_run_gold',
    bash_command='cd dbt_transforms && dbt run --models gold.*',
    dag=dag,
)

# Task 6: Run dbt tests
dbt_test = BashOperator(
    task_id='dbt_test',
    bash_command='cd dbt_transforms && dbt test',
    dag=dag,
)

# Task 7: Validate data quality
validate_quality = PythonOperator(
    task_id='validate_data_quality',
    python_callable=validate_data_quality,
    dag=dag,
)

# Task 8: Train Advanced ML Model (90%+ Accuracy Target)
train_model = BashOperator(
    task_id='train_advanced_ml_model',
    bash_command='python3 src/ml/train_models_advanced_90pct.py',
    dag=dag,
)

# Define task dependencies
# Extract and load tasks run in parallel
[extract_load_jobs, extract_load_skills, extract_load_resumes] >> validate_quality

# After validation, run dbt transformations
validate_quality >> dbt_run_silver >> dbt_run_gold >> dbt_test >> train_model
