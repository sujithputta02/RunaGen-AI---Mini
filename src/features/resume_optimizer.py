"""
Phase 6: Resume Optimization Engine
Optimize resumes based on job requirements and skill trends
"""
import os
from dotenv import load_dotenv
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
from typing import Dict, List, Tuple
import json
import logging
import re
from collections import Counter

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResumeOptimizer:
    """Optimize resumes for better job matching"""
    
    def __init__(self):
        """Initialize BigQuery client and skill database"""
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
        
        # Load skill database
        self.skills_db = self._load_skills_database()
    
    def _load_skills_database(self) -> Dict[str, List[str]]:
        """Load skills database from BigQuery"""
        logger.info("📚 Loading skills database...")
        
        query = f"""
        SELECT skill_category, skill_name
        FROM `{self.project_id}.runagen_bronze.raw_skills`
        WHERE skill_name IS NOT NULL
        GROUP BY skill_category, skill_name
        """
        
        try:
            results = self.bq_client.query(query).to_dataframe()
            
            skills_by_category = {}
            for _, row in results.iterrows():
                category = row['skill_category'] or 'Other'
                if category not in skills_by_category:
                    skills_by_category[category] = []
                skills_by_category[category].append(row['skill_name'].lower())
            
            logger.info(f"✅ Loaded {sum(len(v) for v in skills_by_category.values())} skills")
            return skills_by_category
        
        except Exception as e:
            logger.error(f"❌ Error loading skills database: {e}")
            return {}
    
    def extract_skills_from_resume(self, resume_text: str) -> Dict[str, List[str]]:
        """Extract skills from resume text"""
        logger.info("🔍 Extracting skills from resume...")
        
        resume_lower = resume_text.lower()
        found_skills = {}
        
        for category, skills in self.skills_db.items():
            found_skills[category] = []
            for skill in skills:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, resume_lower):
                    found_skills[category].append(skill)
        
        # Remove empty categories
        found_skills = {k: v for k, v in found_skills.items() if v}
        
        total_skills = sum(len(v) for v in found_skills.values())
        logger.info(f"✅ Found {total_skills} skills in resume")
        
        return found_skills
    
    def get_job_requirements(self, job_title: str, location: str = "India") -> Dict:
        """Get typical requirements for a job title"""
        logger.info(f"📋 Getting requirements for {job_title}...")
        
        query = f"""
        SELECT 
            title,
            requirements,
            salary_min,
            salary_max,
            employment_type,
            experience_level
        FROM `{self.project_id}.runagen_bronze.raw_jobs`
        WHERE LOWER(title) LIKE LOWER('%{job_title}%')
            AND LOWER(location) LIKE LOWER('%{location}%')
        LIMIT 10
        """
        
        try:
            results = self.bq_client.query(query).to_dataframe()
            
            if results.empty:
                return {'status': 'no_jobs_found'}
            
            # Extract common requirements
            all_requirements = []
            for _, row in results.iterrows():
                if row['requirements']:
                    reqs = [r.strip().lower() for r in str(row['requirements']).split(',')]
                    all_requirements.extend(reqs)
            
            # Count frequency
            req_counter = Counter(all_requirements)
            top_requirements = req_counter.most_common(15)
            
            avg_salary_min = results['salary_min'].mean()
            avg_salary_max = results['salary_max'].mean()
            
            return {
                'job_title': job_title,
                'jobs_found': len(results),
                'top_requirements': [{'skill': skill, 'frequency': count} for skill, count in top_requirements],
                'avg_salary_min': round(avg_salary_min, 2),
                'avg_salary_max': round(avg_salary_max, 2),
                'avg_salary_range': f"₹{avg_salary_min:.0f}L - ₹{avg_salary_max:.0f}L",
                'common_experience_levels': results['experience_level'].value_counts().to_dict(),
                'common_employment_types': results['employment_type'].value_counts().to_dict()
            }
        
        except Exception as e:
            logger.error(f"❌ Error getting job requirements: {e}")
            return {'error': str(e)}
    
    def calculate_resume_match_score(self, resume_skills: Dict[str, List[str]], 
                                    job_requirements: List[str]) -> Dict:
        """Calculate how well resume matches job requirements"""
        logger.info("📊 Calculating resume match score...")
        
        # Flatten resume skills
        resume_skills_flat = []
        for category_skills in resume_skills.values():
            resume_skills_flat.extend(category_skills)
        
        resume_skills_flat = [s.lower() for s in resume_skills_flat]
        job_requirements = [r.lower() for r in job_requirements]
        
        # Calculate matches
        matched_skills = [skill for skill in job_requirements if skill in resume_skills_flat]
        missing_skills = [skill for skill in job_requirements if skill not in resume_skills_flat]
        
        match_percentage = (len(matched_skills) / len(job_requirements) * 100) if job_requirements else 0
        
        return {
            'match_percentage': round(match_percentage, 2),
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'matched_count': len(matched_skills),
            'missing_count': len(missing_skills),
            'total_required': len(job_requirements),
            'match_level': 'Excellent' if match_percentage >= 80 else 'Good' if match_percentage >= 60 else 'Fair' if match_percentage >= 40 else 'Poor'
        }
    
    def generate_optimization_suggestions(self, resume_skills: Dict[str, List[str]], 
                                         job_title: str) -> Dict:
        """Generate suggestions to optimize resume"""
        logger.info("💡 Generating optimization suggestions...")
        
        job_reqs = self.get_job_requirements(job_title)
        
        if 'error' in job_reqs or 'status' in job_reqs:
            return {'error': 'Could not fetch job requirements'}
        
        # Extract required skills from job requirements
        required_skills = [req['skill'] for req in job_reqs['top_requirements']]
        
        # Calculate match
        match_score = self.calculate_resume_match_score(resume_skills, required_skills)
        
        suggestions = {
            'job_title': job_title,
            'current_match': match_score['match_percentage'],
            'match_level': match_score['match_level'],
            'matched_skills': match_score['matched_skills'],
            'missing_skills': match_score['missing_skills'][:5],  # Top 5 missing
            'suggestions': []
        }
        
        # Generate specific suggestions
        if match_score['missing_count'] > 0:
            suggestions['suggestions'].append({
                'priority': 'HIGH',
                'action': 'Add Missing Skills',
                'details': f"Add these {match_score['missing_count']} missing skills to your resume: {', '.join(match_score['missing_skills'][:3])}",
                'impact': 'Could increase match score by 20-30%'
            })
        
        # Suggest skill development
        if match_score['missing_count'] > 0:
            suggestions['suggestions'].append({
                'priority': 'HIGH',
                'action': 'Develop Missing Skills',
                'details': f"Consider learning: {', '.join(match_score['missing_skills'][:3])}",
                'impact': 'Significantly improve job prospects'
            })
        
        # Suggest highlighting existing skills
        if match_score['matched_count'] > 0:
            suggestions['suggestions'].append({
                'priority': 'MEDIUM',
                'action': 'Highlight Matching Skills',
                'details': f"Emphasize these {match_score['matched_count']} matching skills in your resume",
                'impact': 'Improve ATS (Applicant Tracking System) score'
            })
        
        # Suggest salary expectations
        if 'avg_salary_range' in job_reqs:
            suggestions['suggestions'].append({
                'priority': 'MEDIUM',
                'action': 'Set Salary Expectations',
                'details': f"Average salary for {job_title}: {job_reqs['avg_salary_range']}",
                'impact': 'Help with salary negotiation'
            })
        
        # Suggest experience level
        if 'common_experience_levels' in job_reqs:
            exp_levels = job_reqs['common_experience_levels']
            most_common = max(exp_levels, key=exp_levels.get) if exp_levels else 'Not specified'
            suggestions['suggestions'].append({
                'priority': 'LOW',
                'action': 'Match Experience Level',
                'details': f"Most common experience level: {most_common}",
                'impact': 'Better alignment with job market'
            })
        
        return suggestions
    
    def optimize_resume_for_role(self, resume_text: str, target_role: str) -> Dict:
        """Complete ATS-focused resume optimization for a target role"""
        logger.info(f"🎯 ATS Optimizing resume for {target_role}...")
        
        # Extract skills from resume
        resume_skills = self.extract_skills_from_resume(resume_text)
        
        # Get job requirements
        job_reqs = self.get_job_requirements(target_role)
        
        if 'error' in job_reqs or 'status' in job_reqs:
            return {'error': 'Could not fetch job requirements'}
        
        # Calculate match
        required_skills = [req['skill'] for req in job_reqs['top_requirements']]
        match_score = self.calculate_resume_match_score(resume_skills, required_skills)
        
        # ATS-specific analysis
        ats_analysis = self._analyze_ats_compatibility(resume_text, required_skills)
        
        # Generate ATS optimization suggestions
        suggestions = []
        
        # 1. CRITICAL: Missing Keywords
        if match_score['missing_skills']:
            missing_top = match_score['missing_skills'][:5]
            suggestions.append({
                'priority': 'CRITICAL',
                'category': 'ATS Keywords',
                'action': 'Add Missing Keywords',
                'details': f"ATS systems scan for these keywords: {', '.join(missing_top)}. Add them to your Skills section and work experience descriptions.",
                'impact': 'Increases ATS pass rate by 40-60%',
                'how_to_fix': [
                    f"Add '{missing_top[0]}' to your Skills section",
                    f"Mention '{missing_top[1] if len(missing_top) > 1 else missing_top[0]}' in your work experience",
                    "Use exact keyword matches (e.g., 'Python' not 'Python programming')"
                ]
            })
        
        # 2. HIGH: Keyword Density
        if ats_analysis['keyword_density'] < 2:
            suggestions.append({
                'priority': 'HIGH',
                'category': 'ATS Keyword Density',
                'action': 'Increase Keyword Frequency',
                'details': f"Your resume mentions key skills only {ats_analysis['keyword_density']:.1f} times on average. ATS systems prefer 2-3 mentions per keyword.",
                'impact': 'Improves ATS ranking by 25-35%',
                'how_to_fix': [
                    "Mention each key skill in: Skills section, Work Experience, and Summary",
                    "Use keywords naturally in context (e.g., 'Led Python development team')",
                    "Include variations (e.g., 'SQL', 'SQL queries', 'SQL databases')"
                ]
            })
        
        # 3. HIGH: Standard Section Headers
        if not ats_analysis['has_standard_sections']:
            suggestions.append({
                'priority': 'HIGH',
                'category': 'ATS Section Headers',
                'action': 'Use Standard Section Headers',
                'details': "ATS systems look for standard headers like 'EXPERIENCE', 'SKILLS', 'EDUCATION'. Avoid creative headers.",
                'impact': 'Ensures ATS can parse your resume correctly',
                'how_to_fix': [
                    "Use: WORK EXPERIENCE (not 'My Journey' or 'Career Path')",
                    "Use: SKILLS (not 'Technical Expertise' or 'What I Know')",
                    "Use: EDUCATION (not 'Academic Background')",
                    "Use: CERTIFICATIONS (not 'Credentials')"
                ]
            })
        
        # 4. MEDIUM: File Format
        suggestions.append({
            'priority': 'MEDIUM',
            'category': 'ATS File Format',
            'action': 'Optimize File Format',
            'details': "Save resume as .docx or .pdf (text-based, not scanned image). Avoid tables, text boxes, headers/footers.",
            'impact': 'Ensures ATS can read your resume',
            'how_to_fix': [
                "Use simple formatting: no tables, columns, or text boxes",
                "Avoid headers/footers (ATS often ignores them)",
                "Use standard fonts: Arial, Calibri, Times New Roman",
                "Save as .docx or text-based PDF (not scanned image)"
            ]
        })
        
        # 5. MEDIUM: Job Title Matching
        if not ats_analysis['has_matching_job_title']:
            suggestions.append({
                'priority': 'MEDIUM',
                'category': 'ATS Job Title Match',
                'action': 'Match Target Job Title',
                'details': f"Include '{target_role}' in your resume. ATS systems prioritize exact job title matches.",
                'impact': 'Increases relevance score by 20-30%',
                'how_to_fix': [
                    f"Add '{target_role}' to your professional summary",
                    f"Use '{target_role}' as your LinkedIn headline",
                    "Mirror the exact job title from the posting"
                ]
            })
        
        # 6. MEDIUM: Quantifiable Achievements
        if ats_analysis['has_numbers'] < 3:
            suggestions.append({
                'priority': 'MEDIUM',
                'category': 'ATS Quantifiable Results',
                'action': 'Add Quantifiable Achievements',
                'details': f"Only {ats_analysis['has_numbers']} numbers found. ATS systems favor measurable results.",
                'impact': 'Improves ranking and human review',
                'how_to_fix': [
                    "Add metrics: 'Improved performance by 40%'",
                    "Include team size: 'Led team of 5 developers'",
                    "Show scale: 'Processed 10M+ records daily'",
                    "Use percentages, dollar amounts, time saved"
                ]
            })
        
        # 7. LOW: Action Verbs
        if not ats_analysis['has_action_verbs']:
            suggestions.append({
                'priority': 'LOW',
                'category': 'ATS Action Verbs',
                'action': 'Use Strong Action Verbs',
                'details': "Start bullet points with action verbs: Developed, Implemented, Led, Optimized, Designed.",
                'impact': 'Improves ATS parsing and readability',
                'how_to_fix': [
                    "Replace 'Responsible for' with 'Led' or 'Managed'",
                    "Use: Developed, Implemented, Designed, Optimized, Achieved",
                    "Avoid: 'Helped with', 'Worked on', 'Assisted'"
                ]
            })
        
        # 8. LOW: Acronyms
        suggestions.append({
            'priority': 'LOW',
            'category': 'ATS Acronym Handling',
            'action': 'Spell Out Acronyms',
            'details': "Write both full term and acronym: 'Application Programming Interface (API)'. ATS searches for both.",
            'impact': 'Captures more keyword variations',
            'how_to_fix': [
                "First mention: 'Machine Learning (ML)'",
                "Later mentions: 'ML' is fine",
                "Include both in Skills: 'API, REST API, RESTful APIs'"
            ]
        })
        
        # Calculate ATS score
        ats_score = self._calculate_ats_score(ats_analysis, match_score)
        
        optimization_report = {
            'target_role': target_role,
            'ats_score': {
                'overall_score': ats_score,
                'rating': 'Excellent' if ats_score >= 80 else 'Good' if ats_score >= 60 else 'Fair' if ats_score >= 40 else 'Poor',
                'keyword_match': match_score['match_percentage'],
                'formatting_score': ats_analysis['formatting_score'],
                'pass_probability': f"{min(95, ats_score)}%"
            },
            'current_status': {
                'skills_found': sum(len(v) for v in resume_skills.values()),
                'keywords_matched': match_score['matched_count'],
                'keywords_missing': match_score['missing_count'],
                'ats_compatible': ats_score >= 60
            },
            'optimization_suggestions': suggestions,
            'quick_wins': [
                s for s in suggestions if s['priority'] in ['CRITICAL', 'HIGH']
            ][:3],
            'ats_checklist': {
                'keyword_optimization': match_score['match_percentage'] >= 70,
                'standard_sections': ats_analysis['has_standard_sections'],
                'simple_formatting': True,  # Assume true for uploaded resume
                'quantifiable_results': ats_analysis['has_numbers'] >= 3,
                'action_verbs': ats_analysis['has_action_verbs'],
                'job_title_match': ats_analysis['has_matching_job_title']
            }
        }
        
        logger.info(f"✅ ATS Score: {ats_score}/100")
        return optimization_report
    
    def _analyze_ats_compatibility(self, resume_text: str, required_skills: List[str]) -> Dict:
        """Analyze resume for ATS compatibility"""
        analysis = {}
        
        # Check for standard section headers
        standard_headers = ['experience', 'skills', 'education', 'work experience', 'professional experience']
        analysis['has_standard_sections'] = any(header in resume_text.lower() for header in standard_headers)
        
        # Check keyword density
        keyword_counts = []
        for skill in required_skills[:10]:
            count = resume_text.lower().count(skill.lower())
            keyword_counts.append(count)
        analysis['keyword_density'] = sum(keyword_counts) / len(keyword_counts) if keyword_counts else 0
        
        # Check for numbers (quantifiable achievements)
        numbers = re.findall(r'\d+[%]?|\$\d+', resume_text)
        analysis['has_numbers'] = len(numbers)
        
        # Check for action verbs
        action_verbs = ['developed', 'implemented', 'led', 'managed', 'designed', 'created', 'built', 'optimized', 'improved', 'achieved']
        analysis['has_action_verbs'] = any(verb in resume_text.lower() for verb in action_verbs)
        
        # Check for job title match
        analysis['has_matching_job_title'] = False  # Will be checked in main function
        
        # Calculate formatting score
        formatting_score = 0
        if analysis['has_standard_sections']:
            formatting_score += 30
        if analysis['has_action_verbs']:
            formatting_score += 20
        if analysis['has_numbers'] >= 3:
            formatting_score += 30
        if analysis['keyword_density'] >= 2:
            formatting_score += 20
        
        analysis['formatting_score'] = formatting_score
        
        return analysis
    
    def _calculate_ats_score(self, ats_analysis: Dict, match_score: Dict) -> int:
        """Calculate overall ATS compatibility score"""
        score = 0
        
        # Keyword match (40% weight)
        score += match_score['match_percentage'] * 0.4
        
        # Formatting (30% weight)
        score += ats_analysis['formatting_score'] * 0.3
        
        # Keyword density (15% weight)
        density_score = min(100, ats_analysis['keyword_density'] * 50)
        score += density_score * 0.15
        
        # Numbers/metrics (15% weight)
        numbers_score = min(100, ats_analysis['has_numbers'] * 20)
        score += numbers_score * 0.15
        
        return int(score)
    
    def _create_action_plan(self, missing_skills: List[str], target_role: str) -> List[Dict]:
        """Create a detailed action plan to improve resume"""
        action_plan = []
        
        for i, skill in enumerate(missing_skills[:5], 1):
            action_plan.append({
                'step': i,
                'skill': skill,
                'timeline': f"Week {i*2}-{i*2+2}",
                'resources': [
                    f"Online course on {skill}",
                    f"Practice projects using {skill}",
                    f"Build portfolio with {skill}"
                ],
                'success_criteria': f"Complete 1-2 projects using {skill}"
            })
        
        return action_plan
    
    def compare_resumes(self, resume1_text: str, resume2_text: str, job_title: str) -> Dict:
        """Compare two resumes for a job"""
        logger.info("🔄 Comparing two resumes...")
        
        # Extract skills from both resumes
        skills1 = self.extract_skills_from_resume(resume1_text)
        skills2 = self.extract_skills_from_resume(resume2_text)
        
        # Get job requirements
        job_reqs = self.get_job_requirements(job_title)
        
        if 'error' in job_reqs or 'status' in job_reqs:
            return {'error': 'Could not fetch job requirements'}
        
        required_skills = [req['skill'] for req in job_reqs['top_requirements']]
        
        # Calculate match scores
        match1 = self.calculate_resume_match_score(skills1, required_skills)
        match2 = self.calculate_resume_match_score(skills2, required_skills)
        
        comparison = {
            'job_title': job_title,
            'resume1': {
                'skills_count': sum(len(v) for v in skills1.values()),
                'match_percentage': match1['match_percentage'],
                'match_level': match1['match_level'],
                'matched_skills': match1['matched_skills'],
                'missing_skills': match1['missing_skills']
            },
            'resume2': {
                'skills_count': sum(len(v) for v in skills2.values()),
                'match_percentage': match2['match_percentage'],
                'match_level': match2['match_level'],
                'matched_skills': match2['matched_skills'],
                'missing_skills': match2['missing_skills']
            },
            'winner': 'Resume 1' if match1['match_percentage'] > match2['match_percentage'] else 'Resume 2' if match2['match_percentage'] > match1['match_percentage'] else 'Tie',
            'difference': abs(match1['match_percentage'] - match2['match_percentage'])
        }
        
        return comparison


