"""
export_tableau_extracts.py
==========================
Builds Tableau Public–ready CSV extracts under dashboard/.

Outputs:
  - dashboard/attrition_summary.csv
  - dashboard/at_risk_employees.csv

Usage:
    python3 src/export_tableau_extracts.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CLEAN_PATH = ROOT / "data" / "processed" / "employee_attrition_clean.csv"
RISK_PATH = ROOT / "data" / "processed" / "employee_risk_scores.csv"
OUT_SUMMARY = ROOT / "dashboard" / "attrition_summary.csv"
OUT_AT_RISK = ROOT / "dashboard" / "at_risk_employees.csv"

# Match Excel cost model / modeling High tier
HIGH_RISK_THRESHOLD = 0.45
SALARY_BAND_ORDER = {"Low": 1, "Mid": 2, "High": 3, "Very High": 4}
TENURE_BAND_ORDER = {"0-2 yrs": 1, "2-5 yrs": 2, "5-10 yrs": 3, "10+ yrs": 4}


def tenure_band(years: pd.Series) -> pd.Series:
    """Match sql/queries.sql CASE on years_at_company (<2 / <5 / <10 / else)."""
    return pd.Series(
        np.select(
            [
                years < 2,
                years < 5,
                years < 10,
            ],
            ["0-2 yrs", "2-5 yrs", "5-10 yrs"],
            default="10+ yrs",
        ),
        index=years.index,
    )


def salary_band(income: pd.Series) -> pd.Series:
    """
    Quartile bands matching SQLite NTILE(4) OVER (ORDER BY monthly_income).

    SQLite NTILE splits rows into 4 buckets by ordered row number; remainder
    rows are distributed to the earlier buckets (sizes 368,368,367,367).
    """
    ordered_idx = income.sort_values(kind="mergesort").index
    n = len(income)
    # Bucket sizes: first (n % 4) buckets get n//4 + 1 rows
    base, rem = divmod(n, 4)
    sizes = [base + (1 if i < rem else 0) for i in range(4)]
    labels = []
    for i, size in enumerate(sizes, start=1):
        labels.extend([i] * size)
    quartile = pd.Series(labels, index=ordered_idx)
    return quartile.reindex(income.index).map(
        {1: "Low", 2: "Mid", 3: "High", 4: "Very High"}
    )


def attrition_block(df: pd.DataFrame, dimension: str, values: pd.Series) -> pd.DataFrame:
    tmp = df.copy()
    tmp["_dim"] = values
    g = (
        tmp.groupby("_dim", observed=True)
        .agg(
            headcount=("attrition", "size"),
            attrition_count=("attrition", lambda s: int((s == "Yes").sum())),
        )
        .reset_index()
        .rename(columns={"_dim": "dimension_value"})
    )
    g["dimension"] = dimension
    g["attrition_rate_pct"] = (100.0 * g["attrition_count"] / g["headcount"]).round(2)
    return g[["dimension", "dimension_value", "headcount", "attrition_count", "attrition_rate_pct"]]


def build_attrition_summary(df: pd.DataFrame) -> pd.DataFrame:
    overall = pd.DataFrame(
        [
            {
                "dimension": "Overall",
                "dimension_value": "All employees",
                "headcount": len(df),
                "attrition_count": int((df["attrition"] == "Yes").sum()),
                "attrition_rate_pct": round(100.0 * (df["attrition"] == "Yes").mean(), 2),
            }
        ]
    )
    parts = [
        overall,
        attrition_block(df, "Department", df["department"]),
        attrition_block(df, "OverTime", df["over_time"]),
        attrition_block(df, "TenureBand", tenure_band(df["years_at_company"])),
        attrition_block(df, "SalaryBand", salary_band(df["monthly_income"])),
    ]
    out = pd.concat(parts, ignore_index=True)

    def sort_key(row):
        dim = row["dimension"]
        val = row["dimension_value"]
        if dim == "Overall":
            return (0, 0)
        if dim == "Department":
            return (1, -row["attrition_rate_pct"])
        if dim == "OverTime":
            return (2, 0 if val == "Yes" else 1)
        if dim == "TenureBand":
            return (3, TENURE_BAND_ORDER.get(val, 99))
        if dim == "SalaryBand":
            return (4, SALARY_BAND_ORDER.get(val, 99))
        return (9, 0)

    out["_sort"] = out.apply(sort_key, axis=1)
    out = out.sort_values("_sort").drop(columns="_sort").reset_index(drop=True)
    return out


def build_at_risk(df: pd.DataFrame, risk: pd.DataFrame) -> pd.DataFrame:
    merged = df.merge(risk, on="employee_number", how="inner")
    current = merged.loc[merged["attrition"] == "No"].copy()
    current["annual_salary"] = current["monthly_income"] * 12
    current["flagged"] = np.where(
        current["attrition_probability"] >= HIGH_RISK_THRESHOLD, "Yes", "No"
    )
    current["tenure_band"] = tenure_band(current["years_at_company"]).astype(str)
    current["salary_band"] = salary_band(current["monthly_income"])

    out = current[
        [
            "employee_number",
            "department",
            "job_role",
            "over_time",
            "tenure_band",
            "salary_band",
            "monthly_income",
            "annual_salary",
            "attrition_probability",
            "risk_tier",
            "flagged",
        ]
    ].sort_values("attrition_probability", ascending=False)
    return out.reset_index(drop=True)


def main() -> None:
    df = pd.read_csv(CLEAN_PATH)
    risk = pd.read_csv(RISK_PATH)

    summary = build_attrition_summary(df)
    at_risk = build_at_risk(df, risk)

    OUT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUT_SUMMARY, index=False)
    at_risk.to_csv(OUT_AT_RISK, index=False)

    print(f"Wrote {OUT_SUMMARY} ({len(summary)} rows)")
    print(summary.to_string(index=False))
    print(f"\nWrote {OUT_AT_RISK} ({len(at_risk)} rows)")
    print(at_risk.head(8).to_string(index=False))
    print("\nFlagged counts:")
    print(at_risk["flagged"].value_counts().to_string())
    print(at_risk["risk_tier"].value_counts().to_string())


if __name__ == "__main__":
    main()
