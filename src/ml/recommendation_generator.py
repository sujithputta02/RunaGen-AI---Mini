"""
LLM-Based Recommendation Generator
Uses Ollama to generate personalized career recommendations
"""
import requests
import json
from typing import List, Dict, Optional

class RecommendationGenerator:
    def __init__(self, use_ollama=True):
        self.use_ollama = use_ollama
        self.ollama_url = "http://localhost:11434/api/generate"
        self.ollama_model = "llama3"
    
    def _call_ollama(self, prompt: str, max_tokens: int = 500) -> Optional[str]:
        """Call Ollama API for LLM-based generation"""
        if not self.use_ollama:
            return None
        
        try:
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,  # Creative but focused
                    "num_predict": max_tokens
                }
            }
            
            # Increase timeout to 120s for llama3 on localized hardware
            response = requests.post(self.ollama_url, json=payload, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                print(f"⚠️  Ollama API error: {response.status_code}")
                return None
        except requests.exceptions.ReadTimeout:
            print("⚠️  Ollama timeout (120s). Generating recommendations is taking too long.")
            return None
        except requests.exceptions.ConnectionError:
            print("⚠️  Ollama not running. Using fallback recommendations.")
            return None
        except Exception as e:
            print(f"⚠️  Ollama error: {e}")
            return None
    
    def generate_recommendations(
        self,
        skills: List[str],
        experience_years: int,
        education: str,
        career_predictions: List[Dict],
        skill_gaps: List[Dict],
        salary_prediction: Dict
    ) -> List[str]:
        """Generate personalized recommendations based on analysis"""
        
        # Build context for LLM
        top_career = career_predictions[0] if career_predictions else {"role": "Unknown", "probability": 0}
        top_skills_needed = [gap['skill'] for gap in skill_gaps[:5]] if skill_gaps else []
        
        prompt = f"""You are a career advisor AI. Based on the following resume analysis, provide 5-7 specific, actionable career recommendations.

CANDIDATE PROFILE:
- Current Skills: {', '.join(skills[:10])}
- Experience: {experience_years} years
- Education: {education}

ANALYSIS RESULTS:
- Top Predicted Career: {top_career['role']} ({top_career['probability']*100:.1f}% match)
- Other Career Options: {', '.join([p['role'] for p in career_predictions[1:3]])}
- Predicted Salary: ₹{salary_prediction.get('predicted_salary', 0)/100000:.1f}L per annum
- Top Skills to Learn: {', '.join(top_skills_needed)}

INSTRUCTIONS:
1. Provide 5-7 specific, actionable recommendations
2. Focus on career growth and skill development
3. Be practical and realistic
4. Consider the Indian job market
5. Each recommendation should be one clear sentence
6. Format as a numbered list

RECOMMENDATIONS:"""

        response = self._call_ollama(prompt, max_tokens=600)
        
        if response:
            # Parse recommendations from response
            recommendations = self._parse_recommendations(response)
            if recommendations:
                return recommendations
        
        # Fallback to rule-based recommendations
        return self._generate_fallback_recommendations(
            skills, experience_years, career_predictions, skill_gaps
        )
    
    def _parse_recommendations(self, response: str) -> List[str]:
        """Parse recommendations from LLM response"""
        recommendations = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            # Remove numbering (1., 2., etc.)
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Clean up the line
                clean_line = line.lstrip('0123456789.-•) ').strip()
                if clean_line and len(clean_line) > 20:  # Meaningful recommendation
                    recommendations.append(clean_line)
        
        return recommendations[:7]  # Limit to 7
    
    def _generate_fallback_recommendations(
        self,
        skills: List[str],
        experience_years: int,
        career_predictions: List[Dict],
        skill_gaps: List[Dict]
    ) -> List[str]:
        """Generate rule-based recommendations as fallback"""
        recommendations = []
        
        top_career = career_predictions[0] if career_predictions else {"role": "Software Engineer"}
        
        # Experience-based recommendations
        if experience_years < 2:
            recommendations.append(
                f"Focus on building a strong foundation in {', '.join(skills[:3])} through hands-on projects"
            )
            recommendations.append(
                "Consider internships or entry-level positions to gain practical experience"
            )
        elif experience_years < 5:
            recommendations.append(
                f"Position yourself for {top_career['role']} roles by showcasing your {', '.join(skills[:2])} expertise"
            )
            recommendations.append(
                "Build a portfolio of projects demonstrating your technical capabilities"
            )
        else:
            recommendations.append(
                f"Leverage your {experience_years} years of experience to transition into senior {top_career['role']} positions"
            )
            recommendations.append(
                "Consider mentoring junior developers and taking on leadership responsibilities"
            )
        
        # Skill gap recommendations
        if skill_gaps:
            top_gaps = [gap['skill'] for gap in skill_gaps[:3]]
            recommendations.append(
                f"Prioritize learning {', '.join(top_gaps)} to increase your market competitiveness"
            )
            recommendations.append(
                f"Enroll in online courses or certifications for {top_gaps[0]} to close critical skill gaps"
            )
        
        # Career-specific recommendations
        if top_career['role'] in ['Data Scientist', 'ML Engineer']:
            recommendations.append(
                "Contribute to open-source ML projects on GitHub to build credibility in the AI/ML community"
            )
        elif top_career['role'] in ['Data Engineer', 'Backend Developer']:
            recommendations.append(
                "Gain experience with cloud platforms (AWS/Azure/GCP) and modern data pipeline tools"
            )
        elif top_career['role'] in ['Frontend Developer', 'Full Stack Developer']:
            recommendations.append(
                "Build a strong portfolio website showcasing your UI/UX design and development skills"
            )
        
        # General recommendations
        recommendations.append(
            "Network with professionals in your target role through LinkedIn and industry events"
        )
        recommendations.append(
            "Update your resume to highlight achievements and quantifiable results from your projects"
        )
        
        return recommendations[:7]

if __name__ == "__main__":
    # Test the recommendation generator
    generator = RecommendationGenerator(use_ollama=True)
    
    test_data = {
        "skills": ["Python", "SQL", "Machine Learning", "Pandas"],
        "experience_years": 3,
        "education": "Bachelors",
        "career_predictions": [
            {"role": "Data Scientist", "probability": 0.85},
            {"role": "ML Engineer", "probability": 0.72}
        ],
        "skill_gaps": [
            {"skill": "TensorFlow", "priority_score": 0.9},
            {"skill": "AWS", "priority_score": 0.85}
        ],
        "salary_prediction": {"predicted_salary": 1200000}
    }
    
    recommendations = generator.generate_recommendations(**test_data)
    
    print("\n📋 Generated Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
