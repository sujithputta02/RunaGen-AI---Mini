"""
Advanced Text Preprocessing Pipeline
Comprehensive text cleaning and feature extraction
"""
import re
import spacy
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.models import Word2Vec
import warnings
warnings.filterwarnings('ignore')

class AdvancedTextPreprocessor:
    def __init__(self):
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except:
            print("⚠️  Spacy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        self.tfidf = TfidfVectorizer(max_features=100, stop_words='english')
        self.word2vec_model = None
    
    def remove_urls(self, text: str) -> str:
        """Remove URLs from text"""
        return re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    def remove_emails(self, text: str) -> str:
        """Remove email addresses"""
        return re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
    
    def remove_phone_numbers(self, text: str) -> str:
        """Remove phone numbers"""
        return re.sub(r'\+?[\d\s\-\(\)]{10,}', '', text)
    
    def remove_special_chars(self, text: str) -> str:
        """Remove special characters but keep important punctuation"""
        # Keep periods, commas, hyphens for sentence structure
        text = re.sub(r'[^\w\s\.\,\-]', ' ', text)
        return text
    
    def standardize_dates(self, text: str) -> str:
        """Standardize date formats"""
        # Convert various date formats to YYYY-MM
        patterns = [
            (r'(\d{1,2})/(\d{1,2})/(\d{4})', r'\3-\1'),  # MM/DD/YYYY -> YYYY-MM
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', r'\1-\2'),  # YYYY-MM-DD -> YYYY-MM
            (r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})', r'\2-\1'),  # Month YYYY
        ]
        
        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def standardize_education(self, text: str) -> str:
        """Standardize education degree names"""
        education_map = {
            r'\b(phd|ph\.d|doctorate|doctoral)\b': 'PhD',
            r'\b(master|masters|msc|m\.sc|ms|m\.s|mba|m\.b\.a)\b': 'Masters',
            r'\b(bachelor|bachelors|bsc|b\.sc|bs|b\.s|btech|b\.tech|be|b\.e)\b': 'Bachelors',
            r'\b(diploma|associate)\b': 'Diploma',
        }
        
        for pattern, replacement in education_map.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def standardize_job_titles(self, text: str) -> str:
        """Standardize common job title variations"""
        title_map = {
            r'\b(sr|senior)\s+(engineer|developer|analyst)\b': r'Senior \2',
            r'\b(jr|junior)\s+(engineer|developer|analyst)\b': r'Junior \2',
            r'\b(full\s*stack|fullstack)\b': 'Full Stack',
            r'\b(front\s*end|frontend)\b': 'Frontend',
            r'\b(back\s*end|backend)\b': 'Backend',
            r'\b(dev\s*ops|devops)\b': 'DevOps',
            r'\b(ml|machine\s*learning)\s*(engineer|developer)\b': 'ML Engineer',
        }
        
        for pattern, replacement in title_map.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def remove_extra_whitespace(self, text: str) -> str:
        """Remove extra whitespace"""
        return re.sub(r'\s+', ' ', text).strip()
    
    def clean_resume_text(self, text: str) -> str:
        """Complete text cleaning pipeline"""
        if not text:
            return ""
        
        # Step 1: Remove noise
        text = self.remove_urls(text)
        text = self.remove_emails(text)
        text = self.remove_phone_numbers(text)
        text = self.remove_special_chars(text)
        
        # Step 2: Standardize
        text = self.standardize_dates(text)
        text = self.standardize_education(text)
        text = self.standardize_job_titles(text)
        
        # Step 3: Normalize
        text = text.lower()
        text = self.remove_extra_whitespace(text)
        
        return text
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities using spaCy"""
        if not self.nlp:
            return {}
        
        doc = self.nlp(text)
        
        entities = {
            'organizations': [],
            'locations': [],
            'dates': [],
            'skills': [],
            'technologies': []
        }
        
        for ent in doc.ents:
            if ent.label_ == 'ORG':
                entities['organizations'].append(ent.text)
            elif ent.label_ in ['GPE', 'LOC']:
                entities['locations'].append(ent.text)
            elif ent.label_ == 'DATE':
                entities['dates'].append(ent.text)
            elif ent.label_ in ['PRODUCT', 'WORK_OF_ART']:
                entities['technologies'].append(ent.text)
        
        return entities
    
    def get_pos_distribution(self, text: str) -> Dict[str, float]:
        """Get part-of-speech tag distribution"""
        if not self.nlp:
            return {}
        
        doc = self.nlp(text)
        
        pos_counts = {}
        total = len(doc)
        
        for token in doc:
            pos_counts[token.pos_] = pos_counts.get(token.pos_, 0) + 1
        
        # Convert to percentages
        pos_distribution = {
            pos: (count / total) * 100
            for pos, count in pos_counts.items()
        }
        
        return pos_distribution
    
    def get_tfidf_features(self, texts: List[str], max_features: int = 100) -> np.ndarray:
        """Extract TF-IDF features"""
        try:
            tfidf_matrix = self.tfidf.fit_transform(texts)
            return tfidf_matrix.toarray()
        except:
            return np.zeros((len(texts), max_features))
    
    def train_word2vec(self, texts: List[str], vector_size: int = 100):
        """Train Word2Vec model on corpus"""
        # Tokenize texts
        tokenized_texts = [text.split() for text in texts]
        
        # Train Word2Vec
        self.word2vec_model = Word2Vec(
            sentences=tokenized_texts,
            vector_size=vector_size,
            window=5,
            min_count=2,
            workers=4,
            epochs=10
        )
        
        return self.word2vec_model
    
    def get_word2vec_embeddings(self, text: str) -> np.ndarray:
        """Get Word2Vec embeddings for text"""
        if not self.word2vec_model:
            return np.zeros(100)
        
        words = text.split()
        word_vectors = []
        
        for word in words:
            try:
                word_vectors.append(self.word2vec_model.wv[word])
            except KeyError:
                continue
        
        if not word_vectors:
            return np.zeros(self.word2vec_model.vector_size)
        
        # Average word vectors
        return np.mean(word_vectors, axis=0)
    
    def extract_skill_ngrams(self, text: str, n: int = 3) -> List[str]:
        """Extract n-grams that might be skills"""
        words = text.split()
        ngrams = []
        
        for i in range(len(words) - n + 1):
            ngram = ' '.join(words[i:i+n])
            # Filter for potential skills (contains tech keywords)
            if any(keyword in ngram for keyword in ['python', 'java', 'sql', 'aws', 'docker', 'react', 'node']):
                ngrams.append(ngram)
        
        return ngrams
    
    def extract_all_features(self, text: str) -> Dict:
        """Extract all features from text"""
        cleaned_text = self.clean_resume_text(text)
        
        features = {
            'cleaned_text': cleaned_text,
            'text_length': len(cleaned_text),
            'word_count': len(cleaned_text.split()),
            'sentence_count': len(re.split(r'[.!?]+', cleaned_text)),
            'avg_word_length': np.mean([len(word) for word in cleaned_text.split()]) if cleaned_text else 0,
            'entities': self.extract_entities(text),
            'pos_distribution': self.get_pos_distribution(cleaned_text),
            'skill_ngrams': self.extract_skill_ngrams(cleaned_text)
        }
        
        return features
    
    def process_batch(self, texts: List[str]) -> pd.DataFrame:
        """Process a batch of texts"""
        results = []
        
        for text in texts:
            features = self.extract_all_features(text)
            results.append(features)
        
        return pd.DataFrame(results)


if __name__ == "__main__":
    # Test the preprocessor
    preprocessor = AdvancedTextPreprocessor()
    
    sample_text = """
    John Doe
    john.doe@email.com | +1-234-567-8900
    
    EDUCATION
    Master of Science in Computer Science - Stanford University (2020)
    Bachelor of Technology in Software Engineering - MIT (2018)
    
    EXPERIENCE
    Senior Full Stack Developer at Google (2020-Present)
    - Developed microservices using Python, Django, and React
    - Implemented CI/CD pipelines with Docker and Kubernetes
    - Led team of 5 developers
    
    Junior Software Engineer at Microsoft (2018-2020)
    - Built REST APIs with Node.js and Express
    - Worked with PostgreSQL and MongoDB databases
    
    SKILLS
    Python, JavaScript, React, Node.js, Docker, Kubernetes, AWS, SQL
    """
    
    print("Original text length:", len(sample_text))
    print("\n" + "="*70)
    
    cleaned = preprocessor.clean_resume_text(sample_text)
    print("\nCleaned text:")
    print(cleaned[:200] + "...")
    
    print("\n" + "="*70)
    features = preprocessor.extract_all_features(sample_text)
    
    print("\nExtracted Features:")
    print(f"- Text length: {features['text_length']}")
    print(f"- Word count: {features['word_count']}")
    print(f"- Sentence count: {features['sentence_count']}")
    print(f"- Avg word length: {features['avg_word_length']:.2f}")
    print(f"\nEntities found:")
    for entity_type, entities in features['entities'].items():
        if entities:
            print(f"  - {entity_type}: {entities[:3]}")
    
    print("\n✅ Preprocessing test complete!")
