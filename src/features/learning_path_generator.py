"""
Phase 4: Learning Path Recommendations
Generates personalized learning paths based on career goals and skill gaps
Enhanced with Ollama AI for intelligent learning resource recommendations
"""
import logging
from typing import List, Dict, Optional
from enum import Enum
import os
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SkillLevel(Enum):
    """Skill proficiency levels"""
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4


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
            LearningResource('Complete Python Bootcamp', 'Udemy', 22, SkillLevel.BEGINNER, 15),
            LearningResource('Advanced Python', 'DataCamp', 30, SkillLevel.ADVANCED, 29),
        ],
        'Machine Learning': [
            LearningResource('ML Specialization', 'Coursera', 60, SkillLevel.BEGINNER, 0),
            LearningResource('Fast.ai Deep Learning', 'Fast.ai', 50, SkillLevel.INTERMEDIATE, 0),
            LearningResource('Advanced ML', 'Coursera', 80, SkillLevel.ADVANCED, 0),
        ],
        'SQL': [
            LearningResource('SQL for Data Analysis', 'Udacity', 40, SkillLevel.BEGINNER, 0),
            LearningResource('Advanced SQL', 'DataCamp', 25, SkillLevel.INTERMEDIATE, 29),
            LearningResource('SQL Performance Tuning', 'Pluralsight', 20, SkillLevel.ADVANCED, 29),
        ],
        'AWS': [
            LearningResource('AWS Fundamentals', 'A Cloud Guru', 30, SkillLevel.BEGINNER, 29),
            LearningResource('AWS Solutions Architect', 'A Cloud Guru', 50, SkillLevel.INTERMEDIATE, 29),
            LearningResource('AWS Advanced', 'Linux Academy', 60, SkillLevel.ADVANCED, 29),
        ],
        'Docker': [
            LearningResource('Docker Essentials', 'Linux Academy', 20, SkillLevel.BEGINNER, 29),
            LearningResource('Docker Deep Dive', 'Pluralsight', 40, SkillLevel.INTERMEDIATE, 29),
            LearningResource('Kubernetes & Docker', 'Linux Academy', 50, SkillLevel.ADVANCED, 29),
        ],
        'React': [
            LearningResource('React Basics', 'Scrimba', 30, SkillLevel.BEGINNER, 0),
            LearningResource('React Complete Guide', 'Udemy', 40, SkillLevel.INTERMEDIATE, 15),
            LearningResource('Advanced React Patterns', 'Frontend Masters', 25, SkillLevel.ADVANCED, 39),
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
            'core': ['Python', 'Java', 'SQL', 'Git'],
            'important': ['Docker', 'AWS', 'Testing'],
            'nice_to_have': ['Kubernetes', 'Microservices', 'CI/CD']
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
                timeout=30
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
        
        # Get required skills
        required_skills = self.CAREER_SKILLS.get(career, {})
        
        # If career not found, try case-insensitive match
        if not required_skills:
            for key in self.CAREER_SKILLS.keys():
                if key.lower() == career.lower():
                    required_skills = self.CAREER_SKILLS[key]
                    career = key  # Use the correct case
                    break
        
        # If still not found, use a generic software development path
        if not required_skills:
            logger.warning(f"Career '{career}' not found, using generic software development path")
            required_skills = {
                'core': ['Python', 'JavaScript', 'SQL', 'Git'],
                'important': ['Docker', 'AWS', 'Testing'],
                'nice_to_have': ['Kubernetes', 'CI/CD', 'Microservices']
            }
        
        # Identify skill gaps
        core_skills = set(required_skills.get('core', []))
        important_skills = set(required_skills.get('important', []))
        nice_to_have = set(required_skills.get('nice_to_have', []))
        
        current_skills_set = set(s.title() for s in current_skills)
        
        missing_core = list(core_skills - current_skills_set)
        missing_important = list(important_skills - current_skills_set)
        missing_nice = list(nice_to_have - current_skills_set)
        
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
        
        # Phase 1: Core skills (highest priority)
        if missing_core:
            phase1 = self._create_phase(
                'Phase 1: Core Skills (Foundation)',
                missing_core,
                SkillLevel.INTERMEDIATE,
                priority=1
            )
            learning_path['phases'].append(phase1)
            learning_path['total_hours_required'] += phase1['total_hours']
        
        # Phase 2: Important skills
        if missing_important:
            phase2 = self._create_phase(
                'Phase 2: Important Skills (Intermediate)',
                missing_important,
                SkillLevel.INTERMEDIATE,
                priority=2
            )
            learning_path['phases'].append(phase2)
            learning_path['total_hours_required'] += phase2['total_hours']
        
        # Phase 3: Nice-to-have skills
        if missing_nice:
            phase3 = self._create_phase(
                'Phase 3: Advanced Skills (Optional)',
                missing_nice,
                SkillLevel.ADVANCED,
                priority=3
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
        
        # Generate AI-powered learning resources for skill gaps using Ollama
        all_missing_skills = missing_core + missing_important + missing_nice
        if all_missing_skills:
            ai_resources = self._generate_ai_learning_resources(
                career, 
                all_missing_skills[:5],  # Top 5 missing skills
                target_level
            )
            if ai_resources:
                learning_path['ai_learning_resources'] = ai_resources
        
        logger.info(f"✓ Learning path generated")
        logger.info(f"   Total hours required: {learning_path['total_hours_required']}")
        logger.info(f"   Estimated weeks: {learning_path['estimated_weeks']:.1f}")
        
        return learning_path
    
    def _create_phase(self, phase_name: str, skills: List[str], 
                     target_level: SkillLevel, priority: int) -> Dict:
        """Create a learning phase"""
        
        phase = {
            'name': phase_name,
            'priority': priority,
            'skills': [],
            'total_hours': 0,
            'total_cost': 0
        }
        
        for skill in skills:
            resources = self.RESOURCES.get(skill, [])
            
            # Select appropriate resource based on target level
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
                phase['skills'].append(skill_entry)
                phase['total_hours'] += selected_resource.duration_hours
                phase['total_cost'] += selected_resource.cost
        
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
    
    def _generate_ai_learning_resources(self, career: str, missing_skills: List[str], 
                                       target_level: SkillLevel) -> Dict:
        """Generate AI-powered learning resources for skill gaps using Ollama"""
        if not self.use_ollama or not missing_skills:
            return {}
        
        logger.info(f"🤖 Generating AI-powered learning resources for {len(missing_skills)} skills...")
        
        # Create prompt for Ollama
        prompt = f"""You are an expert career coach and learning advisor.

Career Goal: {career}
Target Level: {target_level.name}
Missing Skills: {', '.join(missing_skills)}

Task: For each missing skill, recommend specific learning resources and a learning strategy.

For each skill, provide:
SKILL: [skill name]
RESOURCES: [2-3 specific courses, books, or platforms]
STRATEGY: [How to learn this skill effectively in 2-3 sentences]
TIMELINE: [Estimated weeks to learn]

Keep recommendations practical and specific. Focus on popular, high-quality resources."""

        try:
            response = self._call_ollama(prompt, max_tokens=1000)
            
            if not response:
                return {}
            
            # Parse Ollama response
            ai_resources = {
                'generated_by': 'Ollama AI',
                'skills': []
            }
            
            # Split by skill blocks
            skill_blocks = response.split('SKILL:')[1:]  # Skip first empty split
            
            for block in skill_blocks[:5]:  # Max 5 skills
                try:
                    import re
                    skill_name = block.split('\n')[0].strip()
                    
                    resources_match = re.search(r'RESOURCES:\s*(.+?)(?=STRATEGY:|$)', block, re.DOTALL | re.IGNORECASE)
                    strategy_match = re.search(r'STRATEGY:\s*(.+?)(?=TIMELINE:|$)', block, re.DOTALL | re.IGNORECASE)
                    timeline_match = re.search(r'TIMELINE:\s*(.+?)(?=SKILL:|$)', block, re.DOTALL | re.IGNORECASE)
                    
                    skill_resource = {
                        'skill': skill_name,
                        'resources': resources_match.group(1).strip()[:500] if resources_match else 'Check online platforms',
                        'strategy': strategy_match.group(1).strip()[:300] if strategy_match else 'Practice with projects',
                        'timeline': timeline_match.group(1).strip()[:100] if timeline_match else '4-6 weeks'
                    }
                    
                    ai_resources['skills'].append(skill_resource)
                    
                except Exception as parse_error:
                    logger.warning(f"⚠️ Failed to parse skill resource: {parse_error}")
                    continue
            
            if ai_resources['skills']:
                logger.info(f"✓ Generated AI resources for {len(ai_resources['skills'])} skills")
                return ai_resources
            
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
