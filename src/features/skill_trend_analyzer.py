"""
Phase 5: Skill Trend Analysis
Analyze skill demand trends from BigQuery data
"""
import os
from dotenv import load_dotenv
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SkillTrendAnalyzer:
    """Analyze skill trends from job market data"""
    
    def __init__(self):
        """Initialize BigQuery client"""
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'credentials/bigquery-key.json')
        
        if os.path.exists(credentials_path):
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            self.bq_client = bigquery.Client(
                credentials=credentials,
                project=os.getenv('GCP_PROJECT_ID', 'runagen-ai')
            )
        else:
            self.bq_client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID', 'runagen-ai'))
        
        self.project_id = os.getenv('GCP_PROJECT_ID', 'runagen-ai')
        self.dataset = 'runagen_gold'
    
    def get_trending_skills(self, days: int = 30, limit: int = 20) -> List[Dict]:
        """Get trending skills in the last N days"""
        logger.info(f"📊 Analyzing trending skills (last {days} days)...")
        
        query = f"""
        SELECT 
            skill_name,
            skill_category,
            COUNT(*) as demand_count,
            ROUND(COUNT(*) / (SELECT COUNT(*) FROM `{self.project_id}.runagen_bronze.raw_jobs`) * 100, 2) as demand_percentage,
            CURRENT_TIMESTAMP() as analyzed_at
        FROM `{self.project_id}.runagen_bronze.raw_jobs` j
        CROSS JOIN UNNEST(SPLIT(j.requirements, ',')) as skill_name
        LEFT JOIN `{self.project_id}.runagen_bronze.raw_skills` s 
            ON LOWER(TRIM(skill_name)) = LOWER(TRIM(s.skill_name))
        WHERE j.scraped_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
        GROUP BY skill_name, skill_category
        ORDER BY demand_count DESC
        LIMIT {limit}
        """
        
        try:
            results = self.bq_client.query(query).to_dataframe()
            
            trends = []
            for _, row in results.iterrows():
                # Handle NaN values
                skill_category = row['skill_category']
                if pd.isna(skill_category):
                    skill_category = 'Other'
                
                trends.append({
                    'skill_name': str(row['skill_name']).strip(),
                    'skill_category': str(skill_category),
                    'demand_count': int(row['demand_count']),
                    'demand_percentage': float(row['demand_percentage']),
                    'trend_direction': 'rising',  # Can be enhanced with historical data
                    'analyzed_at': str(row['analyzed_at'])
                })
            
            logger.info(f"✅ Found {len(trends)} trending skills")
            return trends
        
        except Exception as e:
            logger.error(f"❌ Error analyzing trending skills: {e}")
            return []
    
    def get_skill_growth_rate(self, skill_name: str, days: int = 90) -> Dict:
        """Calculate growth rate for a specific skill"""
        logger.info(f"📈 Calculating growth rate for {skill_name}...")
        
        query = f"""
        WITH daily_counts AS (
            SELECT 
                DATE(j.scraped_at) as date,
                COUNT(*) as job_count
            FROM `{self.project_id}.runagen_bronze.raw_jobs` j
            WHERE j.scraped_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
                AND LOWER(j.requirements) LIKE LOWER('%{skill_name}%')
            GROUP BY DATE(j.scraped_at)
        )
        SELECT 
            MIN(job_count) as min_jobs,
            MAX(job_count) as max_jobs,
            AVG(job_count) as avg_jobs,
            STDDEV(job_count) as stddev_jobs,
            COUNT(*) as days_with_data
        FROM daily_counts
        """
        
        try:
            results = self.bq_client.query(query).to_dataframe()
            
            if results.empty:
                return {
                    'skill_name': skill_name,
                    'growth_rate': 0,
                    'status': 'no_data'
                }
            
            row = results.iloc[0]
            min_jobs = float(row['min_jobs']) if row['min_jobs'] else 0
            max_jobs = float(row['max_jobs']) if row['max_jobs'] else 0
            
            growth_rate = ((max_jobs - min_jobs) / min_jobs * 100) if min_jobs > 0 else 0
            
            return {
                'skill_name': skill_name,
                'growth_rate': round(growth_rate, 2),
                'min_jobs': int(min_jobs),
                'max_jobs': int(max_jobs),
                'avg_jobs': round(float(row['avg_jobs']), 2),
                'days_analyzed': int(row['days_with_data']),
                'status': 'rising' if growth_rate > 10 else 'stable' if growth_rate > -10 else 'declining'
            }
        
        except Exception as e:
            logger.error(f"❌ Error calculating growth rate: {e}")
            return {'skill_name': skill_name, 'error': str(e)}
    
    def get_skill_salary_correlation(self, skill_name: str) -> Dict:
        """Get salary correlation for a specific skill"""
        logger.info(f"💰 Analyzing salary correlation for {skill_name}...")
        
        query = f"""
        SELECT 
            ROUND(AVG(salary_min), 2) as avg_min_salary,
            ROUND(AVG(salary_max), 2) as avg_max_salary,
            ROUND(AVG((salary_min + salary_max) / 2), 2) as avg_salary,
            COUNT(*) as job_count,
            MIN(salary_min) as min_salary,
            MAX(salary_max) as max_salary
        FROM `{self.project_id}.runagen_bronze.raw_jobs`
        WHERE LOWER(requirements) LIKE LOWER('%{skill_name}%')
            AND salary_min > 0
            AND salary_max > 0
        """
        
        try:
            results = self.bq_client.query(query).to_dataframe()
            
            if results.empty or results.iloc[0]['job_count'] == 0:
                return {
                    'skill_name': skill_name,
                    'status': 'no_salary_data'
                }
            
            row = results.iloc[0]
            
            return {
                'skill_name': skill_name,
                'avg_min_salary': float(row['avg_min_salary']),
                'avg_max_salary': float(row['avg_max_salary']),
                'avg_salary': float(row['avg_salary']),
                'min_salary': float(row['min_salary']),
                'max_salary': float(row['max_salary']),
                'job_count': int(row['job_count']),
                'salary_range': f"₹{row['avg_min_salary']:.0f}L - ₹{row['avg_max_salary']:.0f}L"
            }
        
        except Exception as e:
            logger.error(f"❌ Error analyzing salary correlation: {e}")
            return {'skill_name': skill_name, 'error': str(e)}
    
    def get_skill_by_category(self, category: str = None) -> List[Dict]:
        """Get skills grouped by category"""
        logger.info(f"🏷️  Analyzing skills by category...")
        
        category_filter = f"AND skill_category = '{category}'" if category else ""
        
        query = f"""
        SELECT 
            skill_category,
            skill_name,
            COUNT(*) as frequency
        FROM `{self.project_id}.runagen_bronze.raw_skills`
        WHERE skill_name IS NOT NULL
            {category_filter}
        GROUP BY skill_category, skill_name
        ORDER BY skill_category, frequency DESC
        """
        
        try:
            results = self.bq_client.query(query).to_dataframe()
            
            skills_by_category = []
            for _, row in results.iterrows():
                # Handle NaN values
                skill_category = row['skill_category']
                if pd.isna(skill_category):
                    skill_category = 'Other'
                
                skills_by_category.append({
                    'category': str(skill_category),
                    'skill_name': str(row['skill_name']).strip(),
                    'frequency': int(row['frequency'])
                })
            
            logger.info(f"✅ Found {len(skills_by_category)} skills")
            return skills_by_category
        
        except Exception as e:
            logger.error(f"❌ Error analyzing skills by category: {e}")
            return []
    
    def get_emerging_skills(self, threshold_days: int = 30) -> List[Dict]:
        """Identify emerging skills (recently added to job market)"""
        logger.info(f"🚀 Identifying emerging skills...")
        
        query = f"""
        SELECT 
            skill_name,
            skill_category,
            COUNT(*) as recent_count,
            MIN(extracted_at) as first_seen,
            MAX(extracted_at) as last_seen
        FROM `{self.project_id}.runagen_bronze.raw_skills`
        WHERE extracted_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {threshold_days} DAY)
        GROUP BY skill_name, skill_category
        HAVING COUNT(*) >= 5
        ORDER BY recent_count DESC
        LIMIT 20
        """
        
        try:
            results = self.bq_client.query(query).to_dataframe()
            
            emerging = []
            for _, row in results.iterrows():
                # Handle NaN values
                skill_category = row['skill_category']
                if pd.isna(skill_category):
                    skill_category = 'Other'
                
                emerging.append({
                    'skill_name': str(row['skill_name']).strip(),
                    'skill_category': str(skill_category),
                    'recent_count': int(row['recent_count']),
                    'first_seen': str(row['first_seen']),
                    'last_seen': str(row['last_seen']),
                    'emergence_score': round(int(row['recent_count']) / threshold_days, 2)
                })
            
            logger.info(f"✅ Found {len(emerging)} emerging skills")
            return emerging
        
        except Exception as e:
            logger.error(f"❌ Error identifying emerging skills: {e}")
            return []
    
    def get_skill_demand_by_role(self, role: str) -> Dict:
        """Get skill demand for a specific role"""
        logger.info(f"👔 Analyzing skill demand for {role}...")
        
        query = f"""
        SELECT 
            LOWER(TRIM(skill_name)) as skill,
            COUNT(*) as demand_count
        FROM `{self.project_id}.runagen_bronze.raw_jobs` j
        CROSS JOIN UNNEST(SPLIT(j.requirements, ',')) as skill_name
        WHERE LOWER(j.title) LIKE LOWER('%{role}%')
        GROUP BY skill
        ORDER BY demand_count DESC
        LIMIT 15
        """
        
        try:
            results = self.bq_client.query(query).to_dataframe()
            
            skills = []
            for _, row in results.iterrows():
                skills.append({
                    'skill': row['skill'],
                    'demand_count': int(row['demand_count'])
                })
            
            return {
                'role': role,
                'top_skills': skills,
                'total_jobs': sum(s['demand_count'] for s in skills)
            }
        
        except Exception as e:
            logger.error(f"❌ Error analyzing skill demand by role: {e}")
            return {'role': role, 'error': str(e)}
    
    def generate_trend_report(self) -> Dict:
        """Generate comprehensive trend report"""
        logger.info("📋 Generating comprehensive trend report...")
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'trending_skills': self.get_trending_skills(days=30, limit=10),
            'emerging_skills': self.get_emerging_skills(threshold_days=30),
            'skill_categories': self.get_skill_by_category(),
            'role_skill_demand': {
                'data_analyst': self.get_skill_demand_by_role('Data Analyst'),
                'data_engineer': self.get_skill_demand_by_role('Data Engineer'),
                'backend_developer': self.get_skill_demand_by_role('Backend Developer'),
                'frontend_developer': self.get_skill_demand_by_role('Frontend Developer'),
            }
        }
        
        logger.info("✅ Trend report generated")
        return report


