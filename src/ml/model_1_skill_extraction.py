"""
MODEL 1: Resume Skill Extraction - FIXED VERSION
Strict matching to avoid false positives
"""
import re
from pathlib import Path
import json
import requests

class SkillExtractor:
    def __init__(self, use_ollama=False):
        self.skill_dict = self._load_skill_dictionary()
        self.use_ollama = use_ollama
        self.ollama_url = "http://localhost:11434/api/generate"
        self.ollama_model = "llama3"
    
    def _load_skill_dictionary(self):
        """Load standardized skills from CSV"""
        try:
            import pandas as pd
            df = pd.read_csv('data/csv_exports/silver_skills.csv')
            return set(df['skill_name'].str.lower())
        except:
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
                    "temperature": 0.1,
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
            print("⚠️  Ollama timeout (120s). llama3 is taking too long to respond.")
            return None
        except requests.exceptions.ConnectionError:
            print("⚠️  Ollama not running. Start with: ollama serve")
            return None
        except Exception as e:
            print(f"⚠️  Ollama error: {e}")
            return None
    
    def extract_skills_with_ollama(self, resume_text):
        """Extract categorized skills using Ollama LLM"""
        prompt = f"""You are a resume parser. Extract ALL professional skills mentioned in this resume.
        
        Resume:
        {resume_text}
        
        Instructions:
        1. Extract ONLY skills explicitly mentioned in the resume.
        2. Categorize them into: "Technical", "Cloud/DevOps", "Databases", "Soft Skills", and "Domain Knowledge".
        3. Return AS A SINGLE FLAT JSON ARRAY of strings (standardize names like "Python", "ReactJS", "AWS").
        4. Focus on accuracy; do not include generic words like "Experience" or "Project".
        
        Output format (JSON only, no explanation):
        ["Skill 1", "Skill 2", "Skill 3"]
        
        Skills:"""

        response = self._call_ollama(prompt, max_tokens=400)
        
        if response:
            try:
                json_match = re.search(r'\[.*?\]', response, re.DOTALL)
                if json_match:
                    skills_json = json_match.group(0)
                    skills = json.loads(skills_json)
                    return [s.strip() for s in skills if s.strip() and len(s.strip()) > 1]
                else:
                    lines = response.split('\n')
                    skills = []
                    for line in lines:
                        clean = re.sub(r'^[\s\-\*\•"\']+|[\s"\']+$', '', line)
                        if clean and len(clean) > 1 and len(clean) < 50:
                            skills.append(clean)
                    return skills[:30]
            except json.JSONDecodeError:
                print("⚠️  Could not parse Ollama response as JSON")
                return None
        
        return None
    
    def extract_skills(self, resume_text):
        """Extract skills from resume text with AI validation"""
        
        skills = []
        if self.use_ollama:
            print("🤖 Using Ollama LLM for high-fidelity skill extraction...")
            skills = self.extract_skills_with_ollama(resume_text)
            if not skills:
                print("⚠️  Ollama failed, falling back to heuristic extraction")
                skills = self._extract_skills_strict(resume_text)
        else:
            print("⚡ Using heuristic regex-based skill extraction...")
            skills = self._extract_skills_strict(resume_text)
            
        return self.validate_skills(skills)

    def validate_skills(self, skills):
        """Filter and clean extracted skills to remove noise"""
        if not skills: return []
        
        valid_skills = []
        # Basic noise filter
        noise = {'experience', 'project', 'years', 'responsibilities', 'summary', 'about', 'skills', 'tools', 'using'}
        
        for s in skills:
            s_clean = s.strip('., •*-').strip()
            if len(s_clean) > 1 and s_clean.lower() not in noise:
                valid_skills.append(s_clean)
                
        return sorted(list(set(valid_skills)))
    
    def _extract_skills_strict(self, resume_text):
        """STRICT skill extraction - only exact matches"""
        resume_lower = resume_text.lower()
        extracted_skills = set()
        
        # Define explicit skill patterns with EXACT matching
        explicit_skills = {
            # Programming Languages
            'Python': r'\bpython\b',
            'Java': r'\bjava\b(?!script)',
            'JavaScript': r'\bjavascript\b|\bjs\b',
            'TypeScript': r'\btypescript\b|\bts\b',
            'C++': r'\bc\+\+\b',
            'C#': r'\bc#\b',
            'Go': r'\bgolang\b|\bgo\b(?= programming| lang)',
            'Rust': r'\brust\b',
            'Ruby': r'\bruby\b',
            'PHP': r'\bphp\b',
            'Swift': r'\bswift\b',
            'Kotlin': r'\bkotlin\b',
            'Scala': r'\bscala\b',
            'R': r'\b r \b|\br programming\b',
            
            # Databases
            'SQL': r'\bsql\b',
            'MySQL': r'\bmysql\b',
            'PostgreSQL': r'\bpostgresql\b|\bpostgres\b',
            'MongoDB': r'\bmongodb\b|\bmongo\b',
            'Redis': r'\bredis\b',
            'Cassandra': r'\bcassandra\b',
            'DynamoDB': r'\bdynamodb\b',
            'Oracle': r'\boracle\b(?= database| db)',
            'SQLite': r'\bsqlite\b',
            
            # Cloud Platforms
            'AWS': r'\baws\b|\bamazon web services\b',
            'Azure': r'\bazure\b|\bmicrosoft azure\b',
            'GCP': r'\bgcp\b',
            'Google Cloud': r'\bgoogle cloud platform\b|\bgoogle cloud\b(?= platform| compute| storage)',
            
            # DevOps
            'Docker': r'\bdocker\b',
            'Kubernetes': r'\bkubernetes\b|\bk8s\b',
            'Terraform': r'\bterraform\b',
            'Ansible': r'\bansible\b',
            'Jenkins': r'\bjenkins\b',
            'GitLab': r'\bgitlab\b',
            'GitHub Actions': r'\bgithub actions\b',
            'CI/CD': r'\bci/cd\b|\bci cd\b',
            
            # AI/ML
            'Machine Learning': r'\bmachine learning\b|\bml\b(?= engineer| model)',
            'Deep Learning': r'\bdeep learning\b',
            'TensorFlow': r'\btensorflow\b',
            'PyTorch': r'\bpytorch\b',
            'Scikit-learn': r'\bscikit-learn\b|\bsklearn\b',
            'NLP': r'\bnlp\b|\bnatural language processing\b',
            'Computer Vision': r'\bcomputer vision\b|\bcv\b(?= model| algorithm)',
            
            # Big Data
            'Apache Spark': r'\bapache spark\b|\bspark\b(?= streaming| sql)',
            'Hadoop': r'\bhadoop\b',
            'Kafka': r'\bkafka\b',
            'Airflow': r'\bairflow\b',
            'Flink': r'\bflink\b',
            'ETL': r'\betl\b',
            
            # Frontend
            'React': r'\breact\b|\breactjs\b',
            'Angular': r'\bangular\b',
            'Vue': r'\bvue\b|\bvue\.js\b|\bvuejs\b',
            'HTML': r'\bhtml\b|\bhtml5\b',
            'CSS': r'\bcss\b|\bcss3\b',
            'Sass': r'\bsass\b|\bscss\b',
            'Tailwind': r'\btailwind\b',
            
            # Backend
            'Node.js': r'\bnode\.js\b|\bnodejs\b',
            'Express': r'\bexpress\b|\bexpress\.js\b',
            'Django': r'\bdjango\b',
            'Flask': r'\bflask\b',
            'Spring Boot': r'\bspring boot\b',
            'FastAPI': r'\bfastapi\b',
            
            # Management & Strategy
            'Product Management': r'\bproduct management\b',
            'Project Management': r'\bproject management\b',
            'Agile': r'\bagile\b',
            'Scrum': r'\bscrum\b',
            'Jira': r'\bjira\b',
            'Roadmap': r'\broadmap\b',
            'Strategy': r'\bstrategy\b',
            'Stakeholder Management': r'\bstakeholder\b',
            
            # Sales & Marketing
            'Sales': r'\bsales\b',
            'CRM': r'\bcrm\b|\bsalesforce\b',
            'Negotiation': r'\bnegotiation\b',
            'Business Development': r'\bbusiness development\b|\bbd\b(?= manager| exec)',
            'Lead Generation': r'\blead generation\b',
            'Marketing': r'\bmarketing\b',
            'Branding': r'\bbranding\b',
            'SEO': r'\bseo\b',
            'SEM': r'\bsem\b',
            'Social Media': r'\bsocial media\b',
            'Content Strategy': r'\bcontent strategy\b',
            
            # Finance & Accounting
            'Accounting': r'\baccounting\b|\bbookkeeping\b',
            'Finance': r'\bfinance\b',
            'Taxation': r'\btaxation\b|\btax\b',
            'Auditing': r'\bauditing\b|\baudit\b',
            'Financial Modeling': r'\bfinancial modeling\b',
            'Tally': r'\btally\b',
            'GST': r'\bgst\b',
            
            # HR & Operations
            'Human Resources': r'\bhuman resources\b|\bhr\b(?= manager| exec| dept)',
            'Recruitment': r'\brecruitment\b|\btalent acquisition\b',
            'Payroll': r'\bpayroll\b',
            'Onboarding': r'\bonboarding\b',
            
            # General / Soft Skills
            'Communication': r'\bcommunication skills\b|\binterpersonal skills\b',
            'Leadership': r'\bleadership\b',
            'Problem Solving': r'\bproblem solving\b',
            'Customer Service': r'\bcustomer service\b|\bcustomer support\b',
            'Support': r'\bsupport\b',
            'Linux': r'\blinux\b',
            'REST API': r'\brest api\b|\brestful\b',
            'GraphQL': r'\bgraphql\b',
            'Microservices': r'\bmicroservices\b',
        }
        
        # 1. Regex Match from Dictionary (High-Confidence)
        for skill_name, pattern in explicit_skills.items():
            if re.search(pattern, resume_lower, re.IGNORECASE):
                extracted_skills.add(skill_name)
        
        # 2. Heuristic Extraction for Unlisted Technical Skills
        # Look for CamelCase, tools with numbers, .js, ++, #, @
        tech_patterns = [
            r'\b[A-Z][a-z]+[A-Z][a-z]+\b', # CamelCase (e.g. MySQL, PostgreSql)
            r'\b[a-z0-9]+\.(?:js|py|rb|php|go)\b', # .js, .py, etc.
            r'\b[A-Za-z]+\d+\b', # Tools with versions (e.g. Python3, Vue2)
            r'\b[A-Za-z]+[\+#]{1,2}\b', # C++, C#, F#
            r'\b(?:aws|azure|gcp|ibm)\s+[a-z0-9]+\b' # Cloud services (aws s3, etc)
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, resume_text, re.IGNORECASE)
            for match in matches:
                # Clean and Filter
                clean = str(match).strip('., ')
                if len(clean) > 2 and clean.lower() not in ['this', 'that', 'with', 'from']:
                    extracted_skills.add(clean.title())
        
        # 3. Section-Based Extraction (Skills/Tools section)
        sections = re.split(r'\n\s*(?:skills|tools?|technologies|technical expertise|expertise|competencies)\s*\n', resume_text, flags=re.IGNORECASE)
        if len(sections) > 1:
            skill_section = sections[1].split('\n\n')[0] # Take first block
            # Extract anything that looks like a skill (comma or bullet separated)
            potential_skills = re.split(r'[,|•\*\n]', skill_section)
            for ps in potential_skills:
                ps = ps.strip()
                if ps and 2 < len(ps) < 30 and not any(char.isdigit() for char in ps[:1]):
                    extracted_skills.add(ps.title())

        return sorted(list(extracted_skills))
    
    def extract_experience(self, resume_text):
        """Extract years of experience"""
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
        """Extract job titles from resume"""
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
                title = response.strip().strip('"\'')
                if title and title.lower() != 'not specified' and len(title) < 100:
                    return [title]
        
        # Fallback to regex
        job_title_patterns = [
            r'(?:current role|position|title|designation)\s*:?\s*([^\n]+)',
            r'(?:working as|work as)\s+(?:a|an)?\s*([^\n,\.]+)',
            r'\b((?:senior|junior|lead|principal|staff)?\s*(?:software|data|machine learning|ml|ai|backend|frontend|full stack|devops)\s+(?:engineer|developer|scientist|analyst|architect))\b',
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
    
    def extract_structured_data_with_ollama(self, resume_text):
        """Extract all structured data (skills, exp, edu, titles) in one LLM call"""
        prompt = f"""You are an expert resume parser. Extract structured information from the following resume text.
        
        Resume Text:
        {resume_text}
        
        Instructions:
        1. Parse the resume and extract:
           - "skills": A list of professional technical and soft skills.
           - "experience_years": Total years of professional experience as an integer.
           - "education": Highest education level (e.g., "Bachelors", "Masters", "PhD", "MBA").
           - "job_titles": A list of formal job titles held, most recent first.
           - "certifications": A list of objects representing professional certifications, each with "name", "issuer", "year", and "verification_id" (if available).
        2. Format the output as a STRICT JSON object. No conversational text.
        3. Standardize skill names (e.g., "ReactJS" -> "React", "AWS Services" -> "AWS").
        4. If a field is not found, use [] for lists or null for strings/numbers.
        
        Expected JSON format:
        {{
          "skills": ["Python", "SQL", "Machine Learning"],
          "experience_years": 5,
          "education": "Masters",
          "job_titles": ["Senior Data Engineer", "Data Analyst"],
          "certifications": [
            {{"name": "AWS Certified Solutions Architect", "issuer": "Amazon Web Services", "year": "2023", "verification_id": "ABC-123"}}
          ]
        }}
        
        JSON Output:"""

        # Full token depth restored; efficiency now handled by parallel execution
        response = self._call_ollama(prompt, max_tokens=800)
        
        if response:
            try:
                # Try to find JSON block in case LLM added conversational text
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))
                    
                    # Basic validation and cleaning
                    result = {
                        'skills': [s.strip() for s in data.get('skills', []) if isinstance(s, str) and len(s) > 1],
                        'experience_years': data.get('experience_years'),
                        'education': data.get('education'),
                        'job_titles': [t.strip() for t in data.get('job_titles', []) if isinstance(t, str) and len(t) > 2],
                        'certifications': data.get('certifications', [])
                    }
                    
                    # Ensure experience is a number
                    if result['experience_years'] is not None:
                        try:
                            if isinstance(result['experience_years'], str):
                                nums = re.findall(r'\d+', result['experience_years'])
                                result['experience_years'] = int(nums[0]) if nums else 0
                            else:
                                result['experience_years'] = int(result['experience_years'])
                        except:
                            result['experience_years'] = 0
                    
                    return result
            except Exception as e:
                print(f"⚠️  Failed to parse Ollama JSON response: {e}")
        
        return None

    def extract_all(self, resume_text):
        """Extract all structured data using optimized single-call strategy"""
        if self.use_ollama:
            print("🤖 Using Optimized Ollama context-aware extraction...")
            structured_data = self.extract_structured_data_with_ollama(resume_text)
            
            if structured_data:
                # Still run validation on skills
                structured_data['skills'] = self.validate_skills(structured_data['skills'])
                
                # Check for heuristic fallbacks if LLM missed something critical
                if not structured_data['skills']:
                    structured_data['skills'] = self.extract_skills(resume_text)
                
                if structured_data.get('experience_years') is None:
                    structured_data['experience_years'] = self.extract_experience(resume_text)
                    
                if not structured_data.get('education') or structured_data['education'] == 'null':
                    structured_data['education'] = self.extract_education(resume_text)

                if not structured_data.get('certifications'):
                    structured_data['certifications'] = self.extract_certificates_heuristic(resume_text)
                
                return structured_data
        
        # Fallback to separate calls or heuristics if Ollama fails or is disabled
        return {
            'skills': self.extract_skills(resume_text),
            'experience_years': self.extract_experience(resume_text),
            'education': self.extract_education(resume_text),
            'job_titles': self.extract_job_titles(resume_text),
            'certifications': self.extract_certificates_heuristic(resume_text)
        }
    
    def extract_certificates_heuristic(self, resume_text):
        """Extract certifications using pattern matching and keywords"""
        cert_keywords = ['certified', 'certification', 'license', 'accredited', 'professional certificate']
        certificates = []
        
        lines = resume_text.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in cert_keywords):
                # Basic cleanup
                clean_cert = line.strip(' •*-').split(':')[-1].strip()
                if 5 < len(clean_cert) < 100:
                    # Look for issuer in the same or next line
                    issuer = "Unknown"
                    potential_issuers = ['amazon', 'aws', 'microsoft', 'google', 'coursera', 'udemy', 'cisco', 'oracle', 'itil', 'pmp']
                    for pi in potential_issuers:
                        if pi in line_lower:
                            issuer = pi.title()
                            break
                    
                    certificates.append({
                        "name": clean_cert,
                        "issuer": issuer,
                        "year": None,
                        "verification_id": None
                    })
        
        return certificates[:5] # Limit to top 5

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
