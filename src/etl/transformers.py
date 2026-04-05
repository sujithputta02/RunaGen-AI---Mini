"""
ELT Transformers - Bronze to Silver to Gold
Transforms raw data into cleaned and aggregated features
"""
import os
import sys
import re
from collections import Counter
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.mongodb_client import MongoDBClient
from utils.logger import setup_logger

logger = setup_logger('transformers')

class BronzeToSilverTransformer:
    """Transform Bronze (raw) data to Silver (cleaned) layer"""
    
    def __init__(self):
        self.mongo_client = MongoDBClient()
        self.mongo_client.connect()
    
    def transform_jobs(self):
        """Clean and standardize job postings"""
        logger.info("Transforming jobs: Bronze → Silver")
        
        # Get raw jobs from Bronze
        bronze_jobs = self.mongo_client.get_bronze_data('jobs')
        logger.info(f"Found {len(bronze_jobs)} raw job records")
        
        silver_jobs = []
        
        for record in bronze_jobs:
            job = record.get('data', {})
            
            # Clean and standardize
            cleaned_job = {
                'job_id': job.get('id'),
                'title': self._clean_text(job.get('title', '')),
                'company': self._clean_text(job.get('company', {}).get('display_name', '')),
                'location': job.get('location', {}).get('display_name', ''),
                'description': self._clean_text(job.get('description', '')),
                'salary_min': job.get('salary_min'),
                'salary_max': job.get('salary_max'),
                'created': job.get('created'),
                'category': job.get('category', {}).get('label', ''),
                'contract_type': job.get('contract_type'),
                'extracted_skills': self._extract_skills_from_description(job.get('description', '')),
                'source_metadata': record.get('metadata', {}),
                'bronze_id': str(record.get('_id'))
            }
            
            silver_jobs.append(cleaned_job)
        
        # Insert into Silver layer
        if silver_jobs:
            self.mongo_client.insert_silver('jobs', silver_jobs)
            logger.info(f"Transformed {len(silver_jobs)} jobs to Silver layer")
        
        return len(silver_jobs)
    
    def transform_skills(self):
        """Clean and standardize skills taxonomy"""
        logger.info("Transforming skills: Bronze → Silver")
        
        # Get raw skills from Bronze
        bronze_skills = self.mongo_client.get_bronze_data('skills')
        logger.info(f"Found {len(bronze_skills)} raw skill records")
        
        silver_skills = []
        
        for record in bronze_skills:
            skill = record.get('data', {})
            
            # Standardize skill data
            cleaned_skill = {
                'skill_id': skill.get('id'),
                'skill_name': self._standardize_skill_name(skill.get('name', '')),
                'category': skill.get('category', 'General'),
                'description': self._clean_text(skill.get('description', '')),
                'bronze_id': str(record.get('_id'))
            }
            
            silver_skills.append(cleaned_skill)
        
        # Insert into Silver layer
        if silver_skills:
            self.mongo_client.insert_silver('skills', silver_skills)
            logger.info(f"Transformed {len(silver_skills)} skills to Silver layer")
        
        return len(silver_skills)
    
    def _clean_text(self, text):
        """Clean text data"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text.strip()
    
    def _standardize_skill_name(self, skill_name):
        """Standardize skill names"""
        # Convert to title case and remove extra spaces
        return ' '.join(skill_name.strip().title().split())
    
    def _extract_skills_from_description(self, description):
        """Extract skills from job description"""
        # Common tech skills (simplified)
        skill_keywords = [
            'python', 'java', 'javascript', 'sql', 'aws', 'azure', 'gcp',
            'docker', 'kubernetes', 'spark', 'hadoop', 'machine learning',
            'deep learning', 'tensorflow', 'pytorch', 'pandas', 'numpy',
            'react', 'angular', 'vue', 'node.js', 'mongodb', 'postgresql'
        ]
        
        description_lower = description.lower()
        found_skills = []
        
        for skill in skill_keywords:
            if skill in description_lower:
                found_skills.append(skill.title())
        
        return found_skills
    
    def close(self):
        """Close MongoDB connection"""
        self.mongo_client.close()


class SilverToGoldTransformer:
    """Transform Silver (cleaned) data to Gold (features) layer"""
    
    def __init__(self):
        self.mongo_client = MongoDBClient()
        self.mongo_client.connect()
    
    def create_skill_frequency_features(self):
        """Create skill frequency aggregations"""
        logger.info("Creating skill frequency features: Silver → Gold")
        
        # Get all jobs from Silver
        silver_jobs = self.mongo_client.get_silver_data('jobs')
        
        # Aggregate skill frequencies
        all_skills = []
        skill_salaries = {}
        
        for job in silver_jobs:
            skills = job.get('extracted_skills', [])
            salary_avg = None
            
            if job.get('salary_min') and job.get('salary_max'):
                salary_avg = (job['salary_min'] + job['salary_max']) / 2
            
            for skill in skills:
                all_skills.append(skill)
                
                if salary_avg:
                    if skill not in skill_salaries:
                        skill_salaries[skill] = []
                    skill_salaries[skill].append(salary_avg)
        
        # Calculate frequencies
        skill_counts = Counter(all_skills)
        total_jobs = len(silver_jobs)
        
        # Create feature documents
        skill_features = []
        
        for skill, count in skill_counts.items():
            feature = {
                'skill_name': skill,
                'frequency': count,
                'demand_weight': count / total_jobs if total_jobs > 0 else 0,
                'avg_salary': sum(skill_salaries.get(skill, [0])) / len(skill_salaries.get(skill, [1])),
                'job_count': count,
                'updated_at': datetime.utcnow()
            }
            skill_features.append(feature)
        
        # Upsert into Gold layer
        for feature in skill_features:
            self.mongo_client.upsert_gold(
                'skill_frequency',
                {'skill_name': feature['skill_name']},
                feature
            )
        
        logger.info(f"Created {len(skill_features)} skill frequency features")
        return len(skill_features)
    
    def create_role_skill_matrix(self):
        """Create role-skill co-occurrence matrix"""
        logger.info("Creating role-skill matrix: Silver → Gold")
        
        # Get all jobs from Silver
        silver_jobs = self.mongo_client.get_silver_data('jobs')
        
        # Build role-skill relationships
        role_skills = {}
        
        for job in silver_jobs:
            title = job.get('title', '').lower()
            skills = job.get('extracted_skills', [])
            
            # Categorize role
            role = self._categorize_role(title)
            
            if role not in role_skills:
                role_skills[role] = []
            
            role_skills[role].extend(skills)
        
        # Create matrix features
        matrix_features = []
        
        for role, skills in role_skills.items():
            skill_counts = Counter(skills)
            total_skills = len(skills)
            
            for skill, count in skill_counts.items():
                feature = {
                    'role': role,
                    'skill': skill,
                    'co_occurrence': count,
                    'skill_importance': count / total_skills if total_skills > 0 else 0,
                    'updated_at': datetime.utcnow()
                }
                matrix_features.append(feature)
        
        # Insert into Gold layer
        if matrix_features:
            self.mongo_client.insert_gold('role_skill_matrix', matrix_features)
            logger.info(f"Created {len(matrix_features)} role-skill relationships")
        
        return len(matrix_features)
    
    def _categorize_role(self, title):
        """Categorize job title into role"""
        title_lower = title.lower()
        
        if 'data scientist' in title_lower or 'scientist' in title_lower:
            return 'Data Scientist'
        elif 'machine learning' in title_lower or 'ml engineer' in title_lower:
            return 'ML Engineer'
        elif 'data engineer' in title_lower:
            return 'Data Engineer'
        elif 'data analyst' in title_lower or 'analyst' in title_lower:
            return 'Data Analyst'
        else:
            return 'Other'
    
    def close(self):
        """Close MongoDB connection"""
        self.mongo_client.close()


if __name__ == "__main__":
    # Test transformations
    print("=== Bronze → Silver Transformation ===")
    bronze_to_silver = BronzeToSilverTransformer()
    try:
        jobs_count = bronze_to_silver.transform_jobs()
        skills_count = bronze_to_silver.transform_skills()
        print(f"✓ Transformed {jobs_count} jobs and {skills_count} skills")
    finally:
        bronze_to_silver.close()
    
    print("\n=== Silver → Gold Transformation ===")
    silver_to_gold = SilverToGoldTransformer()
    try:
        skill_features = silver_to_gold.create_skill_frequency_features()
        matrix_features = silver_to_gold.create_role_skill_matrix()
        print(f"✓ Created {skill_features} skill features and {matrix_features} role-skill relationships")
    finally:
        silver_to_gold.close()
