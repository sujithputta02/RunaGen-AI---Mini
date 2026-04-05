"""
Improved Role-Skill Matcher
Maps skills to career roles with weighted scoring
"""
from typing import List, Dict, Tuple

class RoleSkillMatcher:
    def __init__(self):
        # Define comprehensive role-skill profiles with weights (20 Priority Roles)
        self.role_profiles = {
            'Data Scientist': {
                'core_skills': ['python', 'machine learning', 'statistics', 'sql'],
                'important_skills': ['pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'data analysis', 'jupyter'],
                'nice_to_have': ['r', 'spark', 'aws', 'tableau', 'deep learning', 'nlp'],
                'keywords': ['data scientist', 'scientist', 'data science', 'ds ', 'analytics scientist']
            },
            'Data Engineer': {
                'core_skills': ['python', 'sql', 'etl', 'data pipeline'],
                'important_skills': ['spark', 'airflow', 'kafka', 'aws', 'docker', 'postgresql', 'mongodb'],
                'nice_to_have': ['scala', 'hadoop', 'kubernetes', 'redis', 'elasticsearch', 'terraform'],
                'keywords': ['data engineer', 'etl engineer', 'pipeline engineer', 'data platform', 'big data engineer']
            },
            'ML Engineer': {
                'core_skills': ['python', 'machine learning', 'deep learning', 'tensorflow'],
                'important_skills': ['pytorch', 'docker', 'kubernetes', 'mlops', 'aws', 'git'],
                'nice_to_have': ['spark', 'airflow', 'fastapi', 'flask', 'model deployment', 'nlp'],
                'keywords': ['machine learning', 'ml engineer', 'ai engineer', 'mle', 'mlops', 'deep learning']
            },
            'Data Analyst': {
                'core_skills': ['sql', 'excel', 'data analysis', 'visualization'],
                'important_skills': ['python', 'tableau', 'power bi', 'statistics', 'pandas'],
                'nice_to_have': ['r', 'looker', 'google analytics', 'business intelligence'],
                'keywords': ['data analyst', 'business analyst', 'analytics', 'analyst', 'bi analyst']
            },
            'Software Engineer': {
                'core_skills': ['programming', 'algorithms', 'data structures'],
                'important_skills': ['python', 'java', 'javascript', 'git', 'sql', 'rest api', 'testing'],
                'nice_to_have': ['docker', 'kubernetes', 'aws', 'microservices', 'c++', 'system design'],
                'keywords': ['software engineer', 'software developer', 'sde', 'programmer', 'developer', 'qa engineer']
            },
            'Backend Developer': {
                'core_skills': ['backend', 'api', 'database', 'rest'],
                'important_skills': ['python', 'java', 'node.js', 'sql', 'rest', 'docker', 'django', 'flask'],
                'nice_to_have': ['redis', 'mongodb', 'postgresql', 'microservices', 'graphql', 'express'],
                'keywords': ['backend', 'back-end', 'server side', 'node.js', 'django', 'flask']
            },
            'Frontend Developer': {
                'core_skills': ['html', 'css', 'javascript', 'ui', 'frontend'],
                'important_skills': ['react', 'angular', 'vue', 'typescript', 'responsive', 'ux'],
                'nice_to_have': ['redux', 'sass', 'tailwind', 'next.js', 'testing'],
                'keywords': ['frontend', 'front-end', 'ui developer', 'ui engineer', 'react developer']
            },
            'Full Stack Developer': {
                'core_skills': ['frontend', 'backend', 'database', 'full stack', 'javascript'],
                'important_skills': ['react', 'node.js', 'sql', 'git', 'api', 'html', 'css'],
                'nice_to_have': ['docker', 'aws', 'mongodb', 'typescript', 'graphql', 'express'],
                'keywords': ['full stack', 'fullstack', 'full-stack']
            },
            'DevOps Engineer': {
                'core_skills': ['devops', 'ci/cd', 'automation', 'infrastructure'],
                'important_skills': ['docker', 'kubernetes', 'jenkins', 'aws', 'terraform', 'git', 'linux'],
                'nice_to_have': ['ansible', 'prometheus', 'grafana', 'scripting', 'cloudops', 'sre'],
                'keywords': ['devops', 'sre', 'site reliability', 'platform engineer', 'infrastructure']
            },
            'Cloud Engineer': {
                'core_skills': ['cloud', 'aws', 'infrastructure', 'architecture'],
                'important_skills': ['docker', 'kubernetes', 'terraform', 'networking', 'security', 'azure', 'gcp'],
                'nice_to_have': ['lambda', 's3', 'cloudformation', 'solutions architect'],
                'keywords': ['cloud engineer', 'cloud architect', 'aws engineer', 'azure engineer']
            },
            'Product Manager': {
                'core_skills': ['product management', 'roadmap', 'strategy', 'backlog'],
                'important_skills': ['agile', 'scrum', 'jira', 'stakeholder management', 'market research', 'prds'],
                'nice_to_have': ['analytics', 'ux', 'communication', 'leadership', 'kanban'],
                'keywords': ['product manager', 'product owner', 'product lead']
            },
            'Business Analyst': {
                'core_skills': ['business requirements', 'analysis', 'process mapping', 'documentation'],
                'important_skills': ['sql', 'excel', 'agile', 'stakeholder communication', 'gap analysis', 'user stories'],
                'nice_to_have': ['tableau', 'jira', 'uml', 'visio', 'data visualization'],
                'keywords': ['business analyst', 'process analyst', 'systems analyst']
            },
            'Project Manager': {
                'core_skills': ['project management', 'planning', 'delivery', 'budgeting'],
                'important_skills': ['pmp', 'agile', 'scrum', 'risk management', 'scheduling', 'team leadership'],
                'nice_to_have': ['ms project', 'jira', 'stakeholder management', 'operations'],
                'keywords': ['project manager', 'program manager', 'project lead']
            },
            'Account Manager': {
                'core_skills': ['relationship management', 'client management', 'sales', 'growth'],
                'important_skills': ['crm', 'communication', 'negotiation', 'upselling', 'account planning'],
                'nice_to_have': ['marketing', 'strategic planning', 'b2b', 'analytical skills'],
                'keywords': ['account manager', 'key account', 'client manager', 'customer success']
            },
            'Sales Representative': {
                'core_skills': ['sales', 'prospecting', 'lead generation', 'negotiation'],
                'important_skills': ['crm', 'communication', 'cold calling', 'b2b', 'presentation skills'],
                'nice_to_have': ['marketing', 'retail', 'customer service', 'business development'],
                'keywords': ['sales representative', 'inside sales', 'business development', 'sales exec']
            },
            'Financial Analyst': {
                'core_skills': ['financial modeling', 'analysis', 'accounting', 'forecasting'],
                'important_skills': ['excel', 'sql', 'reporting', 'data analysis', 'valuation', 'budgeting'],
                'nice_to_have': ['cfa', 'sap', 'tableau', 'python', 'vba'],
                'keywords': ['financial analyst', 'finance analyst', 'investment analyst']
            },
            'Accountant': {
                'core_skills': ['accounting', 'bookkeeping', 'taxation', 'auditing'],
                'important_skills': ['tally', 'gst', 'excel', 'financial statements', 'reconciliation'],
                'nice_to_have': ['ca', 'sap', 'cost accounting', 'compliance', 'cpa'],
                'keywords': ['accountant', 'chartered accountant', 'auditor']
            },
            'Marketing Manager': {
                'core_skills': ['marketing', 'branding', 'campaign architecture', 'strategy'],
                'important_skills': ['digital marketing', 'seo', 'sem', 'social media', 'analytics', 'content strategy'],
                'nice_to_have': ['google ads', 'hubspot', 'copywriting', 'public relations'],
                'keywords': ['marketing manager', 'digital marketing', 'performance marketing']
            },
            'HR Manager': {
                'core_skills': ['human resources', 'talent acquisition', 'recruitment', 'employee engagement'],
                'important_skills': ['payroll', 'compliance', 'onboarding', 'performance management', 'communication'],
                'nice_to_have': ['hrms', 'compensation', 'benefits', 'labor laws', 'training'],
                'keywords': ['hr manager', 'human resources', 'recruitment', 'talent acquisition']
            },
            'Customer Service': {
                'core_skills': ['customer service', 'communication', 'problem solving', 'support'],
                'important_skills': ['crm', 'ticketing system', 'soft skills', 'customer experience', 'voice support'],
                'nice_to_have': ['bpo', 'zendesk', 'email support', 'technical support'],
                'keywords': ['customer service', 'customer support', 'help desk', 'voice process']
            }
        }
        # Synonym Map for robust matching
        self.skill_synonyms = {
            'ml': 'machine learning',
            'ai': 'machine learning',
            'js': 'javascript',
            'reactjs': 'react',
            'react.js': 'react',
            'node.js': 'node.js',
            'nodejs': 'node.js',
            'sql': 'sql',
            'postgresql': 'postgres',
            'postgresql': 'postgresql',
            'git': 'git',
            'aws': 'aws',
            'amazon web services': 'aws',
            'gcp': 'google cloud',
            'google cloud': 'gcp',
            'ts': 'typescript',
            'mle': 'ml engineer'
        }
    
    def _normalize_skill(self, skill: str) -> str:
        """Normalize skill string for robust comparison"""
        s = skill.lower().strip()
        # Apply synonym mapping
        return self.skill_synonyms.get(s, s)

    def calculate_role_match(self, user_skills: List[str], resume_text: str = "") -> List[Dict]:
        """
        Calculate match scores for all roles based on skills and resume text
        """
        user_skills_norm = [self._normalize_skill(s) for s in user_skills]
        resume_lower = resume_text.lower() if resume_text else ""
        
        role_scores = {}
        
        for role, profile in self.role_profiles.items():
            score = 0.0
            max_score = 0.0
            
            # Core skills (weight: 5.0 - fundamental requirements)
            core_weight = 5.0
            for r_skill in profile['core_skills']:
                max_score += core_weight
                r_skill_norm = self._normalize_skill(r_skill)
                # Check for direct match or word-by-word match
                if any(r_skill_norm in u_skill or u_skill in r_skill_norm for u_skill in user_skills_norm):
                    score += core_weight
            
            # Important skills (weight: 2.0)
            important_weight = 2.0
            for r_skill in profile['important_skills']:
                max_score += important_weight
                r_skill_norm = self._normalize_skill(r_skill)
                if any(r_skill_norm in u_skill or u_skill in r_skill_norm for u_skill in user_skills_norm):
                    score += important_weight
            
            # Nice to have skills (weight: 1.0)
            nice_weight = 1.0
            for r_skill in profile['nice_to_have']:
                max_score += nice_weight
                r_skill_norm = self._normalize_skill(r_skill)
                if any(r_skill_norm in u_skill or u_skill in r_skill_norm for u_skill in user_skills_norm):
                    score += nice_weight
            
            # Keyword bonus (weight: 3.0) - check resume text
            if resume_lower:
                keyword_weight = 3.0
                # Don't add to max_score, treat it as a pure bonus
                for keyword in profile['keywords']:
                    if keyword in resume_lower:
                        score += keyword_weight
            
            # Calculate percentage
            percentage = (score / max_score) if max_score > 0 else 0.0
            role_scores[role] = percentage
        
        # Sort by score
        sorted_roles = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Format results
        results = []
        for role, score in sorted_roles[:5]:  # Top 5 roles
            # Ensure minimum score for display
            display_score = max(score, 0.1)  # At least 10%
            results.append({
                "role": role,
                "probability": float(min(display_score, 0.99))  # Cap at 99%
            })
        
        return results
    
    def get_role_skills(self, role: str) -> List[str]:
        """Get all skills for a specific role"""
        if role not in self.role_profiles:
            return []
        
        profile = self.role_profiles[role]
        all_skills = (
            profile['core_skills'] + 
            profile['important_skills'] + 
            profile['nice_to_have']
        )
        return [s.title() for s in all_skills]
    
    def get_missing_skills(self, user_skills: List[str], target_role: str) -> List[Tuple[str, float]]:
        """
        Get missing skills for a target role with priority scores
        Returns list of (skill, priority) tuples
        """
        if target_role not in self.role_profiles:
            return []
        
        user_skills_norm = [self._normalize_skill(s) for s in user_skills]
        profile = self.role_profiles[target_role]
        
        missing_skills = []
        
        # Core skills (priority: 0.95)
        for r_skill in profile['core_skills']:
            r_skill_norm = self._normalize_skill(r_skill)
            # Symmetric check: Is required skill in user skill, or user skill in required skill?
            is_present = any(
                r_skill_norm == u_skill or 
                r_skill_norm in u_skill or 
                u_skill in r_skill_norm 
                for u_skill in user_skills_norm
            )
            if not is_present:
                missing_skills.append((r_skill.title(), 0.95))
        
        # Important skills (priority: 0.80)
        for r_skill in profile['important_skills']:
            r_skill_norm = self._normalize_skill(r_skill)
            is_present = any(
                r_skill_norm == u_skill or 
                r_skill_norm in u_skill or 
                u_skill in r_skill_norm 
                for u_skill in user_skills_norm
            )
            if not is_present:
                missing_skills.append((r_skill.title(), 0.80))
        
        # Nice to have (priority: 0.60)
        for r_skill in profile['nice_to_have'][:5]:  # Top 5 only
            r_skill_norm = self._normalize_skill(r_skill)
            is_present = any(
                r_skill_norm == u_skill or 
                r_skill_norm in u_skill or 
                u_skill in r_skill_norm 
                for u_skill in user_skills_norm
            )
            if not is_present:
                missing_skills.append((r_skill.title(), 0.60))
        
        # Sort by priority
        missing_skills.sort(key=lambda x: x[1], reverse=True)
        
        return missing_skills[:10]  # Top 10 missing skills

if __name__ == "__main__":
    # Test the matcher
    matcher = RoleSkillMatcher()
    
    # Test case 1: Data Analyst
    analyst_skills = ["SQL", "Python", "Excel", "Tableau", "Pandas"]
    results = matcher.calculate_role_match(analyst_skills)
    
    print("Test Case 1: Data Analyst Skills")
    print("Skills:", analyst_skills)
    print("\nTop 3 Predictions:")
    for i, pred in enumerate(results[:3], 1):
        print(f"{i}. {pred['role']}: {pred['probability']*100:.1f}%")
    
    # Test case 2: Data Engineer
    engineer_skills = ["Python", "SQL", "Spark", "Airflow", "AWS", "Docker", "ETL"]
    results = matcher.calculate_role_match(engineer_skills)
    
    print("\n\nTest Case 2: Data Engineer Skills")
    print("Skills:", engineer_skills)
    print("\nTop 3 Predictions:")
    for i, pred in enumerate(results[:3], 1):
        print(f"{i}. {pred['role']}: {pred['probability']*100:.1f}%")
    
    # Test case 3: Backend Developer
    backend_skills = ["Python", "Django", "REST API", "PostgreSQL", "Docker", "Redis"]
    results = matcher.calculate_role_match(backend_skills)
    
    print("\n\nTest Case 3: Backend Developer Skills")
    print("Skills:", backend_skills)
    print("\nTop 3 Predictions:")
    for i, pred in enumerate(results[:3], 1):
        print(f"{i}. {pred['role']}: {pred['probability']*100:.1f}%")
