#!/usr/bin/env python3
"""
Test script to verify job fetching works correctly
"""
import sys
import os
sys.path.insert(0, 'src')

from features.job_scraper import JobScraper
from api.bigquery_data_provider import get_data_provider
import json

def test_job_scraper():
    """Test the job scraper"""
    print("\n" + "="*70)
    print("Testing Job Scraper")
    print("="*70)
    
    scraper = JobScraper()
    jobs = scraper.scrape_adzuna_jobs(['Data Scientist'], 'India', limit=5)
    
    print(f"\n✅ Found {len(jobs)} jobs")
    
    if jobs:
        print("\n📋 Sample Job:")
        print(json.dumps(jobs[0], indent=2, ensure_ascii=False))
        
        # Verify all required fields are present
        required_fields = ['title', 'company', 'location', 'description', 'salary_min', 'salary_max', 'currency', 'url']
        missing_fields = [field for field in required_fields if field not in jobs[0]]
        
        if missing_fields:
            print(f"\n❌ Missing fields: {missing_fields}")
        else:
            print(f"\n✅ All required fields present")
    else:
        print("\n⚠️ No jobs returned")

def test_bigquery_provider():
    """Test the BigQuery data provider"""
    print("\n" + "="*70)
    print("Testing BigQuery Data Provider")
    print("="*70)
    
    try:
        provider = get_data_provider()
        jobs = provider.search_jobs('Data Scientist', 'India', limit=5)
        
        print(f"\n✅ Found {len(jobs)} jobs from BigQuery")
        
        if jobs:
            print("\n📋 Sample Job:")
            print(json.dumps(jobs[0], indent=2, ensure_ascii=False))
        else:
            print("\n⚠️ BigQuery returned no jobs (table may be empty)")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    test_job_scraper()
    test_bigquery_provider()
    print("\n" + "="*70)
    print("Test Complete")
    print("="*70 + "\n")
