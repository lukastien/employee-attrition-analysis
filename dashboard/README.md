# Tableau Public Dashboard

Build an interactive attrition dashboard in **Tableau Public** using the CSV extracts in this folder. You do not need Tableau Desktop.

## Data files

| File | Purpose |
|------|---------|
| [`attrition_summary.csv`](attrition_summary.csv) | Aggregated attrition by Overall / Department / OverTime / TenureBand / SalaryBand |
| [`at_risk_employees.csv`](at_risk_employees.csv) | Current employees (still employed) with predicted risk, salary, and flagged status |

Regenerate after re-running models:

```bash
python3 src/export_tableau_extracts.py
```

## Published dashboard (fill in after you publish)

**Tableau Public URL:** _TBD — paste your link here_

**Screenshot:** _TBD — add `dashboard/screenshot.png` (or similar) and link it here_

---

## Step-by-step: build in Tableau Public

### A. Create the workbook

1. Go to [https://public.tableau.com](https://public.tableau.com) and sign in.
2. Click **Create** → **Web Authoring** (or open Tableau Public desktop app if you use it).
3. **Connect to Data** → **Text file** → upload `attrition_summary.csv`.
4. Add a second connection: upload `at_risk_employees.csv` (same workbook, second data source).  
   You do **not** need to join them for the views below — use each source on its own sheets.

### B. Sheets to create

#### 1. Attrition by OverTime (bar)

- Data source: `attrition_summary`
- Filter `dimension` = `OverTime`
- **Columns:** `dimension_value` (or OverTime Yes/No)
- **Rows:** `attrition_rate_pct`
- Mark type: **Bar**
- Optional label: show `attrition_rate_pct` and `headcount`
- Title: “Attrition rate by overtime”

Expected pattern: **Yes ≈ 30.5%**, **No ≈ 10.4%**.

#### 2. Attrition by Tenure Band (bar)

- Filter `dimension` = `TenureBand`
- Sort tenure manually: `0-2 yrs` → `2-5 yrs` → `5-10 yrs` → `10+ yrs`
- **Columns:** `dimension_value` | **Rows:** `attrition_rate_pct`
- Mark type: **Bar**
- Title: “Attrition rate by tenure”

Expected pattern: early tenure highest (**0–2 yrs ≈ 34.9%**).

#### 3. Attrition by Salary Band (bar)

- Filter `dimension` = `SalaryBand`
- Sort: Low → Mid → High → Very High
- **Columns:** `dimension_value` | **Rows:** `attrition_rate_pct`
- Mark type: **Bar**
- Title: “Attrition rate by salary band (income quartiles)”

Expected pattern: **Low ≈ 29.4%**, declining toward Very High.

#### 4. Attrition by Department (optional bar / highlight table)

- Filter `dimension` = `Department`
- Sort descending by `attrition_rate_pct`
- Useful as a fourth chart or a compact table

#### 5. Who’s at risk (table)

- Data source: `at_risk_employees`
- Filter `flagged` = `Yes` (or `risk_tier` = `High`) for the headline view
- Table columns (suggested):
  - `employee_number`
  - `department`
  - `job_role`
  - `over_time`
  - `monthly_income` / `annual_salary`
  - `attrition_probability` (format as %)
  - `risk_tier`
  - `flagged`
- Sort by `attrition_probability` descending
- Title: “At-risk employees (current workforce)”

Optional: add a second sheet with **all** current employees and a filter control on `risk_tier` / `flagged`.

#### 6. Cost summary (scorecard)

Tableau Public won’t open the Excel model directly in web authoring as easily as CSVs. Use a simple **Text** / KPI sheet (or a tiny manual “Cost inputs” Excel/CSV you type once) with these portfolio figures from `reports/cost_of_turnover.xlsx`:

| KPI | Value |
|-----|-------|
| Flagged at-risk employees | 31 |
| Expected leavers (no intervention) | ~18 |
| Prevented leavers (program) | ~7.6 |
| **Projected savings** | **~$455,000** |

Assumptions (for a footnote on the dashboard): high-risk threshold 45%, retention effectiveness 42%, replacement cost 150% of annual salary.

### C. Assemble the dashboard

1. New **Dashboard** (e.g. 1000×800 or Browser size).
2. Suggested layout:
   - Top row: OverTime + Tenure + Salary Band charts
   - Middle: At-risk employee table
   - Side / bottom: Cost summary KPIs + short note that overtime is the top model driver
3. Add filters: `department`, `over_time`, `flagged` on the at-risk table.
4. Keep titles short; one insight sentence in a text object is enough  
   (“Employees on overtime attrition ~3× those not on overtime; targeted retention on 31 high-risk employees projects ~$455k savings.”).

### D. Publish

1. **File → Save to Tableau Public As…** (or **Publish** in web authoring).
2. Copy the public URL.
3. Paste it into the **Published dashboard** section at the top of this README.
4. Optional: export a PNG screenshot into `dashboard/screenshot.png` and link it here.

---

## Sanity checks (numbers should match SQL / models)

| Check | Expected |
|-------|----------|
| Overall attrition | 16.12% (237 / 1470) |
| OverTime Yes vs No | 30.53% vs 10.44% |
| Tenure 0–2 yrs | 34.88% |
| Salary Low band | 29.35% |
| Current employees in at-risk file | 1233 |
| Flagged (`flagged`=Yes) | 31 |
