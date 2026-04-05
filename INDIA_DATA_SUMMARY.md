# RunaGen AI - Indian Job Market Data Summary

## Data Configuration

All data has been configured for the **Indian job market**:

### 1. Adzuna API Configuration
- **Country Code**: `in` (India)
- **API Endpoint**: `https://api.adzuna.com/v1/api/jobs/in/search/`
- **Data Source**: Real Indian job postings from Adzuna

### 2. Currency
- **All Salaries**: INR (Indian Rupees)
- **Format**: Annual salary (per annum)
- **Example**: ₹6,00,000 - ₹12,00,000 per annum

### 3. Locations
Indian cities covered in the dataset:
- **Bangalore** (Tech hub - highest salaries)
- **Hyderabad** (Growing tech center)
- **Pune** (IT services hub)
- **Mumbai** (Financial capital)
- **Delhi NCR** (Includes Noida, Gurgaon)
- **Chennai** (South India tech center)
- **Kolkata** (Eastern region)
- **Ahmedabad** (Western region)
- **Remote** (Work from home)

### 4. Companies
Indian companies and MNCs with Indian operations:
- **Indian IT Giants**: TCS, Infosys, Wipro, HCL, Tech Mahindra
- **Global MNCs**: Accenture India, Amazon India, Microsoft India, Google India
- **Indian Startups**: Flipkart, Paytm, Swiggy, Zomato, PhonePe, CRED, Razorpay
- **Product Companies**: Freshworks, Zoho, Ola, Byju's, Unacademy, Meesho

---

## Salary Ranges (INR per annum)

### Entry Level (0-2 years)
| Role | Min | Median | Max |
|------|-----|--------|-----|
| Junior Data Analyst | ₹3,00,000 | ₹4,50,000 | ₹6,00,000 |
| Junior Data Engineer | ₹4,00,000 | ₹6,00,000 | ₹8,00,000 |
| Junior Data Scientist | ₹5,00,000 | ₹7,00,000 | ₹9,00,000 |
| Junior Software Engineer | ₹3,50,000 | ₹5,50,000 | ₹7,50,000 |

### Mid Level (2-5 years)
| Role | Min | Median | Max |
|------|-----|--------|-----|
| Data Engineer | ₹7,00,000 | ₹10,00,000 | ₹14,00,000 |
| Data Scientist | ₹8,00,000 | ₹12,00,000 | ₹16,00,000 |
| ML Engineer | ₹9,00,000 | ₹13,00,000 | ₹18,00,000 |
| Software Engineer | ₹6,00,000 | ₹9,00,000 | ₹13,00,000 |
| DevOps Engineer | ₹7,00,000 | ₹10,00,000 | ₹14,00,000 |

### Senior Level (5-8 years)
| Role | Min | Median | Max |
|------|-----|--------|-----|
| Senior Data Engineer | ₹14,00,000 | ₹19,00,000 | ₹25,00,000 |
| Senior Data Scientist | ₹16,00,000 | ₹22,00,000 | ₹30,00,000 |
| Senior ML Engineer | ₹17,00,000 | ₹23,00,000 | ₹32,00,000 |
| Senior Software Engineer | ₹13,00,000 | ₹18,00,000 | ₹24,00,000 |
| Cloud Architect | ₹15,00,000 | ₹21,00,000 | ₹28,00,000 |

### Lead/Principal Level (8+ years)
| Role | Min | Median | Max |
|------|-----|--------|-----|
| Lead Data Engineer | ₹20,00,000 | ₹28,00,000 | ₹38,00,000 |
| Lead Data Scientist | ₹22,00,000 | ₹30,00,000 | ₹42,00,000 |
| Principal Data Engineer | ₹25,00,000 | ₹35,00,000 | ₹50,00,000 |
| Staff Data Scientist | ₹27,00,000 | ₹38,00,000 | ₹55,00,000 |
| ML Architect | ₹24,00,000 | ₹34,00,000 | ₹48,00,000 |

---

## Location-Based Salary Multipliers

| City | Multiplier | Reason |
|------|------------|--------|
| Bangalore | 1.15x | Highest tech concentration, startup hub |
| Hyderabad | 1.10x | Growing tech center, lower cost of living |
| Pune | 1.10x | IT services hub, good infrastructure |
| Mumbai | 1.00x | High cost of living offset by opportunities |
| Delhi NCR | 1.00x | Government + private sector mix |
| Chennai | 1.00x | Established IT presence |
| Other cities | 1.00x | Base salary |

---

## CSV Files Generated

