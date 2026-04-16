# Automated Data Pipeline

## Overview

The RunaGen AI pipeline automatically collects and updates job market data to keep your ML models trained on fresh data.

## How It Works

### Data Collection
- **2000 jobs** per query from Adzuna API
- **2000 skills** from ESCO API
- **7 job roles** tracked:
  - Data Engineer
  - Data Scientist
  - ML Engineer
  - Data Analyst
  - Software Engineer
  - Backend Developer
  - Frontend Developer

### Update Schedule

#### Production Mode (Recommended)
```bash
./start_scheduler.sh production
```
- **Full Pipeline**: Daily at 2:00 AM
  - Collects 2000 new jobs per role
  - Refreshes skills taxonomy
  - Rebuilds all features
  
- **Incremental Updates**: Every 6 hours
  - Collects 500 new jobs per role
  - Updates existing features
  - Faster, lighter updates

#### Development Mode
```bash
./start_scheduler.sh development
```
- **Full Pipeline**: Every 12 hours
- Good for testing and development

#### Testing Mode
```bash
./start_scheduler.sh testing
```
- **Full Pipeline**: Every hour
- Use for rapid testing only

## Manual Control

### Run Pipeline Once
```bash
# Full pipeline (2000 records)
python src/etl/run_pipeline.py

# Specific layer only
python src/etl/run_pipeline.py --layer bronze
python src/etl/run_pipeline.py --layer silver
python src/etl/run_pipeline.py --layer gold

# View statistics
python src/etl/run_pipeline.py --layer stats
```

### Run Scheduler Once
```bash
python src/scheduler/automated_pipeline.py --run-once
```

## Data Freshness

### Why Automated Updates?

1. **Job Market Changes**: New jobs posted daily
2. **Skill Trends**: Emerging technologies and skills
3. **Salary Data**: Market rates fluctuate
4. **Model Accuracy**: Fresh data = better predictions

### What Gets Updated

**Bronze Layer** (Raw Data):
- New job postings from Adzuna
- Updated skills from ESCO
- Timestamps for tracking

**Silver Layer** (Cleaned):
- Standardized job titles
- Normalized skills
- Cleaned descriptions

**Gold Layer** (Features):
- Skill frequency metrics
- Role-skill relationships
- Salary aggregations
- Market trends

## Monitoring

### Check Pipeline Status
```bash
# View collection statistics
python src/etl/run_pipeline.py --layer stats
```

### Logs
All pipeline runs are logged to:
```
logs/scheduler_YYYYMMDD.log
logs/etl_pipeline_YYYYMMDD.log
```

### MongoDB Collections
Monitor your data in MongoDB:
```python
from src.utils.mongodb_client import MongoDBClient

client = MongoDBClient()
client.connect()

# Get statistics
stats = client.get_collection_stats()
for collection, count in stats.items():
    print(f"{collection}: {count} documents")
```

## Rate Limiting

The pipeline includes automatic rate limiting:
- **0.5 second delay** between API calls
- Prevents hitting API limits
- Ensures stable data collection

## Error Handling

The scheduler is resilient:
- **Automatic retry** on API failures
- **Continues on error** (doesn't stop entire pipeline)
- **Detailed logging** for debugging
- **Prevents duplicate runs** (checks if already running)

## Customization

### Change Collection Targets
Edit `src/etl/run_pipeline.py`:
```python
def run_bronze_layer(target_count=2000):  # Change this number
    ...
```

### Add More Job Queries
Edit `src/etl/run_pipeline.py`:
```python
queries = [
    'data engineer',
    'data scientist',
    'your_new_query_here'  # Add more
]
```

### Adjust Schedule
Edit `src/scheduler/automated_pipeline.py`:
```python
# Change schedule times
schedule.every().day.at("02:00").do(self.run_full_pipeline)  # Change time
schedule.every(6).hours.do(self.run_incremental_update)      # Change frequency
```

## Best Practices

1. **Start with Production Mode**: Balanced updates without overwhelming the API
2. **Monitor Logs**: Check for errors regularly
3. **Verify Data Quality**: Run stats command periodically
4. **Retrain Models**: After significant data updates
5. **Backup MongoDB**: Regular backups of your warehouse

## Stopping the Scheduler

Press `Ctrl+C` in the terminal running the scheduler.

The scheduler will:
- Complete current operation
- Save all data
- Close connections gracefully
- Log shutdown

## Production Deployment

For production environments:

### Using systemd (Linux)
Create `/etc/systemd/system/runagen-scheduler.service`:
```ini
[Unit]
Description=RunaGen AI Pipeline Scheduler
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/runagen-ml-etl
ExecStart=/path/to/venv/bin/python src/scheduler/automated_pipeline.py --mode production
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable runagen-scheduler
sudo systemctl start runagen-scheduler
sudo systemctl status runagen-scheduler
```

### Using Docker
```dockerfile
FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "src/scheduler/automated_pipeline.py", "--mode", "production"]
```

## Troubleshooting

**Scheduler not starting?**
- Check MongoDB connection
- Verify API credentials in `.env`
- Check logs for errors

**Data not updating?**
- Verify scheduler is running
- Check API rate limits
- Review error logs

**Too much data?**
- Reduce `target_count`
- Increase update intervals
- Archive old data

## Summary

The automated pipeline ensures your ML models always have fresh, relevant job market data. Set it up once, and it runs continuously, keeping your career intelligence system up-to-date.
