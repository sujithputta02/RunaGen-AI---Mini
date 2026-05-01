#!/bin/bash

# RunaGen AI - Google Cloud Deployment Script
# Deploys the latest changes to Google Cloud Run

set -e

echo "🚀 RunaGen AI - Google Cloud Deployment"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-runagen-ai}"
SERVICE_NAME="runagen-api"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo -e "${BLUE}Configuration:${NC}"
echo "  Project ID: $PROJECT_ID"
echo "  Service: $SERVICE_NAME"
echo "  Region: $REGION"
echo "  Image: $IMAGE_NAME"
echo ""

# Step 1: Check prerequisites
echo -e "${BLUE}Step 1: Checking prerequisites...${NC}"
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI not found. Please install Google Cloud SDK.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ gcloud CLI found${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker found${NC}"

# Step 2: Authenticate with GCP
echo ""
echo -e "${BLUE}Step 2: Authenticating with GCP...${NC}"
gcloud config set project $PROJECT_ID
gcloud auth configure-docker
echo -e "${GREEN}✓ GCP authentication complete${NC}"

# Step 3: Build Docker image
echo ""
echo -e "${BLUE}Step 3: Building Docker image...${NC}"
if [ ! -f "Dockerfile" ]; then
    echo -e "${YELLOW}⚠️  Dockerfile not found. Creating one...${NC}"
    cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Run the application
CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
    echo -e "${GREEN}✓ Dockerfile created${NC}"
fi

docker build -t $IMAGE_NAME:latest .
echo -e "${GREEN}✓ Docker image built${NC}"

# Step 4: Push image to Container Registry
echo ""
echo -e "${BLUE}Step 4: Pushing image to Google Container Registry...${NC}"
docker push $IMAGE_NAME:latest
echo -e "${GREEN}✓ Image pushed to GCR${NC}"

# Step 5: Deploy to Cloud Run
echo ""
echo -e "${BLUE}Step 5: Deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 3600 \
    --set-env-vars "GCP_PROJECT_ID=$PROJECT_ID" \
    --set-secrets "MONGO_URI=mongo-uri:latest,ADZUNA_APP_ID=adzuna-app-id:latest,ADZUNA_APP_KEY=adzuna-app-key:latest"

echo -e "${GREEN}✓ Deployment complete${NC}"

# Step 6: Get service URL
echo ""
echo -e "${BLUE}Step 6: Getting service URL...${NC}"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')
echo -e "${GREEN}✓ Service deployed at: $SERVICE_URL${NC}"

# Step 7: Test deployment
echo ""
echo -e "${BLUE}Step 7: Testing deployment...${NC}"
sleep 5
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/health")
if [ "$HEALTH_CHECK" = "200" ]; then
    echo -e "${GREEN}✓ Health check passed (HTTP $HEALTH_CHECK)${NC}"
else
    echo -e "${YELLOW}⚠️  Health check returned HTTP $HEALTH_CHECK${NC}"
fi

echo ""
echo -e "${GREEN}=========================================="
echo "✓ Deployment successful!"
echo "==========================================${NC}"
echo ""
echo "📊 Service Details:"
echo "  URL: $SERVICE_URL"
echo "  API Docs: $SERVICE_URL/docs"
echo "  Health: $SERVICE_URL/health"
echo ""
echo "📝 Next steps:"
echo "  1. Monitor logs: gcloud run logs read $SERVICE_NAME --region $REGION"
echo "  2. View metrics: gcloud run services describe $SERVICE_NAME --region $REGION"
echo "  3. Update secrets: gcloud secrets versions add <secret-name> --data-file=<file>"
echo ""
