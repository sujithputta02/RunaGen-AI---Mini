#!/bin/bash

# RunaGen AI - Local Development Startup Script
# This script starts all necessary services for local development

set -e

echo "🚀 RunaGen AI - Local Development Startup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${BLUE}Checking Python version...${NC}"
python3 --version
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Install/update dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found!${NC}"
    echo "Please create .env file from .env.example:"
    echo "  cp .env.example .env"
    echo "  # Edit .env with your credentials"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for credentials
if [ ! -f "credentials/bigquery-key.json" ]; then
    echo -e "${YELLOW}⚠️  BigQuery credentials not found at credentials/bigquery-key.json${NC}"
    echo "This is optional for local testing. You can add it later."
    echo ""
fi

# Check if models exist
if [ ! -f "models/career_predictor_90pct.pkl" ]; then
    echo -e "${YELLOW}⚠️  Trained models not found${NC}"
    echo "The API will use fallback models. For full functionality, train models:"
    echo "  python3 src/ml/train_models_advanced_90pct.py"
    echo ""
fi

echo -e "${GREEN}=========================================="
echo "✓ All checks passed!"
echo "==========================================${NC}"
echo ""

# Start the API
echo -e "${BLUE}Starting FastAPI server...${NC}"
echo "API will be available at: http://localhost:8000"
echo "Swagger UI: http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
