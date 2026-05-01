"""
Phase 4: Learning Path Recommendations
Generates personalized learning paths based on career goals and skill gaps
Enhanced with Ollama AI for intelligent learning resource recommendations
"""
import logging
import os
import requests
import re
import base64
from typing import List, Dict, Optional
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SkillLevel(Enum):
    """Skill proficiency levels"""
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4


def normalize_skill(s):
    """Normalize skill name for comparison"""
    return str(s).lower().strip().replace(' ', '').replace('.', '').replace('-', '')


class LearningResource:
    """Learning resource definition"""
    
    def __init__(self, name: str, platform: str, duration_hours: int, 
                 difficulty: SkillLevel, cost: float = 0, url: str = ""):
        self.name = name
        self.platform = platform
        self.duration_hours = duration_hours
        self.difficulty = difficulty
        self.cost = cost
        self.url = url
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'platform': self.platform,
            'duration_hours': self.duration_hours,
            'difficulty': self.difficulty.name,
            'cost': self.cost,
            'url': self.url
        }


class LearningPathGenerator:
    """Generate personalized learning paths with Ollama AI"""
    
    # Learning resources database
    RESOURCES = {
        'Python': [
            LearningResource('Python for Everybody', 'Coursera', 40, SkillLevel.BEGINNER, 0),
            LearningResource('Complete Python Bootcamp', 'Udemy', 22, SkillLevel.BEGINNER, 499),
            LearningResource('Advanced Python', 'DataCamp', 30, SkillLevel.ADVANCED, 2500),
        ],
        'Machine Learning': [
            LearningResource('ML Specialization', 'Coursera', 60, SkillLevel.BEGINNER, 0),
            LearningResource('Fast.ai Deep Learning', 'Fast.ai', 50, SkillLevel.INTERMEDIATE, 0),
            LearningResource('Advanced ML', 'Coursera', 80, SkillLevel.ADVANCED, 0),
        ],
        'SQL': [
            LearningResource('SQL for Data Analysis', 'Udacity', 40, SkillLevel.BEGINNER, 0),
            LearningResource('Advanced SQL', 'DataCamp', 25, SkillLevel.INTERMEDIATE, 2500),
            LearningResource('SQL Performance Tuning', 'Pluralsight', 20, SkillLevel.ADVANCED, 2500),
        ],
        'AWS': [
            LearningResource('AWS Fundamentals', 'A Cloud Guru', 30, SkillLevel.BEGINNER, 2500),
            LearningResource('AWS Solutions Architect', 'A Cloud Guru', 50, SkillLevel.INTERMEDIATE, 2500),
            LearningResource('AWS Advanced', 'Linux Academy', 60, SkillLevel.ADVANCED, 2500),
        ],
        'Docker': [
            LearningResource('Docker Essentials', 'Linux Academy', 20, SkillLevel.BEGINNER, 2500),
            LearningResource('Docker Deep Dive', 'Pluralsight', 40, SkillLevel.INTERMEDIATE, 2500),
            LearningResource('Kubernetes & Docker', 'Linux Academy', 50, SkillLevel.ADVANCED, 2500),
        ],
        'React': [
            LearningResource('React Basics', 'Scrimba', 30, SkillLevel.BEGINNER, 0),
            LearningResource('React Complete Guide', 'Udemy', 40, SkillLevel.INTERMEDIATE, 499),
            LearningResource('Advanced React Patterns', 'Frontend Masters', 25, SkillLevel.ADVANCED, 3500),
        ],
        'Statistics': [
            LearningResource('Statistics Fundamentals', 'Khan Academy', 50, SkillLevel.BEGINNER, 0),
            LearningResource('Statistical Analysis', 'Coursera', 40, SkillLevel.INTERMEDIATE, 0),
            LearningResource('Advanced Statistics', 'MIT OpenCourseWare', 60, SkillLevel.ADVANCED, 0),
        ],
        'TensorFlow': [
            LearningResource('TensorFlow Basics', 'Coursera', 30, SkillLevel.BEGINNER, 0),
            LearningResource('TensorFlow Advanced', 'Coursera', 40, SkillLevel.INTERMEDIATE, 0),
            LearningResource('TensorFlow Production', 'Coursera', 50, SkillLevel.ADVANCED, 0),
        ],
    }
    
    # Career skill requirements
    CAREER_SKILLS = {
        'Data Scientist': {
            'core': ['Python', 'Machine Learning', 'Statistics', 'SQL'],
            'important': ['TensorFlow', 'AWS', 'Docker'],
            'nice_to_have': ['Spark', 'Scala', 'Tableau']
        },
        'Data Engineer': {
            'core': ['Python', 'SQL', 'Docker', 'AWS'],
            'important': ['Spark', 'Kafka', 'BigQuery'],
            'nice_to_have': ['Scala', 'Airflow', 'dbt']
        },
        'Software Developer': {
            'core': ['Python', 'JavaScript', 'SQL', 'Git'],
            'important': ['Docker', 'AWS', 'React'],
            'nice_to_have': ['Kubernetes', 'TypeScript', 'GraphQL']
        },
        'Software Engineer': {
            'core': ['Python', 'Java', 'Data Structures', 'Algorithms', 'SQL', 'Git'],
            'important': ['System Design', 'Docker', 'Kubernetes', 'AWS', 'Testing (PyTest/JUnit)', 'Microservices'],
            'nice_to_have': ['CI/CD', 'Kafka', 'Redis', 'NoSQL', 'TypeScript', 'GraphQL']
        },
        'Backend Developer': {
            'core': ['Python', 'SQL', 'Docker', 'AWS'],
            'important': ['REST APIs', 'Microservices', 'Git'],
            'nice_to_have': ['Kubernetes', 'GraphQL', 'gRPC']
        },
        'Frontend Developer': {
            'core': ['JavaScript', 'React', 'CSS', 'HTML'],
            'important': ['TypeScript', 'Testing', 'Git'],
            'nice_to_have': ['Vue', 'Angular', 'WebAssembly']
        },
        'DevOps Engineer': {
            'core': ['Docker', 'AWS', 'Linux', 'CI/CD'],
            'important': ['Kubernetes', 'Terraform', 'Monitoring'],
            'nice_to_have': ['Ansible', 'Jenkins', 'GitLab']
        },
    }
    
    def __init__(self):
        """Initialize generator with Ollama support"""
        # Ollama configuration
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')
        self.use_ollama = self._check_ollama_available()
        
        logger.info("✓ Learning Path Generator initialized")
    
    def _check_ollama_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            if response.status_code == 200:
                logger.info(f"✓ Ollama available for learning path generation")
                return True
        except Exception as e:
            logger.warning(f"⚠️ Ollama not available: {e}")
        return False
    
    def _call_ollama(self, prompt: str, max_tokens: int = 500) -> str:
        """Call Ollama API for text generation"""
        if not self.use_ollama:
            return ""
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": 0.7
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
        except Exception as e:
            logger.error(f"❌ Ollama API error: {e}")
        
        return ""
    
    def generate_learning_path(self, career: str, current_skills: List[str], 
                              target_level: SkillLevel = SkillLevel.ADVANCED,
                              weeks_available: int = 12) -> Dict:
        """Generate personalized learning path"""
        
        logger.info(f"\n📚 Generating learning path for {career}")
        logger.info(f"   Current skills: {current_skills}")
        logger.info(f"   Target level: {target_level.name}")
        logger.info(f"   Weeks available: {weeks_available}")
        
        # Get required skills - Priority 1: Ollama AI
        required_skills = {}
        if self.use_ollama:
            logger.info(f"🔍 Fetching requirements for '{career}' from Ollama...")
            ai_required = self._get_ai_required_skills(career)
            if ai_required:
                required_skills = ai_required
                logger.info(f"✅ Received dynamic requirements from Ollama for {career}")
        
        # Priority 2: Local registry fallback
        if not required_skills:
            logger.info(f"📚 Using local registry for '{career}' skills")
            required_skills = self.CAREER_SKILLS.get(career, {})
            
            # If career not found, try case-insensitive match
            if not required_skills:
                for key in self.CAREER_SKILLS.keys():
                    if key.lower() == career.lower():
                        required_skills = self.CAREER_SKILLS[key]
                        career = key
                        break
        
        # Priority 3: Generic fallback
        if not required_skills:
            logger.warning(f"Career '{career}' not found anywhere, using generic software development path")
            required_skills = {
                'core': ['Python', 'JavaScript', 'SQL', 'Git'],
                'important': ['Docker', 'AWS', 'System Design'],
                'nice_to_have': ['Kubernetes', 'CI/CD', 'Microservices']
            }
        
        # Identify skill gaps
        core_skills = set(required_skills.get('core', []))
        important_skills = set(required_skills.get('important', []))
        nice_to_have = set(required_skills.get('nice_to_have', []))
        
        current_skills_normalized = set(normalize_skill(s) for s in current_skills)
        
        missing_core = [s for s in core_skills if normalize_skill(s) not in current_skills_normalized]
        missing_important = [s for s in important_skills if normalize_skill(s) not in current_skills_normalized]
        missing_nice = [s for s in nice_to_have if normalize_skill(s) not in current_skills_normalized]
        
        # Build learning path
        learning_path = {
            'career': career,
            'target_level': target_level.name,
            'weeks_available': weeks_available,
            'total_hours_available': weeks_available * 20,  # Assume 20 hours/week
            'phases': [],
            'total_hours_required': 0,
            'estimated_weeks': 0
        }
        
        # Generate AI-powered learning resources for ALL missing skills FIRST
        all_missing_skills = missing_core + missing_important + missing_nice
        ai_resources = {}
        if all_missing_skills and self.use_ollama:
            logger.info(f"🤖 Generating AI-powered learning resources for {len(all_missing_skills)} skills...")
            ai_resources = self._generate_ai_learning_resources(
                career, 
                all_missing_skills, 
                target_level,
                current_skills=current_skills
            )
            if ai_resources:
                learning_path['ai_learning_resources'] = ai_resources
                logger.info(f"✓ Generated AI resources for {len(ai_resources)} skills")

        # Phase 1: Core skills (highest priority)
        if missing_core:
            phase1 = self._create_phase(
                'Phase 1: Core Skills (Foundation)',
                missing_core,
                SkillLevel.INTERMEDIATE,
                priority=1,
                ai_resources=ai_resources
            )
            learning_path['phases'].append(phase1)
            learning_path['total_hours_required'] += phase1['total_hours']
        
        # Phase 2: Important skills
        if missing_important:
            phase2 = self._create_phase(
                'Phase 2: Important Skills (Intermediate)',
                missing_important,
                SkillLevel.INTERMEDIATE,
                priority=2,
                ai_resources=ai_resources
            )
            learning_path['phases'].append(phase2)
            learning_path['total_hours_required'] += phase2['total_hours']
        
        # Phase 3: Nice-to-have skills
        if missing_nice:
            phase3 = self._create_phase(
                'Phase 3: Advanced Skills (Optional)',
                missing_nice,
                SkillLevel.ADVANCED,
                priority=3,
                ai_resources=ai_resources
            )
            learning_path['phases'].append(phase3)
            learning_path['total_hours_required'] += phase3['total_hours']
        
        # Calculate timeline
        hours_per_week = learning_path['total_hours_available'] / weeks_available
        learning_path['estimated_weeks'] = learning_path['total_hours_required'] / hours_per_week
        
        # Add recommendations
        learning_path['recommendations'] = self._generate_recommendations(
            learning_path['estimated_weeks'],
            weeks_available,
            learning_path['total_hours_required']
        )
        
        # AI resources are now integrated into phases
        
        logger.info(f"✓ Learning path generated")
        logger.info(f"   Total hours required: {learning_path['total_hours_required']}")
        logger.info(f"   Estimated weeks: {learning_path['estimated_weeks']:.1f}")
        
        return learning_path
    
    def _create_phase(self, phase_name: str, skills: List[str], 
                     target_level: SkillLevel, priority: int, ai_resources: Dict = None) -> Dict:
        """Create a learning phase with AI resources as primary"""
        
        phase = {
            'name': phase_name,
            'priority': priority,
            'skills': [],
            'total_hours': 0,
            'total_cost': 0
        }
        
        for skill in skills:
            skill_entry = None
            
            # Check AI resources first (normalized lookup)
            normalized_skill = normalize_skill(skill)
            if ai_resources and normalized_skill in ai_resources:
                res = ai_resources[normalized_skill]
                # Try to parse cost from string (e.g., "₹500")
                cost = 0
                cost_match = re.search(r'[₹$](\d+)', res.get('resources', ''))
                if cost_match:
                    cost = int(cost_match.group(1))
                
                skill_entry = {
                    'skill': skill,
                    'resources': [{
                        'name': res.get('resources', 'Recommended Resource'),
                        'platform': 'AI Recommended',
                        'duration_hours': 20, # Default estimate
                        'difficulty': target_level.name,
                        'cost': cost,
                        'link': '#'
                    }],
                    'hours': 20,
                    'cost': cost,
                    'strategy': res.get('strategy', '')
                }
            
            # Fallback to hardcoded resources
            if not skill_entry:
                resources = self.RESOURCES.get(skill, [])
                selected_resource = None
                for resource in resources:
                    if resource.difficulty == target_level:
                        selected_resource = resource
                        break
                
                if not selected_resource and resources:
                    selected_resource = resources[0]
                
                if selected_resource:
                    skill_entry = {
                        'skill': skill,
                        'resources': [selected_resource.to_dict()],
                        'hours': selected_resource.duration_hours,
                        'cost': selected_resource.cost
                    }
            
            if skill_entry:
                phase['skills'].append(skill_entry)
                phase['total_hours'] += skill_entry['hours']
                phase['total_cost'] += skill_entry['cost']
        
        return phase
    
    def _generate_recommendations(self, estimated_weeks: float, 
                                 weeks_available: int, total_hours: int) -> List[str]:
        """Generate recommendations based on timeline"""
        
        recommendations = []
        
        if estimated_weeks <= weeks_available:
            recommendations.append(f"✓ You can complete this path in {estimated_weeks:.1f} weeks")
            recommendations.append("Consider adding advanced topics to accelerate your career growth")
        else:
            recommendations.append(f"⚠️  This path requires {estimated_weeks:.1f} weeks (you have {weeks_available})")
            recommendations.append("Consider focusing on core skills first, then advanced topics later")
        
        if total_hours > 200:
            recommendations.append("This is an intensive program. Dedicate 20+ hours per week")
        elif total_hours > 100:
            recommendations.append("This is a moderate program. Dedicate 10-15 hours per week")
        else:
            recommendations.append("This is a light program. Dedicate 5-10 hours per week")
        
        recommendations.append("Join online communities and practice with real projects")
        recommendations.append("Consider getting certifications to validate your skills")
        
        return recommendations
    
    def _get_ai_required_skills(self, career: str) -> Optional[Dict]:
        """Get required skills for a career using Ollama"""
        prompt = f"""You are an expert technical recruiter. 
What are the standard technical skill requirements for a {career}?
 
Provide the answer in JSON format ONLY:
{{
  "core": ["skill1", "skill2", "skill3", "skill4"],
  "important": ["skill5", "skill6", "skill7"],
  "nice_to_have": ["skill8", "skill9"]
}}
 
Limit to most important industry-standard technical skills. No explanation, just JSON."""

        try:
            response = self._call_ollama(prompt, max_tokens=300)
            if response:
                import json
                import re
                # Find JSON in response
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))
        except Exception as e:
            logger.error(f"❌ Error getting AI required skills: {e}")
        return None
    
    def _generate_ai_learning_resources(self, career: str, missing_skills: List[str], 
                                       target_level: SkillLevel, current_skills: List[str] = None) -> Dict:
        """Generate AI-powered learning resources for skill gaps using Ollama"""
        if not self.use_ollama or not missing_skills:
            return {}
        
        logger.info(f"🤖 Generating AI-powered learning resources for {len(missing_skills)} skills...")
        
        # Create prompt for Ollama
        current_skills_str = ", ".join(current_skills) if current_skills else "None identified"
        
        prompt = f"""You are an expert career coach and learning advisor.
 
Career Goal: {career}
Target Level: {target_level.name}
User's Current Skills: {current_skills_str}
Missing Skills to Learn: {', '.join(missing_skills)}
 
Task: For each missing skill, recommend specific learning resources and a learning strategy that builds upon the user's current knowledge.
 
For each skill, provide:
SKILL: [skill name]
RESOURCES: [2-3 specific real-world courses, books, or platforms. Include estimated cost in Indian Rupees (₹) if applicable]
STRATEGY: [How to learn this skill effectively, considering their background in {current_skills_str}. Be technical and specific.]
TIMELINE: [Estimated weeks to learn]
 
IMPORTANT: Use Indian Rupees (₹) for all currency mentions. Provide ACTUAL high-quality resources like Udemy, Coursera, official documentation, or top YouTube channels. No mock data. Be very specific to {career}."""

        try:
            response = self._call_ollama(prompt, max_tokens=1000)
            
            if not response:
                return {}
            
            # Parse Ollama response into a skill-to-resource mapping
            resource_map = {}
            
            # Split by skill blocks
            skill_blocks = response.split('SKILL:')[1:]  # Skip first empty split
            
            for block in skill_blocks:
                try:
                    skill_name = block.split('\n')[0].strip()
                    
                    resources_match = re.search(r'RESOURCES:\s*(.+?)(?=STRATEGY:|$)', block, re.DOTALL | re.IGNORECASE)
                    strategy_match = re.search(r'STRATEGY:\s*(.+?)(?=TIMELINE:|$)', block, re.DOTALL | re.IGNORECASE)
                    
                    normalized_name = normalize_skill(skill_name)
                    resource_map[normalized_name] = {
                        'skill_original': skill_name,
                        'resources': resources_match.group(1).strip()[:500] if resources_match else 'Check online platforms',
                        'strategy': strategy_match.group(1).strip()[:300] if strategy_match else 'Practice with projects'
                    }
                    
                except Exception as parse_error:
                    logger.warning(f"⚠️ Failed to parse skill resource: {parse_error}")
                    continue
                    
            return resource_map
            
        except Exception as e:
            logger.error(f"❌ Error generating AI learning resources: {e}")
        
        return {}
    
    def get_free_resources(self, skill: str) -> List[Dict]:
        """Get free learning resources for a skill"""
        
        resources = self.RESOURCES.get(skill, [])
        free_resources = [r.to_dict() for r in resources if r.cost == 0]
        
        return free_resources
    
    def get_paid_resources(self, skill: str) -> List[Dict]:
        """Get paid learning resources for a skill"""
        
        resources = self.RESOURCES.get(skill, [])
        paid_resources = [r.to_dict() for r in resources if r.cost > 0]
        
        return paid_resources


def main():
    """Test learning path generation"""
    
    generator = LearningPathGenerator()
    
    # Example: Data Scientist learning path
    path = generator.generate_learning_path(
        career='Data Scientist',
        current_skills=['Python', 'SQL'],
        target_level=SkillLevel.ADVANCED,
        weeks_available=12
    )
    
    print("\n" + "="*70)
    print("📚 Learning Path Generated")
    print("="*70)
    print(f"Career: {path['career']}")
    print(f"Total Hours Required: {path['total_hours_required']}")
    print(f"Estimated Weeks: {path['estimated_weeks']:.1f}")
    print(f"\nPhases:")
    for phase in path['phases']:
        print(f"\n{phase['name']}")
        for skill in phase['skills']:
            print(f"  - {skill['skill']}: {skill['hours']} hours")
    
    print(f"\nRecommendations:")
    for rec in path['recommendations']:
        print(f"  • {rec}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
