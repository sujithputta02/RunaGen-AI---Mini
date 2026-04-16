# Tableau Public Dashboard Guide

## Overview
Create 4 interactive dashboards using Tableau Public to visualize career intelligence data from the RunaGen AI ML-ETL project.

## Prerequisites
- Tableau Public account (free): https://public.tableau.com/
- CSV files in `powerbi_data/` folder

## Step-by-Step Instructions

### SHEET 1: Career Transitions Dashboard

**Goal**: Show career pathway transitions and success rates

1. **Upload Data**:
   - Open Tableau Public
   - Click "Connect to Data" → "Text file"
   - Select `career_transitions.csv`
   - Click "Sheet 1" at bottom

2. **Create Bar Chart**:
   - Drag `from_role` to Rows
   - Drag `transition_count` to Columns
   - Drag `to_role` to Color
   - Sort by transition_count (descending)

3. **Add Labels**:
   - Drag `transition_count` to Label
   - Right-click axis → Format → Add title "Career Transitions"

4. **Filter Top Transitions**:
   - Drag `transition_count` to Filters
   - Select "Top" → "By field" → Top 20

---

### SHEET 2: Skills Analysis Dashboard

**Goal**: Show most in-demand skills and their market value

1. **Add New Data Source**:
   - Click "Data" menu → "New Data Source"
   - Select `skills.csv`
   - Click "Sheet 2" at bottom (or click + icon to add new sheet)

2. **Create Horizontal Bar Chart**:
   - Drag `skill_name` to Rows
   - Drag `demand_frequency` to Columns
   - Drag `category` to Color
   - Sort by demand_frequency (descending)

3. **Add Salary Premium**:
   - Drag `salary_premium` to Size
   - This shows which skills pay more (bigger bars = higher premium)

4. **Filter Top Skills**:
   - Drag `demand_frequency` to Filters
   - Select "Top" → "By field" → Top 30

5. **Format**:
   - Right-click axis → Format
   - Title: "Top In-Demand Skills by Category"

---

### SHEET 3: Salary Insights Dashboard

**Goal**: Show salary ranges by role and experience level

1. **Add New Data Source**:
   - Click "Data" menu → "New Data Source"
   - Select `salaries.csv`
   - Click "Sheet 3" at bottom

2. **Create Box Plot**:
   - Drag `role` to Rows
   - Drag `median_salary` to Columns
   - Drag `min_salary` to Columns (add as reference line)
   - Drag `max_salary` to Columns (add as reference line)

3. **Alternative: Simple Bar Chart**:
   - Drag `role` to Rows
   - Drag `median_salary` to Columns
   - Drag `experience_level` to Color
   - Sort by median_salary (descending)

4. **Add Salary Labels**:
   - Drag `median_salary` to Label
   - Format as Currency: Right-click → Format → Currency (Custom) → $0K

5. **Filter**:
   - Drag `experience_level` to Filters
   - Select levels you want to show (Entry, Mid, Senior)

---

### SHEET 4: Skill Gaps Dashboard

**Goal**: Show skill gaps and learning priorities

1. **Add New Data Source**:
   - Click "Data" menu → "New Data Source"
   - Select `skill_gaps.csv`
   - Click "Sheet 4" at bottom

2. **Create Heatmap**:
   - Drag `skill_name` to Rows
   - Drag `category` to Columns
   - Drag `priority_score` to Color
   - Drag `priority_score` to Label

3. **Color Formatting**:
   - Click Color → Edit Colors
   - Choose "Red-Yellow-Green Diverging"
   - Higher priority = Red (urgent)
   - Lower priority = Green (less urgent)

4. **Alternative: Treemap**:
   - Change mark type to "Square"
   - Drag `skill_name` to Label
   - Drag `priority_score` to Size
   - Drag `category` to Color

5. **Filter Top Gaps**:
   - Drag `priority_score` to Filters
   - Select "Top" → "By field" → Top 25

---

### FINAL STEP: Create Combined Dashboard

1. **Create Dashboard**:
   - Click "Dashboard" menu → "New Dashboard"
   - Or click the dashboard icon at bottom

