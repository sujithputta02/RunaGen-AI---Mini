"""
Complete Pipeline: Adzuna API → MongoDB → ML Models → Tableau Export
This script runs the entire data pipeline for Tableau visualization
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from utils.logger import setup_logger
from utils.mongodb_client import MongoDBClient

logger = setup_logger('full_pipeline')

def check_mongodb_connection():
    """Check if MongoDB is accessible"""
    logger.info("Checking MongoDB connection...")
    client = MongoDBClient()
    if client.connect():
        stats = client.get_collection_stats()
        logger.info(f"✓ MongoDB connected. Collections: {len(stats)}")
        for collection, count in stats.items():
            logger.info(f"  - {collection}: {count} documents")
        client.close()
        return True
    else:
        logger.error("✗ MongoDB connection failed")
        return False

def run_adzuna_collection():
    """Step 1: Collect data from Adzuna API"""
    logger.info("\n" + "="*60)
    logger.info("STEP 1: Collecting data from Adzuna API")
    logger.info("="*60)
    
    try:
        from etl.adzuna_collector import AdzunaCollector
        
        collector = AdzunaCollector()
        
        # Collect jobs for key roles in India
        queries = [
            'data engineer',
            'data scientist', 
            'machine learning engineer',
            'data analyst',
            'software engineer'
        ]
        
        total_jobs = 0
        for query in queries:
            logger.info(f"\nCollecting jobs for: {query} (India)")
            jobs = collector.fetch_jobs(country='in', query=query, target_count=500)
            if jobs:
                collector.save_to_bronze(jobs, query)
                total_jobs += len(jobs)
        
        collector.close()
        logger.info(f"\n✓ Collected {total_jobs} total jobs from Adzuna API")
        return True
        
    except Exception as e:
        logger.error(f"✗ Error in Adzuna collection: {e}")
        return False

def run_etl_pipeline():
    """Step 2: Run ELT pipeline (Bronze → Silver → Gold)"""
    logger.info("\n" + "="*60)
    logger.info("STEP 2: Running ELT Pipeline (Bronze → Silver → Gold)")
    logger.info("="*60)
    
    try:
        from etl.run_pipeline import run_full_pipeline
        
        run_full_pipeline()
        logger.info("✓ ELT Pipeline completed")
        return True
        
    except Exception as e:
        logger.error(f"✗ Error in ELT pipeline: {e}")
        return False

def train_ml_models():
    """Step 3: Train ML models"""
    logger.info("\n" + "="*60)
    logger.info("STEP 3: Training ML Models")
    logger.info("="*60)
    
    try:
        from ml.train_models import train_all_models
        
        train_all_models()
        logger.info("✓ ML Models trained successfully")
        return True
        
    except Exception as e:
        logger.error(f"✗ Error training ML models: {e}")
        logger.warning("Continuing without ML models...")
        return False

def export_to_tableau():
    """Step 4: Export data for Tableau"""
    logger.info("\n" + "="*60)
    logger.info("STEP 4: Exporting Data for Tableau")
    logger.info("="*60)
    
    try:
        from powerbi.export_to_powerbi import PowerBIExporter
        
        exporter = PowerBIExporter()
        exporter.export_all_data()
        logger.info("✓ Data exported for Tableau")
        return True
        
    except Exception as e:
        logger.error(f"✗ Error exporting to Tableau: {e}")
        return False

def main():
    """Run complete pipeline"""
    logger.info("="*60)
    logger.info("RUNAGEN AI - COMPLETE DATA PIPELINE FOR TABLEAU")
    logger.info("="*60)
    logger.info("Pipeline: Adzuna API → MongoDB → ML Models → Tableau CSV")
    logger.info("")
    
    # Check prerequisites
    if not check_mongodb_connection():
        logger.error("MongoDB connection required. Please check your .env file")
        return
    
    # Ask user what to run
    print("\nWhat would you like to do?")
    print("1. Run complete pipeline (Adzuna → MongoDB → ML → Tableau)")
    print("2. Skip Adzuna collection (use existing MongoDB data)")
    print("3. Only export to Tableau (skip collection and ML)")
    print("4. Check MongoDB data status")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        # Full pipeline
        logger.info("\nRunning COMPLETE pipeline...")
        
        if run_adzuna_collection():
            if run_etl_pipeline():
                train_ml_models()  # Optional - continue even if fails
                export_to_tableau()
    
    elif choice == "2":
        # Skip Adzuna, use existing data
        logger.info("\nSkipping Adzuna collection, using existing MongoDB data...")
        
        if run_etl_pipeline():
            train_ml_models()  # Optional
            export_to_tableau()
    
    elif choice == "3":
        # Only export
        logger.info("\nExporting existing data to Tableau...")
        export_to_tableau()
    
    elif choice == "4":
        # Check status
        logger.info("\nChecking MongoDB data status...")
        check_mongodb_connection()
    
    else:
        logger.error("Invalid choice")
        return
    
    logger.info("\n" + "="*60)
    logger.info("PIPELINE COMPLETE!")
    logger.info("="*60)
    logger.info("\nNext steps:")
    logger.info("1. Check powerbi_data/ folder for CSV files")
    logger.info("2. Open Tableau Public")
    logger.info("3. Follow TABLEAU_GUIDE.md for creating dashboards")
    logger.info("4. Upload CSV files and create visualizations")

if __name__ == "__main__":
    main()
