#!/bin/bash

echo "🌐 Starting RunaGen AI Web Interface..."
echo ""
echo "Opening browser at: http://localhost:8080"
echo "Press Ctrl+C to stop the server"
echo ""

# Start simple HTTP server
cd web && python3 -m http.server 8080
