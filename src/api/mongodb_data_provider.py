"""
MongoDB Data Provider for API
Provides real data from MongoDB (sourced from Adzuna API) for resume analysis
"""
import sys
import os
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.mongodb_client import MongoDBClient

class MongoDBDataProvider:
    def __init__(self):
        self.client = MongoDBClient()
        self.client.connect()
        self._skills_cache = None
        self._jobs_cache = None
        self._role_skills_cache = None
    
    def get_all_skills(self):
        """Get all skills from MongoDB Silver layer (from Adzuna data)"""
        if self._skills_cache is None:
            skills = self.client.get_silver_data('skills')
            self._skills_cache = [
                {
                    'skill_name': s.get('skill_name', ''),
                    'category': s.get('category', 'Other')
                }
                for s in skills
            ]
        return self._skills_cache
    
    def get_all_jobs(self):
        """Get all jobs from MongoDB Silver layer (from Adzuna data)"""
        if self._jobs_cache is None:
            jobs = self.client.get_silver_data('jobs')
            self._jobs_cache = jobs
        return self._jobs_cache
    
    def get_role_skill_mappings(self):
        """
        Build role-skill mappings from real Adzuna job data in MongoDB
        Returns dict: {role: [list of skills]}
        """
        if self._role_skills_cache is not None:
            return self._role_skills_cache
        
        # Build role-skill mapping from real job data
        try:
            # Get jobs from MongoDB
            jobs = self.get_all_jobs()
            
            if not jobs or len(jobs) == 0:
                # Fallback to default mappings if no jobs in MongoDB
                return self._get_default_role_skills()
            
            role_skills = defaultdict(set)
            
            for job in jobs:
                title = job.get('title', '').lower()
                skills = job.get('skills', [])
                
                # Normalize role title
                role = self._normalize_role_title(title)
                
                if role and skills:
                    for skill in skills:
                        if isinstance(skill, str):
                            role_skills[role].add(skill.lower())
            
            # Convert sets to lists
            self._role_skills_cache = {
                role: list(skills) 
                for role, skills in role_skills.items()
                if len(skills) >= 3  # Only include roles with at least 3 skills
            }
        except Exception as e:
            print(f"⚠️  Error building role-skill mappings from MongoDB: {e}")
            # Fallback will handle it below
        
        # If still empty, use defaults
        if not self._role_skills_cache:
            self._role_skills_cache = self._get_default_role_skills()
        
        return self._role_skills_cache
    
    def _normalize_role_title(self, title):
        """Normalize job title to standard role"""
        title_lower = title.lower()
        
        if 'data scientist' in title_lower or 'data science' in title_lower:
            return 'Data Scientist'
        elif 'data engineer' in title_lower:
            return 'Data Engineer'
        elif 'machine learning' in title_lower or 'ml engineer' in title_lower:
            return 'ML Engineer'
        elif 'data analyst' in title_lower:
            return 'Data Analyst'
        elif 'software engineer' in title_lower or 'software developer' in title_lower:
            return 'Software Engineer'
        elif 'backend' in title_lower:
            return 'Backend Developer'
        elif 'frontend' in title_lower:
            return 'Frontend Developer'
        elif 'full stack' in title_lower or 'fullstack' in title_lower:
            return 'Full Stack Developer'
        elif 'devops' in title_lower:
            return 'DevOps Engineer'
        elif 'cloud' in title_lower:
            return 'Cloud Engineer'
        
        return None
    
    def _get_default_role_skills(self):
        """Default role-skill mappings (fallback when MongoDB is empty)"""
        return {
            'Software Engineer': ['python', 'java', 'javascript', 'git', 'docker', 'kubernetes', 'react', 'node', 'api', 'testing'],
            'Data Scientist': ['python', 'machine learning', 'statistics', 'deep learning', 'tensorflow', 'pytorch', 'sql', 'data analysis'],
            'Data Engineer': ['python', 'sql', 'spark', 'airflow', 'etl', 'aws', 'kafka', 'hadoop', 'data pipeline'],
            'ML Engineer': ['python', 'machine learning', 'deep learning', 'mlops', 'docker', 'kubernetes', 'tensorflow', 'model deployment'],
            'Data Analyst': ['sql', 'python', 'excel', 'tableau', 'power bi', 'statistics', 'data visualization'],
            'Backend Developer': ['python', 'java', 'node', 'sql', 'api', 'docker', 'microservices'],
            'Frontend Developer': ['javascript', 'react', 'html', 'css', 'typescript', 'vue', 'angular'],
            'Full Stack Developer': ['javascript', 'python', 'react', 'node', 'sql', 'docker', 'api'],
            'DevOps Engineer': ['docker', 'kubernetes', 'ci/cd', 'aws', 'terraform', 'jenkins', 'linux'],
            'Cloud Engineer': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'networking']
        }
    
    def get_skill_priorities(self):
        """
        Get skill priority scores from MongoDB Gold layer
        Returns dict: {skill_name: priority_score}
        """
        try:
            skill_gaps = self.client.get_gold_data('skill_gaps')
            
            if skill_gaps and len(skill_gaps) > 0:
                return {
                    sg.get('skill_name', ''): sg.get('priority_score', 0.75)
                    for sg in skill_gaps
                }
        except:
            pass
        
        # Fallback priorities
        return {
            "Python": 0.95, "SQL": 0.93, "Machine Learning": 0.95,
            "JavaScript": 0.90, "AWS": 0.90, "Docker": 0.88,
            "Kubernetes": 0.85, "Git": 0.92, "Java": 0.85,
            "React": 0.88, "Node.js": 0.85, "TensorFlow": 0.85,
            "Deep Learning": 0.90, "Spark": 0.87, "Airflow": 0.85
        }
    
    def get_salary_data_by_role(self, role):
        """
        Get salary data for a specific role from MongoDB Gold layer
        Returns: {min, median, max} in INR
        """
        try:
            salaries = self.client.get_gold_data('salary_predictions')
            
            for sal in salaries:
                if sal.get('role', '').lower() == role.lower():
                    return {
                        'min_salary': sal.get('min_salary', 0),
                        'median_salary': sal.get('median_salary', 0),
                        'max_salary': sal.get('max_salary', 0),
                        'currency': 'INR'
                    }
        except:
            pass
        
        # Fallback salary data (INR)
        salary_map = {
            'Data Scientist': {'min': 800000, 'median': 1200000, 'max': 1600000},
            'Data Engineer': {'min': 700000, 'median': 1000000, 'max': 1400000},
            'ML Engineer': {'min': 900000, 'median': 1300000, 'max': 1800000},
            'Software Engineer': {'min': 600000, 'median': 900000, 'max': 1300000},
            'Data Analyst': {'min': 400000, 'median': 600000, 'max': 800000}
        }
        
        data = salary_map.get(role, {'min': 500000, 'median': 800000, 'max': 1200000})
        return {
            'min_salary': data['min'],
            'median_salary': data['median'],
            'max_salary': data['max'],
            'currency': 'INR'
        }
    
    def get_suggested_jobs(self, role_name, limit=5):
        """
        Fetch real jobs from MongoDB matching a predicted role
        """
        try:
            # Simple regex search on title for the role
            query = {"title": {"$regex": role_name, "$options": "i"}}
            jobs = self.client.get_silver_data('jobs', query=query, limit=limit)
            
            if not jobs:
                # Try a broader search if no exact matches
                keywords = role_name.split()
                if len(keywords) > 1:
                    query = {"title": {"$regex": keywords[0], "$options": "i"}}
                    jobs = self.client.get_silver_data('jobs', query=query, limit=limit)
            
            suggested = []
            for j in jobs:
                suggested.append({
                    "title": j.get('title', 'Position'),
                    "company": j.get('company', 'Not specified'),
                    "location": j.get('location', 'Remote/Various'),
                    "salary_min": j.get('salary_min', 0),
                    "salary_max": j.get('salary_max', 0),
                    "currency": j.get('currency', 'INR'),
                    "description": j.get('description', '')[:100] + "..." if j.get('description') else ""
                })
            return suggested
        except Exception as e:
            print(f"⚠️  Error fetching suggested jobs: {e}")
            return []
    
    def close(self):
        """Close MongoDB connection"""
        self.client.close()

# Global instance
_data_provider = None

def get_data_provider():
    """Get or create global data provider instance"""
    global _data_provider
    if _data_provider is None:
        _data_provider = MongoDBDataProvider()
    return _data_provider
