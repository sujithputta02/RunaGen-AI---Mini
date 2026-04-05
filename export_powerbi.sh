#!/bin/bash
# Export data for Power BI

echo "📊 Exporting Data for Power BI..."
echo "=================================="
echo ""

cd "$(dirname "$0")"

python3 src/powerbi/export_to_powerbi.py

echo ""
echo "=================================="
echo "✅ Export complete!"
echo ""
echo "Next steps:"
echo "1. Open Power BI Desktop"
echo "2. Import CSV files from: powerbi_data/"
echo "3. Or use the connection script in: powerbi_data/PowerBI_Connection.txt"
echo ""
echo "See powerbi_data/README.md for detailed instructions"
