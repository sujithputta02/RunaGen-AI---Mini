# Power BI Data Import Guide

## Files Exported

1. **skills.csv** - All skills data from MongoDB
2. **jobs.csv** - Job postings data
3. **career_transitions.csv** - Career pathway transitions
4. **salaries.csv** - Salary data by role and experience
5. **skill_gaps.csv** - Skill gap analysis with priorities

## How to Import into Power BI

### Method 1: Direct CSV Import (Easiest)

1. Open Power BI Desktop
2. Click "Get Data" → "Text/CSV"
3. Select each CSV file one by one
4. Click "Load"

### Method 2: Using Connection Script (Recommended)

1. Open Power BI Desktop
2. Click "Get Data" → "Blank Query"
3. Go to "Advanced Editor"
4. Copy the content from `PowerBI_Connection.txt`
5. Paste into the editor
6. Update the `FolderPath` to match your system
7. Click "Done"

## Suggested Visualizations

### Dashboard 1: Career Transitions
- **Sankey Diagram**: from_role → to_role (use transition_count for width)
- **Bar Chart**: Average transition time by role
- **KPI Cards**: Success rates

### Dashboard 2: Skill Analysis
- **Bar Chart**: Top skills by demand_frequency
- **Scatter Plot**: Salary premium vs Market growth
- **Heatmap**: Skills by category and priority

### Dashboard 3: Salary Insights
- **Box Plot**: Salary distribution by role
- **Line Chart**: Salary vs Experience
- **Table**: Detailed salary breakdown

### Dashboard 4: Skill Gaps
- **Waterfall Chart**: Priority scores by skill
- **Pie Chart**: Skills by category
- **Matrix**: Skill metrics comparison

## Data Relationships

Create these relationships in Power BI:
- skills.csv → skill_gaps.csv (on skill name)
- jobs.csv → salaries.csv (on role)

## Refresh Data

To refresh data:
1. Run: `python src/powerbi/export_to_powerbi.py`
2. In Power BI, click "Refresh"

## Tips

- Use slicers for filtering by role, category, experience
- Add calculated columns for custom metrics
- Create bookmarks for different views
- Use drill-through for detailed analysis

---

Generated: {pd.Timestamp.now()}
RunaGen AI - ML-Powered Career Intelligence
