#!/bin/bash

# BigQuery Setup Script for RunaGen AI

echo "🚀 Setting up BigQuery Data Warehouse..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set project ID
PROJECT_ID="runagen-ai-warehouse"
REGION="us-central1"

echo "📦 Creating GCP project: $PROJECT_ID"
# gcloud projects create $PROJECT_ID --name="RunaGen AI Warehouse"
# gcloud config set project $PROJECT_ID

echo "💳 Note: Enable billing for the project in GCP Console"
echo "🔗 https://console.cloud.google.com/billing"

# Enable BigQuery API
echo "🔌 Enabling BigQuery API..."
gcloud services enable bigquery.googleapis.com

# Create datasets (Bronze, Silver, Gold layers)
echo "📊 Creating BigQuery datasets..."

bq mk --dataset \
    --location=$REGION \
    --description="Bronze layer - Raw data from sources" \
    ${PROJECT_ID}:runagen_bronze

bq mk --dataset \
    --location=$REGION \
    --description="Silver layer - Cleaned and standardized data" \
    ${PROJECT_ID}:runagen_silver

bq mk --dataset \
    --location=$REGION \
    --description="Gold layer - Analytics-ready aggregated data" \
    ${PROJECT_ID}:runagen_gold

echo "✅ BigQuery datasets created!"

# Create service account for authentication
echo "🔑 Creating service account..."
SERVICE_ACCOUNT="runagen-etl@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud iam service-accounts create runagen-etl \
    --display-name="RunaGen ETL Service Account" \
    --description="Service account for ETL pipeline"

# Grant BigQuery permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/bigquery.jobUser"

# Create and download key
echo "📥 Creating service account key..."
gcloud iam service-accounts keys create credentials/bigquery-key.json \
    --iam-account=$SERVICE_ACCOUNT

echo "✅ Service account key saved to credentials/bigquery-key.json"

echo ""
echo "🎉 BigQuery setup complete!"
echo ""
echo "Next steps:"
echo "1. Set environment variable: export GOOGLE_APPLICATION_CREDENTIALS=credentials/bigquery-key.json"
echo "2. Install dbt: pip install dbt-bigquery"
echo "3. Initialize dbt project: dbt init runagen_transforms"
