"""
Advanced ML Model Training Pipeline
Trains models using cleaned data from BigQuery Silver/Gold layers
"""
import os
import sys
from dotenv import load_dotenv
import logging
from datetime import datetime
import json

# Load environment variables
load_dotenv()

import pandas as pd
import numpy as np
from google.cloud import bigquery
from google.oauth2 import service_account
import joblib
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier, XGBRegressor
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, r2_score, mean_absolute_error,
    confusion_matrix, classification_report
)
import warnings
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BigQueryMLTrainer:
    """Train ML models using data from BigQuery"""
    
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
        self.dataset_silver = 'runagen_silver_silver'  # dbt created with this naming
        self.dataset_gold = 'runagen_silver_gold'  # dbt created with this naming
        
        # Model storage
        self.models = {}
        self.scalers = {}
        self.encoders = {}
    
    def fetch_jobs_data(self) -> pd.DataFrame:
        """Fetch cleaned jobs data from BigQuery Silver layer"""
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
        LIMIT 10000
        """
        
        # Fetch results and convert to DataFrame manually
        query_job = self.bq_client.query(query)
        rows = query_job.result()
        
        # Convert to list of dicts
        data = [dict(row) for row in rows]
        df = pd.DataFrame(data)
        
        logger.info(f"✅ Fetched {len(df)} jobs records")
        return df
    
    def fetch_skills_data(self) -> pd.DataFrame:
        """Fetch standardized skills data from BigQuery Silver layer"""
        logger.info("📥 Fetching skills data from BigQuery...")
        
        query = f"""
        SELECT
            skill_id,
            skill_name,
            skill_category
        FROM `{self.project_id}.{self.dataset_silver}.skills_standardized`
        """
        
        # Fetch results and convert to DataFrame manually
        query_job = self.bq_client.query(query)
        rows = query_job.result()
        
        # Convert to list of dicts
        data = [dict(row) for row in rows]
        df = pd.DataFrame(data)
        
        logger.info(f"✅ Fetched {len(df)} skills records")
        return df
    
    def engineer_features(self, jobs_df: pd.DataFrame, skills_df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features for ML models"""
        logger.info("🔧 Engineering features...")
        
        # Create feature matrix
        features_df = jobs_df.copy()
        
        # 1. Text-based features
        features_df['title_length'] = features_df['title_clean'].str.len()
        features_df['description_length'] = features_df['description_clean'].str.len()
        features_df['requirements_length'] = features_df['requirements'].fillna('').str.len()
        
        # 2. Salary features
        features_df['salary_range'] = features_df['salary_max_usd'] - features_df['salary_min_usd']
        features_df['salary_midpoint'] = (features_df['salary_min_usd'] + features_df['salary_max_usd']) / 2
        features_df['salary_ratio'] = features_df['salary_max_usd'] / (features_df['salary_min_usd'] + 1)
        
        # 3. Location features
        features_df['is_remote'] = features_df['location_standardized'].str.lower().str.contains('remote', na=False).astype(int)
        features_df['is_india'] = features_df['location_standardized'].str.lower().str.contains('india', na=False).astype(int)
        
        # 4. Experience level encoding
        exp_mapping = {'Entry': 1, 'Mid': 2, 'Senior': 3, 'Lead': 4, 'Not Specified': 0}
        features_df['experience_level_encoded'] = features_df['experience_level_standardized'].map(exp_mapping).fillna(0)
        
        # 5. Employment type encoding
        emp_mapping = {'Full-time': 1, 'Part-time': 0.5, 'Contract': 0.75, 'Internship': 0.25, 'Other': 0}
        features_df['employment_type_encoded'] = features_df['employment_type_standardized'].map(emp_mapping).fillna(0)
        
        # 6. Skill diversity (count unique skills mentioned)
        features_df['skill_count'] = 0
        for idx, row in features_df.iterrows():
            text = (str(row['description_clean']) + ' ' + str(row['requirements'])).lower()
            skill_count = sum(1 for skill in skills_df['skill_name'] if skill.lower() in text)
            features_df.at[idx, 'skill_count'] = skill_count
        
        logger.info(f"✅ Engineered {len(features_df.columns)} features")
        return features_df
    
    def prepare_career_prediction_data(self, features_df: pd.DataFrame) -> tuple:
        """Prepare data for career prediction model"""
        logger.info("📊 Preparing career prediction data...")
        
        # Create target: career category based on title
        career_keywords = {
            'Data Scientist': ['data scientist', 'ml engineer', 'machine learning'],
            'Data Engineer': ['data engineer', 'etl', 'pipeline'],
            'Backend Developer': ['backend', 'python', 'java', 'node.js'],
            'Frontend Developer': ['frontend', 'react', 'angular', 'vue'],
            'Full Stack Developer': ['full stack', 'full-stack'],
            'DevOps Engineer': ['devops', 'kubernetes', 'docker'],
            'Cloud Architect': ['cloud architect', 'aws', 'gcp', 'azure'],
            'Software Engineer': ['software engineer', 'engineer']
        }
        
        def classify_career(title):
            title_lower = str(title).lower()
            for career, keywords in career_keywords.items():
                if any(kw in title_lower for kw in keywords):
                    return career
            return 'Other'
        
        features_df['career_category'] = features_df['title_clean'].apply(classify_career)
        
        # Select features for model
        feature_cols = [
            'title_length', 'description_length', 'requirements_length',
            'salary_midpoint', 'salary_ratio', 'is_remote', 'is_india',
            'experience_level_encoded', 'employment_type_encoded', 'skill_count'
        ]
        
        X = features_df[feature_cols].fillna(0)
        y = features_df['career_category']
        
        logger.info(f"✅ Career classes: {y.unique()}")
        logger.info(f"✅ Feature matrix shape: {X.shape}")
        
        return X, y, feature_cols
    
    def prepare_salary_prediction_data(self, features_df: pd.DataFrame) -> tuple:
        """Prepare data for salary prediction model"""
        logger.info("📊 Preparing salary prediction data...")
        
        # Select features for model
        feature_cols = [
            'title_length', 'description_length', 'requirements_length',
            'salary_range', 'is_remote', 'is_india',
            'experience_level_encoded', 'employment_type_encoded', 'skill_count'
        ]
        
        X = features_df[feature_cols].fillna(0)
        y = features_df['salary_midpoint']
        
        logger.info(f"✅ Salary range: ₹{y.min():.0f} - ₹{y.max():.0f}")
        logger.info(f"✅ Feature matrix shape: {X.shape}")
        
        return X, y, feature_cols
    
    def train_career_model(self, X: pd.DataFrame, y: pd.Series) -> dict:
        """Train career prediction model"""
        logger.info("\n🚀 Training Career Prediction Model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Encode labels
        le = LabelEncoder()
        y_train_encoded = le.fit_transform(y_train)
        y_test_encoded = le.transform(y_test)
        
        # Train XGBoost model
        model = XGBClassifier(
            n_estimators=200,
            max_depth=8,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1,
            eval_metric='mlogloss'
        )
        
        model.fit(
            X_train_scaled, y_train_encoded,
            eval_set=[(X_test_scaled, y_test_encoded)],
            verbose=False
        )
        
        # Predictions
        y_pred = model.predict(X_test_scaled)
        
        # Metrics
        accuracy = accuracy_score(y_test_encoded, y_pred)
        precision = precision_score(y_test_encoded, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test_encoded, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test_encoded, y_pred, average='weighted', zero_division=0)
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_train_scaled, y_train_encoded, cv=5)
        
        logger.info(f"✅ Career Model Performance:")
        logger.info(f"   - Test Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
        logger.info(f"   - Precision: {precision:.4f}")
        logger.info(f"   - Recall: {recall:.4f}")
        logger.info(f"   - F1-Score: {f1:.4f}")
        logger.info(f"   - CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        # Store model and preprocessing objects
        self.models['career'] = model
        self.scalers['career'] = scaler
        self.encoders['career'] = le
        
        return {
            'model': model,
            'scaler': scaler,
            'encoder': le,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std()
        }
    
    def train_salary_model(self, X: pd.DataFrame, y: pd.Series) -> dict:
        """Train salary prediction model"""
        logger.info("\n🚀 Training Salary Prediction Model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train XGBoost model
        model = XGBRegressor(
            n_estimators=200,
            max_depth=8,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(
            X_train_scaled, y_train,
            eval_set=[(X_test_scaled, y_test)],
            verbose=False
        )
        
        # Predictions
        y_pred = model.predict(X_test_scaled)
        
        # Metrics
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
        
        logger.info(f"✅ Salary Model Performance:")
        logger.info(f"   - R² Score: {r2:.4f}")
        logger.info(f"   - RMSE: ₹{rmse:.2f}")
        logger.info(f"   - MAE: ₹{mae:.2f}")
        logger.info(f"   - CV R² Score: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        # Store model and preprocessing objects
        self.models['salary'] = model
        self.scalers['salary'] = scaler
        
        return {
            'model': model,
            'scaler': scaler,
            'r2': r2,
            'rmse': rmse,
            'mae': mae,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std()
        }
    
    def save_models(self, output_dir: str = 'models'):
        """Save trained models to disk"""
        logger.info(f"\n💾 Saving models to {output_dir}...")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Save career model
        joblib.dump(self.models['career'], f'{output_dir}/career_predictor_bq.pkl')
        joblib.dump(self.scalers['career'], f'{output_dir}/career_scaler_bq.pkl')
        joblib.dump(self.encoders['career'], f'{output_dir}/career_encoder_bq.pkl')
        
        # Save salary model
        joblib.dump(self.models['salary'], f'{output_dir}/salary_predictor_bq.pkl')
        joblib.dump(self.scalers['salary'], f'{output_dir}/salary_scaler_bq.pkl')
        
        logger.info(f"✅ Models saved successfully")
    
    def run_training_pipeline(self):
        """Run complete training pipeline"""
        logger.info("="*70)
        logger.info("🚀 BigQuery ML Training Pipeline")
        logger.info("="*70)
        
        start_time = datetime.now()
        
        # Fetch data
        jobs_df = self.fetch_jobs_data()
        skills_df = self.fetch_skills_data()
        
        # Engineer features
        features_df = self.engineer_features(jobs_df, skills_df)
        
        # Train career model
        X_career, y_career, career_features = self.prepare_career_prediction_data(features_df)
        career_results = self.train_career_model(X_career, y_career)
        
        # Train salary model
        X_salary, y_salary, salary_features = self.prepare_salary_prediction_data(features_df)
        salary_results = self.train_salary_model(X_salary, y_salary)
        
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
    trainer = BigQueryMLTrainer()
    results = trainer.run_training_pipeline()
    
    # Save results to file
    with open('BIGQUERY_TRAINING_RESULTS.json', 'w') as f:
        json.dump({
            'career_accuracy': float(results['career_results']['accuracy']),
            'career_f1': float(results['career_results']['f1']),
            'salary_r2': float(results['salary_results']['r2']),
            'salary_rmse': float(results['salary_results']['rmse']),
            'duration_seconds': results['duration'],
            'data_records': results['data_records']
        }, f, indent=2)
    
    return results


if __name__ == "__main__":
    main()
