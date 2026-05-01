#!/bin/bash
# Lightweight deployment for mobile data
# Runs in background with minimal output

set -e

LOG_FILE="deployment.log"
echo "Starting deployment at $(date)" > $LOG_FILE

# Step 1: Set project
gcloud config set project runagen-ai >> $LOG_FILE 2>&1

# Step 2: Enable APIs (quiet)
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com --quiet >> $LOG_FILE 2>&1

# Step 3: Configure Docker (quiet)
gcloud auth configure-docker gcr.io --quiet >> $LOG_FILE 2>&1

# Step 4: Build and push (with minimal output)
echo "Building Docker image..."
gcloud builds submit --tag gcr.io/runagen-ai/runagen-api:latest . --quiet >> $LOG_FILE 2>&1
echo "✓ Image built"

# Step 5: Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy runagen-api \
  --image gcr.io/runagen-ai/runagen-api:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --set-env-vars "GCP_PROJECT_ID=runagen-ai,PYTHONUNBUFFERED=1,PYTHONPATH=/app/src" \
  --quiet >> $LOG_FILE 2>&1
echo "✓ Deployed"

# Step 6: Get URL
SERVICE_URL=$(gcloud run services describe runagen-api --region us-central1 --format='value(status.url)' 2>/dev/null)

# Output results
echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "Service URL: $SERVICE_URL"
echo "API Docs: $SERVICE_URL/docs"
echo "Health: $SERVICE_URL/health"
echo ""
echo "Logs saved to: $LOG_FILE"
