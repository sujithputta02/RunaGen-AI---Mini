"""
MODEL 2: Career Trajectory Prediction
Multi-class classification to predict next career roles
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
import joblib
from pathlib import Path
from sentence_transformers import SentenceTransformer

# Role keyword mappings (must match training script exactly)
ROLE_MAPPINGS = {
    'Data Scientist': ['data scientist', 'scientist', 'data science', 'ds ', 'analytics scientist', 'applied scientist', 'ml scientist', 'data sci'],
    'Data Engineer': ['data engineer', 'etl engineer', 'pipeline engineer', 'data platform', 'big data engineer', 'analytics engineer', 'data eng', 'azure data engineer', 'aws data engineer'],
    'ML Engineer': ['machine learning', 'ml engineer', 'ai engineer', 'mle', 'mlops', 'deep learning engineer', 'ai/ml engineer', 'ml eng', 'artificial intelligence engineer'],
    'Data Analyst': ['data analyst', 'business analyst', 'analytics', 'analyst', 'bi analyst', 'business intelligence', 'reporting analyst', 'data and analytics'],
    'Full Stack Developer': ['full stack', 'fullstack', 'full-stack', 'fullstack dev', 'full-stack dev'],
    'Backend Developer': ['backend', 'back-end', 'server side', 'node.js', 'django', 'flask', 'api developer', 'java developer', 'c# developer', 'python developer', 'back end'],
    'Frontend Developer': ['frontend', 'front-end', 'ui developer', 'ui engineer', 'react developer', 'javascript developer', 'angular developer', 'vue developer', 'web developer', 'front end'],
    'DevOps Engineer': ['devops', 'sre', 'site reliability', 'platform engineer', 'infrastructure engineer', 'cloudops', 'sysops'],
    'Cloud Engineer': ['cloud engineer', 'cloud architect', 'aws engineer', 'azure engineer', 'solutions architect', 'cloud infrastructure', 'security engineer'],
    'Software Engineer': ['software engineer', 'software developer', 'sde', 'programmer', 'developer', 'application developer', 'software architect', 'qa engineer', 'automation engineer'],
    'Product Manager': ['product manager', 'product lead', 'product owner', 'pm '],
    'Business Analyst': ['business analyst', 'ba ', 'process analyst', 'systems analyst'],
    'Project Manager': ['project manager', 'project lead', 'program manager', 'pmp'],
    'Account Manager': ['account manager', 'key account', 'client manager', 'customer success'],
    'Sales Representative': ['sales representative', 'inside sales', 'outside sales', 'business development', 'sales exec', 'sales associate'],
    'Financial Analyst': ['financial analyst', 'finance analyst', 'investment analyst'],
    'Accountant': ['accountant', 'chartered accountant', 'junior accountant', 'senior accountant', 'staff accountant'],
    'Marketing Manager': ['marketing manager', 'digital marketing', 'performance marketing', 'content marketing', 'influencer marketing', 'marketing lead'],
    'HR Manager': ['hr manager', 'human resources', 'recruitment', 'talent acquisition', 'hr executive', 'hr specialist'],
    'Customer Service': ['customer service', 'customer support', 'support representative', 'help desk', 'customer care', 'voice process']
}

class CareerPredictor:
    def __init__(self):
        self.model = None
        self.label_encoder = LabelEncoder()
        self.sbert_model = None
        self.feature_cols = None
        self.model_path = Path("models")
        self.model_path.mkdir(exist_ok=True)
        # Avoid loading SBERT here, load it when required or in load_model
    
    def prepare_inference_features(self, skills_list, raw_text="", feature_cols=None):
        """
        Prepare features for inference using BERT embeddings and match scores
        """
        skills_str = ' '.join([s.lower() for s in skills_list])
        combined_text = (skills_str + " " + raw_text.lower()).strip()
        
        # 1. BERT Embedding (with network-safe fallback)
        X_semantic = None
        if self.sbert_model is not None:
            try:
                X_semantic = self.sbert_model.encode([skills_str])
            except Exception as e:
                print(f"⚠️  SBERT Encoding error: {e}. Using meta-features only.")
        
        if X_semantic is None:
            # Fallback to zero embeddings (384 dims for all-MiniLM-L6-v2)
            X_semantic = np.zeros((1, 384))
        
        # 2. Meta-features
        data_keywords = ['data', 'sql', 'analysis', 'statistics', 'ml', 'pandas', 'tableau']
        dev_keywords = ['software', 'developer', 'web', 'javascript', 'frontend', 'backend', 'api']
        mgmt_keywords = ['product', 'project', 'management', 'agile', 'scrum', 'roadmap', 'strategy']
        sales_keywords = ['sales', 'crm', 'client', 'relationship', 'negotiation', 'marketing', 'branding']
        finance_keywords = ['finance', 'accounting', 'audit', 'tax', 'excel', 'financial']
        hr_keywords = ['hr', 'recruitment', 'talent', 'human resources', 'payroll', 'onboarding']
        
        data_count = sum(1 for k in data_keywords if k in combined_text)
        dev_count = sum(1 for k in dev_keywords if k in combined_text)
        mgmt_count = sum(1 for k in mgmt_keywords if k in combined_text)
        sales_count = sum(1 for k in sales_keywords if k in combined_text)
        finance_count = sum(1 for k in finance_keywords if k in combined_text)
        hr_count = sum(1 for k in hr_keywords if k in combined_text)
        
        meta = {
            'skill_count': len(skills_list),
            'data_focus': data_count / (len(skills_list) + 1),
            'dev_focus': dev_count / (len(skills_list) + 1),
            'mgmt_focus': mgmt_count / (len(skills_list) + 1),
            'sales_focus': sales_count / (len(skills_list) + 1),
            'finance_focus': finance_count / (len(skills_list) + 1),
            'hr_focus': hr_count / (len(skills_list) + 1),
            'has_python': int('python' in combined_text),
            'has_sql': int('sql' in combined_text or 'mysql' in combined_text or 'postgresql' in combined_text),
            'skill_diversity': 5 # Default
        }
        
        # 3. Role-specific match features
        for r_name, r_keywords in ROLE_MAPPINGS.items():
            match_count = sum(1 for kw in r_keywords if kw in combined_text)
            meta[f'match_{r_name.replace(" ", "_")}'] = match_count / (len(skills_list) + 1)
        
        # Use feature_cols from the model if available
        current_cols = self.feature_cols if self.feature_cols else [k for k in meta.keys()]
        X_meta = np.array([[meta[col] for col in current_cols]])
        
        return np.hstack([X_semantic, X_meta])
    
    def train(self, X, y, model_type='random_forest'):
        """Train career prediction model"""
        # Encode target labels
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        # Select model
        if model_type == 'logistic':
            self.model = LogisticRegression(max_iter=1000, random_state=42)
        elif model_type == 'random_forest':
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        elif model_type == 'gradient_boosting':
            self.model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        elif model_type == 'xgboost':
            self.model = xgb.XGBClassifier(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=8,
                min_child_weight=1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                eval_metric='mlogloss'
            )
        
        # Train
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X, y_encoded, cv=5)
        
        print(f"Model: {model_type}")
        print(f"Accuracy: {accuracy:.4f}")
        print(f"CV Score: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, 
                                   target_names=self.label_encoder.classes_))
        
        # Feature importance (for tree-based models)
        if hasattr(self.model, 'feature_importances_'):
            print("\nTop 5 Feature Importances:")
            feature_names = X.columns if hasattr(X, 'columns') else [f'feature_{i}' for i in range(X.shape[1])]
            importances = pd.DataFrame({
                'feature': feature_names,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            for _, row in importances.head(5).iterrows():
                print(f"  {row['feature']}: {row['importance']:.4f}")
        
        return {
            'accuracy': accuracy,
            'cv_score': cv_scores.mean(),
            'model': model_type
        }
    
    def compare_models(self, X, y):
        """Compare Random Forest vs XGBoost performance"""
        print("\n" + "="*60)
        print("COMPARING MODELS: Random Forest vs XGBoost")
        print("="*60)
        
        results = {}
        
        # Train Random Forest
        print("\n1. Training Random Forest...")
        results['random_forest'] = self.train(X, y, model_type='random_forest')
        rf_model = self.model
        
        # Train XGBoost
        print("\n2. Training XGBoost...")
        results['xgboost'] = self.train(X, y, model_type='xgboost')
        xgb_model = self.model
        
        # Compare results
        print("\n" + "="*60)
        print("COMPARISON RESULTS")
        print("="*60)
        print(f"\nRandom Forest:")
        print(f"  Accuracy: {results['random_forest']['accuracy']:.4f}")
        print(f"  CV Score: {results['random_forest']['cv_score']:.4f}")
        
        print(f"\nXGBoost:")
        print(f"  Accuracy: {results['xgboost']['accuracy']:.4f}")
        print(f"  CV Score: {results['xgboost']['cv_score']:.4f}")
        
        # Select best model
        if results['xgboost']['cv_score'] > results['random_forest']['cv_score']:
            print(f"\n✓ Winner: XGBoost (CV Score: {results['xgboost']['cv_score']:.4f})")
            self.model = xgb_model
            best_model = 'xgboost'
        else:
            print(f"\n✓ Winner: Random Forest (CV Score: {results['random_forest']['cv_score']:.4f})")
            self.model = rf_model
            best_model = 'random_forest'
        
        return results, best_model
    def predict(self, X):
        """Simple prediction method"""
        y_pred_encoded = self.model.predict(X)
        return self.label_encoder.inverse_transform(y_pred_encoded)
    
    def compare_models(self, X, y):
        """Compare Random Forest vs XGBoost performance"""
        print("\n" + "="*60)
        print("COMPARING MODELS: Random Forest vs XGBoost")
        print("="*60)
        
        results = {}
        
        # Train Random Forest
        print("\n1. Training Random Forest...")
        results['random_forest'] = self.train(X, y, model_type='random_forest')
        rf_model = self.model
        
        # Train XGBoost
        print("\n2. Training XGBoost...")
        results['xgboost'] = self.train(X, y, model_type='xgboost')
        xgb_model = self.model
        
        # Compare results
        print("\n" + "="*60)
        print("COMPARISON RESULTS")
        print("="*60)
        print(f"\nRandom Forest:")
        print(f"  Accuracy: {results['random_forest']['accuracy']:.4f}")
        print(f"  CV Score: {results['random_forest']['cv_score']:.4f}")
        
        print(f"\nXGBoost:")
        print(f"  Accuracy: {results['xgboost']['accuracy']:.4f}")
        print(f"  CV Score: {results['xgboost']['cv_score']:.4f}")
        
        # Select best model
        if results['xgboost']['cv_score'] > results['random_forest']['cv_score']:
            print(f"\n✓ Winner: XGBoost (CV Score: {results['xgboost']['cv_score']:.4f})")
            self.model = xgb_model
            best_model = 'xgboost'
        else:
            print(f"\n✓ Winner: Random Forest (CV Score: {results['random_forest']['cv_score']:.4f})")
            self.model = rf_model
            best_model = 'random_forest'
        
        return results, best_model
    
    def predict_top_k(self, X, k=3):
        """Predict top-k most probable career roles"""
        probabilities = self.model.predict_proba(X)
        top_k_indices = np.argsort(probabilities, axis=1)[:, -k:][:, ::-1]
        
        results = []
        for i, indices in enumerate(top_k_indices):
            predictions = []
            for idx in indices:
                role = self.label_encoder.inverse_transform([idx])[0]
                prob = probabilities[i][idx]
                predictions.append({'role': role, 'probability': prob})
            results.append(predictions)
        
        return results
    
    def save_model(self, filename='career_predictor.pkl'):
        """Save trained model"""
        filepath = self.model_path / filename
        joblib.dump({
            'model': self.model,
            'label_encoder': self.label_encoder,
            'tfidf_vectorizer': self.tfidf_vectorizer,
            'feature_cols': self.feature_cols
        }, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filename='career_predictor.pkl'):
        """Load trained model"""
        filepath = self.model_path / filename
        data = joblib.load(filepath)
        self.model = data['model']
        self.label_encoder = data['label_encoder']
        self.tfidf_vectorizer = data.get('tfidf_vectorizer')
        self.feature_cols = data.get('feature_cols')
        print(f"Model loaded from {filepath}")
        
        # Try to pre-load SBERT
        try:
            print("⏳ Pre-loading SBERT model for career prediction...")
            self.sbert_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✓ SBERT model ready")
        except Exception as e:
            print(f"⚠️  Could not pre-load SBERT: {e}. Will use legacy matching if network remains unstable.")
            self.sbert_model = None

if __name__ == "__main__":
    # Example usage with mock data
    predictor = CareerPredictor()
    
    # Mock training data
    np.random.seed(42)
    n_samples = 1000
    X = pd.DataFrame({
        'skill_overlap_score': np.random.rand(n_samples),
        'jaccard_similarity': np.random.rand(n_samples),
        'demand_growth_rate': np.random.rand(n_samples),
        'salary_difference': np.random.randint(-20000, 50000, n_samples),
        'experience_match': np.random.rand(n_samples)
    })
    y = np.random.choice(['Data Scientist', 'ML Engineer', 'Data Engineer'], n_samples)
    
    # Train model
    predictor.train(X, y, model_type='random_forest')
    
    # Save model
    predictor.save_model()
