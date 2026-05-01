# Skill Extraction Fix - Complete Guide

## Problem Summary

The skill extraction was not working correctly in the cloud deployment because:

1. **Ollama not available in cloud**: Ollama is a local-only service and cannot run in Google Cloud Run
2. **Missing Gemini API key**: The cloud deployment needs Gemini API for LLM-based extraction
3. **Incorrect API URL**: The API was trying to use local Ollama URL in cloud environment
4. **No environment detection**: The code didn't distinguish between local and cloud deployments

## Solution Overview

### 1. Environment-Aware Skill Extraction

The `SkillExtractor` class now detects the environment and configures accordingly:

```python
# Local Development (uses Ollama if available)
ENVIRONMENT=local
OLLAMA_URL=http://localhost:11434

# Cloud Deployment (uses Gemini API)
ENVIRONMENT=cloud
GEMINI_API_KEY=your_gemini_api_key
```

### 2. Fallback Chain

The skill extraction now uses a smart fallback chain:

1. **Primary**: Gemini API (best for cloud, most accurate)
2. **Secondary**: Ollama (local development only)
3. **Fallback**: Heuristic regex-based extraction (always works)

## Setup Instructions

### For Local Development

1. **Install Ollama** (already installed on your system):
   ```bash
   ollama --version  # Should show: ollama version 0.21.2
   ```

2. **Pull a model** (if not already done):
   ```bash
   ollama pull llama3
   ```

3. **Start Ollama service**:
   ```bash
   ollama serve
   ```

4. **Update .env file**:
   ```env
   ENVIRONMENT=local
   OLLAMA_URL=http://localhost:11434
   OLLAMA_MODEL=llama3
   GEMINI_API_KEY=your_gemini_api_key  # Optional, but recommended
   ```

5. **Test locally**:
   ```bash
   python -c "
   from src.ml.model_1_skill_extraction import SkillExtractor
   extractor = SkillExtractor(use_ollama=True, use_gemini=True)
   result = extractor.extract_all('Python, AWS, Docker, 5 years experience')
   print(result)
   "
   ```

### For Cloud Deployment (Google Cloud Run)

1. **Get Gemini API Key**:
   - Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Create a new API key
   - Copy the key

2. **Create .env.cloud file**:
   ```bash
   cp .env.cloud .env.cloud
   # Edit .env.cloud and add your Gemini API key
   ```

3. **Deploy to Cloud Run**:
   ```bash
   chmod +x deploy_cloud_run.sh
   ./deploy_cloud_run.sh
   ```

4. **Verify deployment**:
   ```bash
   # Get the service URL
   gcloud run services describe runagen-api --region us-central1 --format='value(status.url)'
   
   # Test health endpoint
   curl https://runagen-api-krtyiuzqka-uc.a.run.app/health
   
   # Test skill extraction
   curl -X POST https://runagen-api-krtyiuzqka-uc.a.run.app/api/analyze-resume \
     -H "Content-Type: application/json" \
     -d '{"resume_text": "Python, AWS, Docker, 5 years experience"}'
   ```

## Configuration Files

### .env (Local Development)
```env
ENVIRONMENT=local
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3
GEMINI_API_KEY=your_gemini_api_key
```

### .env.cloud (Cloud Deployment)
```env
ENVIRONMENT=cloud
GEMINI_API_KEY=your_gemini_api_key
ADZUNA_APP_ID=42cf8c86
ADZUNA_APP_KEY=1706dc3ca402aab909d9b8ba7f57092a
MONGO_URI=your_mongodb_uri
```

### app.yaml (Cloud Run Configuration)
```yaml
runtime: python311
env: standard
entrypoint: gunicorn -w 4 -b :$PORT "src.api.main:app" --worker-class uvicorn.workers.UvicornWorker
env_variables:
  ENVIRONMENT: "cloud"
  GEMINI_API_KEY: "${GEMINI_API_KEY}"
```

## API Endpoints

### Health Check
```bash
curl https://runagen-api-krtyiuzqka-uc.a.run.app/health
```

Response:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "models_loaded": {
    "career": true,
    "salary": true
  }
}
```

### Analyze Resume
```bash
curl -X POST https://runagen-api-krtyiuzqka-uc.a.run.app/api/analyze-resume \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Senior Python Developer with 5 years experience in AWS, Docker, and Kubernetes. Master's degree in Computer Science."
  }'
```

Response:
```json
{
  "skills": ["Python", "AWS", "Docker", "Kubernetes"],
  "career_predictions": [
    {
      "role": "Senior Software Engineer",
      "probability": 0.92
    }
  ],
  "salary_prediction": {
    "predicted_salary": 1200000,
    "min_salary": 1020000,
    "max_salary": 1380000,
    "currency": "INR"
  },
  "skill_gaps": [
    {
      "skill": "Terraform",
      "priority_score": 0.8
    }
  ],
  "recommendations": [
    "Learn Terraform for Infrastructure as Code",
    "Explore Kubernetes advanced patterns"
  ]
}
```

## Troubleshooting

### Issue: "Ollama not available" in local development

**Solution**: Start Ollama service
```bash
ollama serve
```

### Issue: "Gemini API error" in cloud

**Solution**: Verify Gemini API key
```bash
# Check if secret is set
gcloud secrets describe gemini-api-key

# Update secret if needed
echo -n "your_new_key" | gcloud secrets versions add gemini-api-key --data-file=-
```

### Issue: Skill extraction returns empty list

**Solution**: Check logs
```bash
# Local
python -c "from src.ml.model_1_skill_extraction import SkillExtractor; print(SkillExtractor().extract_all('Python, AWS'))"

# Cloud
gcloud run logs read runagen-api --region us-central1 --limit 50
```

### Issue: "Model not loaded" error

**Solution**: The models will load on first use. Check if model files exist:
```bash
ls -la models/
```

## Performance Optimization

### Local Development
- Ollama provides fast, local inference
- No API calls needed
- Best for development and testing

### Cloud Deployment
- Gemini API provides high accuracy
- Automatic scaling
- Pay-per-use pricing
- No infrastructure management

## Cost Estimation

### Gemini API (Cloud)
- Free tier: 60 requests per minute
- Paid: $0.075 per 1M input tokens, $0.30 per 1M output tokens
- Typical resume: ~500 tokens = $0.00004 per analysis

### Google Cloud Run
- Free tier: 2M requests/month
- Paid: $0.40 per 1M requests
- Memory: $0.0000417 per GB-second

## Next Steps

1. **Test locally** with Ollama
2. **Get Gemini API key** from Google AI Studio
3. **Deploy to Cloud Run** using the deployment script
4. **Monitor logs** and performance
5. **Optimize** based on usage patterns

## Support

For issues or questions:
1. Check logs: `gcloud run logs read runagen-api`
2. Review this guide
3. Check [Google Cloud Run documentation](https://cloud.google.com/run/docs)
4. Check [Gemini API documentation](https://ai.google.dev/docs)

---

**Last Updated**: May 2026
**Version**: 2.0.0