### 1. skills.csv (300 records)
- Real skills extracted from MongoDB (Adzuna API data)
- Categories: Programming, Database, Cloud, AI/ML, DevOps, etc.
- Demand frequency and market trends

### 2. jobs.csv (500 records)
- **Job IDs**: IND-JOB-0001 to IND-JOB-0500
- **Companies**: Indian companies and MNCs
- **Locations**: Indian cities
- **Salaries**: INR (Indian Rupees)
- **Remote Options**: Yes/No
- **Experience Required**: 0-2, 2-5, 5-8, 8+ years

### 3. salaries.csv (148 records)
- **Currency**: INR
- **Roles**: 37 different tech roles
- **Locations**: 4 city variations per role
- **Experience Levels**: Entry, Mid, Senior, Lead/Principal

### 4. career_transitions.csv (35 records)
- Common career paths in Indian tech industry
- Transition counts and success rates
- Average time to transition

### 5. skill_gaps.csv (85 records)
- Top skills in demand in India
- Priority scores for learning
- Salary premium per skill
- Market growth rates

---

## Data Pipeline Flow

```
Adzuna API (India)
    ↓
MongoDB Bronze Layer (Raw Indian job data)
    ↓
MongoDB Silver Layer (Cleaned & standardized)
    ↓
MongoDB Gold Layer (ML features & predictions)
    ↓
CSV Export (powerbi_data/)
    ↓
Tableau Public (Visualizations)
```

---

## How to Collect Fresh Indian Data

### Option 1: Run Complete Pipeline
```bash
python run_full_pipeline_for_tableau.py
```
Choose option 1 to:
1. Fetch jobs from Adzuna India API
2. Process through ELT pipeline
3. Train ML models
4. Export to CSV

### Option 2: Only Collect from Adzuna
```bash
python src/etl/adzuna_collector.py
```
This will fetch 2000 jobs per query from Indian job market.

### Option 3: Use Existing Data
The current CSV files already contain:
- 300 real skills from MongoDB
- 500 Indian job postings
- 148 salary records (INR)
- 35 career transitions
- 85 skill gaps

---

## Tableau Visualization Guide

Follow `TABLEAU_GUIDE.md` to create dashboards with Indian data:

### Dashboard 1: Career Transitions
- Shows common career paths in Indian tech industry
- Transition success rates
- Average time to move between roles

### Dashboard 2: Skills Analysis
- Top skills in demand in India
- Skills by category (Programming, Cloud, AI/ML, etc.)
- Salary premium for each skill

### Dashboard 3: Salary Insights (INR)
- Salary ranges by role and experience
- City-wise salary comparison
- Entry to Principal level progression

### Dashboard 4: Skill Gaps
- Priority skills to learn
- Market growth rates
- Learning difficulty and time estimates

---

## Key Differences from US Data

| Aspect | US Data | India Data |
|--------|---------|------------|
| Currency | USD | INR |
| Salary Range | $60K - $250K | ₹3L - ₹55L |
| Cities | SF, NY, Seattle | Bangalore, Hyderabad, Pune |
| Companies | FAANG | TCS, Infosys, Flipkart, etc. |
| Cost of Living | Higher | Lower |
| Remote Work | Common | Growing |

---

## Verification

To verify Indian data is being used:

```bash
# Check jobs file
head powerbi_data/jobs.csv
# Should show: IND-JOB-XXXX, Indian companies, Indian cities, INR

# Check salaries file
head powerbi_data/salaries.csv
# Should show: INR currency, Indian cities, lakhs range

# Check Adzuna collector
grep "country=" src/etl/adzuna_collector.py
# Should show: country='in'
```

---

## Faculty Review Points

✅ **Data Source**: Adzuna API (India)  
✅ **Currency**: INR (Indian Rupees)  
✅ **Locations**: Indian cities (Bangalore, Hyderabad, etc.)  
✅ **Companies**: Indian companies and MNCs in India  
✅ **Salary Ranges**: Realistic Indian market rates  
✅ **ELT Pipeline**: Bronze → Silver → Gold (MongoDB)  
✅ **ML Models**: Trained on Indian job market data  
✅ **Visualization**: Tableau Public dashboards

---

## Next Steps

1. ✅ Data configured for India
2. ✅ CSV files generated with Indian data
3. ⏳ Create Tableau dashboards (follow TABLEAU_GUIDE.md)
4. ⏳ Publish to Tableau Public
5. ⏳ Share link with faculty

---

**Project**: RunaGen AI - ML-Powered Career Intelligence  
**Market**: India  
**Currency**: INR  
**Data Source**: Adzuna API (India) + MongoDB  
**Last Updated**: March 1, 2026
