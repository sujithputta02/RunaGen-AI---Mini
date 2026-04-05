#!/bin/bash
# Start FastAPI server

echo "Starting RunaGen AI API Server..."
echo "=================================="
echo ""

cd "$(dirname "$0")"

# Check if models exist
if [ ! -f "models/career_predictor.pkl" ] || [ ! -f "models/salary_predictor.pkl" ]; then
    echo "⚠ Warning: ML models not found. Training models first..."
    python3 src/ml/train_models.py
    echo ""
fi

echo "Starting API server on http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 src/api/main.py