2. **Add All Sheets**:
   - Drag "Sheet 1" (Career Transitions) to top-left
   - Drag "Sheet 2" (Skills) to top-right
   - Drag "Sheet 3" (Salaries) to bottom-left
   - Drag "Sheet 4" (Skill Gaps) to bottom-right

3. **Resize and Arrange**:
   - Adjust sizes so all 4 visualizations fit nicely
   - Use "Tiled" layout for automatic arrangement

4. **Add Title**:
   - Drag "Text" object to top
   - Type: "RunaGen AI - Career Intelligence Dashboard"
   - Format: Bold, Size 20

5. **Add Filters** (Optional):
   - Right-click any visualization → "Filters" → "Add to Dashboard"
   - This allows interactive filtering across all sheets

---

### PUBLISH TO TABLEAU PUBLIC

1. **Save Workbook**:
   - Click "File" → "Save to Tableau Public"
   - Sign in to your Tableau Public account
   - Name: "RunaGen-AI-Career-Intelligence"

2. **Get Shareable Link**:
   - After publishing, copy the URL
   - Format: `https://public.tableau.com/views/RunaGen-AI-Career-Intelligence/Dashboard1`

3. **Share**:
   - Click "Share" button
   - Copy embed code or direct link
   - Add to your project documentation

---

## Quick Tips

### For Each Sheet:
- **Rows** = Categories (what you want to compare)
- **Columns** = Values (numbers to measure)
- **Color** = Additional dimension (categories or ranges)
- **Size** = Emphasis (bigger = more important)
- **Label** = Show actual numbers on chart

### Common Issues:
- **Can't find CSV**: Make sure file path is correct
- **Data not showing**: Check if fields are in correct shelf (Rows/Columns)
- **Too many items**: Use Filters to show Top N items
- **Colors not working**: Drag field to Color shelf, not Columns

### Best Practices:
- Sort by the main metric (descending)
- Show Top 20-30 items (not all data)
- Use consistent colors across dashboards
- Add clear titles and labels
- Format numbers (currency, percentages)

---

## Expected Results

### Dashboard 1: Career Transitions
- Shows which career moves are most common
- Identifies popular transition paths
- Helps users plan career changes

### Dashboard 2: Skills Analysis
- Highlights most in-demand skills
- Shows which skills pay premium salaries
- Organized by skill category

### Dashboard 3: Salary Insights
- Displays salary ranges by role
- Compares compensation across experience levels
- Helps with salary negotiations

### Dashboard 4: Skill Gaps
- Identifies critical skill gaps
- Prioritizes learning opportunities
- Guides professional development

---

## Troubleshooting

**Q: I uploaded career_transitions.csv twice and it shows "career-transitions (2)"**
A: That's fine! Tableau adds (2) to avoid duplicates. Just use the latest one.

**Q: Can I add multiple CSV files to Sheet 1?**
A: No, each sheet uses one data source. Create separate sheets for each CSV, then combine in Dashboard.

**Q: How do I change from Sheet 1 to Sheet 2?**
A: Click the sheet tabs at the bottom of the screen, or click the "+" icon to add new sheet.

**Q: Where do I drag fields?**
A: Look for the shelves at the top: Columns, Rows, Filters, Marks (Color, Size, Label, Detail)

**Q: My chart looks wrong**
A: Check the "Show Me" panel on the right - it suggests best chart types for your data.

---

## Data Files Summary

| File | Records | Use Case |
|------|---------|----------|
| career_transitions.csv | ~500 | Career pathway analysis |
| skills.csv | ~200 | Skill demand and value |
| salaries.csv | ~150 | Compensation insights |
| skill_gaps.csv | ~100 | Learning priorities |
| jobs.csv | ~1000 | Job market trends |

---

## Next Steps After Publishing

1. Copy the Tableau Public URL
2. Add to your project README
3. Include in presentation slides
4. Share with faculty for review
5. Embed in project website (optional)

---

**Created for**: RunaGen AI ML-ETL Project  
**Purpose**: Faculty review and project demonstration  
**Tool**: Tableau Public (Free)  
**Data Source**: MongoDB → CSV exports
