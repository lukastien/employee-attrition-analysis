-- ============================================================
-- Employee Attrition Analytics Queries
-- ============================================================
-- Run against the loaded SQLite database (does not modify schema):
--   sqlite3 -header -column data/processed/attrition.db < sql/queries.sql
--
-- Or: bash sql/run_analytics.sh
--
-- Prerequisite: data/processed/attrition.db from python3 src/etl_pipeline.py

.headers on
.mode column
.timer off

-- ------------------------------------------------------------
-- 1. Overall attrition rate
-- ------------------------------------------------------------
SELECT
    '1. Overall attrition' AS analysis,
    COUNT(*) AS headcount,
    SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) AS attrition_count,
    ROUND(100.0 * SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS attrition_rate_pct
FROM employees;

-- ------------------------------------------------------------
-- 2. Attrition rate by department
-- ------------------------------------------------------------
SELECT
    department,
    COUNT(*) AS headcount,
    SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) AS attrition_count,
    ROUND(100.0 * SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS attrition_rate_pct
FROM employees
GROUP BY department
ORDER BY attrition_rate_pct DESC;

-- ------------------------------------------------------------
-- 3. Attrition rate by overtime status
-- ------------------------------------------------------------
SELECT
    over_time,
    COUNT(*) AS headcount,
    SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) AS attrition_count,
    ROUND(100.0 * SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS attrition_rate_pct
FROM employees
GROUP BY over_time
ORDER BY attrition_rate_pct DESC;

-- ------------------------------------------------------------
-- 4. Attrition rate by tenure band
-- ------------------------------------------------------------
SELECT
    CASE
        WHEN years_at_company < 2 THEN '0-2 yrs'
        WHEN years_at_company < 5 THEN '2-5 yrs'
        WHEN years_at_company < 10 THEN '5-10 yrs'
        ELSE '10+ yrs'
    END AS tenure_band,
    COUNT(*) AS headcount,
    SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) AS attrition_count,
    ROUND(100.0 * SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS attrition_rate_pct
FROM employees
GROUP BY tenure_band
ORDER BY MIN(years_at_company);

-- ------------------------------------------------------------
-- 5. Attrition rate by salary band (monthly_income quartiles)
--    Low / Mid / High / Very High via NTILE(4)
-- ------------------------------------------------------------
WITH income_ranked AS (
    SELECT
        attrition,
        monthly_income,
        NTILE(4) OVER (ORDER BY monthly_income) AS income_quartile
    FROM employees
)
SELECT
    CASE income_quartile
        WHEN 1 THEN 'Low'
        WHEN 2 THEN 'Mid'
        WHEN 3 THEN 'High'
        WHEN 4 THEN 'Very High'
    END AS salary_band,
    MIN(monthly_income) AS income_min,
    MAX(monthly_income) AS income_max,
    COUNT(*) AS headcount,
    SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) AS attrition_count,
    ROUND(100.0 * SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS attrition_rate_pct
FROM income_ranked
GROUP BY income_quartile
ORDER BY income_quartile;

-- ------------------------------------------------------------
-- 6. Average salary by attrition status
-- ------------------------------------------------------------
SELECT
    attrition,
    COUNT(*) AS headcount,
    ROUND(AVG(monthly_income), 0) AS avg_monthly_income
FROM employees
GROUP BY attrition
ORDER BY attrition;
