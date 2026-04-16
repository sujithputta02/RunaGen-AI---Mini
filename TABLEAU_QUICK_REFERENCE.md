# Tableau Quick Reference Card

## 🎯 Your Task: Create 4 Dashboards

### ✅ Sheet 1: Career Transitions (DONE)
- File: `career_transitions.csv`
- Chart: Bar chart
- Rows: `from_role`
- Columns: `transition_count`
- Color: `to_role`

---

### 📊 Sheet 2: Skills Analysis (TODO)

**Steps**:
1. Click "Data" → "New Data Source" → Select `skills.csv`
2. Click "+" at bottom to add new sheet (Sheet 2)
3. Drag `skill_name` to Rows
4. Drag `demand_frequency` to Columns
5. Drag `category` to Color
6. Sort descending
7. Add filter: Top 30 by demand_frequency

**Result**: Horizontal bar chart showing top skills by category

---

### 💰 Sheet 3: Salary Insights (TODO)

**Steps**:
1. Click "Data" → "New Data Source" → Select `salaries.csv`
2. Click "+" at bottom to add new sheet (Sheet 3)
3. Drag `role` to Rows
4. Drag `median_salary` to Columns
5. Drag `experience_level` to Color
6. Sort descending
7. Format salary as currency

**Result**: Bar chart showing salaries by role and experience

---

### 🎓 Sheet 4: Skill Gaps (TODO)

**Steps**:
1. Click "Data" → "New Data Source" → Select `skill_gaps.csv`
2. Click "+" at bottom to add new sheet (Sheet 4)
3. Drag `skill_name` to Rows
4. Drag `category` to Columns
5. Drag `priority_score` to Color
6. Drag `priority_score` to Label
7. Change color to Red-Yellow-Green

**Result**: Heatmap showing skill gaps by priority

---

### 📱 Final Dashboard (TODO)

**Steps**:
1. Click "Dashboard" → "New Dashboard"
2. Drag Sheet 1 to top-left
3. Drag Sheet 2 to top-right
4. Drag Sheet 3 to bottom-left
5. Drag Sheet 4 to bottom-right
6. Add title: "RunaGen AI - Career Intelligence"
7. Save to Tableau Public

---

## 🔑 Key Concepts

| Shelf | Purpose | Example |
|-------|---------|---------|
| **Rows** | What to compare | Roles, Skills, Categories |
| **Columns** | Numbers to measure | Counts, Salaries, Scores |
| **Color** | Group by category | Experience level, Category |
| **Size** | Emphasize importance | Salary premium, Priority |
| **Label** | Show values | Display numbers on chart |
| **Filters** | Limit data shown | Top 20, Specific roles |

---

## 🚀 Quick Actions

### Add New Data Source
```
Data menu → New Data Source → Text file → Select CSV
```

### Add New Sheet
```
Click "+" icon at bottom of screen
```

### Sort Data
```
Click sort icon on axis (ascending/descending)
```

### Filter Top N
```
Drag field to Filters → Top → By field → Enter number
```

### Change Chart Type
```
Click "Show Me" panel → Select chart type
```

### Format Numbers
```
Right-click field → Format → Number/Currency
```

---

## ⚠️ Common Mistakes

❌ **Don't**: Try to add multiple CSV files to one sheet  
✅ **Do**: Create separate sheets, combine in dashboard

❌ **Don't**: Show all data (too cluttered)  
✅ **Do**: Filter to Top 20-30 items

❌ **Don't**: Forget to sort by main metric  
✅ **Do**: Sort descending by count/value

❌ **Don't**: Use default colors  
✅ **Do**: Choose meaningful color schemes

---

## 📍 Where to Find Things

- **Add data**: Top menu → Data → New Data Source
- **Add sheet**: Bottom tabs → Click "+" icon
- **Add dashboard**: Bottom tabs → Dashboard icon
- **Change chart**: Right panel → "Show Me"
- **Format**: Right-click any element → Format
- **Publish**: Top menu → File → Save to Tableau Public

---

## 🎨 Recommended Colors

- **Career Transitions**: Blue gradient
- **Skills**: Category colors (automatic)
- **Salaries**: Green gradient (money)
- **Skill Gaps**: Red-Yellow-Green (priority)

---

## ✨ Pro Tips

1. **Name your sheets clearly** (right-click tab → Rename)
2. **Add titles to each chart** (drag "Text" to sheet)
3. **Use tooltips** (hover shows details automatically)
4. **Test filters** (make sure they work before publishing)
5. **Preview dashboard** (click "Device Preview" to check layout)

---

## 📤 Publishing Checklist

- [ ] All 4 sheets created
- [ ] Charts are sorted and filtered
- [ ] Labels and titles added
- [ ] Dashboard combines all sheets
- [ ] Dashboard title added
- [ ] Saved to Tableau Public
- [ ] URL copied for submission

---

## 🆘 Need Help?

**Issue**: Can't find where to drag fields  
**Solution**: Look for shelves at top: Columns, Rows, Filters, Marks

**Issue**: Chart looks wrong  
**Solution**: Check "Show Me" panel - it suggests best chart type

**Issue**: Too much data  
**Solution**: Add filter → Top N items

**Issue**: Colors not showing  
**Solution**: Drag field to "Color" in Marks card (left side)

---

**File Location**: `runagen-ml-etl/powerbi_data/*.csv`  
**Full Guide**: See `TABLEAU_GUIDE.md` for detailed instructions  
**Project**: RunaGen AI ML-ETL Career Intelligence Platform
