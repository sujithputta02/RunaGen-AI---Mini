#!/bin/bash
# Generate BI Dashboards

echo "Generating RunaGen AI BI Dashboards..."
echo "======================================"
echo ""

cd "$(dirname "$0")"

# Generate dashboards
python3 src/dashboards/dashboard_generator.py

echo ""
echo "======================================"
echo "✅ Dashboards generated successfully!"
echo ""
echo "To view dashboards:"
echo "  macOS: open dashboards/html/index.html"
echo "  Linux: xdg-open dashboards/html/index.html"
echo "  Or navigate to: $(pwd)/dashboards/html/index.html"
echo ""

# Auto-open on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Opening dashboards in browser..."
    open dashboards/html/index.html
fi
