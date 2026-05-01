# Deploy RunaGen with Ollama in Google Cloud

This guide deploys both Ollama and the RunaGen API to Google Cloud using Cloud Run and Compute Engine.

## Architecture

```
┌─────────────────────────────────────────┐
│     Google Cloud Platform               │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  Cloud Run (RunaGen API)         │  │
│  │  - Handles resume uploads        │  │
│  │  - Calls Ollama for extraction   │  │
│  └──────────────────────────────────┘  │
│           ↓ (HTTP)                      │
│  ┌──────────────────────────────────┐  │
│  │  Compute Engine (Ollama)         │  │
│  │  - Runs Ollama service           │  │
│  │  - Exposes port 11434            │  │
│  └──────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
```

## Prerequisites

- Google Cloud Project with billing enabled
- `gcloud` CLI installed and configured
- Docker installed locally
- At least 8GB RAM available in Compute Engine

## Step 1: Create Compute Engine Instance for Ollama

```bash
# Set variables
export PROJECT_ID="runagen-ai"
export INSTANCE_NAME="runagen-ollama"
export ZONE="us-central1-a"
export MACHINE_TYPE="n1-standard-2"  # 2 vCPU, 7.5GB RAM

# Set project
gcloud config set project $PROJECT_ID

# Create instance
gcloud compute instances create $INSTANCE_NAME \
    --zone=$ZONE \
    --machine-type=$MACHINE_TYPE \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=50GB \
    --scopes=default,cloud-platform \
    --tags=ollama,http-server,https-server

# Wait for instance to start
echo "Waiting for instance to start..."
sleep 30

# Get instance IP
export OLLAMA_IP=$(gcloud compute instances describe $INSTANCE_NAME \
    --zone=$ZONE \
    --format='get(networkInterfaces[0].networkIP)')

echo "Ollama instance IP: $OLLAMA_IP"
```

## Step 2: Install Ollama on Compute Engine

```bash
# SSH into the instance
gcloud compute ssh $INSTANCE_NAME --zone=$ZONE

# Inside the instance, run these commands:

# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Pull and run Ollama
docker run -d \
    --name ollama \
    -p 11434:11434 \
    -v ollama_data:/root/.ollama \
    --restart unless-stopped \
    ollama/ollama:latest

# Wait for Ollama to start
sleep 10

# Pull llama3 model (this takes ~5-10 minutes)
docker exec ollama ollama pull llama3

# Verify Ollama is running
curl http://localhost:11434/api/tags

# Exit SSH
exit
```

## Step 3: Configure Firewall Rules

```bash
# Allow traffic from Cloud Run to Ollama
gcloud compute firewall-rules create allow-ollama-from-cloud-run \
    --allow=tcp:11434 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=ollama \
    --description="Allow Cloud Run to access Ollama"

# Verify
gcloud compute firewall-rules list --filter="name:allow-ollama"
```

## Step 4: Update .env.cloud with Ollama URL

```bash
# Get the external IP of Ollama instance
export OLLAMA_EXTERNAL_IP=$(gcloud compute instances describe $INSTANCE_NAME \
    --zone=$ZONE \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)')

echo "Ollama external IP: $OLLAMA_EXTERNAL_IP"

# Update .env.cloud
cat > .env.cloud << EOF
# Cloud Deployment Environment Variables
ENVIRONMENT=cloud
OLLAMA_URL=http://$OLLAMA_EXTERNAL_IP:11434
OLLAMA_MODEL=llama3

# MongoDB Configuration
MONGO_URI=mongodb+srv://nasasujith265_db_user:z9d9cSbDedbyA1aA@cluster0runagen.dbw0rxl.mongodb.net/runagen_ml_warehouse?retryWrites=true&w=majority&appName=Cluster0runagen
MONGO_DB=runagen_ml_warehouse

# Adzuna API
ADZUNA_APP_ID=42cf8c86
ADZUNA_APP_KEY=1706dc3ca402aab909d9b8ba7f57092a

# GCP
GCP_PROJECT_ID=runagen-ai
GOOGLE_APPLICATION_CREDENTIALS=/var/secrets/google/key.json

# API Configuration
API_HOST=0.0.0.0
API_PORT=8080

# Python
PYTHONUNBUFFERED=1
PYTHONPATH=/app/src
EOF

cat .env.cloud
```

## Step 5: Deploy API to Cloud Run

