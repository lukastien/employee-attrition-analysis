# Employee Attrition & Retention Analysis

Predicting employee attrition risk and quantifying the cost impact of turnover, using SQL analytics, classification modeling, an Excel cost-of-turnover model, and a Tableau Public dashboard.

> **Status:** Analysis complete (portfolio project, Jul 2026). Illustrative results on a public HR dataset — not advice for a specific employer.

## Business Question

Which employees are at the highest risk of leaving, what factors drive that risk, and how much could a targeted retention program realistically save?

## Key Results

| Finding | Result |
|---------|--------|
| Overall attrition | **16.1%** (237 of 1,470 employees) |
| Top driver | **OverTime** — #1 in logistic regression and XGBoost; overtime Yes **30.5%** attrition vs No **10.4%** |
| Model performance (held-out test) | Logistic regression ROC-AUC **0.81**; XGBoost ROC-AUC **0.75** |
| At-risk cohort (current employees) | **31** flagged at P(attrition) ≥ 45% |
| Projected retention savings | **~$455,000** |

**Recommendation (summary):** Run a focused retention pilot on the flagged high-risk group — overtime/workload review, structured manager stay conversations, and selective retention support. Details: [`reports/strategy_brief.md`](reports/strategy_brief.md).

## Data

Real, public dataset: [IBM HR Analytics Employee Attrition & Performance](https://raw.githubusercontent.com/IBM/employee-attrition-aif360/master/data/emp_attrition.csv) — 1,470 employee records, 35 features (demographics, compensation, job role, satisfaction scores, and attrition outcome).

Raw source: `data/raw/employee_attrition.csv`  
Cleaned extract: `data/processed/employee_attrition_clean.csv`

## Deliverables

| Deliverable | Location |
|-------------|----------|
| SQL schema + analytics | [`sql/schema.sql`](sql/schema.sql), [`sql/queries.sql`](sql/queries.sql) |
| EDA + modeling notebook | [`notebooks/01_eda_and_modeling.ipynb`](notebooks/01_eda_and_modeling.ipynb) |
| Model training + risk scores | [`src/model_training.py`](src/model_training.py), `data/processed/employee_risk_scores.csv` |
| Excel cost-of-turnover model | [`reports/cost_of_turnover.xlsx`](reports/cost_of_turnover.xlsx) |
| Tableau Public extracts + build guide | [`dashboard/`](dashboard/) — [README](dashboard/README.md) |
| Strategy brief | [`reports/strategy_brief.md`](reports/strategy_brief.md) |
| Market context (light) | [`reports/market_research_brief.md`](reports/market_research_brief.md) |

**Tableau Public URL:** _TBD — publish from `dashboard/` CSVs using [dashboard/README.md](dashboard/README.md), then paste the link here_

## Project Structure

```
employee-attrition-analysis/
├── data/
│   ├── raw/                  # Original IBM HR extract
│   └── processed/            # Clean CSV, risk scores (SQLite DB gitignored)
├── sql/
│   ├── schema.sql            # DDL + documented analytics
│   ├── queries.sql           # Runnable attrition queries
│   └── run_analytics.sh
├── notebooks/
│   └── 01_eda_and_modeling.ipynb
├── src/
│   ├── etl_pipeline.py
│   ├── model_training.py
│   ├── build_cost_model.py
│   └── export_tableau_extracts.py
├── reports/
│   ├── cost_of_turnover.xlsx
│   ├── strategy_brief.md
│   └── market_research_brief.md
├── dashboard/
│   ├── attrition_summary.csv
│   ├── at_risk_employees.csv
│   └── README.md
├── requirements.txt
└── README.md
```

## Methodology

1. **Data processing** — clean the HR extract and load SQLite; SQL attrition rates by department, tenure, overtime, and salary band
2. **Modeling** — logistic regression baseline + XGBoost; feature importance identifies overtime as the top driver; export per-employee risk scores
3. **Cost modeling** — Excel workbook flags high-risk current employees and projects retention savings (~$455k under documented assumptions)
4. **Dashboard** — Tableau Public views from prepared CSVs (attrition breakdowns, at-risk table, cost KPIs)
5. **Recommendation** — strategy brief for non-technical stakeholders

## Tools

Python (pandas, scikit-learn, XGBoost, openpyxl), SQL (SQLite), Excel, Tableau Public

## Status / Checklist

- [x] Repo structure + real dataset sourced
- [x] ETL pipeline (`src/etl_pipeline.py`)
- [x] SQL schema + exploratory queries (`sql/schema.sql`, `sql/queries.sql`)
- [x] EDA + modeling notebook / training script
- [x] Cost-of-turnover Excel model (`reports/cost_of_turnover.xlsx`)
- [x] Tableau-ready extracts + Public build guide (`dashboard/`)
- [x] Strategy brief write-up (`reports/strategy_brief.md`)
- [ ] Tableau Public URL published and linked above _(your step after publishing)_

## Quick start

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
# macOS only if xgboost fails to load OpenMP:
#   bash scripts/fix_xgboost_macos.sh

.venv/bin/python src/etl_pipeline.py
bash sql/run_analytics.sh
.venv/bin/python src/model_training.py
.venv/bin/python src/build_cost_model.py
.venv/bin/python src/export_tableau_extracts.py
```

---
*Self-directed portfolio project using a real public dataset for illustrative analysis.*
