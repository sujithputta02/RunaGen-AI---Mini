#!/bin/bash
# Start the automated pipeline scheduler

echo "🚀 Starting RunaGen AI Automated Pipeline Scheduler"
echo "=================================================="

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set mode (production, development, or testing)
MODE=${1:-production}

# Set collection mode (priority, full, or category)
COLLECTION=${2:-priority}

echo "Scheduler Mode: $MODE"
echo "Collection Mode: $COLLECTION"
echo ""

# Start scheduler
python src/scheduler/automated_pipeline.py --mode $MODE --collection $COLLECTION
