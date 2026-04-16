"""
MODEL 4: Salary Prediction
Regression model to predict salary based on role, skills, experience
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import joblib
from pathlib import Path
import numpy as np
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

class SalaryPredictor:
    def __init__(self):
        self.model = None
        self.location_encoder = None
        self.sbert_model = None
        self.feature_cols = None
        self.log_target = False
        self.model_path = Path("models")
        self.model_path.mkdir(exist_ok=True)
    
    def prepare_inference_features(self, skills_list, experience=0, location="Unknown", raw_text=""):
        """
        Prepare high-dimensional features for salary inference
        """
        skills_str = ' '.join([s.lower() for s in skills_list])
        combined_text = (skills_str + " " + raw_text.lower()).strip()
        
        # 1. BERT Embedding (with network-safe fallback)
        X_semantic = None
        if self.sbert_model is not None:
            try:
                X_semantic = self.sbert_model.encode([skills_str])
            except Exception as e:
                print(f"⚠️  SBERT Encoding error (Salary): {e}. Using meta-features only.")
        
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
            'experience_years': experience,
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
        
        # 4. Combine in specific order
        # Ensure we use feature_cols from training if available
        current_cols = self.feature_cols if self.feature_cols else [k for k in meta.keys()]
        X_meta_vals = np.array([[meta[col] for col in current_cols]])
        
        # 5. Location encoding
        try:
            loc_idx = self.location_encoder.transform([location])[0]
        except:
            loc_idx = 0 # Default to unknown
            
        X_combined = np.hstack([X_semantic, X_meta_vals, [[loc_idx]]])
        return X_combined
    
    def train(self, X, y, model_type='random_forest'):
        """Train salary prediction model"""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Select model
        if model_type == 'linear':
            self.model = LinearRegression()
        elif model_type == 'random_forest':
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        elif model_type == 'gradient_boosting':
            self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        elif model_type == 'xgboost':
            self.model = xgb.XGBRegressor(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=8,
                min_child_weight=1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42
            )
        
        # Train
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        print(f"Model: {model_type}")
        print(f"MAE: ₹{mae:,.2f}")
        print(f"RMSE: ₹{rmse:,.2f}")
        print(f"R² Score: {r2:.4f}")
        
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
        
        return {'mae': mae, 'rmse': rmse, 'r2': r2}
    
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
        rf_scaler = self.scaler
        
        # Train XGBoost
        print("\n2. Training XGBoost...")
        results['xgboost'] = self.train(X, y, model_type='xgboost')
        xgb_model = self.model
        xgb_scaler = self.scaler
        
        # Compare results
        print("\n" + "="*60)
        print("COMPARISON RESULTS")
        print("="*60)
        print(f"\nRandom Forest:")
        print(f"  MAE: ${results['random_forest']['mae']:,.2f}")
        print(f"  RMSE: ${results['random_forest']['rmse']:,.2f}")
        print(f"  R² Score: {results['random_forest']['r2']:.4f}")
        
        print(f"\nXGBoost:")
        print(f"  MAE: ${results['xgboost']['mae']:,.2f}")
        print(f"  RMSE: ${results['xgboost']['rmse']:,.2f}")
        print(f"  R² Score: {results['xgboost']['r2']:.4f}")
        
        # Select best model (higher R² is better)
        if results['xgboost']['r2'] > results['random_forest']['r2']:
            print(f"\n✓ Winner: XGBoost (R² Score: {results['xgboost']['r2']:.4f})")
            self.model = xgb_model
            self.scaler = xgb_scaler
            best_model = 'xgboost'
        else:
            print(f"\n✓ Winner: Random Forest (R² Score: {results['random_forest']['r2']:.4f})")
            self.model = rf_model
            self.scaler = rf_scaler
            best_model = 'random_forest'
        
        return results, best_model
    def predict(self, X):
        """High-precision prediction with Log-Inversion"""
        pred_log = self.model.predict(X)
        if self.log_target:
            return np.expm1(pred_log)
        return pred_log
    
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
        rf_scaler = self.scaler
        
        # Train XGBoost
        print("\n2. Training XGBoost...")
        results['xgboost'] = self.train(X, y, model_type='xgboost')
        xgb_model = self.model
        xgb_scaler = self.scaler
        
        # Compare results
        print("\n" + "="*60)
        print("COMPARISON RESULTS")
        print("="*60)
        print(f"\nRandom Forest:")
        print(f"  MAE: ${results['random_forest']['mae']:,.2f}")
        print(f"  RMSE: ${results['random_forest']['rmse']:,.2f}")
        print(f"  R² Score: {results['random_forest']['r2']:.4f}")
        
        print(f"\nXGBoost:")
        print(f"  MAE: ${results['xgboost']['mae']:,.2f}")
        print(f"  RMSE: ${results['xgboost']['rmse']:,.2f}")
        print(f"  R² Score: {results['xgboost']['r2']:.4f}")
        
        # Select best model (higher R² is better)
        if results['xgboost']['r2'] > results['random_forest']['r2']:
            print(f"\n✓ Winner: XGBoost (R² Score: {results['xgboost']['r2']:.4f})")
            self.model = xgb_model
            self.scaler = xgb_scaler
            best_model = 'xgboost'
        else:
            print(f"\n✓ Winner: Random Forest (R² Score: {results['random_forest']['r2']:.4f})")
            self.model = rf_model
            self.scaler = rf_scaler
            best_model = 'random_forest'
        
        return results, best_model
    
    def predict_salary_range(self, X, confidence=0.1):
        """Predict salary with confidence interval"""
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        
        # Calculate range (simplified)
        margin = predictions * confidence
        
        results = []
        for pred, marg in zip(predictions, margin):
            results.append({
                'predicted_salary': pred,
                'min_salary': pred - marg,
                'max_salary': pred + marg
            })
        
        return results
    
    def save_model(self, filename='salary_predictor.pkl'):
        """Save trained model"""
        filepath = self.model_path / filename
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler
        }, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filename='salary_predictor.pkl'):
        """Load high-precision trained model"""
        filepath = self.model_path / filename
        data = joblib.load(filepath)
        self.model = data['model']
        self.location_encoder = data.get('location_encoder')
        self.feature_cols = data.get('feature_cols')
        self.log_target = data.get('log_target', True)
        print(f"✓ High-precision Salary Model loaded from {filepath}")
        
        # Try to pre-load SBERT
        try:
            print("⏳ Pre-loading SBERT model for salary prediction...")
            self.sbert_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✓ SBERT model ready")
        except Exception as e:
            print(f"⚠️  Could not pre-load SBERT (Salary): {e}. Will use meta-features only.")
            self.sbert_model = None

if __name__ == "__main__":
    predictor = SalaryPredictor()
    
    # Mock data
    np.random.seed(42)
    n_samples = 1000
    X = pd.DataFrame({
        'role_encoded': np.random.randint(0, 5, n_samples),
        'skill_count': np.random.randint(3, 15, n_samples),
        'experience_years': np.random.randint(0, 20, n_samples),
        'location_encoded': np.random.randint(0, 10, n_samples),
        'market_demand_score': np.random.rand(n_samples)
    })
    y = 50000 + X['experience_years'] * 5000 + X['skill_count'] * 2000 + np.random.normal(0, 10000, n_samples)
    
    # Train
    predictor.train(X, y, model_type='random_forest')
    predictor.save_model()
