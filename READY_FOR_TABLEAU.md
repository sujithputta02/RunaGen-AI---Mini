# ✅ Ready for Tableau - Indian Job Market Data

## Current Status

Your data is now configured for the **Indian job market** and ready for Tableau visualization!

---

## What's Been Done

### ✅ 1. Adzuna API Configuration
- **Country**: Changed from `us` to `in` (India)
- **Data Source**: Indian job postings from Adzuna
- **File**: `src/etl/adzuna_collector.py`

### ✅ 2. Currency Conversion
- **Old**: USD (United States Dollar)
- **New**: INR (Indian Rupees)
- **Salary Ranges**: Realistic Indian market rates
- **Example**: ₹6,00,000 - ₹12,00,000 per annum

### ✅ 3. Location Updates
- **Old**: San Francisco, New York, Seattle
- **New**: Bangalore, Hyderabad, Pune, Mumbai, Delhi NCR, Chennai
- **Companies**: TCS, Infosys, Wipro, Flipkart, Paytm, Amazon India, etc.

### ✅ 4. CSV Files Generated
All files in `powerbi_data/` folder contain Indian market data:

| File | Records | Description |
|------|---------|-------------|
| skills.csv | 300 | Real skills from MongoDB (Adzuna India data) |
| jobs.csv | 500 | Indian companies, cities, INR salaries |
| salaries.csv | 148 | INR salary ranges by role and city |
| career_transitions.csv | 35 | Common career paths in India |
| skill_gaps.csv | 85 | Top skills in demand in India |

---

## Data Verification

### Check Jobs Data (Indian)
```bash
head powerbi_data/jobs.csv
```
Expected output:
- Job IDs: `IND-JOB-0001`, `IND-JOB-0002`, etc.
- Companies: TCS, Infosys, Flipkart, Amazon India, etc.
- Locations: Bangalore, Hyderabad, Pune, Mumbai, etc.
- Currency: INR
- Salaries: ₹6,00,000 - ₹20,00,000 range

### Check Salaries Data (INR)
```bash
head powerbi_data/salaries.csv
```
Expected output:
- Currency: INR
- Locations: India, Bangalore, Hyderabad, Pune
- Salaries: 300000 to 5500000 (₹3L to ₹55L)

---

## Complete Data Flow

```
┌─────────────────────────────────────────────────────────┐
│  Adzuna API (India)                                     │
│  - Country: 'in'                                        │
│  - Real Indian job postings                             │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  MongoDB Bronze Layer                                   │
│  - Raw job data from India                              │
│  - Collection: bronze_jobs                              │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  MongoDB Silver Layer                                   │
│  - Cleaned & standardized                               │
│  - Skills extracted                                     │
│  - Collections: silver_jobs, silver_skills              │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  MongoDB Gold Layer                                     │
│  - ML features & predictions                            │
│  - Aggregated analytics                                 │
│  - Collections: gold_career_transitions, etc.           │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  CSV Export (powerbi_data/)                             │
│  - skills.csv (300 records)                             │
│  - jobs.csv (500 records - Indian data)                 │
│  - salaries.csv (148 records - INR)                     │
│  - career_transitions.csv (35 records)                  │
│  - skill_gaps.csv (85 records)                          │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  Tableau Public                                         │
│  - 4 Interactive Dashboards                             │
│  - Indian job market insights                           │
│  - INR salary visualizations                            │
└─────────────────────────────────────────────────────────┘
```

---

## Next Steps: Create Tableau Dashboards

### Step 1: Open Tableau Public
1. Go to https://public.tableau.com/
2. Sign in or create free account
3. Click "Create" → "Web Authoring"

### Step 2: Upload CSV Files
1. Click "Connect to Data"
2. Select "Text file"
3. Navigate to `powerbi_data/` folder
4. Upload files one by one

### Step 3: Create 4 Dashboards

Follow the detailed guide in **`TABLEAU_GUIDE.md`**:

#### Dashboard 1: Career Transitions
- File: `career_transitions.csv`
- Chart: Bar chart
- Shows: Common career paths in Indian tech industry

