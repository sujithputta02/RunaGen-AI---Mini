"""
MODEL 1: Resume Skill Extraction
Uses Ollama LLM for intelligent skill extraction from resumes
"""
import re
from pathlib import Path
import json
import requests

class SkillExtractor:
    def __init__(self, use_ollama=False):  # Default to False for speed
        # Load skill dictionary from CSV
        self.skill_dict = self._load_skill_dictionary()
        self.use_ollama = use_ollama
        self.ollama_url = "http://localhost:11434/api/generate"
        self.ollama_model = "llama3"  # Using llama3 model
    
    def _load_skill_dictionary(self):
        """Load standardized skills from CSV"""
        try:
            import pandas as pd
            df = pd.read_csv('data/csv_exports/silver_skills.csv')
            return set(df['skill_name'].str.lower())
        except:
            # Fallback to basic skills
            return {
                'python', 'java', 'sql', 'javascript', 'aws', 'azure', 'gcp',
                'machine learning', 'deep learning', 'data analysis',
                'etl', 'spark', 'hadoop', 'docker', 'kubernetes',
                'mongodb', 'postgresql', 'redis', 'react', 'angular'
            }
    
    def _call_ollama(self, prompt, max_tokens=500):
        """Call Ollama API for LLM-based extraction"""
        try:
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Low temperature for consistent extraction
                    "num_predict": max_tokens
                }
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                print(f"⚠️  Ollama API error: {response.status_code}")
                return None
        except requests.exceptions.ConnectionError:
            print("⚠️  Ollama not running. Start with: ollama serve")
            return None
        except Exception as e:
            print(f"⚠️  Ollama error: {e}")
            return None
    
    def extract_skills_with_ollama(self, resume_text):
        """Extract skills using Ollama LLM"""
        prompt = f"""You are a resume parser. Extract ONLY the technical skills that are explicitly mentioned in this resume.

Resume:
{resume_text}

Instructions:
1. Extract ONLY skills that are clearly stated in the resume
2. Include programming languages, frameworks, tools, databases, cloud platforms
3. Do NOT infer or add skills that are not mentioned
4. Return as a JSON array of strings
5. Use proper capitalization (e.g., "Python", "JavaScript", "AWS")

Output format (JSON only, no explanation):
["skill1", "skill2", "skill3"]

Skills:"""

        response = self._call_ollama(prompt, max_tokens=300)
        
        if response:
            try:
                # Try to extract JSON from response
                # Look for array pattern
                json_match = re.search(r'\[.*?\]', response, re.DOTALL)
                if json_match:
                    skills_json = json_match.group(0)
                    skills = json.loads(skills_json)
                    # Clean and validate
                    return [s.strip() for s in skills if s.strip() and len(s.strip()) > 1]
                else:
                    # Fallback: parse line by line
                    lines = response.split('\n')
                    skills = []
                    for line in lines:
                        # Remove bullets, quotes, etc.
                        clean = re.sub(r'^[\s\-\*\•"\']+|[\s"\']+$', '', line)
                        if clean and len(clean) > 1 and len(clean) < 50:
                            skills.append(clean)
                    return skills[:30]  # Limit to 30 skills
            except json.JSONDecodeError:
                print("⚠️  Could not parse Ollama response as JSON")
                return None
        
        return None
    
    def extract_skills(self, resume_text):
        """Extract skills from resume text - uses fast regex by default"""
        
        # Try Ollama only if explicitly enabled
        if self.use_ollama:
            print("🤖 Using Ollama LLM for skill extraction...")
            ollama_skills = self.extract_skills_with_ollama(resume_text)
            if ollama_skills:
                print(f"✓ Ollama extracted {len(ollama_skills)} skills")
                return sorted(ollama_skills)
            else:
                print("⚠️  Ollama failed, falling back to regex extraction")
        
        # Fast regex-based extraction (default)
        print("⚡ Using fast regex-based skill extraction...")
        return self._extract_skills_regex(resume_text)
    
    def _extract_skills_regex(self, resume_text):
        """Fallback regex-based skill extraction"""
        resume_lower = resume_text.lower()
        extracted_skills = set()
        
        # Method 1: Strict dictionary matching with context validation
        for skill in self.skill_dict:
            skill_lower = skill.lower()
            
            # Skip very short/generic terms that cause false positives
            if len(skill_lower) <= 2 and skill_lower not in ['r', 'c', 'go']:
                continue
            
            # Match whole words with word boundaries
            pattern = r'\b' + re.escape(skill_lower) + r'\b'
            matches = list(re.finditer(pattern, resume_lower))
            
            if matches:
                # Validate each match has proper context (not in middle of sentence about something else)
                for match in matches:
                    start = max(0, match.start() - 50)
                    end = min(len(resume_lower), match.end() + 50)
                    context = resume_lower[start:end]
                    
                    # Check if it's in a skills/technical context
                    skill_indicators = [
                        'skill', 'experience', 'proficient', 'knowledge', 'expertise',
                        'worked with', 'using', 'technologies', 'tools', 'programming',
                        'framework', 'language', 'database', 'platform', 'familiar'
                    ]
                    
                    # If context contains skill indicators OR it's a well-known tech term, include it
                    if any(indicator in context for indicator in skill_indicators):
                        extracted_skills.add(skill.title())
                        break
                    # Also include if it's a common tech term (even without indicators)
                    elif skill_lower in ['python', 'java', 'javascript', 'sql', 'aws', 'azure', 
                                        'docker', 'kubernetes', 'react', 'angular', 'node.js',
                                        'mongodb', 'postgresql', 'git', 'linux', 'machine learning',
                                        'deep learning', 'data analysis', 'spark', 'hadoop']:
                        extracted_skills.add(skill.title())
                        break
        
        # Method 2: Explicit tech patterns (only for clear technical terms)
        tech_patterns = {
            r'\b(python|java|javascript|typescript|c\+\+|c#|golang|rust|ruby|php|swift|kotlin|scala)\b': 'Programming',
            r'\b(sql|mysql|postgresql|mongodb|redis|cassandra|dynamodb|oracle|sqlite)\b': 'Database',
            r'\b(aws|azure|gcp|google cloud|amazon web services|microsoft azure)\b': 'Cloud',
            r'\b(docker|kubernetes|k8s|terraform|ansible|jenkins|gitlab|github actions)\b': 'DevOps',
            r'\b(machine learning|deep learning|neural network|nlp|computer vision|tensorflow|pytorch)\b': 'AI/ML',
            r'\b(apache spark|hadoop|kafka|airflow|flink)\b': 'Big Data',
            r'\b(react|angular|vue\.js|node\.js|express|django|flask|spring boot)\b': 'Frameworks',
            r'\b(git|github|gitlab|bitbucket|svn)\b': 'Version Control'
        }
        
        for pattern, category in tech_patterns.items():
            matches = re.findall(pattern, resume_lower, re.IGNORECASE)
            for match in matches:
                # Normalize the match
                normalized = match.strip().title()
                if match.lower() in ['k8s']:
                    normalized = 'Kubernetes'
                elif match.lower() in ['golang']:
                    normalized = 'Go'
                extracted_skills.add(normalized)
        
        return sorted(list(extracted_skills))
    
    def extract_experience(self, resume_text):
        """Extract years of experience - uses Ollama if available"""
        
        # Try Ollama first
        if self.use_ollama:
            prompt = f"""Extract the total years of professional experience from this resume.

Resume:
{resume_text}

Instructions:
1. Look for phrases like "X years of experience", "X+ years", etc.
2. Return ONLY a number (integer)
3. If not found, return 0

Output (number only):"""
            
            response = self._call_ollama(prompt, max_tokens=10)
            if response:
                # Extract number from response
                numbers = re.findall(r'\d+', response)
                if numbers:
                    return int(numbers[0])
        
        # Fallback to regex
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of)?\s*experience',
            r'experience\s*:\s*(\d+)\s*years?',
            r'(\d+)\s*years?\s*in\s*(?:the\s*)?(?:field|industry)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, resume_text.lower())
            if match:
                return int(match.group(1))
        
        return None
    
    def extract_education(self, resume_text):
        """Extract education level"""
        education_keywords = {
            'phd': 'PhD',
            'doctorate': 'PhD',
            'master': 'Masters',
            'mba': 'MBA',
            'bachelor': 'Bachelors',
            'b.tech': 'Bachelors',
            'b.e': 'Bachelors',
            'b.s': 'Bachelors',
            'm.s': 'Masters',
            'm.tech': 'Masters'
        }
        
        text_lower = resume_text.lower()
        for keyword, level in education_keywords.items():
            if keyword in text_lower:
                return level
        
        return 'Not specified'
    
    def extract_job_titles(self, resume_text):
        """Extract job titles from resume - uses Ollama if available"""
        
        # Try Ollama first
        if self.use_ollama:
            prompt = f"""Extract the current or most recent job title from this resume.

Resume:
{resume_text}

Instructions:
1. Find the most recent job title/position
2. Return ONLY the job title (e.g., "Data Engineer", "Software Developer")
3. If multiple titles, return the most recent one
4. If not found, return "Not specified"

Output (job title only):"""
            
            response = self._call_ollama(prompt, max_tokens=50)
            if response:
                # Clean the response
                title = response.strip().strip('"\'')
                if title and title.lower() != 'not specified' and len(title) < 100:
                    return [title]
        
        # Fallback to regex
        job_title_patterns = [
            r'(?:current role|position|title|designation)\s*:?\s*([^\n]+)',
            r'(?:working as|work as)\s+(?:a|an)?\s*([^\n,\.]+)',
            r'\b((?:senior|junior|lead|principal|staff)?\s*(?:software|data|machine learning|ml|ai|backend|frontend|full stack|devops)\s+(?:engineer|developer|scientist|analyst|architect))\b',
            r'\b((?:product|project|engineering|technical)\s+manager)\b',
            r'\b(data\s+(?:scientist|engineer|analyst|architect))\b',
            r'\b(software\s+(?:engineer|developer|architect))\b',
            r'\b(machine\s+learning\s+engineer)\b',
            r'\b(devops\s+engineer)\b',
            r'\b(full\s+stack\s+developer)\b'
        ]
        
        titles = set()
        text_lower = resume_text.lower()
        
        for pattern in job_title_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match[0] else match[1] if len(match) > 1 else ''
                title = match.strip()
                if title and len(title) > 3 and len(title) < 50:
                    titles.add(title.title())
        
        return list(titles)
    
    def extract_all(self, resume_text):
        """Extract all structured data from resume"""
        return {
            'skills': self.extract_skills(resume_text),
            'experience_years': self.extract_experience(resume_text),
            'education': self.extract_education(resume_text),
            'job_titles': self.extract_job_titles(resume_text)
        }

# Evaluation metrics
def evaluate_extraction(predictions, ground_truth):
    """Calculate precision, recall, F1"""
    tp = len(set(predictions) & set(ground_truth))
    fp = len(set(predictions) - set(ground_truth))
    fn = len(set(ground_truth) - set(predictions))
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {'precision': precision, 'recall': recall, 'f1': f1}

if __name__ == "__main__":
    extractor = SkillExtractor()
    
    # Test with sample resume
    sample_resume = """
    Data Engineer with 5 years of experience in Python, SQL, and AWS.
    Master's degree in Computer Science.
    Expertise in ETL pipelines, Apache Spark, and machine learning.
    """
    
    result = extractor.extract_all(sample_resume)
    print(json.dumps(result, indent=2))
