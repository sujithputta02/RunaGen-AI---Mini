"""
Advanced Feature Engineering
Create powerful features for ML models
"""
import pandas as pd
import numpy as np
from typing import List, Dict
from datetime import datetime
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

class FeatureEngineer:
    def __init__(self):
        self.skill_rarity_scores = {}
        self.role_skill_mappings = {}
    
    def calculate_skill_diversity(self, skills: List[str]) -> float:
        """
        Calculate skill diversity using Shannon entropy
        Higher diversity = more varied skill set
        """
        if not skills:
            return 0.0
        
        # Count skill categories
        categories = [self._get_skill_category(skill) for skill in skills]
        category_counts = Counter(categories)
        
        # Calculate Shannon entropy
        total = len(categories)
        entropy = 0.0
        
        for count in category_counts.values():
            p = count / total
            if p > 0:
                entropy -= p * np.log2(p)
        
        # Normalize to 0-1 range
        max_entropy = np.log2(len(category_counts)) if len(category_counts) > 1 else 1
        diversity_score = entropy / max_entropy if max_entropy > 0 else 0
        
        return diversity_score
    
    def _get_skill_category(self, skill: str) -> str:
        """Categorize a skill"""
        skill_lower = skill.lower()
        
        if any(lang in skill_lower for lang in ['python', 'java', 'javascript', 'c++', 'go', 'rust', 'ruby']):
            return 'programming'
        elif any(fw in skill_lower for fw in ['react', 'angular', 'vue', 'django', 'flask', 'spring']):
            return 'framework'
        elif any(db in skill_lower for db in ['sql', 'mongodb', 'postgresql', 'redis', 'elasticsearch']):
            return 'database'
        elif any(cloud in skill_lower for cloud in ['aws', 'azure', 'gcp', 'cloud']):
            return 'cloud'
        elif any(ml in skill_lower for ml in ['machine learning', 'deep learning', 'tensorflow', 'pytorch']):
            return 'ml_ai'
        elif any(devops in skill_lower for devops in ['docker', 'kubernetes', 'jenkins', 'ci/cd']):
            return 'devops'
        else:
            return 'other'
    
    def calculate_skill_rarity(self, skills: List[str], all_skills_freq: Dict[str, int] = None) -> float:
        """
        Calculate rarity score - rare skills are more valuable
        """
        if not skills or not all_skills_freq:
            return 0.5  # Default medium rarity
        
        total_resumes = sum(all_skills_freq.values())
        rarity_scores = []
        
        for skill in skills:
            freq = all_skills_freq.get(skill.lower(), 1)
            # Inverse frequency: rare skills have higher scores
            rarity = 1 - (freq / total_resumes)
            rarity_scores.append(rarity)
        
        return np.mean(rarity_scores) if rarity_scores else 0.5
    
    def calculate_total_experience(self, work_history: List[Dict]) -> float:
        """Calculate total years of experience"""
        if not work_history:
            return 0.0
        
        total_months = 0
        
        for job in work_history:
            start_date = job.get('start_date')
            end_date = job.get('end_date', datetime.now())
            
            if start_date:
                if isinstance(start_date, str):
                    start_date = datetime.strptime(start_date, '%Y-%m')
                if isinstance(end_date, str):
                    end_date = datetime.strptime(end_date, '%Y-%m')
                
                months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                total_months += months
        
        return total_months / 12.0  # Convert to years
    
    def calculate_avg_job_duration(self, work_history: List[Dict]) -> float:
        """Calculate average duration per job"""
        if not work_history:
            return 0.0
        
        durations = []
        
        for job in work_history:
            start_date = job.get('start_date')
            end_date = job.get('end_date', datetime.now())
            
            if start_date:
                if isinstance(start_date, str):
                    start_date = datetime.strptime(start_date, '%Y-%m')
                if isinstance(end_date, str):
                    end_date = datetime.strptime(end_date, '%Y-%m')
                
                months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                durations.append(months)
        
        return np.mean(durations) / 12.0 if durations else 0.0
    
    def calculate_career_progression(self, work_history: List[Dict]) -> float:
        """
        Calculate career progression score
        Based on job title seniority and salary growth
        """
        if not work_history or len(work_history) < 2:
            return 0.5  # Default medium progression
        
        # Sort by date
        sorted_history = sorted(work_history, key=lambda x: x.get('start_date', ''))
        
        seniority_levels = {
            'intern': 1,
            'junior': 2,
            'associate': 3,
            'mid': 4,
            'senior': 5,
            'lead': 6,
            'principal': 7,
            'director': 8,
            'vp': 9,
            'c-level': 10
        }
        
        progression_score = 0
        
        for i in range(1, len(sorted_history)):
            prev_job = sorted_history[i-1]
            curr_job = sorted_history[i]
            
            # Check title progression
            prev_title = prev_job.get('title', '').lower()
            curr_title = curr_job.get('title', '').lower()
            
            prev_level = 3  # Default mid-level
            curr_level = 3
            
            for keyword, level in seniority_levels.items():
                if keyword in prev_title:
                    prev_level = level
                if keyword in curr_title:
                    curr_level = level
            
            if curr_level > prev_level:
                progression_score += (curr_level - prev_level) / 10.0
        
        # Normalize to 0-1
        max_possible_progression = (len(sorted_history) - 1) * 0.7
        normalized_score = min(1.0, progression_score / max_possible_progression) if max_possible_progression > 0 else 0.5
        
        return normalized_score
    
    def encode_education_level(self, education: str) -> int:
        """Encode education level as numeric"""
        if not education:
            return 0
        
        education_lower = education.lower()
        
        if 'phd' in education_lower or 'doctorate' in education_lower:
            return 5
        elif 'master' in education_lower or 'mba' in education_lower:
            return 4
        elif 'bachelor' in education_lower:
            return 3
        elif 'diploma' in education_lower or 'associate' in education_lower:
            return 2
        elif 'high school' in education_lower:
            return 1
        else:
            return 0
    
    def calculate_education_relevance(self, education: str, target_role: str) -> float:
        """Calculate how relevant education is to target role"""
        if not education or not target_role:
            return 0.5
        
        education_lower = education.lower()
        role_lower = target_role.lower()
        
        # Define relevant keywords for each role
        role_keywords = {
            'data scientist': ['data', 'statistics', 'mathematics', 'computer science', 'analytics'],
            'data engineer': ['computer science', 'engineering', 'data', 'software'],
            'ml engineer': ['computer science', 'machine learning', 'ai', 'mathematics'],
            'software engineer': ['computer science', 'software', 'engineering', 'technology'],
            'data analyst': ['data', 'statistics', 'analytics', 'business', 'mathematics']
        }
        
        relevant_keywords = role_keywords.get(role_lower, ['computer', 'technology', 'engineering'])
        
        # Count matching keywords
        matches = sum(1 for keyword in relevant_keywords if keyword in education_lower)
        relevance_score = matches / len(relevant_keywords)
        
        return relevance_score
    
    def calculate_skill_recency(self, skills: List[str], work_history: List[Dict]) -> float:
        """
        Calculate how recently skills were used
        Recent usage = higher score
        """
        if not work_history:
            return 0.5
        
        # Get most recent job
        sorted_history = sorted(work_history, key=lambda x: x.get('end_date', '9999-12'), reverse=True)
        most_recent_job = sorted_history[0]
        
        recent_skills = most_recent_job.get('skills', [])
        
        if not recent_skills:
            return 0.5
        
        # Calculate overlap with current skills
        skill_overlap = len(set(skills) & set(recent_skills)) / len(skills) if skills else 0
        
        return skill_overlap
    
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create all engineered features"""
        print("🔧 Engineering features...")
        
        # 1. Skill-based features
        if 'skills' in df.columns:
            print("  - Creating skill features...")
            df['skill_count'] = df['skills'].apply(lambda x: len(x) if isinstance(x, list) else 0)
            df['skill_diversity'] = df['skills'].apply(self.calculate_skill_diversity)
            df['skill_rarity_score'] = df['skills'].apply(
                lambda x: self.calculate_skill_rarity(x, self.skill_rarity_scores)
            )
        
        # 2. Experience features
        if 'work_history' in df.columns:
            print("  - Creating experience features...")
            df['total_experience'] = df['work_history'].apply(self.calculate_total_experience)
            df['avg_job_duration'] = df['work_history'].apply(self.calculate_avg_job_duration)
            df['career_progression'] = df['work_history'].apply(self.calculate_career_progression)
            df['job_count'] = df['work_history'].apply(lambda x: len(x) if isinstance(x, list) else 0)
        
        # 3. Education features
        if 'education' in df.columns:
            print("  - Creating education features...")
            df['education_level'] = df['education'].apply(self.encode_education_level)
            
            if 'target_role' in df.columns:
                df['education_relevance'] = df.apply(
                    lambda row: self.calculate_education_relevance(row['education'], row['target_role']),
                    axis=1
                )
        
        # 4. Interaction features
        if 'skill_count' in df.columns and 'total_experience' in df.columns:
            print("  - Creating interaction features...")
            df['skill_exp_interaction'] = df['skill_count'] * df['total_experience']
            df['skills_per_year'] = df['skill_count'] / (df['total_experience'] + 1)  # Avoid division by zero
        
        # 5. Temporal features
        if 'graduation_year' in df.columns:
            print("  - Creating temporal features...")
            current_year = datetime.now().year
            df['years_since_graduation'] = current_year - df['graduation_year']
        
        if 'work_history' in df.columns and 'skills' in df.columns:
            df['skill_recency'] = df.apply(
                lambda row: self.calculate_skill_recency(row['skills'], row['work_history']),
                axis=1
            )
        
        print("✅ Feature engineering complete!")
        print(f"   Total features: {len(df.columns)}")
        
        return df
    
    def get_feature_importance_names(self) -> List[str]:
        """Get list of all engineered feature names"""
        return [
            'skill_count',
            'skill_diversity',
            'skill_rarity_score',
            'total_experience',
            'avg_job_duration',
            'career_progression',
            'job_count',
            'education_level',
            'education_relevance',
            'skill_exp_interaction',
            'skills_per_year',
            'years_since_graduation',
            'skill_recency'
        ]


if __name__ == "__main__":
    # Test feature engineering
    engineer = FeatureEngineer()
    
    # Sample data
    sample_data = {
        'skills': [
            ['Python', 'SQL', 'Machine Learning', 'AWS', 'Docker'],
            ['JavaScript', 'React', 'Node.js', 'MongoDB'],
            ['Java', 'Spring', 'PostgreSQL', 'Kubernetes']
        ],
        'work_history': [
            [
                {'title': 'Junior Data Scientist', 'start_date': '2020-01', 'end_date': '2022-06'},
                {'title': 'Senior Data Scientist', 'start_date': '2022-07', 'end_date': '2024-12'}
            ],
            [
                {'title': 'Frontend Developer', 'start_date': '2021-03', 'end_date': '2024-12'}
            ],
            [
                {'title': 'Software Engineer', 'start_date': '2019-06', 'end_date': '2024-12'}
            ]
        ],
        'education': ['Masters in Computer Science', 'Bachelors in Engineering', 'Bachelors in Computer Science'],
        'graduation_year': [2020, 2021, 2019],
        'target_role': ['Data Scientist', 'Frontend Developer', 'Software Engineer']
    }
    
    df = pd.DataFrame(sample_data)
    
    print("Original DataFrame:")
    print(df[['skills', 'education']].head())
    print("\n" + "="*70 + "\n")
    
    # Engineer features
    df_engineered = engineer.create_features(df)
    
    print("\nEngineered Features:")
    feature_cols = engineer.get_feature_importance_names()
    available_cols = [col for col in feature_cols if col in df_engineered.columns]
    print(df_engineered[available_cols])
    
    print("\n✅ Feature engineering test complete!")
