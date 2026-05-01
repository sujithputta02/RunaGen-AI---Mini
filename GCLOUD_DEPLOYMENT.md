# RunaGen AI - Google Cloud Deployment Guide

## 🚀 Quick Deployment

### Prerequisites
1. Google Cloud Project created
2. `gcloud` CLI installed and configured
3. Docker installed
4. Billing enabled on GCP project

### Step 1: Set Up GCP Project

```bash
# Set your project ID
export GCP_PROJECT_ID="runagen-ai"

# Set the project
gcloud config set project $GCP_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable storage-api.googleapis.com
```

### Step 2: Set Up Secrets (for sensitive data)

```bash
# Create secrets for environment variables
echo -n "your-mongodb-uri" | gcloud secrets create mongo-uri --data-file=-
echo -n "your-adzuna-app-id" | gcloud secrets create adzuna-app-id --data-file=-
echo -n "your-adzuna-app-key" | gcloud secrets create adzuna-app-key --data-file=-

# Upload BigQuery credentials
gcloud secrets create bigquery-key --data-file=credentials/bigquery-key.json
```

### Step 3: Deploy Using Script

```bash
# Make script executable
chmod +x deploy_to_gcloud.sh

# Run deployment
./deploy_to_gcloud.sh
```

### Step 4: Manual Deployment (if script fails)

```bash
# Build Docker image
docker build -t gcr.io/$GCP_PROJECT_ID/runagen-api:latest .

# Push to Container Registry
docker push gcr.io/$GCP_PROJECT_ID/runagen-api:latest

# Deploy to Cloud Run
gcloud run deploy runagen-api \
    --image gcr.io/$GCP_PROJECT_ID/runagen-api:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 3600 \
    --set-env-vars "GCP_PROJECT_ID=$GCP_PROJECT_ID" \
    --set-secrets "MONGO_URI=mongo-uri:latest,ADZUNA_APP_ID=adzuna-app-id:latest,ADZUNA_APP_KEY=adzuna-app-key:latest"
```

## 📊 Deployment Configuration

### Cloud Run Settings
- **Memory**: 2 GB (adjustable based on load)
- **CPU**: 2 (adjustable based on load)
- **Timeout**: 3600 seconds (1 hour)
- **Concurrency**: 100 (default)
- **Min Instances**: 0 (scales to 0 when idle)
- **Max Instances**: 100 (adjustable)

### Environment Variables
```
GCP_PROJECT_ID=runagen-ai
PYTHONUNBUFFERED=1
PORT=8000
PYTHONPATH=/app/src
```

### Secrets (from Secret Manager)
```
MONGO_URI=mongo-uri:latest
ADZUNA_APP_ID=adzuna-app-id:latest
ADZUNA_APP_KEY=adzuna-app-key:latest
GOOGLE_APPLICATION_CREDENTIALS=/var/secrets/google/key.json
```

## 🔍 Monitoring & Logs

### View Logs
```bash
# Real-time logs
gcloud run logs read runagen-api --region us-central1 --limit 50 --follow

# Logs from specific time
gcloud run logs read runagen-api --region us-central1 --limit 100 --start-time 2024-01-01T00:00:00Z
```

### View Metrics
```bash
# Service details
gcloud run services describe runagen-api --region us-central1

# View traffic
gcloud run services describe runagen-api --region us-central1 --format='value(status.traffic)'
```

### Set Up Alerts
```bash
# Create alert policy for high error rate
gcloud alpha monitoring policies create \
    --notification-channels=CHANNEL_ID \
    --display-name="RunaGen API High Error Rate" \
    --condition-display-name="Error rate > 5%" \
    --condition-threshold-value=0.05
```

## 🔄 Continuous Deployment

### Using GitHub Actions
Create `.github/workflows/deploy-gcloud.yml`:

```yaml
name: Deploy to Google Cloud Run

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
        with:
          project_id: ${{ secrets.GCP_PROJECT_ID }}
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          export_default_credentials: true
      
      - name: Build and push Docker image
        run: |
          gcloud builds submit \
            --tag gcr.io/${{ secrets.GCP_PROJECT_ID }}/runagen-api:latest
      
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy runagen-api \
            --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/runagen-api:latest \
            --region us-central1 \
            --platform managed
```

## 📈 Scaling & Performance

### Auto-scaling Configuration
```bash
# Update service with auto-scaling
gcloud run services update runagen-api \
    --region us-central1 \
    --min-instances 1 \
    --max-instances 100
```

### Performance Optimization
1. **Increase Memory**: For ML model loading
   ```bash
   gcloud run services update runagen-api --memory 4Gi
   ```

2. **Increase CPU**: For concurrent requests
   ```bash
   gcloud run services update runagen-api --cpu 4
   ```

3. **Concurrency**: Handle multiple requests
   ```bash
   gcloud run services update runagen-api --concurrency 200
   ```

## 🔐 Security Best Practices

1. **Use Secret Manager** for sensitive data
2. **Enable VPC Connector** for private database access
3. **Set up IAM roles** for least privilege
4. **Enable Cloud Armor** for DDoS protection
5. **Use private service accounts** for authentication

## 🚨 Troubleshooting

### Service won't start
```bash
# Check logs
gcloud run logs read runagen-api --region us-central1 --limit 100

# Check service status
gcloud run services describe runagen-api --region us-central1
```

### High latency
```bash
# Check metrics
gcloud monitoring time-series list \
    --filter='resource.type="cloud_run_revision"'

# Increase memory/CPU
gcloud run services update runagen-api --memory 4Gi --cpu 4
```

### Out of memory errors
```bash
# Increase memory allocation
gcloud run services update runagen-api --memory 8Gi
```

## 📝 Rollback

### Rollback to previous version
```bash
# List revisions
gcloud run revisions list --service runagen-api --region us-central1

# Route traffic to previous revision
gcloud run services update-traffic runagen-api \
    --to-revisions REVISION_NAME=100 \
    --region us-central1
```

## 💰 Cost Optimization

1. **Set min instances to 0** (scales down when idle)
2. **Use smaller memory** if possible (512MB - 2GB)
3. **Set appropriate timeout** (don't waste resources)
4. **Monitor usage** and adjust resources accordingly

## 📞 Support

For issues:
1. Check logs: `gcloud run logs read runagen-api`
2. Review metrics: `gcloud run services describe runagen-api`
3. Check GCP status: https://status.cloud.google.com/
4. Contact GCP support for infrastructure issues

---

**Last Updated**: May 2026
**Version**: 2.0.0
