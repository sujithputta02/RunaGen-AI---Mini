"""
Advanced ML Model Training Pipeline - 90%+ Accuracy Target
Uses ensemble methods, advanced feature engineering, and aggressive optimization
"""
import os
import sys
from dotenv import load_dotenv
import logging
from datetime import datetime
import json
import warnings
warnings.filterwarnings('ignore')

load_dotenv()

import pandas as pd
import numpy as np
from google.cloud import bigquery
from google.oauth2 import service_account
import joblib

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder, PolynomialFeatures
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import (
    RandomForestClassifier, GradientBoostingClassifier, 
    VotingClassifier, StackingClassifier, AdaBoostClassifier,
    RandomForestRegressor, GradientBoostingRegressor, VotingRegressor
)
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier, XGBRegressor
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, r2_score, mean_absolute_error,
    confusion_matrix, classification_report, roc_auc_score
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedMLTrainer:
    """Advanced ML trainer with 90%+ accuracy target"""
    
    def __init__(self):
        """Initialize BigQuery client"""
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
        self.dataset_silver = 'runagen_silver_silver'
        self.models = {}
        self.scalers = {}
        self.encoders = {}
    
    def fetch_jobs_data(self) -> pd.DataFrame:
        """Fetch cleaned jobs data from BigQuery"""
        logger.info("📥 Fetching jobs data from BigQuery...")
        
        query = f"""
        SELECT
            job_id,
            title_clean,
            company,
            location_standardized,
            description_clean,
            requirements,
            salary_min_usd,
            salary_max_usd,
            employment_type_standardized,
            experience_level_standardized,
            missing_salary,
            short_description
        FROM `{self.project_id}.{self.dataset_silver}.jobs_cleaned`
        WHERE NOT missing_salary
            AND NOT short_description
            AND salary_min_usd > 0
            AND salary_max_usd > 0
        LIMIT 15000
        """
        
        query_job = self.bq_client.query(query)
        rows = query_job.result()
        data = [dict(row) for row in rows]
        df = pd.DataFrame(data)
        
        logger.info(f"✅ Fetched {len(df)} jobs records")
        return df
    
    def fetch_skills_data(self) -> pd.DataFrame:
        """Fetch skills data from BigQuery"""
        logger.info("📥 Fetching skills data from BigQuery...")
        
        query = f"""
        SELECT skill_name FROM `{self.project_id}.{self.dataset_silver}.skills_standardized`
        """
        
        query_job = self.bq_client.query(query)
        rows = query_job.result()
        data = [dict(row) for row in rows]
        df = pd.DataFrame(data)
        
        logger.info(f"✅ Fetched {len(df)} skills records")
        return df
    
    def engineer_advanced_features(self, jobs_df: pd.DataFrame, skills_df: pd.DataFrame) -> pd.DataFrame:
        """Engineer 50+ advanced features"""
        logger.info("🔧 Engineering 50+ advanced features...")
        
        features_df = jobs_df.copy()
        
        # ===== TEXT FEATURES =====
        features_df['title_length'] = features_df['title_clean'].str.len()
        features_df['title_word_count'] = features_df['title_clean'].str.split().str.len()
        features_df['description_length'] = features_df['description_clean'].str.len()
        features_df['description_word_count'] = features_df['description_clean'].str.split().str.len()
        features_df['requirements_length'] = features_df['requirements'].fillna('').str.len()
        features_df['requirements_word_count'] = features_df['requirements'].fillna('').str.split().str.len()
        
        # Text complexity
        features_df['title_avg_word_length'] = features_df['title_clean'].apply(
            lambda x: np.mean([len(w) for w in str(x).split()]) if len(str(x).split()) > 0 else 0
        )
        features_df['description_avg_word_length'] = features_df['description_clean'].apply(
            lambda x: np.mean([len(w) for w in str(x).split()]) if len(str(x).split()) > 0 else 0
        )
        
        # ===== SALARY FEATURES =====
        features_df['salary_range'] = features_df['salary_max_usd'] - features_df['salary_min_usd']
        features_df['salary_midpoint'] = (features_df['salary_min_usd'] + features_df['salary_max_usd']) / 2
        features_df['salary_ratio'] = features_df['salary_max_usd'] / (features_df['salary_min_usd'] + 1)
        features_df['salary_log_min'] = np.log1p(features_df['salary_min_usd'])
        features_df['salary_log_max'] = np.log1p(features_df['salary_max_usd'])
        features_df['salary_log_mid'] = np.log1p(features_df['salary_midpoint'])
        
        # Salary percentiles
        salary_percentiles = features_df['salary_midpoint'].quantile([0.25, 0.5, 0.75])
        features_df['salary_percentile'] = pd.cut(
            features_df['salary_midpoint'], 
            bins=[0, salary_percentiles[0.25], salary_percentiles[0.5], salary_percentiles[0.75], np.inf],
            labels=[1, 2, 3, 4]
        ).astype(int)
        
        # ===== LOCATION FEATURES =====
        features_df['is_remote'] = features_df['location_standardized'].str.lower().str.contains('remote', na=False).astype(int)
        features_df['is_india'] = features_df['location_standardized'].str.lower().str.contains('india', na=False).astype(int)
        features_df['is_usa'] = features_df['location_standardized'].str.lower().str.contains('usa|united states', na=False).astype(int)
        features_df['is_uk'] = features_df['location_standardized'].str.lower().str.contains('uk|united kingdom', na=False).astype(int)
        features_df['location_length'] = features_df['location_standardized'].str.len()
        
        # ===== EXPERIENCE & EMPLOYMENT =====
        exp_mapping = {'Entry': 1, 'Mid': 2, 'Senior': 3, 'Lead': 4, 'Not Specified': 0}
        features_df['experience_level_encoded'] = features_df['experience_level_standardized'].map(exp_mapping).fillna(0)
        
        emp_mapping = {'Full-time': 1, 'Part-time': 0.5, 'Contract': 0.75, 'Internship': 0.25, 'Other': 0}
        features_df['employment_type_encoded'] = features_df['employment_type_standardized'].map(emp_mapping).fillna(0)
        
        # ===== SKILL FEATURES =====
        skill_list = skills_df['skill_name'].str.lower().tolist()
        
        features_df['skill_count'] = 0
        features_df['skill_density'] = 0.0
        
        for idx, row in features_df.iterrows():
            text = (str(row['description_clean']) + ' ' + str(row['requirements'])).lower()
            skill_count = sum(1 for skill in skill_list if skill in text)
            features_df.at[idx, 'skill_count'] = skill_count
            features_df.at[idx, 'skill_density'] = skill_count / (len(text.split()) + 1)
        
        # ===== KEYWORD FEATURES =====
        keywords = {
            'python': ['python'],
            'java': ['java'],
            'javascript': ['javascript', 'js', 'node'],
            'sql': ['sql', 'database'],
            'cloud': ['aws', 'gcp', 'azure', 'cloud'],
            'ml': ['machine learning', 'ml', 'ai', 'deep learning'],
            'devops': ['devops', 'kubernetes', 'docker'],
            'frontend': ['react', 'angular', 'vue', 'frontend'],
            'backend': ['backend', 'api', 'rest'],
            'data': ['data', 'analytics', 'bi'],
            'leadership': ['lead', 'manager', 'director', 'principal'],
            'startup': ['startup', 'scale-up'],
            'enterprise': ['enterprise', 'fortune', 'large'],
        }
        
        for keyword, terms in keywords.items():
            features_df[f'has_{keyword}'] = 0
            for idx, row in features_df.iterrows():
                text = (str(row['title_clean']) + ' ' + str(row['description_clean'])).lower()
                if any(term in text for term in terms):
                    features_df.at[idx, f'has_{keyword}'] = 1
        
        # ===== INTERACTION FEATURES =====
        features_df['senior_high_salary'] = (features_df['experience_level_encoded'] >= 3).astype(int) * (features_df['salary_percentile'] >= 3).astype(int)
        features_df['remote_tech_role'] = features_df['is_remote'] * (features_df['has_python'] + features_df['has_java'] + features_df['has_javascript'])
        features_df['startup_ml'] = features_df['has_startup'] * features_df['has_ml']
        
        logger.info(f"✅ Engineered {len(features_df.columns)} total features")
        return features_df
    
    def prepare_career_data(self, features_df: pd.DataFrame) -> tuple:
        """Prepare data for career prediction"""
        logger.info("📊 Preparing career prediction data...")
        
        # Define career categories with better mapping
        career_keywords = {
            'Data Scientist': ['data scientist', 'ml engineer', 'machine learning engineer', 'ai engineer'],
            'Data Engineer': ['data engineer', 'etl engineer', 'pipeline engineer', 'big data'],
            'Backend Developer': ['backend developer', 'backend engineer', 'server-side', 'api developer'],
            'Frontend Developer': ['frontend developer', 'frontend engineer', 'ui developer', 'ux engineer'],
            'Full Stack Developer': ['full stack', 'full-stack', 'fullstack'],
            'DevOps Engineer': ['devops', 'devops engineer', 'sre', 'infrastructure'],
            'Cloud Architect': ['cloud architect', 'solutions architect', 'aws architect', 'gcp architect'],
            'Software Engineer': ['software engineer', 'engineer', 'developer']
        }
        
        def classify_career(title):
            title_lower = str(title).lower()
            for career, keywords in career_keywords.items():
                if any(kw in title_lower for kw in keywords):
                    return career
            return 'Software Engineer'  # Default
        
        features_df['career_category'] = features_df['title_clean'].apply(classify_career)
        
        # Select all engineered features
        feature_cols = [col for col in features_df.columns 
                       if col not in ['job_id', 'title_clean', 'company', 'location_standardized',
                                     'description_clean', 'requirements', 'employment_type_standardized',
                                     'experience_level_standardized', 'missing_salary', 'short_description',
                                     'career_category']]
        
        X = features_df[feature_cols].fillna(0)
        y = features_df['career_category']
        
        logger.info(f"✅ Career classes: {y.unique()}")
        logger.info(f"✅ Feature matrix shape: {X.shape}")
        
        return X, y, feature_cols
    
    def train_ensemble_career_model(self, X: pd.DataFrame, y: pd.Series) -> dict:
        """Train ensemble career model with 90%+ accuracy"""
        logger.info("\n🚀 Training Ensemble Career Model (90%+ Target)...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.15, random_state=42, stratify=y
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Encode labels
        le = LabelEncoder()
        y_train_encoded = le.fit_transform(y_train)
        y_test_encoded = le.transform(y_test)
        
        # ===== BASE MODELS =====
        logger.info("  Training base models...")
        
        # XGBoost
        xgb_model = XGBClassifier(
            n_estimators=300,
            max_depth=10,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=42,
            n_jobs=-1,
            eval_metric='mlogloss',
            verbosity=0
        )
        
        # Gradient Boosting
        gb_model = GradientBoostingClassifier(
            n_estimators=300,
            max_depth=10,
            learning_rate=0.05,
            subsample=0.9,
            random_state=42
        )
        
        # Random Forest
        rf_model = RandomForestClassifier(
            n_estimators=300,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        # AdaBoost
        ada_model = AdaBoostClassifier(
            n_estimators=300,
            learning_rate=0.05,
            random_state=42
        )
        
        # ===== VOTING ENSEMBLE =====
        logger.info("  Creating voting ensemble...")
        
        voting_model = VotingClassifier(
            estimators=[
                ('xgb', xgb_model),
                ('gb', gb_model),
                ('rf', rf_model),
                ('ada', ada_model)
            ],
            voting='soft',
            n_jobs=-1
        )
        
        voting_model.fit(X_train_scaled, y_train_encoded)
        
        # Predictions
        y_pred = voting_model.predict(X_test_scaled)
        y_pred_proba = voting_model.predict_proba(X_test_scaled)
        
        # Metrics
        accuracy = accuracy_score(y_test_encoded, y_pred)
        precision = precision_score(y_test_encoded, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test_encoded, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test_encoded, y_pred, average='weighted', zero_division=0)
        
        # Cross-validation
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(voting_model, X_train_scaled, y_train_encoded, cv=cv, scoring='accuracy')
        
        logger.info(f"✅ Ensemble Career Model Performance:")
        logger.info(f"   - Test Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
        logger.info(f"   - Precision: {precision:.4f}")
        logger.info(f"   - Recall: {recall:.4f}")
        logger.info(f"   - F1-Score: {f1:.4f}")
        logger.info(f"   - CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        self.models['career'] = voting_model
        self.scalers['career'] = scaler
        self.encoders['career'] = le
        
        return {
            'model': voting_model,
            'scaler': scaler,
            'encoder': le,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std()
        }
    
    def train_ensemble_salary_model(self, X: pd.DataFrame, y: pd.Series) -> dict:
        """Train ensemble salary model"""
        logger.info("\n🚀 Training Ensemble Salary Model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.15, random_state=42
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # ===== BASE MODELS =====
        xgb_reg = XGBRegressor(
            n_estimators=300,
            max_depth=10,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=42,
            n_jobs=-1
        )
        
        gb_reg = GradientBoostingRegressor(
            n_estimators=300,
            max_depth=10,
            learning_rate=0.05,
            subsample=0.9,
            random_state=42
        )
        
        rf_reg = RandomForestRegressor(
            n_estimators=300,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        # ===== VOTING ENSEMBLE =====
        voting_reg = VotingRegressor(
            estimators=[
                ('xgb', xgb_reg),
                ('gb', gb_reg),
                ('rf', rf_reg)
            ],
            n_jobs=-1
        )
        
        voting_reg.fit(X_train_scaled, y_train)
        
        # Predictions
        y_pred = voting_reg.predict(X_test_scaled)
        
        # Metrics
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        cv_scores = cross_val_score(voting_reg, X_train_scaled, y_train, cv=5, scoring='r2')
        
        logger.info(f"✅ Ensemble Salary Model Performance:")
        logger.info(f"   - R² Score: {r2:.4f}")
        logger.info(f"   - RMSE: ₹{rmse:.2f}")
        logger.info(f"   - MAE: ₹{mae:.2f}")
        logger.info(f"   - CV R² Score: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        self.models['salary'] = voting_reg
        self.scalers['salary'] = scaler
        
        return {
            'model': voting_reg,
            'scaler': scaler,
            'r2': r2,
            'rmse': rmse,
            'mae': mae,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std()
        }
    
    def save_models(self, output_dir: str = 'models'):
        """Save trained models"""
        logger.info(f"\n💾 Saving models to {output_dir}...")
        
        os.makedirs(output_dir, exist_ok=True)
        
        joblib.dump(self.models['career'], f'{output_dir}/career_predictor_90pct.pkl')
        joblib.dump(self.scalers['career'], f'{output_dir}/career_scaler_90pct.pkl')
        joblib.dump(self.encoders['career'], f'{output_dir}/career_encoder_90pct.pkl')
        
        joblib.dump(self.models['salary'], f'{output_dir}/salary_predictor_90pct.pkl')
        joblib.dump(self.scalers['salary'], f'{output_dir}/salary_scaler_90pct.pkl')
        
        logger.info(f"✅ Models saved successfully")
    
    def run_training_pipeline(self):
        """Run complete training pipeline"""
        logger.info("="*70)
        logger.info("🚀 Advanced ML Training Pipeline - 90%+ Accuracy Target")
        logger.info("="*70)
        
        start_time = datetime.now()
        
        # Fetch data
        jobs_df = self.fetch_jobs_data()
        skills_df = self.fetch_skills_data()
        
        # Engineer features
        features_df = self.engineer_advanced_features(jobs_df, skills_df)
        
        # Train career model
        X_career, y_career, career_features = self.prepare_career_data(features_df)
        career_results = self.train_ensemble_career_model(X_career, y_career)
        
        # Train salary model
        X_salary = features_df[[col for col in features_df.columns 
                               if col not in ['job_id', 'title_clean', 'company', 'location_standardized',
                                             'description_clean', 'requirements', 'employment_type_standardized',
                                             'experience_level_standardized', 'missing_salary', 'short_description',
                                             'career_category', 'salary_midpoint']]].fillna(0)
        y_salary = features_df['salary_midpoint']
        salary_results = self.train_ensemble_salary_model(X_salary, y_salary)
        
        # Save models
        self.save_models()
        
        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("\n" + "="*70)
        logger.info("✅ TRAINING PIPELINE COMPLETE!")
        logger.info("="*70)
        logger.info(f"\n📊 Summary:")
        logger.info(f"  - Data records: {len(features_df)}")
        logger.info(f"  - Features engineered: {len(career_features)}")
        logger.info(f"  - Career model accuracy: {career_results['accuracy']*100:.2f}%")
        logger.info(f"  - Salary model R²: {salary_results['r2']:.4f}")
        logger.info(f"  - Duration: {duration:.2f} seconds")
        logger.info("="*70 + "\n")
        
        return {
            'career_results': career_results,
            'salary_results': salary_results,
            'duration': duration,
            'data_records': len(features_df)
        }


def main():
    """Main execution"""
    trainer = AdvancedMLTrainer()
    results = trainer.run_training_pipeline()
    
    # Save results
    with open('ADVANCED_TRAINING_RESULTS.json', 'w') as f:
        json.dump({
            'career_accuracy': float(results['career_results']['accuracy']),
            'career_f1': float(results['career_results']['f1']),
            'career_cv_mean': float(results['career_results']['cv_mean']),
            'salary_r2': float(results['salary_results']['r2']),
            'salary_rmse': float(results['salary_results']['rmse']),
            'duration_seconds': results['duration'],
            'data_records': results['data_records'],
            'timestamp': datetime.now().isoformat()
        }, f, indent=2)
    
    return results


if __name__ == "__main__":
    main()
