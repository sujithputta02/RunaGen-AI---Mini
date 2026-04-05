"""
Generate synthetic training data for ML models
Based on real skills from MongoDB and industry standards
"""
import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.mongodb_client import MongoDBClient
from utils.logger import setup_logger

logger = setup_logger('data_generation')

def load_skills_from_mongodb():
    """Load real skills from MongoDB"""
    client = MongoDBClient()
    client.connect()
    
    skills = client.get_silver_data('skills')
    client.close()
    
    skill_names = [s.get('skill_name', '') for s in skills if s.get('skill_name')]
    return skill_names

def generate_job_training_data(skills, n_samples=5000):
    """Generate synthetic job data for training"""
    logger.info(f"Generating {n_samples} synthetic job records...")
    
    # Define role templates with typical skills
    role_templates = {
        'Data Scientist': {
            'core_skills': ['Python', 'Machine Learning', 'Statistics', 'SQL', 'Data Analysis'],
            'common_skills': ['Deep Learning', 'TensorFlow', 'PyTorch', 'Pandas', 'NumPy', 'Scikit-learn', 'R'],
            'salary_range': (800000, 1800000),
            'weight': 0.15
        },
        'Data Engineer': {
            'core_skills': ['Python', 'SQL', 'ETL', 'Data Pipeline', 'Apache Spark'],
            'common_skills': ['Airflow', 'Kafka', 'AWS', 'Docker', 'Kubernetes', 'Hadoop', 'MongoDB'],
            'salary_range': (700000, 1600000),
            'weight': 0.15
        },
        'ML Engineer': {
            'core_skills': ['Python', 'Machine Learning', 'Deep Learning', 'MLOps', 'TensorFlow'],
            'common_skills': ['PyTorch', 'Docker', 'Kubernetes', 'AWS', 'Model Deployment', 'CI/CD'],
            'salary_range': (900000, 2000000),
            'weight': 0.12
        },
        'Software Engineer': {
            'core_skills': ['Python', 'Java', 'Git', 'API', 'Testing'],
            'common_skills': ['Docker', 'Kubernetes', 'React', 'Node.js', 'SQL', 'MongoDB', 'Microservices'],
            'salary_range': (600000, 1500000),
            'weight': 0.20
        },
        'Data Analyst': {
            'core_skills': ['SQL', 'Excel', 'Data Analysis', 'Tableau', 'Python'],
            'common_skills': ['Power BI', 'Statistics', 'Data Visualization', 'Pandas', 'R'],
            'salary_range': (400000, 900000),
            'weight': 0.12
        },
        'Backend Developer': {
            'core_skills': ['Python', 'Java', 'Node.js', 'SQL', 'API'],
            'common_skills': ['Docker', 'Microservices', 'MongoDB', 'PostgreSQL', 'Redis', 'REST'],
            'salary_range': (600000, 1400000),
            'weight': 0.10
        },
        'Frontend Developer': {
            'core_skills': ['JavaScript', 'React', 'HTML', 'CSS', 'TypeScript'],
            'common_skills': ['Vue.js', 'Angular', 'Redux', 'Webpack', 'Git', 'Responsive Design'],
            'salary_range': (500000, 1200000),
            'weight': 0.08
        },
        'Full Stack Developer': {
            'core_skills': ['JavaScript', 'Python', 'React', 'Node.js', 'SQL'],
            'common_skills': ['Docker', 'MongoDB', 'API', 'Git', 'AWS', 'TypeScript'],
            'salary_range': (700000, 1500000),
            'weight': 0.08
        }
    }
    
    # Generate samples
    jobs = []
    
    for role, template in role_templates.items():
        n_role_samples = int(n_samples * template['weight'])
        
        for _ in range(n_role_samples):
            # Select skills
            n_core = np.random.randint(3, len(template['core_skills']) + 1)
            n_common = np.random.randint(2, 6)
            
            selected_skills = (
                list(np.random.choice(template['core_skills'], n_core, replace=False)) +
                list(np.random.choice(template['common_skills'], 
                                    min(n_common, len(template['common_skills'])), 
                                    replace=False))
            )
            
            # Generate salary based on experience
            experience = np.random.randint(0, 15)
            base_salary = np.random.uniform(*template['salary_range'])
            
            # Adjust for experience
            exp_multiplier = 1.0 + (experience * 0.08)
            salary = base_salary * exp_multiplier
            
            # Add some noise
            salary = salary * np.random.uniform(0.9, 1.1)
            
            jobs.append({
                'title': role,
                'skills': selected_skills,
                'skill_count': len(selected_skills),
                'experience_years': experience,
                'salary_min': int(salary * 0.85),
                'salary_max': int(salary * 1.15),
                'location': np.random.choice(['Bangalore', 'Mumbai', 'Delhi', 'Hyderabad', 'Pune'])
            })
    
    df = pd.DataFrame(jobs)
    logger.info(f"✓ Generated {len(df)} job records")
    logger.info(f"  Roles: {df['title'].nunique()}")
    logger.info(f"  Avg skills per job: {df['skill_count'].mean():.1f}")
    
    return df

def save_to_csv(df, filename):
    """Save dataframe to CSV"""
    output_dir = Path('data/csv_exports')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = output_dir / filename
    df.to_csv(filepath, index=False)
    logger.info(f"✓ Saved to {filepath}")

def main():
    """Generate all training data"""
    logger.info("="*70)
    logger.info("🎲 GENERATING SYNTHETIC TRAINING DATA")
    logger.info("="*70)
    
    # Load real skills
    logger.info("\n📊 Loading skills from MongoDB...")
    skills = load_skills_from_mongodb()
    logger.info(f"✓ Loaded {len(skills)} skills")
    
    # Generate job data
    jobs_df = generate_job_training_data(skills, n_samples=5000)
    
    # Save to CSV
    logger.info("\n💾 Saving training data...")
    save_to_csv(jobs_df, 'synthetic_jobs.csv')
    
    # Statistics
    logger.info("\n📊 TRAINING DATA STATISTICS:")
    logger.info(f"  Total jobs: {len(jobs_df)}")
    logger.info(f"  Roles: {jobs_df['title'].nunique()}")
    logger.info(f"\n  Role distribution:")
    for role, count in jobs_df['title'].value_counts().items():
        logger.info(f"    {role}: {count}")
    
    logger.info(f"\n  Salary statistics (INR):")
    logger.info(f"    Min: ₹{jobs_df['salary_min'].min()/100000:.1f}L")
    logger.info(f"    Max: ₹{jobs_df['salary_max'].max()/100000:.1f}L")
    logger.info(f"    Mean: ₹{((jobs_df['salary_min'] + jobs_df['salary_max'])/2).mean()/100000:.1f}L")
    
    logger.info("\n✅ Training data generation complete!")
    logger.info("   Ready for model training")
    
    return jobs_df

if __name__ == "__main__":
    main()
