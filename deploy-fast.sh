#!/bin/bash
# Ultra-fast deployment - uses existing image if available

set -e

echo "🚀 Fast Deployment to Google Cloud Run"
echo "======================================"
echo ""

# Check if image already exists
IMAGE="gcr.io/runagen-ai/runagen-api:latest"

echo "Checking for existing image..."
if gcloud container images describe $IMAGE --quiet 2>/dev/null; then
    echo "✓ Image found, skipping build"
    SKIP_BUILD=true
else
    echo "⚠ Image not found, will build"
    SKIP_BUILD=false
fi

echo ""
echo "Deploying to Cloud Run..."

# Deploy directly
gcloud run deploy runagen-api \
  --image $IMAGE \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --set-env-vars "GCP_PROJECT_ID=runagen-ai,PYTHONUNBUFFERED=1,PYTHONPATH=/app/src" \
  --quiet 2>&1 | grep -v "^$" || true

echo ""
echo "✅ Deployment Complete!"
echo ""

# Get URL
SERVICE_URL=$(gcloud run services describe runagen-api --region us-central1 --format='value(status.url)' 2>/dev/null)

echo "📊 Service Details:"
echo "  URL: $SERVICE_URL"
echo "  Docs: $SERVICE_URL/docs"
echo "  Health: $SERVICE_URL/health"
echo ""
