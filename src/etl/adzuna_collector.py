"""
Adzuna API Data Collector
Fetches job postings and stores in MongoDB Bronze layer
"""
import os
import sys
import requests
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.mongodb_client import MongoDBClient

load_dotenv()

class AdzunaCollector:
    def __init__(self):
        self.app_id = os.getenv('ADZUNA_APP_ID')
        self.api_key = os.getenv('ADZUNA_APP_KEY') or os.getenv('ADZUNA_API_KEY')  # Support both names
        self.base_url = "https://api.adzuna.com/v1/api/jobs"
        self.mongo_client = MongoDBClient()
        self.mongo_client.connect()
    
    def fetch_jobs(self, country='in', query='data engineer', results_per_page=50, target_count=2000):
        """
        Fetch job postings from Adzuna API
        Collects up to target_count jobs (default: 2000)
        """
        all_jobs = []
        max_pages = (target_count // results_per_page) + 1
        
        print(f"Fetching up to {target_count} jobs for query: '{query}'")
        
        for page in range(1, max_pages + 1):
            if len(all_jobs) >= target_count:
                print(f"Reached target of {target_count} jobs")
                break
            
            url = f"{self.base_url}/{country}/search/{page}"
            params = {
                'app_id': self.app_id,
                'app_key': self.api_key,
                'results_per_page': results_per_page,
                'what': query
            }
            
            try:
                response = requests.get(url, params=params, timeout=10)
                
                # Check for API errors
                if response.status_code == 400:
                    print(f"⚠️  API Error 400: Bad Request - Check API credentials")
                    print(f"   Response: {response.text[:200]}")
                    break
                elif response.status_code == 401:
                    print(f"⚠️  API Error 401: Unauthorized - Invalid API key")
                    break
                elif response.status_code == 429:
                    print(f"⚠️  API Error 429: Rate limit exceeded - Waiting...")
                    import time
                    time.sleep(5)
                    continue
                
                response.raise_for_status()
                data = response.json()
                
                jobs = data.get('results', [])
                if not jobs:
                    print(f"No more jobs available at page {page}")
                    break
                
                all_jobs.extend(jobs)
                print(f"Fetched page {page}: {len(jobs)} jobs (Total: {len(all_jobs)})")
                
                # Rate limiting - be nice to the API
                import time
                time.sleep(0.5)
                
            except requests.exceptions.Timeout:
                print(f"⚠️  Timeout on page {page}, skipping...")
                continue
            except requests.exceptions.RequestException as e:
                print(f"Error fetching page {page}: {e}")
                break
            except Exception as e:
                print(f"Unexpected error on page {page}: {e}")
                break
        
        print(f"✓ Collected {len(all_jobs)} jobs for '{query}'")
        return all_jobs
    
    def save_to_bronze(self, jobs, query, category=None):
        """Save raw data to MongoDB Bronze layer"""
        # Skip if no jobs collected
        if not jobs or len(jobs) == 0:
            print(f"⚠️  No jobs to save for query: {query}")
            return []
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        metadata = {
            'collected_at': timestamp,
            'query': query,
            'category': category,
            'count': len(jobs),
            'source': 'adzuna'
        }
        
        # Insert into MongoDB
        inserted_ids = self.mongo_client.insert_bronze_many(
            collection_name='jobs',
            data_list=jobs,
            metadata=metadata
        )
        
        print(f"Saved {len(jobs)} jobs to MongoDB bronze_jobs collection")
        return inserted_ids
    
    def close(self):
        """Close MongoDB connection"""
        self.mongo_client.close()

if __name__ == "__main__":
    collector = AdzunaCollector()
    
    try:
        # Collect 2000 jobs for each role in India
        queries = ['data engineer', 'data scientist', 'ml engineer', 'data analyst']
        
        for query in queries:
            jobs = collector.fetch_jobs(country='in', query=query, target_count=2000)
            collector.save_to_bronze(jobs, query)
    
    finally:
        collector.close()