def main():
    """Main execution"""
    print("\n" + "="*70)
    print("🚀 Phase 5: Skill Trend Analysis")
    print("="*70 + "\n")
    
    analyzer = SkillTrendAnalyzer()
    
    # Get trending skills
    print("📊 Top Trending Skills:")
    print("-"*70)
    trending = analyzer.get_trending_skills(days=30, limit=10)
    for i, skill in enumerate(trending, 1):
        print(f"{i}. {skill['skill_name']} ({skill['skill_category']})")
        print(f"   Demand: {skill['demand_count']} jobs ({skill['demand_percentage']}%)")
    
    # Get emerging skills
    print("\n🚀 Emerging Skills:")
    print("-"*70)
    emerging = analyzer.get_emerging_skills(threshold_days=30)
    for i, skill in enumerate(emerging[:5], 1):
        print(f"{i}. {skill['skill_name']} ({skill['skill_category']})")
        print(f"   Emergence Score: {skill['emergence_score']}")
    
    # Get skill demand by role
    print("\n👔 Skill Demand by Role:")
    print("-"*70)
    for role in ['Data Analyst', 'Data Engineer', 'Backend Developer']:
        demand = analyzer.get_skill_demand_by_role(role)
        print(f"\n{role}:")
        if 'top_skills' in demand:
            for skill in demand['top_skills'][:5]:
                print(f"  - {skill['skill']}: {skill['demand_count']} jobs")
    
    # Generate full report
    print("\n📋 Generating Full Report...")
    print("-"*70)
    report = analyzer.generate_trend_report()
    print(f"✅ Report generated with {len(report['trending_skills'])} trending skills")
    print(f"✅ Found {len(report['emerging_skills'])} emerging skills")
    
    print("\n" + "="*70)
    print("✅ Phase 5 Complete!")
    print("="*70 + "\n")
    
    return report


if __name__ == "__main__":
    main()
