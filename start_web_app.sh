#!/bin/bash
# Start RunaGen AI Web Application

echo "🚀 Starting RunaGen AI Web Application"
echo "======================================"
echo ""

cd "$(dirname "$0")"

# Check if models exist
if [ ! -f "models/career_predictor.pkl" ] || [ ! -f "models/salary_predictor.pkl" ]; then
    echo "⚠️  ML models not found. Training models first..."
    python3 src/ml/train_models.py
    echo ""
fi

# Start API server in background
echo "Starting API server..."
python3 src/api/main.py &
API_PID=$!

# Wait for API to start
echo "Waiting for API server to initialize (loading ML models)..."
MAX_RETRIES=60
COUNT=0
API_READY=false

while [ $COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8000/health > /dev/null; then
        API_READY=true
        break
    fi
    sleep 1
    COUNT=$((COUNT + 1))
    if [ $((COUNT % 5)) -eq 0 ]; then
        echo "Still waiting for API... ($COUNT/$MAX_RETRIES)"
    fi
done

if [ "$API_READY" = true ]; then
    echo "✓ API server is running on http://localhost:8000"
else
    echo "⚠️  Warning: API server failed to start within $MAX_RETRIES seconds."
    echo "Check logs for errors."
fi

echo ""
echo "======================================"
echo "✅ RunaGen AI is ready!"
echo ""
echo "📱 Web Interface: Opening in browser..."
echo "🔗 API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo "======================================"
echo ""

# Open web interface
if [[ "$OSTYPE" == "darwin"* ]]; then
    open web/index.html
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open web/index.html
fi

# Wait for Ctrl+C
trap "echo ''; echo 'Stopping API server...'; kill $API_PID; exit" INT
wait $API_PID
