"""
ETL Pipeline: MongoDB → BigQuery
Extract data from MongoDB and load into BigQuery data warehouse
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from pymongo import MongoClient
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
from datetime import datetime
from typing import List, Dict
import logging
import warnings

# Suppress warnings from BigQuery library
warnings.filterwarnings('ignore', category=FutureWarning, module='google.cloud.bigquery._pandas_helpers')
warnings.filterwarnings('ignore', category=UserWarning, module='google.cloud.bigquery._pandas_helpers')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MongoDBToBigQueryETL:
    def __init__(self):
        # MongoDB connection - use MONGO_URI from .env
        mongo_uri = os.getenv('MONGO_URI', os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
        self.mongo_client = MongoClient(mongo_uri)
        
        # Get database name from URI or use default
        mongo_db = os.getenv('MONGO_DB', os.getenv('MONGODB_DB', 'runagen_db'))
        self.mongo_db = self.mongo_client[mongo_db]
        
        # BigQuery connection
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'credentials/bigquery-key.json')
        
        if os.path.exists(credentials_path):
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            self.bq_client = bigquery.Client(
                credentials=credentials,
                project=os.getenv('GCP_PROJECT_ID', 'runagen-ai-warehouse')
            )
        else:
            logger.warning("⚠️  BigQuery credentials not found. Using default credentials.")
            self.bq_client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID', 'runagen-ai-warehouse'))
        
        self.project_id = os.getenv('GCP_PROJECT_ID', 'runagen-ai-warehouse')
        self.dataset_bronze = 'runagen_bronze'
        self.dataset_silver = 'runagen_silver'
        self.dataset_gold = 'runagen_gold'
    
    def extract_jobs_from_mongodb(self) -> pd.DataFrame:
        """Extract job data from MongoDB"""
        logger.info("📥 Extracting jobs from MongoDB...")
        
        try:
            # Try different collection names
            collection_names = ['bronze_jobs', 'jobs', 'silver_jobs']
            jobs_collection = None
            collection_name_used = None
            
            for coll_name in collection_names:
                if coll_name in self.mongo_db.list_collection_names():
                    jobs_collection = self.mongo_db[coll_name]
                    collection_name_used = coll_name
                    break
            
            if collection_name_used is None:
                logger.warning("⚠️  No jobs collection found in MongoDB")
                return pd.DataFrame()
            
            logger.info(f"   Using collection: {collection_name_used}")
            jobs = list(jobs_collection.find())
            
            if not jobs:
                logger.warning("⚠️  No jobs found in MongoDB")
                return pd.DataFrame()
            
            # Extract data from nested structure
            extracted_jobs = []
            for job in jobs:
                if 'data' in job and isinstance(job['data'], dict):
                    job_data = job['data'].copy()
                    job_data['_id'] = job['_id']
                    extracted_jobs.append(job_data)
                else:
                    extracted_jobs.append(job)
            
            # Convert to DataFrame
            df = pd.DataFrame(extracted_jobs)
            
            # Rename columns to match our schema
            column_mapping = {
                '_id': 'job_id',
                'id': 'external_id',
                'title': 'title',
                'company': 'company',
                'location': 'location',
                'description': 'description',
                'salary_min': 'salary_min',
                'salary_max': 'salary_max',
                'created': 'posted_date',
                'redirect_url': 'url'
            }
            
            # Rename columns that exist
            for old_col, new_col in column_mapping.items():
                if old_col in df.columns:
                    df = df.rename(columns={old_col: new_col})
            
            # Convert job_id to string
            if 'job_id' in df.columns:
                df['job_id'] = df['job_id'].astype(str)
            
            # Add metadata
            df['source'] = 'mongodb'
            df['scraped_at'] = datetime.now()
            
            # Ensure required columns exist with proper types
            required_columns = [
                'job_id', 'source', 'title', 'company', 'location', 
                'description', 'requirements', 'salary_min', 'salary_max', 
                'currency', 'employment_type', 'experience_level', 
                'posted_date', 'scraped_at', 'url'
            ]
            
            for col in required_columns:
                if col not in df.columns:
                    df[col] = None
            
            # Cast columns to proper types to avoid BigQuery type detection issues
            df['job_id'] = df['job_id'].astype(str)
            df['source'] = df['source'].astype(str)
            df['title'] = df['title'].fillna('').astype(str)
            df['company'] = df['company'].fillna('').astype(str)
            df['location'] = df['location'].fillna('').astype(str)
            df['description'] = df['description'].fillna('').astype(str)
            df['requirements'] = df['requirements'].fillna('').astype(str)
            df['currency'] = df['currency'].fillna('').astype(str)
            df['employment_type'] = df['employment_type'].fillna('').astype(str)
            df['experience_level'] = df['experience_level'].fillna('').astype(str)
            df['url'] = df['url'].fillna('').astype(str)
            
            # Convert salary columns to float
            df['salary_min'] = pd.to_numeric(df['salary_min'], errors='coerce')
            df['salary_max'] = pd.to_numeric(df['salary_max'], errors='coerce')
            
            # Select only required columns
            df = df[required_columns]
            
            logger.info(f"✅ Extracted {len(df)} jobs from MongoDB")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error extracting jobs: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def extract_skills_from_mongodb(self) -> pd.DataFrame:
        """Extract skills data from MongoDB"""
        logger.info("📥 Extracting skills from MongoDB...")
        
        try:
            # Try different collection names
            collection_names = ['bronze_skills', 'skills', 'silver_skills']
            skills_collection = None
            collection_name_used = None
            
            for coll_name in collection_names:
                if coll_name in self.mongo_db.list_collection_names():
                    skills_collection = self.mongo_db[coll_name]
                    collection_name_used = coll_name
                    break
            
            if collection_name_used is None:
                logger.warning("⚠️  No skills collection found in MongoDB")
                return pd.DataFrame()
            
            logger.info(f"   Using collection: {collection_name_used}")
            skills = list(skills_collection.find())
            
            if not skills:
                logger.warning("⚠️  No skills found in MongoDB")
                return pd.DataFrame()
            
            # Extract data from nested structure
            extracted_skills = []
            for skill in skills:
                if 'data' in skill and isinstance(skill['data'], dict):
                    skill_data = skill['data'].copy()
                    skill_data['_id'] = skill['_id']
                    extracted_skills.append(skill_data)
                else:
                    extracted_skills.append(skill)
            
            # Convert to DataFrame
            df = pd.DataFrame(extracted_skills)
            
            # Rename columns to match our schema
            column_mapping = {
                '_id': 'skill_id',
                'id': 'external_id',
                'name': 'skill_name',
                'category': 'skill_category'
            }
            
            # Rename columns that exist
            for old_col, new_col in column_mapping.items():
                if old_col in df.columns:
                    df = df.rename(columns={old_col: new_col})
            
            # Convert skill_id to string
            if 'skill_id' in df.columns:
                df['skill_id'] = df['skill_id'].astype(str)
            
            # Add metadata
            df['source'] = 'mongodb'
            df['extracted_at'] = datetime.now()
            
            # Ensure required columns with proper types
            required_columns = ['skill_id', 'skill_name', 'skill_category', 'source', 'extracted_at']
            
            for col in required_columns:
                if col not in df.columns:
                    df[col] = None
            
            # Cast columns to proper types
            df['skill_id'] = df['skill_id'].astype(str)
            df['skill_name'] = df['skill_name'].fillna('').astype(str)
            df['skill_category'] = df['skill_category'].fillna('').astype(str)
            df['source'] = df['source'].astype(str)
            
            # Select only required columns
            df = df[required_columns]
            
            logger.info(f"✅ Extracted {len(df)} skills from MongoDB")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error extracting skills: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def extract_resumes_from_mongodb(self) -> pd.DataFrame:
        """Extract resume data from MongoDB (if stored)"""
        logger.info("📥 Extracting resumes from MongoDB...")
        
        try:
            # Check if resumes collection exists
            if 'resumes' not in self.mongo_db.list_collection_names():
                logger.info("ℹ️  No resumes collection found in MongoDB")
                return pd.DataFrame()
            
            resumes_collection = self.mongo_db['resumes']
            resumes = list(resumes_collection.find())
            
            if not resumes:
                logger.warning("⚠️  No resumes found in MongoDB")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(resumes)
            
            # Rename _id to resume_id
            if '_id' in df.columns:
                df['resume_id'] = df['_id'].astype(str)
                df = df.drop('_id', axis=1)
            
            # Add metadata
            df['uploaded_at'] = datetime.now()
            df['processing_status'] = 'pending'
            
            # Ensure required columns
            required_columns = [
                'resume_id', 'user_id', 'raw_text', 'file_name', 
                'file_size', 'uploaded_at', 'processing_status'
            ]
            
            for col in required_columns:
                if col not in df.columns:
                    df[col] = None
            
            df = df[required_columns]
            
            logger.info(f"✅ Extracted {len(df)} resumes from MongoDB")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error extracting resumes: {e}")
            return pd.DataFrame()
    
    def load_to_bigquery(self, df: pd.DataFrame, table_name: str, dataset: str = None):
        """Load DataFrame to BigQuery with explicit schema"""
        if df.empty:
            logger.warning(f"⚠️  No data to load for {table_name}")
            return
        
        dataset = dataset or self.dataset_bronze
        table_id = f"{self.project_id}.{dataset}.{table_name}"
        
        logger.info(f"📤 Loading {len(df)} rows to {table_id}...")
        
        try:
            # Define explicit schemas to avoid type detection warnings
            schema = None
            
            if table_name == 'raw_jobs':
                schema = [
                    bigquery.SchemaField("job_id", "STRING", mode="NULLABLE"),
                    bigquery.SchemaField("source", "STRING", mode="NULLABLE"),
                    bigquery.SchemaField("title", "STRING", mode="NULLABLE"),
                    bigquery.SchemaField("company", "STRING", mode="NULLABLE"),
                    bigquery.SchemaField("location", "STRING", mode="NULLABLE"),
                    bigquery.SchemaField("description", "STRING", mode="NULLABLE"),
                    bigquery.SchemaField("requirements", "STRING", mode="NULLABLE"),
                    bigquery.SchemaField("salary_min", "FLOAT64", mode="NULLABLE"),
                    bigquery.SchemaField("salary_max", "FLOAT64", mode="NULLABLE"),
                    bigquery.SchemaField("currency", "STRING", mode="NULLABLE"),
                    bigquery.SchemaField("employment_type", "STRING", mode="NULLABLE"),
                    bigquery.SchemaField("experience_level", "STRING", mode="NULLABLE"),
                    bigquery.SchemaField("posted_date", "TIMESTAMP", mode="NULLABLE"),
                    bigquery.SchemaField("scraped_at", "TIMESTAMP", mode="NULLABLE"),
                    bigquery.SchemaField("url", "STRING", mode="NULLABLE"),
                ]
            
            elif table_name == 'raw_skills':
                schema = [
                    bigquery.SchemaField("skill_id", "STRING", mode="NULLABLE"),
                    bigquery.SchemaField("skill_name", "STRING", mode="NULLABLE"),
                    bigquery.SchemaField("skill_category", "STRING", mode="NULLABLE"),
                    bigquery.SchemaField("source", "STRING", mode="NULLABLE"),
                    bigquery.SchemaField("extracted_at", "TIMESTAMP", mode="NULLABLE"),
                ]
            
            elif table_name == 'raw_resumes':
                schema = [
                    bigquery.SchemaField("resume_id", "STRING", mode="NULLABLE"),
                    bigquery.SchemaField("user_id", "STRING", mode="NULLABLE"),
                    bigquery.SchemaField("raw_text", "STRING", mode="NULLABLE"),
                    bigquery.SchemaField("file_name", "STRING", mode="NULLABLE"),
                    bigquery.SchemaField("file_size", "INTEGER", mode="NULLABLE"),
                    bigquery.SchemaField("uploaded_at", "TIMESTAMP", mode="NULLABLE"),
                    bigquery.SchemaField("processing_status", "STRING", mode="NULLABLE"),
                ]
            
            # Configure load job with explicit schema
            job_config = bigquery.LoadJobConfig(
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # Replace table
                schema=schema,  # Use explicit schema
            )
            
            # Load data
            job = self.bq_client.load_table_from_dataframe(
                df, table_id, job_config=job_config
            )
            
            # Wait for job to complete
            job.result()
            
            logger.info(f"✅ Loaded {len(df)} rows to {table_id}")
            
        except Exception as e:
            logger.error(f"❌ Error loading to BigQuery: {e}")
            raise
    
    def run_full_etl(self):
        """Run complete ETL pipeline"""
        logger.info("🚀 Starting MongoDB → BigQuery ETL Pipeline...")
        logger.info("="*70)
        
        start_time = datetime.now()
        
        # Extract from MongoDB
        logger.info("\n📥 EXTRACTION PHASE")
        logger.info("-"*70)
        
        jobs_df = self.extract_jobs_from_mongodb()
        skills_df = self.extract_skills_from_mongodb()
        resumes_df = self.extract_resumes_from_mongodb()
        
        # Load to BigQuery (Bronze layer)
        logger.info("\n📤 LOADING PHASE (Bronze Layer)")
        logger.info("-"*70)
        
        if not jobs_df.empty:
            self.load_to_bigquery(jobs_df, 'raw_jobs', self.dataset_bronze)
        
        if not skills_df.empty:
            self.load_to_bigquery(skills_df, 'raw_skills', self.dataset_bronze)
        
        if not resumes_df.empty:
            self.load_to_bigquery(resumes_df, 'raw_resumes', self.dataset_bronze)
        
        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("\n" + "="*70)
        logger.info("✅ ETL PIPELINE COMPLETE!")
        logger.info("="*70)
        logger.info(f"📊 Summary:")
        logger.info(f"  - Jobs extracted: {len(jobs_df)}")
        logger.info(f"  - Skills extracted: {len(skills_df)}")
        logger.info(f"  - Resumes extracted: {len(resumes_df)}")
        logger.info(f"  - Duration: {duration:.2f} seconds")
        logger.info(f"  - Destination: {self.project_id}.{self.dataset_bronze}")
        logger.info("="*70)
        
        return {
            'jobs_count': len(jobs_df),
            'skills_count': len(skills_df),
            'resumes_count': len(resumes_df),
            'duration_seconds': duration,
            'status': 'success'
        }
    
    def run_incremental_load(self, collection_name: str, last_sync_time: datetime = None):
        """Run incremental load for a specific collection"""
        logger.info(f"🔄 Running incremental load for {collection_name}...")
        
        collection = self.mongo_db[collection_name]
        
        # Query for new/updated records
        query = {}
        if last_sync_time:
            query = {'updated_at': {'$gt': last_sync_time}}
        
        records = list(collection.find(query))
        
        if not records:
            logger.info(f"ℹ️  No new records found for {collection_name}")
            return
        
        df = pd.DataFrame(records)
        
        # Convert _id to string
        if '_id' in df.columns:
            df['id'] = df['_id'].astype(str)
            df = df.drop('_id', axis=1)
        
        # Load to BigQuery
        table_name = f"raw_{collection_name}"
        self.load_to_bigquery(df, table_name, self.dataset_bronze)
        
        logger.info(f"✅ Incremental load complete: {len(df)} records")
    
    def get_mongodb_stats(self) -> Dict:
        """Get statistics from MongoDB"""
        stats = {}
        
        # Try different collection name patterns
        collection_patterns = {
            'jobs': ['bronze_jobs', 'jobs', 'silver_jobs'],
            'skills': ['bronze_skills', 'skills', 'silver_skills'],
            'resumes': ['resumes']
        }
        
        for key, patterns in collection_patterns.items():
            count = 0
            for pattern in patterns:
                if pattern in self.mongo_db.list_collection_names():
                    count = self.mongo_db[pattern].count_documents({})
                    break
            stats[key] = count
        
        return stats
    
    def get_bigquery_stats(self) -> Dict:
        """Get statistics from BigQuery"""
        stats = {}
        
        for table_name in ['raw_jobs', 'raw_skills', 'raw_resumes']:
            try:
                table_id = f"{self.project_id}.{self.dataset_bronze}.{table_name}"
                table = self.bq_client.get_table(table_id)
                stats[table_name] = table.num_rows
            except Exception:
                stats[table_name] = 0
        
        return stats


def main():
    """Main ETL execution"""
    print("\n" + "="*70)
    print("🚀 MongoDB → BigQuery ETL Pipeline")
    print("="*70 + "\n")
    
    # Initialize ETL
    etl = MongoDBToBigQueryETL()
    
    # Show MongoDB stats
    print("📊 MongoDB Statistics:")
    mongo_stats = etl.get_mongodb_stats()
    for collection, count in mongo_stats.items():
        print(f"  - {collection}: {count:,} records")
    print()
    
    # Run ETL
    result = etl.run_full_etl()
    
    # Show BigQuery stats
    print("\n📊 BigQuery Statistics:")
    bq_stats = etl.get_bigquery_stats()
    for table, count in bq_stats.items():
        print(f"  - {table}: {count:,} rows")
    
    print("\n✅ Pipeline execution complete!")
    print("="*70 + "\n")
    
    return result


if __name__ == "__main__":
    main()
