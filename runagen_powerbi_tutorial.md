# 🚀 RunaGen-AI: Power BI Ultimate Master Guide
**"Pin-to-Pin" Procedure for building a High-Resolution Market Intelligence Dashboard**

This document is the absolute blueprint. Follow it exactly to create a world-class AI analytics dashboard.

---

## 🎨 The HEX Color Bible (Aesthetics)
Use these codes in **Format Paintbrush > Visual > Colors** for a premium look:
- **Background (Canvas)**: `#0F172A` (Deep Slate)
- **Primary Accent (Bubbles/KPIs)**: `#38BDF8` (Neon Blue)
- **Salary Highs**: `#2DD4BF` (Teal)
- **Salary Lows**: `#6366F1` (Indigo)
- **Text (Headlines)**: `#F8FAFC` (Clean White)

---

## 🛠️ Phase 1: Data Injection & Logic Initialization
**Logic**: We use CSV because it's portable, but we must "Type-Cast" columns so the math works.

1. **Connect**: Click **"Get Data" > "Text/CSV"**. Select `runagen_market_intelligence.csv`.
2. **Transform**: Click **"Transform Data"**.
   - **Click Header** `Average_Salary_INR` > Right Click > **Change Type** > **Decimal Number**.
   - **Click Header** `Skills_Count` > Right Click > **Change Type** > **Whole Number**.
3. **Commit**: Click **"Close & Apply"** (Top Left).

---

## 🧪 Phase 2: Building the "DAX Math Engine"
**Logic**: Measures are dynamic. They change instantly when you click a city on the map.

1. **Count Logic**: Click **"New Measure"** (Top Ribbon).
   - Enter: `Total Opportunities = COUNTROWS('runagen_market_intelligence')`
2. **Benchmark Logic**: Click **"New Measure"**.
   - Enter: `Avg Market Salary = AVERAGE('runagen_market_intelligence'[Average_Salary_INR])`
3. **Intensity Logic**: Click **"New Column"** (Right Sidebar).
   - Enter: `Skill Intensity = IF('runagen_market_intelligence'[Skills_Count] > 5, "High Demand", "Standard")`

---

## 📊 Phase 3: Visual Construction (Pin-to-Pin)

### 1. 📍 Visual 1: The Geographic Heatmap
- **Visual**: Select the **Map** icon (Visualizations Pane).
- **Setup**: Drag `Location` into **Location** bucket. Drag `Total Opportunities` into **Bubble size**.
- **Formatting**:
  - **Bubbles**: Set Color to Neon Blue (`#38BDF8`).
  - **Category Labels**: On.
  - **Title**: "🗺️ AI Talent Clusters: Demand by City".
  - **Logic**: Uses bubbles to show job density. Larger bubbles = More hiring.

### 2. 📊 Visual 2: The Salary Spectrum (Bar Chart)
- **Visual**: Select **Clustered Bar Chart**.
- **Setup**:
  - **Y-Axis**: `Role_Title`.
  - **X-Axis**: `Average_Salary_INR`. (Click arrow and select **Average**).
- **Formatting**:
  - **Bars**: Go to **Colors** > **Conditional Formatting** (fx button).
  - **Color**: Set a gradient from Indigo (`#6366F1`) to Teal (`#2DD4BF`).
  - **Title**: "💰 Annual Package Variance by Career Path".
  - **Logic**: Immediately shows which roles are currently paying the premium.

### 3. 🌩️ Visual 3: The Talent Pulse (Word Cloud)
- **Visual**: Import **Word Cloud** (from AppSource).
- **Setup**:
  - **Category**: `Skills_Required`.
  - **Values**: `Total Opportunities`.
- **Formatting**:
  - **Stop Words**: On.
  - **Title**: "🌩️ Tech Stack Popularity index".
  - **Logic**: Visualizes "Keyword Frequency"—the bigger the word, the more recruiters are asking for it.

---

## 💎 Phase 4: Branding & Layout (The "WOW" Factor)
1. **Canvas Background**: Click empty space > **Format Paintbrush** > **Canvas Background**. Change Color to `#0F172A`. Set **Transparency** to `0%`.
2. **Master Header**: 
   - **Insert** > **Text Box**.
   - **Text**: `RUNAGEN-AI: GLOBAL CAREER INTELLIGENCE DASHBOARD`
   - **Font**: Segoe UI Bold, Size 28, Color White.
3. **Borders**: Click every chart.
   - **Format** > **General** > **Effects** > **Visual Border**.
   - **Color**: `#38BDF8` (Neon Blue).
   - **Rounded Corners**: `15px`.
4. **Slicer (The Interactive Funnel)**:
   - **Visual**: Slicer icon.
   - **Field**: `Experience_Level`.
   - **Style**: Change to **"Tile"** in settings.
   - **Logic**: Allows the user to toggle between "Junior" and "Senior" markets instantly.

---

## 🔎 Verification Checklist for your Friend:
- [ ] If I click a City, do the salaries change? (Yes = Success)
- [ ] Are the large bubbles over the correct cities? (Yes = Success)
- [ ] Is the data sorted from High Salary to Low Salary? (Yes = Success)

**Blueprint generated for RunaGen-AI Teams.** 📈🇮🇳✨