def main():
    """Main execution"""
    print("\n" + "="*70)
    print("🚀 Phase 6: Resume Optimization Engine")
    print("="*70 + "\n")
    
    optimizer = ResumeOptimizer()
    
    # Sample resume text
    sample_resume = """
    John Doe
    Data Analyst | Python | SQL | Tableau
    
    Skills:
    - Python, SQL, R
    - Tableau, Power BI
    - Excel, Google Sheets
    - Data Analysis, Statistical Analysis
    - Machine Learning basics
    
    Experience:
    - 3 years as Data Analyst
    - Worked with BigQuery, PostgreSQL
    - Created dashboards and reports
    """
    
    # Optimize for Data Analyst role
    print("📋 Optimizing resume for Data Analyst role...")
    print("-"*70)
    
    optimization = optimizer.optimize_resume_for_role(sample_resume, "Data Analyst")
    
    print(f"\n✅ Current Match: {optimization['current_status']['match_percentage']}%")
    print(f"📈 Potential Match: {optimization['improvement_potential']['potential_match_percentage']}%")
    print(f"⏱️  Time to Improve: {optimization['improvement_potential']['estimated_time_to_improve']}")
    
    print("\n💡 Top Suggestions:")
    for i, suggestion in enumerate(optimization['optimization_suggestions'][:3], 1):
        print(f"{i}. [{suggestion['priority']}] {suggestion['action']}")
        print(f"   {suggestion['details']}")
    
    print("\n📋 Action Plan:")
    for step in optimization['action_plan'][:3]:
        print(f"Step {step['step']}: Learn {step['skill']} ({step['timeline']})")
    
    print("\n" + "="*70)
    print("✅ Phase 6 Complete!")
    print("="*70 + "\n")
    
    return optimization


if __name__ == "__main__":
    main()
