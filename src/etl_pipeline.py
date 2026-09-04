"""
etl_pipeline.py
================
Loads the raw IBM HR Analytics Employee Attrition dataset, cleans it,
and writes it into a local SQLite database for querying (see sql/schema.sql).

Usage:
    python src/etl_pipeline.py
"""

import re
import sqlite3
from pathlib import Path

import pandas as pd

RAW_DATA_PATH = Path("data/raw/employee_attrition.csv")
PROCESSED_DATA_PATH = Path("data/processed/employee_attrition_clean.csv")
DB_PATH = Path("data/processed/attrition.db")
SCHEMA_PATH = Path("sql/schema.sql")

# Constant / no-signal columns in the IBM HR export
DROP_COLUMNS = {"EmployeeCount", "Over18", "StandardHours"}

# Columns defined in sql/schema.sql (order matches CREATE TABLE)
SCHEMA_COLUMNS = [
    "employee_number",
    "age",
    "attrition",
    "business_travel",
    "daily_rate",
    "department",
    "distance_from_home",
    "education",
    "education_field",
    "environment_satisfaction",
    "gender",
    "job_involvement",
    "job_level",
    "job_role",
    "job_satisfaction",
    "marital_status",
    "monthly_income",
    "num_companies_worked",
    "over_time",
    "percent_salary_hike",
    "performance_rating",
    "relationship_satisfaction",
    "stock_option_level",
    "total_working_years",
    "training_times_last_year",
    "work_life_balance",
    "years_at_company",
    "years_in_current_role",
    "years_since_last_promotion",
    "years_with_curr_manager",
]


def to_snake_case(name: str) -> str:
    """Convert PascalCase / camelCase column names to snake_case."""
    name = name.replace("\ufeff", "").strip()
    name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return name.lower()


def load_raw_data(path: Path) -> pd.DataFrame:
    """Load the raw CSV export into a DataFrame (utf-8-sig strips BOM)."""
    return pd.read_csv(path, encoding="utf-8-sig")


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize the raw dataset.

    - Strip BOM / standardize column names to snake_case
    - Drop constant/no-signal columns
    - Leave dtypes as-is after rename (integers stay numeric; Yes/No stay text)
    """
    out = df.copy()

    # Drop constants before rename (names still match the raw CSV)
    drop = [c for c in out.columns if c.replace("\ufeff", "") in DROP_COLUMNS or c in DROP_COLUMNS]
    out = out.drop(columns=drop)

    out.columns = [to_snake_case(c) for c in out.columns]

    if out.isna().any().any():
        out = out.dropna()

    return out


def load_to_sqlite(df: pd.DataFrame, db_path: Path, schema_path: Path = SCHEMA_PATH) -> None:
    """Apply schema.sql, then insert cleaned rows into the employees table."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    schema_sql = schema_path.read_text(encoding="utf-8")
    missing = [c for c in SCHEMA_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Cleaned data missing schema columns: {missing}")

    to_insert = df[SCHEMA_COLUMNS]

    with sqlite3.connect(db_path) as conn:
        conn.executescript(schema_sql)
        to_insert.to_sql("employees", conn, if_exists="append", index=False)


def main():
    df_raw = load_raw_data(RAW_DATA_PATH)
    print(f"Loaded {len(df_raw)} rows from {RAW_DATA_PATH}")

    df_clean = clean_data(df_raw)
    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(PROCESSED_DATA_PATH, index=False)
    print(f"Wrote cleaned data ({len(df_clean)} rows) to {PROCESSED_DATA_PATH}")

    load_to_sqlite(df_clean, DB_PATH)
    with sqlite3.connect(DB_PATH) as conn:
        count = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    print(f"Loaded {count} rows into {DB_PATH}")
    print(f"Processed {len(df_clean)} rows successfully.")


if __name__ == "__main__":
    main()
