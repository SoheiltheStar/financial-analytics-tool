# 📊 Financial Analytics Tool

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)

A local-only month-over-month financial analytics tool built with Python, Streamlit, DuckDB, and Plotly.

**No cloud, no SaaS** — All data stays on your machine.

---

## ✨ Features

### Core Functionality
- **Excel Upload** — Import monthly financial reports (.xlsx)
- **Month Tagging** — Tag each upload with YYYY-MM format
- **Historical Snapshots** — Store and compare multiple months
- **One-Time Column Mapping** — Configure once, reuse forever
- **Ledger Mapping** — Map ledgers to buckets/drivers/controllable flags

### Dashboards
- **Market Scoreboard** — Overview of all markets with Actual vs Plan vs Forecast
- **MoM Analysis** — Month-over-month changes with top movers
- **Pareto Chart** — Identify vital few items driving variance
- **Trend Analysis** — 3-6 month performance trends
- **Action Plan** — Auto-generated action items based on variance thresholds

### Export
- Export charts as **PNG** or **PDF**
- Export action plans as **CSV**

---

## 🖥️ Compatibility

| Platform | Supported |
|----------|-----------|
| macOS    | ✅        |
| Windows  | ✅        |
| Linux    | ✅        |

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate Sample Data (Optional)

```bash
python sample_data_generator.py
```

This creates 6 months of sample financial data in `sample_data/` folder.

### 3. Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📁 Project Structure

```
├── app.py                    # Main Streamlit application
├── database.py               # DuckDB database layer
├── charts.py                 # Plotly chart functions
├── sample_data_generator.py  # Demo data generator
├── requirements.txt          # Python dependencies
├── data/                     # DuckDB database (auto-created)
└── sample_data/              # Sample Excel files (after running generator)
```

---

## 📖 Usage Guide

### First-Time Setup

1. **Configure Column Mapping** (Settings → Column Mapping)
   - Upload any sample Excel file
   - Map: Market, Ledger, Actual, Plan, Forecast columns
   - Save (one-time only)

2. **Configure Ledger Mapping** (Settings → Ledger Mapping)
   - Upload ledger mapping Excel with columns:
     - `ledger`: Account name
     - `bucket`: Category (Revenue, COGS, SG&A, etc.)
     - `driver`: Cost driver (Volume, Headcount, Fixed, etc.)
     - `controllable`: TRUE/FALSE

### Monthly Workflow

1. **Upload Report** (Home & Upload)
   - Upload your Excel file
   - Enter month tag (e.g., 2024-12)
   - Click "Save Snapshot"

2. **Analyze** (Navigate to any dashboard)
   - Market Scoreboard: Overall performance
   - MoM Analysis: Compare two months
   - Pareto: Find biggest variances
   - Trends: Multi-month patterns
   - Action Plan: Prioritized issues

3. **Export**
   - Click export buttons on any chart
   - Download PNG, PDF, or CSV

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend  | Streamlit  |
| Database  | DuckDB     |
| Charts    | Plotly     |
| Data      | Pandas     |
| Export    | Kaleido    |

---

## 📊 Sample Data Structure

Your Excel files should have columns like:

| Market       | Ledger Account      | Actual    | Plan      | Forecast  |
|--------------|---------------------|-----------|-----------|-----------|
| North America| Revenue - Products  | 1,500,000 | 1,400,000 | 1,450,000 |
| Europe       | COGS - Materials    | -600,000  | -580,000  | -590,000  |
| ...          | ...                 | ...       | ...       | ...       |

---

## 🔒 Privacy & Security

- **100% Local** — No data leaves your machine
- **No Cloud Dependencies** — Works offline
- **DuckDB** — Fast, embedded analytics database
- **No Telemetry** — We don't track anything

---

## 📝 License

MIT License — Use freely for personal or commercial projects.

---

## 🤝 Support

Questions or issues? Feel free to reach out!

