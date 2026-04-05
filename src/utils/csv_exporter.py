"""
CSV Exporter for ML Model Training
Exports MongoDB data to CSV files for ML models
"""
import os
import sys
import pandas as pd
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.mongodb_client import MongoDBClient
from utils.logger import setup_logger

logger = setup_logger('csv_exporter')

class CSVExporter:
    def __init__(self):
        self.mongo_client = MongoDBClient()
        self.mongo_client.connect()
        self.export_dir = Path("data/csv_exports")
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def export_bronze_jobs(self, output_file='bronze_jobs.csv'):
        """Export Bronze layer jobs to CSV"""
        logger.info("Exporting Bronze jobs to CSV...")
        
        # Get data from MongoDB
        jobs_data = self.mongo_client.get_bronze_data('jobs')
        
        if not jobs_data:
            logger.warning("No jobs data found in Bronze layer")
            return None
        
        # Flatten the nested structure
        rows = []
        for record in jobs_data:
            job = record.get('data', {})
            metadata = record.get('metadata', {})
            
            row = {
                'job_id': job.get('id'),
                'title': job.get('title'),
                'company': job.get('company', {}).get('display_name', ''),
                'location': job.get('location', {}).get('display_name', ''),
                'description': job.get('description', ''),
                'salary_min': job.get('salary_min'),
                'salary_max': job.get('salary_max'),
                'created': job.get('created'),
                'category': job.get('category', {}).get('label', ''),
                'contract_type': job.get('contract_type'),
                'query': metadata.get('query'),
                'collected_at': metadata.get('collected_at'),
                'source': metadata.get('source')
            }
            rows.append(row)
        
        # Create DataFrame and export
        df = pd.DataFrame(rows)
        filepath = self.export_dir / output_file
        df.to_csv(filepath, index=False)
        
        logger.info(f"✓ Exported {len(df)} jobs to {filepath}")
        return filepath
    
    def export_silver_jobs(self, output_file='silver_jobs.csv'):
        """Export Silver layer jobs to CSV"""
        logger.info("Exporting Silver jobs to CSV...")
        
        # Get data from MongoDB
        jobs_data = self.mongo_client.get_silver_data('jobs')
        
        if not jobs_data:
            logger.warning("No jobs data found in Silver layer")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(jobs_data)
        
        # Remove MongoDB internal fields
        df = df.drop(columns=['_id', 'bronze_id'], errors='ignore')
        
        filepath = self.export_dir / output_file
        df.to_csv(filepath, index=False)
        
        logger.info(f"✓ Exported {len(df)} jobs to {filepath}")
        return filepath
    
    def export_silver_skills(self, output_file='silver_skills.csv'):
        """Export Silver layer skills to CSV"""
        logger.info("Exporting Silver skills to CSV...")
        
        # Get data from MongoDB
        skills_data = self.mongo_client.get_silver_data('skills')
        
        if not skills_data:
            logger.warning("No skills data found in Silver layer")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(skills_data)
        
        # Remove MongoDB internal fields
        df = df.drop(columns=['_id', 'bronze_id'], errors='ignore')
        
        filepath = self.export_dir / output_file
        df.to_csv(filepath, index=False)
        
        logger.info(f"✓ Exported {len(df)} skills to {filepath}")
        return filepath
    
    def export_gold_skill_frequency(self, output_file='gold_skill_frequency.csv'):
        """Export Gold layer skill frequency features to CSV"""
        logger.info("Exporting Gold skill frequency to CSV...")
        
        # Get data from MongoDB
        features_data = self.mongo_client.get_gold_data('skill_frequency')
        
        if not features_data:
            logger.warning("No skill frequency data found in Gold layer")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(features_data)
        
        # Remove MongoDB internal fields
        df = df.drop(columns=['_id'], errors='ignore')
        
        filepath = self.export_dir / output_file
        df.to_csv(filepath, index=False)
        
        logger.info(f"✓ Exported {len(df)} skill features to {filepath}")
        return filepath
    
    def export_gold_role_skill_matrix(self, output_file='gold_role_skill_matrix.csv'):
        """Export Gold layer role-skill matrix to CSV"""
        logger.info("Exporting Gold role-skill matrix to CSV...")
        
        # Get data from MongoDB
        matrix_data = self.mongo_client.get_gold_data('role_skill_matrix')
        
        if not matrix_data:
            logger.warning("No role-skill matrix data found in Gold layer")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(matrix_data)
        
        # Remove MongoDB internal fields
        df = df.drop(columns=['_id'], errors='ignore')
        
        filepath = self.export_dir / output_file
        df.to_csv(filepath, index=False)
        
        logger.info(f"✓ Exported {len(df)} role-skill relationships to {filepath}")
        return filepath
    
    def export_all(self):
        """Export all data to CSV files"""
        logger.info("=== Exporting All Data to CSV ===")
        
        exported_files = []
        
        # Export Bronze layer
        bronze_jobs = self.export_bronze_jobs()
        if bronze_jobs:
            exported_files.append(bronze_jobs)
        
        # Export Silver layer
        silver_jobs = self.export_silver_jobs()
        if silver_jobs:
            exported_files.append(silver_jobs)
        
        silver_skills = self.export_silver_skills()
        if silver_skills:
            exported_files.append(silver_skills)
        
        # Export Gold layer
        skill_freq = self.export_gold_skill_frequency()
        if skill_freq:
            exported_files.append(skill_freq)
        
        role_skill = self.export_gold_role_skill_matrix()
        if role_skill:
            exported_files.append(role_skill)
        
        logger.info(f"\n✓ Exported {len(exported_files)} CSV files to {self.export_dir}")
        
        return exported_files
    
    def create_ml_training_dataset(self, output_file='ml_training_dataset.csv'):
        """Create a combined dataset for ML model training"""
        logger.info("Creating ML training dataset...")
        
        # Get jobs and skills
        jobs = self.mongo_client.get_silver_data('jobs')
        skills = self.mongo_client.get_silver_data('skills')
        
        if not jobs:
            logger.warning("No jobs data available for ML dataset")
            return None
        
        # Create training dataset
        training_data = []
        
        for job in jobs:
            row = {
                'job_title': job.get('title', ''),
                'company': job.get('company', ''),
                'location': job.get('location', ''),
                'description': job.get('description', ''),
                'salary_min': job.get('salary_min', 0),
                'salary_max': job.get('salary_max', 0),
                'salary_avg': (job.get('salary_min', 0) + job.get('salary_max', 0)) / 2 if job.get('salary_min') and job.get('salary_max') else 0,
                'category': job.get('category', ''),
                'contract_type': job.get('contract_type', ''),
                'extracted_skills': ','.join(job.get('extracted_skills', [])),
                'skill_count': len(job.get('extracted_skills', []))
            }
            training_data.append(row)
        
        df = pd.DataFrame(training_data)
        filepath = self.export_dir / output_file
        df.to_csv(filepath, index=False)
        
        logger.info(f"✓ Created ML training dataset: {filepath}")
        logger.info(f"   Rows: {len(df)}, Columns: {len(df.columns)}")
        
        return filepath
    
    def close(self):
        """Close MongoDB connection"""
        self.mongo_client.close()

if __name__ == "__main__":
    exporter = CSVExporter()
    
    try:
        # Export all data
        files = exporter.export_all()
        
        # Create ML training dataset
        ml_dataset = exporter.create_ml_training_dataset()
        
        print("\n" + "="*60)
        print("CSV Export Summary")
        print("="*60)
        print(f"\nExported Files:")
        for f in files:
            print(f"  ✓ {f}")
        
        if ml_dataset:
            print(f"\nML Training Dataset:")
            print(f"  ✓ {ml_dataset}")
        
        print(f"\nAll files saved to: data/csv_exports/")
        print("="*60)
        
    finally:
        exporter.close()
