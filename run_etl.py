#!/usr/bin/env python3
"""
Manual ETL Execution Script
Run MongoDB → BigQuery ETL pipeline manually
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...\n")
    
    required_packages = {
        'pandas': 'pandas',
        'pymongo': 'pymongo',
        'google.cloud.bigquery': 'google-cloud-bigquery',
        'google.oauth2': 'google-auth',
        'pyarrow': 'pyarrow',
    }
    
    missing_packages = []
    
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"  ✅ {package_name}")
        except ImportError:
            print(f"  ❌ {package_name} (missing)")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("\nTo install missing packages, run:")
        print(f"  pip3 install {' '.join(missing_packages)}")
        print("\nOr install all dependencies:")
        print("  pip3 install -r requirements.txt")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(1)
    
    print()


from etl.mongodb_to_bigquery import MongoDBToBigQueryETL


def main():
    print("\n" + "="*70)
    print("🚀 RunaGen AI - ETL Pipeline")
    print("   MongoDB → BigQuery Data Warehouse")
    print("="*70 + "\n")
    
    # Check dependencies
    check_dependencies()
    
    # Check environment variables
    print("🔍 Checking configuration...")
    
    mongodb_uri = os.getenv('MONGO_URI', os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
    gcp_project = os.getenv('GCP_PROJECT_ID', 'runagen-ai-warehouse')
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'credentials/bigquery-key.json')
    
    print(f"  ✓ MongoDB URI: {mongodb_uri[:50]}...")
    print(f"  ✓ GCP Project: {gcp_project}")
    print(f"  ✓ Credentials: {credentials_path}")
    
    if not os.path.exists(credentials_path):
        print(f"\n⚠️  Warning: BigQuery credentials not found at {credentials_path}")
        print("   The ETL will attempt to use default credentials.")
        response = input("\n   Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("   Aborted.")
            return
    
    print("\n" + "-"*70 + "\n")
    
    # Initialize ETL
    try:
        etl = MongoDBToBigQueryETL()
    except Exception as e:
        print(f"❌ Failed to initialize ETL: {e}")
        return
    
    # Show MongoDB statistics
    print("📊 MongoDB Statistics (Source):")
    try:
        mongo_stats = etl.get_mongodb_stats()
        for collection, count in mongo_stats.items():
            print(f"  - {collection}: {count:,} records")
        
        total_records = sum(mongo_stats.values())
        if total_records == 0:
            print("\n⚠️  Warning: No data found in MongoDB!")
            print("   Make sure MongoDB is running and contains data.")
            response = input("\n   Continue anyway? (y/n): ")
            if response.lower() != 'y':
                print("   Aborted.")
                return
    except Exception as e:
        print(f"❌ Failed to get MongoDB stats: {e}")
        return
    
    print("\n" + "-"*70 + "\n")
    
    # Run ETL
    print("🚀 Starting ETL pipeline...\n")
    
    try:
        result = etl.run_full_etl()
        
        # Show results
        print("\n" + "="*70)
        print("✅ ETL PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*70)
        print(f"\n📈 Results:")
        print(f"  - Jobs loaded: {result['jobs_count']:,}")
        print(f"  - Skills loaded: {result['skills_count']:,}")
        print(f"  - Resumes loaded: {result['resumes_count']:,}")
        print(f"  - Duration: {result['duration_seconds']:.2f} seconds")
        print(f"  - Status: {result['status']}")
        
        # Show BigQuery statistics
        print("\n📊 BigQuery Statistics (Destination):")
        try:
            bq_stats = etl.get_bigquery_stats()
            for table, count in bq_stats.items():
                print(f"  - {table}: {count:,} rows")
        except Exception as e:
            print(f"  ⚠️  Could not fetch BigQuery stats: {e}")
        
        print("\n" + "="*70)
        print("\n🎉 Next Steps:")
        print("  1. Run dbt transformations: cd dbt_transforms && dbt run")
        print("  2. Test data quality: cd dbt_transforms && dbt test")
        print("  3. View data in BigQuery Console")
        print("\n" + "="*70 + "\n")
        
    except Exception as e:
        print("\n" + "="*70)
        print("❌ ETL PIPELINE FAILED!")
        print("="*70)
        print(f"\nError: {e}")
        print("\nPlease check:")
        print("  1. MongoDB is running and accessible")
        print("  2. BigQuery credentials are valid")
        print("  3. GCP project and datasets exist")
        print("\n" + "="*70 + "\n")
        raise


if __name__ == "__main__":
    main()