```bash
# Set variables
export GCP_PROJECT_ID="runagen-ai"
export SERVICE_NAME="runagen-api"
export REGION="us-central1"
export IMAGE_NAME="gcr.io/${GCP_PROJECT_ID}/${SERVICE_NAME}"

# Build Docker image
docker build -t $IMAGE_NAME:latest -f Dockerfile.cloud .

# Push to Container Registry
docker push $IMAGE_NAME:latest

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 3600 \
    --set-env-vars "ENVIRONMENT=cloud,OLLAMA_URL=http://$OLLAMA_EXTERNAL_IP:11434,OLLAMA_MODEL=llama3,GCP_PROJECT_ID=$GCP_PROJECT_ID,PYTHONUNBUFFERED=1,PYTHONPATH=/app/src" \
    --set-secrets "MONGO_URI=mongo-uri:latest,ADZUNA_APP_ID=adzuna-app-id:latest,ADZUNA_APP_KEY=adzuna-app-key:latest" \
    --max-instances 100 \
    --min-instances 0

# Get service URL
export API_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format='value(status.url)')
echo "API URL: $API_URL"
```

## Step 6: Test the Deployment

```bash
# Test health endpoint
curl $API_URL/health

# Test skill extraction
curl -X POST $API_URL/api/analyze-resume \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Senior Python Developer with 5 years experience in AWS, Docker, and Kubernetes. Master'\''s degree in Computer Science."
  }'
```

## Step 7: Monitor Ollama

```bash
# SSH into Ollama instance
gcloud compute ssh $INSTANCE_NAME --zone=$ZONE

# Check Ollama logs
docker logs -f ollama

# Check Ollama status
curl http://localhost:11434/api/tags

# Exit
exit
```

## Troubleshooting

### Ollama not responding from Cloud Run

```bash
# Check if Ollama instance is running
gcloud compute instances list

# Check firewall rules
gcloud compute firewall-rules list

# SSH into Ollama instance and check Docker
gcloud compute ssh $INSTANCE_NAME --zone=$ZONE
docker ps
docker logs ollama
```

### Cloud Run can't reach Ollama

```bash
# Check VPC connectivity
gcloud compute networks list

# Check if firewall allows traffic
gcloud compute firewall-rules describe allow-ollama-from-cloud-run

# Test connectivity from Cloud Run logs
gcloud run logs read $SERVICE_NAME --region $REGION --limit 50
```

### Ollama model not loaded

```bash
# SSH into instance
gcloud compute ssh $INSTANCE_NAME --zone=$ZONE

# Check if model is loaded
docker exec ollama ollama list

# If not, pull it
docker exec ollama ollama pull llama3

# Exit
exit
```

## Cost Estimation

### Compute Engine (Ollama)
- Machine: n1-standard-2 (2 vCPU, 7.5GB RAM)
- Cost: ~$50-60/month (always running)
- Storage: 50GB boot disk + 20GB model = ~$5/month

### Cloud Run (API)
- Free tier: 2M requests/month
- Paid: $0.40 per 1M requests
- Memory: $0.0000417 per GB-second

### Total Monthly Cost
- Ollama: ~$55-65/month
- API: ~$0.40 per 1M requests
- **Total: ~$60-70/month + usage**

## Optimization Tips

1. **Use preemptible instances** for Ollama (50% cheaper):
   ```bash
   gcloud compute instances create $INSTANCE_NAME \
       --preemptible \
       ...
   ```

2. **Scale down Ollama** when not in use:
   ```bash
   gcloud compute instances stop $INSTANCE_NAME --zone=$ZONE
   ```

3. **Use smaller machine type** if possible:
   ```bash
   --machine-type=n1-standard-1  # 1 vCPU, 3.75GB RAM
   ```

## Cleanup

```bash
# Delete Cloud Run service
gcloud run services delete $SERVICE_NAME --region $REGION

# Delete Compute Engine instance
gcloud compute instances delete $INSTANCE_NAME --zone=$ZONE

# Delete firewall rule
gcloud compute firewall-rules delete allow-ollama-from-cloud-run

# Delete container image
gcloud container images delete $IMAGE_NAME:latest
```

## Next Steps

1. Deploy Ollama instance
2. Deploy API to Cloud Run
3. Test skill extraction with resume upload
4. Monitor logs and performance
5. Optimize costs

---

**Status**: Ready to deploy
**Version**: 2.0.0
