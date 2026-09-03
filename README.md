# Employee Attrition & Retention Analysis

Predicting employee attrition risk and quantifying the cost impact of turnover, using classification modeling and an interactive Tableau dashboard.

> **Status:** 🚧 Placeholder scaffold — full analysis in progress. This repo currently contains the project structure, real source data, and stub code to be filled in.

## Business Question

Which employees are at the highest risk of leaving, what factors drive that risk, and how much could a targeted retention program realistically save?

## Data

Real, public dataset: [IBM HR Analytics Employee Attrition & Performance](https://raw.githubusercontent.com/IBM/employee-attrition-aif360/master/data/emp_attrition.csv) — 1,470 employee records, 35 features (demographics, compensation, job role, satisfaction scores, and attrition outcome).

Data source: `data/raw/employee_attrition.csv`

## Project Structure

```
employee-attrition-analysis/
├── data/
│   ├── raw/                  # Original, unmodified dataset
│   └── processed/            # Cleaned data ready for modeling
├── sql/
│   └── schema.sql            # Relational schema + exploratory queries
├── notebooks/
│   └── 01_eda_and_modeling.ipynb   # EDA, feature engineering, modeling
├── src/
│   ├── etl_pipeline.py       # Data cleaning / loading script
│   └── model_training.py     # Model training + evaluation
├── reports/
│   ├── market_research_brief.md
│   └── strategy_brief.md
├── dashboard/
│   └── README.md             # Link to published Tableau dashboard
├── requirements.txt
└── README.md
```

## Methodology (planned)

1. **Data Processing** — clean and load data into a SQLite database; SQL queries for attrition rate by department, tenure, overtime, and salary band
2. **Modeling** — logistic regression baseline + XGBoost classifier to predict attrition risk; feature importance to identify key drivers
3. **Cost Modeling** — translate model output into an estimated cost-of-turnover and projected retention savings
4. **Dashboard** — Tableau dashboard flagging at-risk employees and visualizing attrition trends
5. **Recommendation** — a short strategy brief translating findings into an actionable retention plan

## Tools

Python (pandas, scikit-learn, XGBoost), SQL (SQLite), Excel, Tableau

## Status / To Do

- [x] Repo structure + real dataset sourced
- [ ] ETL pipeline (`src/etl_pipeline.py`)
- [ ] SQL schema + exploratory queries (`sql/schema.sql`)
- [ ] EDA + modeling notebook
- [ ] Cost-of-turnover Excel model
- [ ] Tableau dashboard
- [ ] Strategy brief write-up

---
*This is a self-directed portfolio project using a real public dataset for illustrative analysis.*
