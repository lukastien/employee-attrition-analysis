"""
etl_pipeline.py
================
Loads the raw IBM HR Analytics Employee Attrition dataset, cleans it,
and writes it into a local SQLite database for querying (see sql/schema.sql).

STATUS: placeholder stub — logic to be filled in.

Usage (once implemented):
    python src/etl_pipeline.py
"""

import pandas as pd
import sqlite3
from pathlib import Path

RAW_DATA_PATH = Path("data/raw/employee_attrition.csv")
PROCESSED_DATA_PATH = Path("data/processed/employee_attrition_clean.csv")
DB_PATH = Path("data/processed/attrition.db")


def load_raw_data(path: Path) -> pd.DataFrame:
    """Load the raw CSV export into a DataFrame."""
    # TODO: read_csv, inspect dtypes
    df = pd.read_csv(path)
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize the raw dataset.

    TODO:
      - Standardize column names to snake_case
      - Drop constant/no-signal columns (e.g. EmployeeCount, Over18, StandardHours)
      - Handle any missing values
      - Cast categorical columns appropriately
    """
    raise NotImplementedError("Fill in cleaning logic")


def load_to_sqlite(df: pd.DataFrame, db_path: Path):
    """Write the cleaned DataFrame into the SQLite database defined in sql/schema.sql."""
    # TODO: connect to sqlite3, execute schema.sql, insert cleaned data
    raise NotImplementedError("Fill in database load logic")


def main():
    df_raw = load_raw_data(RAW_DATA_PATH)
    print(f"Loaded {len(df_raw)} rows from {RAW_DATA_PATH}")

    # df_clean = clean_data(df_raw)
    # df_clean.to_csv(PROCESSED_DATA_PATH, index=False)
    # load_to_sqlite(df_clean, DB_PATH)
    print("TODO: implement clean_data() and load_to_sqlite()")


if __name__ == "__main__":
    main()
