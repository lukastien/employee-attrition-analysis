# Strategy Brief — Retention Recommendation

**Audience:** HR / People Operations leadership  
**Dataset:** IBM HR Analytics Employee Attrition (1,470 employees; illustrative portfolio analysis)  
**Date context:** Jul 2026 portfolio project

## Key Finding

**Overtime is the strongest driver of attrition risk in this workforce.**

Employees who work overtime leave at **30.5%**, versus **10.4%** for those who do not — roughly **three times** the attrition rate. The same signal ranks **#1** in both the logistic regression and XGBoost attrition models, ahead of role, tenure, and compensation features.

Early tenure and lower pay amplify risk as well (about **35%** attrition in the first two years; about **29%** in the lowest income quartile), but overtime is the clearest, most actionable lever that shows up consistently in both SQL analysis and predictive modeling.

Overall attrition in the dataset is **16.1%** (237 of 1,470 employees).

## Recommended Actions

Focus a 90-day retention pilot on the **31 current employees** flagged as high risk (model probability ≥ 45%):

1. **Workload and overtime review** — For each flagged employee (especially those marked OverTime = Yes), have the manager and HR partner audit hours, staffing coverage, and non-essential after-hours work. Cap or redistribute overtime where coverage allows; document exceptions.
2. **Structured manager check-ins** — Require a documented stay conversation within two weeks: career path, blockers, and one concrete relief action (role scope, schedule flexibility, or project load). Track completion in the same at-risk list used for the dashboard.
3. **Targeted retention support** — Where risk remains high after the check-in, deploy selective support (temporary workload relief, recognition/bonus, or internal mobility) rather than a broad across-the-board program. Prioritize early-tenure and lower-salary flagged employees, who show elevated baseline attrition.

## Projected Impact

Using the Excel cost-of-turnover model (`reports/cost_of_turnover.xlsx`):

| Metric | Estimate |
|--------|----------|
| Flagged current employees | 31 |
| Expected leavers without intervention | ~18 |
| Prevented leavers (42% program effectiveness) | ~7.6 |
| Replacement cost assumption | 150% of annual salary |
| **Projected savings** | **~$455,000** |

In plain terms: intervening successfully on this small high-risk cohort is estimated to avoid roughly eight departures and about **$455k** in replacement cost, under conservative effectiveness and mid-range cost-of-turnover assumptions.

## Methodology Note

- Risk scores come from an XGBoost classifier trained on the cleaned HR extract (`src/model_training.py`); logistic regression was used as an interpretable baseline (test ROC-AUC ≈ 0.81).
- Savings are probability-weighted: for each flagged employee,  
  `P(attrition) × retention effectiveness × replacement cost % × annual salary`, summed across the flagged group. Assumptions live on the workbook’s **Assumptions** sheet and drive all formulas.
- Full write-up of drivers and evaluation: `notebooks/01_eda_and_modeling.ipynb`. Dashboard extracts and Tableau Public build steps: `dashboard/README.md`.
