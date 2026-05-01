"""
MODEL 1: Resume Skill Extraction - FIXED VERSION
Strict matching to avoid false positives
"""
import re
from pathlib import Path
import json
import requests

class SkillExtractor:
    def __init__(self, use_ollama=False, use_gemini=True):
        import os
        self.skill_dict = self._load_skill_dictionary()
        self.use_ollama = use_ollama
        self.use_gemini = use_gemini
        
        # Ollama config - Check if running in cloud or local
        self.is_cloud = os.getenv("ENVIRONMENT", "local").lower() == "cloud"
        
        if self.is_cloud:
            # Cloud deployment: Use Ollama from Compute Engine
            self.ollama_url = os.getenv("OLLAMA_URL", "")
            if self.ollama_url:
                self.use_ollama = True  # Enable Ollama in cloud
                print("☁️  Cloud environment detected - Using Ollama from Compute Engine")
            else:
                self.use_ollama = False
                print("☁️  Cloud environment detected - No Ollama URL configured")
        else:
            # Local development: Use local Ollama
            self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
            self.use_ollama = use_ollama
        
        # Ensure Ollama URL has correct endpoint
        if self.use_ollama and self.ollama_url:
            if not self.ollama_url.endswith("/api/generate"):
                self.ollama_url = self.ollama_url.rstrip("/") + "/api/generate"
        
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3")
        
        # Gemini config (disabled when using Ollama)
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.client = None
        if self.use_gemini and self.gemini_api_key and not self.use_ollama:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.gemini_api_key)
                print("✓ Gemini LLM initialized for skill extraction")
            except Exception as e:
                print(f"⚠️  Failed to initialize Gemini: {e}")
                self.use_gemini = False

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
                'mongodb', 'postgresql', 'redis', 'react', 'angular',
                'fastapi', 'django', 'flask', 'pytorch', 'tensorflow'
            }

    def _call_gemini(self, prompt):
        """Call Gemini API for LLM-based extraction"""
        if not self.client:
            return None
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"⚠️  Gemini API error: {e}")
            return None

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
            
            response = requests.post(self.ollama_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            return None
        except:
            return None

    def validate_skills(self, skills):
        """Filter and clean extracted skills to remove noise"""
        if not skills: return []
        
        valid_skills = []
        # ULTRA-STRICT Noise Filter - includes common resume words that are NOT skills
        noise = {
            'experience', 'project', 'years', 'responsibilities', 'summary', 'about', 
            'skills', 'tools', 'using', 'various', 'including', 'knowledge', 'understanding',
            'professional', 'work', 'ability', 'across', 'achievements', 'actions', 'apr', 'jan', 'feb',
            'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec',
            'academy', 'accuracy', 'achieving', 'agent', 'agents', 'and',
            'based', 'between', 'building', 'built', 'challenge', 'completion', 'complex', 'complexity',
            'concepts', 'control', 'converts', 'cycle', 'defined', 'delivered', 'delivering', 'delivery',
            'designing', 'developed', 'developing', 'development', 'driven', 'effective', 'effectively',
            'excellent', 'expertise', 'flexible', 'following', 'highly', 'implemented', 'improving',
            'increased', 'independent', 'innovative', 'involved', 'leading', 'managed', 'managing',
            'mentoring', 'optimized', 'participated', 'performed', 'planned', 'presented', 'problem',
            'processed', 'produced', 'provided', 'quality', 'reduced', 'related', 'relevant', 'resolved',
            'responsible', 'result', 'results', 'role', 'roles', 'served', 'strong', 'successfully',
            'supported', 'supporting', 'team', 'teams', 'technical', 'technology', 'trained', 'training',
            'updated', 'updating', 'user', 'users', 'various', 'within', 'worked', 'working', 'writing',
            'with', 'from', 'that', 'this', 'their', 'the', 'for', 'was', 'were', 'had', 'been',
            'education', 'university', 'college', 'school', 'bachelor', 'master', 'phd', 'degree', 
            'internship', 'intern', 'trainee', 'fresher', 'india', 'bangalore', 'pune', 'hyderabad',
            'ambiguously', 'analysis', 'analyzing', 'application', 'applications', 'apps', 'architected',
            'architecture', 'auth', 'basics', 'campus', 'career', 'cgpa', 'concurrent', 'core', 'course',
            'coursework', 'cup', 'data', 'data-driven', 'databases', 'dayananda', 'dbms', 'dbt', 'debugging',
            'dependency', 'deploy', 'deployed', 'deployment', 'designed', 'devops', 'digital', 'distributed',
            'document', 'earth', 'efficient', 'enabling', 'end-to-end', 'enforce', 'engine', 'engineered',
            'engineering', 'environments', 'event', 'events', 'exchange', 'executed', 'experienced',
            'fast', 'fault', 'fault-tolerant', 'features', 'flow', 'flows', 'forecasts', 'foundations',
            'full', 'full-stack', 'functional', 'fundamentals', 'gapped', 'gen', 'generate', 'generation',
            'global', 'graduate', 'graph', 'hack', 'hackathon', 'hallucinations', 'handling', 'helping',
            'high', 'historical', 'hybrid', 'imagine', 'implement', 'indexing', 'ingestion',
            'insights', 'integrating', 'intelligence', 'intelligently', 'intensive', 'interactive',
            'internet', 'into', 'introduction', 'invoicing', 'isolated', 'job', 'json', 'labs', 'languages',
            'latency', 'layers', 'leveraging', 'life', 'local', 'lovable', 'maintenance', 'management',
            'microsoft', 'model', 'models', 'modular', 'multi', 'multi-agent', 'multi-model', 'multi-tiered',
            'multiple', 'navigable', 'nosql', 'object', 'object-oriented', 'observation', 'offline',
            'optimizing', 'oriented', 'outdoor', 'paced', 'parade', 'participant', 'pass', 'passion',
            'personalized', 'pipeline', 'pipelines', 'plan', 'platform', 'powered', 'practices', 'present',
            'probability', 'probability-based', 'problems', 'processes', 'processing', 'programming',
            'projects', 'prompt', 'proven', 'qualifier', 'queries', 'query', 'real', 'real-world', 'reduce',
            'reducing', 'relational', 'release', 'reliability', 'reliable', 'reservation', 'rest',
            'restaurant', 'restful', 'retrieval', 'roadmap', 'role-based', 'round', 'route', 'scalable',
            'scenario', 'scenarios', 'science', 'search', 'season', 'secure', 'security', 'services',
            'serving', 'significantly', 'simulation', 'simulations', 'skill', 'skill-gap', 'software',
            'solving', 'sovereign', 'space', 'stack', 'step', 'step-by-step', 'structured', 'structures',
            'systematic', 'systems', 'tech', 'techniques', 'test', 'testing', 'through', 'tiered', 'time',
            'tolerant', 'undergraduate', 'user-navigable', 'validation', 'vector', 'via', 'vibe', 'wallet',
            'wallet-pass', 'wars', 'weather', 'web', 'will', 'workflow', 'world', 'yaml', 'young', 'badge',
            'nordics', 'nexora', 'nsac', 'sagar', 'sujith', 'putta', 'runagen', 'vibe', 'parade', 'turks',
            'season', 'season-2', 'dineingo', 'techflix'
        }
        
        for s in skills:
            if not isinstance(s, str): continue
            
            # 1. Strip special characters and whitespace
            s_clean = s.strip('., •*-()[]{}"\'').strip()
            
            # 2. Basic quality checks
            s_lower = s_clean.lower()
            if (len(s_clean) > 1 and 
                re.search(r'[a-zA-Z]', s_clean) and 
                not s_clean.isdigit() and
                s_lower not in noise and
                not re.match(r'^(?:19|20)\d{2}$', s_clean)): 
                
                # Check for single generic words that are usually not skills unless known
                is_known = s_lower in self.skill_dict
                is_technical = bool(re.search(r'\d|\+|#|\.js|/|[A-Z][a-z]+[A-Z]', s_clean))
                
                # If it's a very common word and not in our known list, skip it
                common_generic = {'data', 'web', 'app', 'system', 'software', 'management', 'analysis', 'cloud', 'design', 'service'}
                if s_lower in common_generic and not is_known:
                    continue
                
                # Length check for non-technical words
                if not is_known and not is_technical and len(s_clean) < 3:
                    continue
                    
                if is_known:
                    # Use the standard casing from dictionary if possible
                    valid_skills.append(s_clean)
                else:
                    # Heuristic check: most technical skills are either short acronyms (AWS, SQL) 
                    # or TitleCase (React, Python). 
                    # If it's all lowercase and not known, it's likely noise.
                    if s_clean.islower() and len(s_clean) > 4:
                        continue
                    valid_skills.append(s_clean)
                
        # Deduplicate while preserving case-normalized versions
        seen = set()
        final_skills = []
        for s in valid_skills:
            if s.lower() not in seen:
                final_skills.append(s)
                seen.add(s.lower())
                
        return sorted(final_skills)

    def extract_all(self, resume_text):
        """Extract all structured data using LLM with heuristic fallback"""
        # Try Gemini first (Best for Cloud)
        if self.use_gemini and self.client:
            print("🤖 Using Gemini Pro for high-fidelity extraction...")
            data = self.extract_structured_data_llm(resume_text, provider="gemini")
            if data and data.get('skills'):
                return data
                
        # Try Ollama (Local development fallback)
        if self.use_ollama:
            print("🤖 Using Ollama for extraction...")
            data = self.extract_structured_data_llm(resume_text, provider="ollama")
            if data and data.get('skills'):
                return data

        # Final Heuristic Fallback
        print("⚡ Using strict heuristic extraction fallback...")
        return {
            'skills': self.extract_skills_heuristic(resume_text),
            'experience_years': self.extract_experience_heuristic(resume_text),
            'education': self.extract_education_heuristic(resume_text),
            'job_titles': self.extract_job_titles_heuristic(resume_text),
            'certifications': self.extract_certifications_heuristic(resume_text),
            'projects': self.extract_projects_heuristic(resume_text)
        }

    def extract_structured_data_llm(self, resume_text, provider="gemini"):
        """Extract structured data using specified LLM provider"""
        prompt = f"""You are an expert resume parser. Extract structured information from the following resume text.
        
        Resume Text:
        {resume_text}
        
        Instructions:
        1. Parse the resume and extract:
           - "skills": A list of professional technical skills ONLY (e.g. "Python", "Docker", "AWS").
             * STRICTLY EXCLUDE: common verbs (e.g. "Analyzing", "Building"), generic nouns (e.g. "Experience", "Data"), locations, and universities.
           - "experience_years": ONLY if there is a dedicated "Work Experience" or "Professional Experience" section with actual job titles and companies. Return 0 if no work experience section exists. Do NOT count internships, courses, or projects as experience.
           - "education": Highest degree level.
           - "job_titles": List of formal job titles held.
           - "certifications": List of certifications with format [{{"name": "cert_name", "issuer": "issuer_name", "year": year_or_null}}]
        
        Return ONLY valid JSON with all fields.
        """

        if provider == "gemini":
            response = self._call_gemini(prompt)
        else:
            response = self._call_ollama(prompt, max_tokens=1500)
            
        if response:
            try:
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))
                    data['skills'] = self.validate_skills(data.get('skills', []))
                    # Ensure certifications is a list
                    if 'certifications' not in data:
                        data['certifications'] = []
                    # Force experience_years to 0 if LLM returns suspicious values
                    exp_years = data.get('experience_years', 0)
                    if not isinstance(exp_years, int) or exp_years < 0 or exp_years > 60:
                        data['experience_years'] = 0
                    return data
            except:
                pass
        return None

    def extract_skills_heuristic(self, resume_text):
        """Fallback regex extraction"""
        found = set()
        resume_lower = resume_text.lower()
        
        # 1. Exact matches from dictionary
        for skill in self.skill_dict:
            if len(skill) > 2:
                if re.search(r'\b' + re.escape(skill) + r'\b', resume_lower):
                    found.add(skill.title())
            else: # Short skills like C, R, Go
                if re.search(r'\b' + re.escape(skill) + r'\b', resume_text):
                    found.add(skill.upper())
        
        return self.validate_skills(list(found))

    def extract_experience_heuristic(self, resume_text):
        """Extract years of experience - ULTRA STRICT matching only"""
        # Only match if it's explicitly about work/professional experience
        # Avoid matching certifications, courses, or other contexts
        
        # First, check for explicit work experience section headers
        has_work_section = bool(re.search(
            r'(?:work\s+experience|professional\s+experience|employment|career|experience)',
            resume_text,
            re.IGNORECASE
        ))
        
        if not has_work_section:
            # If there's no work experience section header, return 0
            return 0
        
        patterns = [
            # Explicit work experience mentions (must be in context of work)
            r'total\s+(?:professional\s+)?experience[:\s]+(\d+)\+?\s*years?',
            r'(?:professional\s+)?experience[:\s]+(\d+)\+?\s*years?(?:\s+in\s+(?:industry|field|software|development|it))?',
            r'(\d+)\+?\s*years?\s+(?:of\s+)?(?:professional\s+)?(?:work\s+)?experience',
            r'(\d+)\+?\s*years?\s+in\s+(?:industry|field|software|development|it|tech|engineering)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, resume_text, re.IGNORECASE)
            if match:
                years = int(match.group(1))
                # Only return if it's a reasonable number (1-60 years)
                if 1 <= years <= 60:
                    return years
        
        # If no explicit match, return 0
        return 0

    def extract_education_heuristic(self, resume_text):
        for deg in ['phd', 'master', 'bachelor', 'b.tech', 'm.tech']:
            if deg in resume_text.lower():
                return deg.title()
        return "N/A"

    def extract_job_titles_heuristic(self, resume_text):
        titles = []
        patterns = [r'\b(?:senior|junior|lead)?\s*(?:software|data|system|cloud)\s+(?:engineer|developer|analyst)\b']
        for p in patterns:
            matches = re.findall(p, resume_text, re.IGNORECASE)
            titles.extend(matches)
        return list(set(titles))

    def extract_certifications_heuristic(self, resume_text):
        """Extract certifications from resume text - STRICT matching only"""
        certifications = []
        
        # ULTRA-STRICT certification patterns - only match ACTUAL certifications held
        # Avoid matching hackathons, competitions, or aspirational mentions
        cert_patterns = [
            # AWS Certifications - STRICT (must have "Certified" or specific cert codes)
            (r'AWS\s+(?:Certified|Certification)\s+(?:Solutions Architect|Developer|SysOps|Cloud Practitioner|Associate|Professional)', 'AWS Certified'),
            (r'AWS\s+(?:SAA|DVA|SOA|CLF|SAP|DOP|ANS|MLS|DAS|PAS|DBS|DMS|APS|ACS|AES|AMS|APS|ARS|ASS|ATS|AUS|AVS|AWS|AXS|AYS|AZS)', 'AWS Certified'),
            (r'Amazon\s+Web\s+Services\s+(?:Certified|Certification)', 'AWS Certified'),
            (r'AWS\s+Academy\s+Graduate', 'AWS Academy Graduate'),
            
            # Microsoft/Azure - STRICT (must have cert code or "Certified" - NOT "Imagine Cup")
            (r'Microsoft\s+(?:Certified|Certification):\s+(?:Azure|Administrator|Developer|Solutions Architect)', 'Microsoft Certified'),
            (r'AZ-\d{3}\s*(?::|–|-)', 'Microsoft Azure'),
            (r'Microsoft\s+Azure\s+(?:Administrator|Developer|Solutions Architect)', 'Microsoft Azure'),
            
            # Google Cloud - STRICT
            (r'Google\s+Cloud\s+(?:Certified|Certification)\s+(?:Associate|Professional)', 'Google Cloud Certified'),
            (r'Google\s+Cloud\s+(?:Associate|Professional)\s+(?:Cloud Architect|Data Engineer|Cloud Developer)', 'Google Cloud Certified'),
            
            # Kubernetes - STRICT (specific cert codes)
            (r'(?:Certified Kubernetes Administrator|CKA)(?:\s|:|–|-|$)', 'Kubernetes CKA'),
            (r'(?:Certified Kubernetes Application Developer|CKAD)(?:\s|:|–|-|$)', 'Kubernetes CKAD'),
            
            # Docker - STRICT
            (r'Docker\s+(?:Certified|Certification)\s+(?:Associate|Professional)', 'Docker Certified'),
            
            # Scrum/Agile - STRICT (must have "Certified")
            (r'Certified\s+Scrum\s+Master(?:\s|:|–|-|$)', 'Certified Scrum Master'),
            (r'Certified\s+Scrum\s+Product\s+Owner(?:\s|:|–|-|$)', 'Certified Scrum Product Owner'),
            
            # Project Management - STRICT
            (r'Project\s+Management\s+Professional(?:\s|:|–|-|$)', 'PMP'),
            (r'(?:^|\s)PMP(?:\s|:|–|-|$)', 'PMP'),
            
            # CompTIA - STRICT (specific certs)
            (r'CompTIA\s+(?:Security\+|Network\+|A\+|Linux\+|CySA\+|PenTest\+)', 'CompTIA'),
            (r'(?:Security\+|Network\+|A\+|Linux\+|CySA\+|PenTest\+)\s+(?:Certification|Certified)', 'CompTIA'),
            
            # Oracle - STRICT (specific cert codes)
            (r'Oracle\s+(?:Certified|Certification)\s+(?:Associate|Professional)', 'Oracle Certified'),
            (r'OCA\s+(?:Java|Database)', 'Oracle Certified'),
            (r'OCP\s+(?:Java|Database)', 'Oracle Certified'),
            
            # Java - STRICT
            (r'Oracle\s+Certified\s+Associate\s+Java\s+Programmer', 'Java Certified'),
            (r'OCAJP|OCPJP', 'Java Certified'),
            
            # Cisco - STRICT
            (r'Cisco\s+(?:Certified|Certification)\s+(?:Network Associate|Network Professional)', 'Cisco Certified'),
            (r'CCNA|CCNP|CCIE', 'Cisco Certified'),
            
            # Security - STRICT
            (r'(?:CISSP|CCNA|CCNP|CEH|OSCP|GIAC|SANS)(?:\s|:|–|-|$)', 'Security Certification'),
            
            # Online Platforms - STRICT (must say "Certificate" or "Certification")
            (r'(?:Coursera|Udemy|LinkedIn Learning|edX|Pluralsight)\s+(?:Certificate|Certification)', 'Online Certificate'),
            
            # SAP, Salesforce, Tableau, Power BI - STRICT
            (r'(?:SAP|Salesforce|Tableau|Power BI)\s+(?:Certified|Certification)', 'Enterprise Certification'),
            
            # Kaggle - STRICT (only if explicitly "Certified" or "Badge")
            (r'Kaggle\s+(?:Certified|Certification|Badge)', 'Kaggle Certificate'),
        ]
        
        found_certs = set()  # Use set to avoid duplicates
        
        for pattern, cert_name in cert_patterns:
            matches = re.finditer(pattern, resume_text, re.IGNORECASE)
            for match in matches:
                # Try to extract year if available (look around the match)
                year = None
                start_pos = max(0, match.start() - 50)
                end_pos = min(len(resume_text), match.end() + 50)
                context = resume_text[start_pos:end_pos]
                
                year_match = re.search(r'(20\d{2}|19\d{2})', context)
                if year_match:
                    year = int(year_match.group(1))
                
                # Create a unique key to avoid duplicates
                cert_key = (cert_name, year)
                if cert_key not in found_certs:
                    found_certs.add(cert_key)
                    
                    # Extract issuer more intelligently
                    if 'AWS' in cert_name:
                        issuer = 'AWS'
                    elif 'Microsoft' in cert_name or 'Azure' in cert_name:
                        issuer = 'Microsoft'
                    elif 'Google' in cert_name:
                        issuer = 'Google'
                    elif 'Kubernetes' in cert_name:
                        issuer = 'Linux Foundation'
                    elif 'Docker' in cert_name:
                        issuer = 'Docker'
                    elif 'Scrum' in cert_name:
                        issuer = 'Scrum Alliance'
                    elif 'PMP' in cert_name:
                        issuer = 'PMI'
                    elif 'CompTIA' in cert_name:
                        issuer = 'CompTIA'
                    elif 'Oracle' in cert_name or 'Java' in cert_name:
                        issuer = 'Oracle'
                    elif 'Cisco' in cert_name:
                        issuer = 'Cisco'
                    elif 'Security' in cert_name:
                        issuer = 'Security'
                    elif 'Online' in cert_name:
                        issuer = 'Online Platform'
                    elif 'Enterprise' in cert_name:
                        issuer = 'Enterprise'
                    elif 'Kaggle' in cert_name:
                        issuer = 'Kaggle'
                    else:
                        issuer = cert_name.split()[0]
                    
                    certifications.append({
                        'name': cert_name,
                        'issuer': issuer,
                        'year': year,
                        'verification_id': None
                    })
        
        return certifications

    def extract_projects_heuristic(self, resume_text):
        """Extract projects from resume text"""
        projects = []
        
        # Look for project sections
        project_section_pattern = r'(?:projects?|portfolio|work samples?)\s*:?\s*\n(.*?)(?:\n\s*\n|\Z)'
        matches = re.findall(project_section_pattern, resume_text, re.IGNORECASE | re.DOTALL)
        
        if matches:
            for section in matches:
                # Split by bullet points or numbered lists
                project_items = re.split(r'\n\s*[•\-\*\d+\.]\s*', section)
                
                for item in project_items:
                    item = item.strip()
                    if len(item) > 20:  # Minimum length for a project description
                        # Extract project name (usually first line or before colon)
                        lines = item.split('\n')
                        name = lines[0].split(':')[0].strip()
                        
                        # Extract technologies mentioned
                        tech_pattern = r'\b(?:using|with|technologies?|stack|built with)\s*:?\s*([^\n\.]+)'
                        tech_match = re.search(tech_pattern, item, re.IGNORECASE)
                        technologies = []
                        if tech_match:
                            tech_text = tech_match.group(1)
                            technologies = [t.strip() for t in re.split(r'[,;]', tech_text) if t.strip()]
                        
                        projects.append({
                            'name': name[:100],  # Limit length
                            'description': item[:300],  # Limit description
                            'technologies': technologies[:10]  # Limit tech list
                        })
        
        return projects[:10]  # Limit to 10 projects

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
