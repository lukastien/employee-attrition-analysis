-- ============================================================
-- Employee Attrition & Retention Analysis — Schema
-- ============================================================
-- Loads the IBM HR Analytics dataset into a single flat table.
-- (A single denormalized table is sufficient here since the
-- source data has no natural multi-table structure; queries
-- below simulate the kind of relational analysis a real HRIS
-- database would support.)

DROP TABLE IF EXISTS employees;

CREATE TABLE employees (
    employee_number         INTEGER PRIMARY KEY,
    age                     INTEGER,
    attrition               TEXT,       -- 'Yes' / 'No'
    business_travel         TEXT,
    daily_rate              INTEGER,
    department              TEXT,
    distance_from_home      INTEGER,
    education               INTEGER,
    education_field         TEXT,
    environment_satisfaction INTEGER,
    gender                  TEXT,
    job_involvement         INTEGER,
    job_level               INTEGER,
    job_role                TEXT,
    job_satisfaction        INTEGER,
    marital_status           TEXT,
    monthly_income           INTEGER,
    num_companies_worked      INTEGER,
    over_time                TEXT,
    percent_salary_hike      INTEGER,
    performance_rating        INTEGER,
    relationship_satisfaction INTEGER,
    stock_option_level       INTEGER,
    total_working_years      INTEGER,
    training_times_last_year INTEGER,
    work_life_balance        INTEGER,
    years_at_company         INTEGER,
    years_in_current_role    INTEGER,
    years_since_last_promotion INTEGER,
    years_with_curr_manager   INTEGER
);

-- ============================================================
-- TODO: Example exploratory queries to build out
-- ============================================================

-- 1. Overall attrition rate
-- SELECT
--     ROUND(100.0 * SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS attrition_rate_pct
-- FROM employees;

-- 2. Attrition rate by department
-- SELECT
--     department,
--     COUNT(*) AS headcount,
--     ROUND(100.0 * SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS attrition_rate_pct
-- FROM employees
-- GROUP BY department
-- ORDER BY attrition_rate_pct DESC;

-- 3. Attrition rate by overtime status
-- SELECT
--     over_time,
--     COUNT(*) AS headcount,
--     ROUND(100.0 * SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS attrition_rate_pct
-- FROM employees
-- GROUP BY over_time;

-- 4. Attrition rate by tenure bucket
-- SELECT
--     CASE
--         WHEN years_at_company < 2 THEN '0-2 yrs'
--         WHEN years_at_company < 5 THEN '2-5 yrs'
--         WHEN years_at_company < 10 THEN '5-10 yrs'
--         ELSE '10+ yrs'
--     END AS tenure_bucket,
--     COUNT(*) AS headcount,
--     ROUND(100.0 * SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS attrition_rate_pct
-- FROM employees
-- GROUP BY tenure_bucket
-- ORDER BY MIN(years_at_company);

-- 5. Average salary by attrition status (are we losing higher earners?)
-- SELECT
--     attrition,
--     ROUND(AVG(monthly_income), 0) AS avg_monthly_income
-- FROM employees
-- GROUP BY attrition;
