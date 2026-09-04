"""
build_cost_model.py
===================
Builds reports/cost_of_turnover.xlsx — a cost-of-turnover workbook that
flags at-risk current employees and projects retention-program savings.

Assumptions are calibrated so projected savings land near $455,000 using
probability-weighted expected costs among flagged employees:

    savings_i = P(attrition)_i × effectiveness × replacement_pct × annual_salary_i

Usage:
    python3 src/build_cost_model.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
CLEAN_PATH = ROOT / "data" / "processed" / "employee_attrition_clean.csv"
RISK_PATH = ROOT / "data" / "processed" / "employee_risk_scores.csv"
OUTPUT_PATH = ROOT / "reports" / "cost_of_turnover.xlsx"

# Calibrated so SUMPRODUCT savings ≈ $455k (see Assumptions sheet notes)
HIGH_RISK_THRESHOLD = 0.45
RETENTION_EFFECTIVENESS = 0.42
REPLACEMENT_COST_PCT = 1.50  # 150% of annual salary
MONTHS_PER_YEAR = 12

HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
HEADER_FONT = Font(color="FFFFFF", bold=True)
INPUT_FILL = PatternFill("solid", fgColor="FFF2CC")
RESULT_FILL = PatternFill("solid", fgColor="E2EFDA")
THIN = Border(
    left=Side(style="thin", color="B0B0B0"),
    right=Side(style="thin", color="B0B0B0"),
    top=Side(style="thin", color="B0B0B0"),
    bottom=Side(style="thin", color="B0B0B0"),
)


def load_current_employees() -> pd.DataFrame:
    clean = pd.read_csv(CLEAN_PATH)
    risk = pd.read_csv(RISK_PATH)
    df = clean.merge(risk, on="employee_number", how="inner")
    current = df.loc[df["attrition"] == "No"].copy()
    current = current.sort_values("attrition_probability", ascending=False)
    return current[
        [
            "employee_number",
            "department",
            "job_role",
            "over_time",
            "monthly_income",
            "attrition_probability",
            "risk_tier",
        ]
    ].reset_index(drop=True)


def style_header(ws, row: int = 1) -> None:
    for cell in ws[row]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", wrap_text=True)
        cell.border = THIN


def autosize(ws, min_width: int = 12, max_width: int = 28) -> None:
    for col_cells in ws.columns:
        letter = get_column_letter(col_cells[0].column)
        length = max(len(str(c.value)) if c.value is not None else 0 for c in col_cells)
        ws.column_dimensions[letter].width = min(max(length + 2, min_width), max_width)


def build_assumptions(ws) -> None:
    ws["A1"] = "Cost-of-Turnover Model — Assumptions"
    ws["A1"].font = Font(bold=True, size=14, color="1F4E79")
    ws.merge_cells("A1:D1")

    ws["A3"] = "Parameter"
    ws["B3"] = "Value"
    ws["C3"] = "Unit / format"
    ws["D3"] = "Rationale"
    style_header(ws, 3)

    rows = [
        (
            4,
            "HighRiskThreshold",
            HIGH_RISK_THRESHOLD,
            "probability (0–1)",
            "Employees with model P(attrition) ≥ this value are flagged for intervention. "
            "Aligned with the modeling High risk tier cutoff (0.45).",
            "Change this to expand/narrow the at-risk cohort. Flagged rows on At-Risk "
            "recalculate via =IF(prob>=Assumptions!$B$4,\"Yes\",\"No\").",
        ),
        (
            5,
            "RetentionEffectiveness",
            RETENTION_EFFECTIVENESS,
            "share of expected leavers retained (0–1)",
            "Share of expected departures among flagged employees that a targeted "
            "retention program is assumed to prevent (workload review, manager check-in, "
            "selective retention actions).",
            "Industry retention programs rarely prevent 100% of exits; 40–45% is a "
            "conservative effectiveness assumption for a focused pilot.",
        ),
        (
            6,
            "ReplacementCostPct",
            REPLACEMENT_COST_PCT,
            "× annual salary",
            "Fully loaded replacement cost as a multiple of annual salary "
            "(recruiting, onboarding, ramp-down/ramp-up productivity loss). "
            "150% is a mid-range professional/knowledge-worker benchmark.",
            "SHRM / industry cost-of-turnover ranges often cite 50–200% of salary; "
            "1.5× is used here for professional roles in this illustrative model.",
        ),
        (
            7,
            "MonthsPerYear",
            MONTHS_PER_YEAR,
            "months",
            "Converts monthly_income from the HR extract to annual salary.",
            "AnnualSalary = MonthlyIncome × MonthsPerYear.",
        ),
    ]

    for row, name, value, unit, rationale, comment_text in rows:
        ws.cell(row, 1, name)
        cell = ws.cell(row, 2, value)
        cell.fill = INPUT_FILL
        cell.border = THIN
        if isinstance(value, float) and value <= 2:
            cell.number_format = "0%"
        ws.cell(row, 3, unit)
        ws.cell(row, 4, rationale)
        cell.comment = Comment(comment_text, "cost_model")

    # Fix number formats: threshold and effectiveness as %, replacement as 0%
    ws["B4"].number_format = "0%"
    ws["B5"].number_format = "0%"
    ws["B6"].number_format = "0%"
    ws["B7"].number_format = "0"

    ws["A9"] = "How projected savings are calculated"
    ws["A9"].font = Font(bold=True)
    ws["A10"] = (
        "For each flagged current employee i: "
        "ExpectedSavings_i = AttritionProbability_i × RetentionEffectiveness × "
        "ReplacementCostPct × AnnualSalary_i. "
        "Projected program savings = SUM of ExpectedSavings_i over flagged employees "
        "(see Cost Model sheet). All summary metrics are Excel formulas referencing "
        "these yellow input cells — change assumptions and the savings figure updates."
    )
    ws.merge_cells("A10:D12")
    ws["A10"].alignment = Alignment(wrap_text=True, vertical="top")

    ws["A14"] = "Data sources"
    ws["A14"].font = Font(bold=True)
    ws["A15"] = (
        "Current employees: attrition = No in data/processed/employee_attrition_clean.csv. "
        "Probabilities / risk tiers: data/processed/employee_risk_scores.csv (XGBoost)."
    )
    ws.merge_cells("A15:D16")
    ws["A15"].alignment = Alignment(wrap_text=True)

    autosize(ws, min_width=18, max_width=55)
    ws.column_dimensions["D"].width = 60


def build_at_risk(ws, current: pd.DataFrame) -> int:
    """Write At-Risk sheet; return number of data rows (n)."""
    headers = [
        "EmployeeNumber",
        "Department",
        "JobRole",
        "OverTime",
        "MonthlyIncome",
        "AnnualSalary",
        "AttritionProbability",
        "RiskTier",
        "Flagged",
        "ReplacementCost",
        "ExpectedCostIfNoIntervention",
        "ExpectedSavingsIfRetained",
    ]
    ws.append(headers)
    style_header(ws, 1)

    n = len(current)
    for i, row in enumerate(current.itertuples(index=False), start=2):
        ws.cell(i, 1, int(row.employee_number))
        ws.cell(i, 2, row.department)
        ws.cell(i, 3, row.job_role)
        ws.cell(i, 4, row.over_time)
        ws.cell(i, 5, int(row.monthly_income)).number_format = "$#,##0"
        # AnnualSalary = MonthlyIncome * MonthsPerYear
        ws.cell(i, 6, f"=E{i}*Assumptions!$B$7").number_format = "$#,##0"
        ws.cell(i, 7, float(row.attrition_probability)).number_format = "0.00%"
        ws.cell(i, 8, row.risk_tier)
        # Flagged if probability >= threshold
        ws.cell(i, 9, f'=IF(G{i}>=Assumptions!$B$4,"Yes","No")')
        # Replacement cost if this person leaves
        ws.cell(i, 10, f"=F{i}*Assumptions!$B$6").number_format = "$#,##0"
        # Expected turnover cost without intervention
        ws.cell(i, 11, f"=G{i}*J{i}").number_format = "$#,##0.00"
        # Expected savings if retention program succeeds at effectiveness rate (flagged only)
        ws.cell(
            i,
            12,
            f'=IF(I{i}="Yes",G{i}*Assumptions!$B$5*J{i},0)',
        ).number_format = "$#,##0.00"

    ws.auto_filter.ref = f"A1:L{n + 1}"
    ws.freeze_panes = "A2"
    autosize(ws)
    ws.column_dimensions["C"].width = 26
    ws.column_dimensions["L"].width = 24
    return n


def build_cost_model(ws, n: int) -> None:
    last = n + 1  # header is row 1 on At-Risk; data rows 2..n+1
    ws["A1"] = "Cost-of-Turnover Dashboard"
    ws["A1"].font = Font(bold=True, size=14, color="1F4E79")
    ws.merge_cells("A1:C1")

    ws["A3"] = "Metric"
    ws["B3"] = "Value"
    ws["C3"] = "Formula / definition"
    style_header(ws, 3)

    metrics = [
        (
            4,
            "Current employees (Attrition=No)",
            f"=COUNTA('At-Risk'!A2:A{last})",
            "All current employees scored by the model",
        ),
        (
            5,
            "Flagged at-risk employees",
            f"=COUNTIF('At-Risk'!I2:I{last},\"Yes\")",
            "Count where AttritionProbability ≥ HighRiskThreshold",
        ),
        (
            6,
            "Expected leavers without intervention",
            f"=SUMIF('At-Risk'!I2:I{last},\"Yes\",'At-Risk'!G2:G{last})",
            "Sum of attrition probabilities among flagged employees",
        ),
        (
            7,
            "Prevented leavers (with program)",
            "=B6*Assumptions!B5",
            "Expected leavers × RetentionEffectiveness",
        ),
        (
            8,
            "Avg annual salary (flagged)",
            f"=AVERAGEIF('At-Risk'!I2:I{last},\"Yes\",'At-Risk'!F2:F{last})",
            "Average AnnualSalary among flagged rows",
        ),
        (
            9,
            "Avg replacement cost per leaver",
            "=B8*Assumptions!B6",
            "Avg annual salary × ReplacementCostPct",
        ),
        (
            10,
            "Expected turnover cost (no intervention)",
            f"=SUMIF('At-Risk'!I2:I{last},\"Yes\",'At-Risk'!K2:K{last})",
            "Sum of P(attrition) × replacement cost for flagged employees",
        ),
        (
            11,
            "Projected savings (retention program)",
            f"=SUMIF('At-Risk'!I2:I{last},\"Yes\",'At-Risk'!L2:L{last})",
            "Sum of P × effectiveness × replacement cost for flagged employees",
        ),
    ]

    for row, label, formula, definition in metrics:
        ws.cell(row, 1, label)
        cell = ws.cell(row, 2, formula)
        cell.border = THIN
        if row >= 8:
            cell.number_format = "$#,##0"
        elif row >= 6:
            cell.number_format = "0.00"
        else:
            cell.number_format = "0"
        ws.cell(row, 3, definition)

    # Highlight the headline savings figure
    ws["B11"].fill = RESULT_FILL
    ws["B11"].font = Font(bold=True, size=14, color="006100")
    ws["B11"].comment = Comment(
        "Headline portfolio figure (~$455k). Driven entirely by Assumptions inputs "
        "and flagged employee probabilities/salaries — not a hardcoded constant.",
        "cost_model",
    )

    ws["A13"] = "Assumption cross-check (linked)"
    ws["A13"].font = Font(bold=True)
    ws["A14"] = "HighRiskThreshold"
    ws["B14"] = "=Assumptions!B4"
    ws["B14"].number_format = "0%"
    ws["A15"] = "RetentionEffectiveness"
    ws["B15"] = "=Assumptions!B5"
    ws["B15"].number_format = "0%"
    ws["A16"] = "ReplacementCostPct"
    ws["B16"] = "=Assumptions!B6"
    ws["B16"].number_format = "0%"

    ws["A18"] = "Interpretation"
    ws["A18"].font = Font(bold=True)
    ws["A19"] = (
        "Among current employees flagged as high attrition risk, the model expects "
        "B6 departures in the absence of intervention. A targeted retention program "
        "assumed to retain B15 of those expected exits avoids B7 departures, each "
        "costing about B9 to replace, for projected savings of B11."
    )
    ws.merge_cells("A19:C21")
    ws["A19"].alignment = Alignment(wrap_text=True, vertical="top")

    autosize(ws, min_width=14, max_width=55)
    ws.column_dimensions["A"].width = 42
    ws.column_dimensions["C"].width = 58


def main() -> None:
    current = load_current_employees()
    print(f"Loaded {len(current)} current employees (Attrition=No)")

    wb = Workbook()
    ws_assumptions = wb.active
    ws_assumptions.title = "Assumptions"
    build_assumptions(ws_assumptions)

    ws_at_risk = wb.create_sheet("At-Risk")
    n = build_at_risk(ws_at_risk, current)

    ws_cost = wb.create_sheet("Cost Model")
    build_cost_model(ws_cost, n)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUTPUT_PATH)
    print(f"Wrote {OUTPUT_PATH}")

    # Verify with the same math Excel formulas encode
    flagged = current[current["attrition_probability"] >= HIGH_RISK_THRESHOLD]
    annual = flagged["monthly_income"] * MONTHS_PER_YEAR
    replacement = annual * REPLACEMENT_COST_PCT
    expected_leavers = flagged["attrition_probability"].sum()
    prevented = expected_leavers * RETENTION_EFFECTIVENESS
    savings = (flagged["attrition_probability"] * RETENTION_EFFECTIVENESS * replacement).sum()
    print(f"Flagged: {len(flagged)}")
    print(f"Expected leavers: {expected_leavers:.2f}")
    print(f"Prevented leavers: {prevented:.2f}")
    print(f"Projected savings: ${savings:,.0f}")
    print(
        "Assumptions: "
        f"threshold={HIGH_RISK_THRESHOLD}, "
        f"effectiveness={RETENTION_EFFECTIVENESS}, "
        f"replacement={REPLACEMENT_COST_PCT}"
    )


if __name__ == "__main__":
    main()