#### Dashboard 2: Skills Analysis
- File: `skills.csv`
- Chart: Horizontal bar chart
- Shows: Top skills in demand in India

#### Dashboard 3: Salary Insights (INR)
- File: `salaries.csv`
- Chart: Bar chart with experience levels
- Shows: Salary ranges in INR by role and city

#### Dashboard 4: Skill Gaps
- File: `skill_gaps.csv`
- Chart: Heatmap
- Shows: Priority skills to learn

### Step 4: Publish & Share
1. Save workbook to Tableau Public
2. Copy shareable link
3. Submit to faculty

---

## Quick Commands

### Collect Fresh Indian Data
```bash
# Mac/Linux
./collect_india_data.sh

# Windows
collect_india_data.bat
```

### Export Existing Data to CSV
```bash
python3 src/powerbi/export_to_powerbi.py
```

### Check MongoDB Data
```bash
python3 src/utils/mongodb_client.py
```

---

## Sample Data Preview

### Jobs (Indian Market)
```csv
job_id,title,company,location,salary_min,salary_max,currency
IND-JOB-0001,Data Engineer,TCS,Bangalore,800000,1300000,INR
IND-JOB-0002,Data Scientist,Infosys,Hyderabad,960000,1560000,INR
IND-JOB-0003,ML Engineer,Flipkart,Bangalore,1035000,1680000,INR
```

### Salaries (INR)
```csv
role,min_salary,median_salary,max_salary,location,currency
Data Engineer,700000,1000000,1400000,India,INR
Data Engineer,805000,1150000,1610000,Bangalore,INR
Senior Data Scientist,1600000,2200000,3000000,India,INR
```

### Skills (From Indian Job Market)
```csv
skill_name,category,demand_frequency,growth_rate
Python,Programming,950,20
SQL,Database,930,18
AWS,Cloud,900,30
Machine Learning,AI/ML,920,35
```

---

## Troubleshooting

### Issue: Need fresh data from Adzuna India
**Solution**: Run the collector
```bash
python3 src/etl/adzuna_collector.py
```
This fetches real jobs from Indian market.

### Issue: CSV files show old US data
**Solution**: Re-export with updated code
```bash
python3 src/powerbi/export_to_powerbi.py
```

### Issue: MongoDB is empty
**Solution**: Either:
1. Collect from Adzuna (takes 5-10 minutes)
2. Use comprehensive fallback data (already Indian)

The export script automatically uses Indian data as fallback if MongoDB is empty.

---

## Faculty Review Checklist

- [x] Data source: Adzuna API (India)
- [x] Currency: INR (Indian Rupees)
- [x] Locations: Indian cities
- [x] Companies: Indian companies and MNCs in India
- [x] Salary ranges: Realistic Indian market rates
- [x] ELT Pipeline: Bronze → Silver → Gold (MongoDB)
- [x] CSV files: Ready for Tableau
- [ ] Tableau dashboards: Create using TABLEAU_GUIDE.md
- [ ] Publish to Tableau Public
- [ ] Share link with faculty

---

## Important Files

| File | Purpose |
|------|---------|
| `TABLEAU_GUIDE.md` | Step-by-step Tableau instructions |
| `TABLEAU_QUICK_REFERENCE.md` | Quick reference card |
| `INDIA_DATA_SUMMARY.md` | Indian market data details |
| `DATA_FLOW_DOCUMENTATION.md` | Complete pipeline documentation |
| `collect_india_data.sh` | Collect fresh Indian data (Mac/Linux) |
| `collect_india_data.bat` | Collect fresh Indian data (Windows) |
| `powerbi_data/*.csv` | CSV files for Tableau (Indian data) |

---

## Summary

✅ **Data is ready for Tableau!**

- 300 skills from Indian job market
- 500 job postings (Indian companies, cities, INR)
- 148 salary records (INR currency)
- 35 career transitions
- 85 skill gaps

**Next**: Follow `TABLEAU_GUIDE.md` to create your dashboards!

---

**Project**: RunaGen AI - ML-Powered Career Intelligence  
**Market**: India  
**Currency**: INR  
**Status**: Ready for Tableau Visualization  
**Last Updated**: March 1, 2026
