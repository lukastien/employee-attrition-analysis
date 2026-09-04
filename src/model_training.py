"""
model_training.py
==================
Trains and evaluates classification models to predict employee attrition.

Approach:
    1. Baseline: Logistic Regression (interpretable coefficients)
    2. Main model: XGBoost classifier
    3. Evaluate with ROC-AUC, precision/recall (attrition ~16% positive class)
    4. Extract feature importance — OverTime is expected among top drivers
    5. Export risk scores for all employees

Usage:
    python3 src/model_training.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

PROCESSED_DATA_PATH = Path("data/processed/employee_attrition_clean.csv")
RISK_SCORES_PATH = Path("data/processed/employee_risk_scores.csv")
RANDOM_STATE = 42
TEST_SIZE = 0.25

# Columns that must not be used as predictors
ID_COL = "employee_number"
TARGET_COL = "attrition"

CATEGORICAL_COLS = [
    "business_travel",
    "department",
    "education_field",
    "gender",
    "job_role",
    "marital_status",
    "over_time",
]


def load_features(path: Path) -> pd.DataFrame:
    """Load the cleaned dataset ready for modeling."""
    return pd.read_csv(path)


def prepare_xy(df: pd.DataFrame):
    """Split into feature matrix X, target y, and employee ids."""
    y = (df[TARGET_COL] == "Yes").astype(int)
    ids = df[ID_COL]
    X = df.drop(columns=[TARGET_COL, ID_COL])
    return X, y, ids


def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    """One-hot encode categoricals; scale numerics for logistic regression."""
    categorical = [c for c in CATEGORICAL_COLS if c in X.columns]
    numeric = [c for c in X.columns if c not in categorical]
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", drop="if_binary"),
                categorical,
            ),
        ]
    )


def train_baseline_model(X_train, y_train, preprocessor: ColumnTransformer) -> Pipeline:
    """Train a logistic regression baseline with preprocessing."""
    pipe = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            (
                "model",
                LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )
    pipe.fit(X_train, y_train)
    return pipe


def train_xgboost_model(X_train, y_train, preprocessor: ColumnTransformer) -> Pipeline:
    """Train the main XGBoost classifier (handles class imbalance via scale_pos_weight)."""
    neg = int((y_train == 0).sum())
    pos = int((y_train == 1).sum())
    scale_pos_weight = neg / max(pos, 1)

    # XGBoost does not need scaled numerics; reuse same OHE via passthrough scaler identity
    # by fitting a preprocessor without scaling for tree models.
    categorical = [c for c in CATEGORICAL_COLS if c in X_train.columns]
    numeric = [c for c in X_train.columns if c not in categorical]
    tree_preprocessor = ColumnTransformer(
        transformers=[
            ("num", "passthrough", numeric),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", drop="if_binary"),
                categorical,
            ),
        ]
    )

    pipe = Pipeline(
        steps=[
            ("preprocess", tree_preprocessor),
            (
                "model",
                XGBClassifier(
                    n_estimators=200,
                    max_depth=4,
                    learning_rate=0.08,
                    subsample=0.9,
                    colsample_bytree=0.9,
                    scale_pos_weight=scale_pos_weight,
                    eval_metric="logloss",
                    random_state=RANDOM_STATE,
                    n_jobs=2,
                ),
            ),
        ]
    )
    pipe.fit(X_train, y_train)
    return pipe


def evaluate_model(model, X_test, y_test, name: str = "model") -> dict:
    """Evaluate a trained model: ROC-AUC, precision/recall, classification report."""
    proba = model.predict_proba(X_test)[:, 1]
    pred = (proba >= 0.5).astype(int)
    metrics = {
        "name": name,
        "roc_auc": float(roc_auc_score(y_test, proba)),
        "precision": float(precision_score(y_test, pred, zero_division=0)),
        "recall": float(recall_score(y_test, pred, zero_division=0)),
    }
    print(f"\n=== {name} ===")
    print(
        f"ROC-AUC: {metrics['roc_auc']:.3f} | "
        f"Precision: {metrics['precision']:.3f} | "
        f"Recall: {metrics['recall']:.3f}"
    )
    print(classification_report(y_test, pred, target_names=["Stayed", "Left"], digits=3))
    return metrics


def _transformed_feature_names(preprocessor: ColumnTransformer) -> list[str]:
    return list(preprocessor.get_feature_names_out())


def get_feature_importance(model: Pipeline, top_n: int = 15) -> pd.DataFrame:
    """
    Extract and rank feature importance.
    LogisticRegression -> absolute coefficients
    XGBClassifier -> gain-based feature_importances_
    """
    preprocessor = model.named_steps["preprocess"]
    clf = model.named_steps["model"]
    names = _transformed_feature_names(preprocessor)

    if isinstance(clf, LogisticRegression):
        values = np.abs(clf.coef_.ravel())
        label = "abs_coefficient"
    else:
        values = clf.feature_importances_
        label = "importance"

    importance = (
        pd.DataFrame({"feature": names, label: values})
        .sort_values(label, ascending=False)
        .reset_index(drop=True)
    )
    return importance.head(top_n)


def assign_risk_tier(proba: np.ndarray) -> pd.Series:
    """Map predicted attrition probability to Low / Medium / High risk tiers."""
    tiers = np.where(proba >= 0.45, "High", np.where(proba >= 0.25, "Medium", "Low"))
    return pd.Series(tiers)


def export_risk_scores(
    model: Pipeline,
    X: pd.DataFrame,
    ids: pd.Series,
    path: Path,
) -> pd.DataFrame:
    """Score all employees and write employee_risk_scores.csv."""
    proba = model.predict_proba(X)[:, 1]
    out = pd.DataFrame(
        {
            "employee_number": ids.values,
            "attrition_probability": np.round(proba, 4),
            "risk_tier": assign_risk_tier(proba),
        }
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(path, index=False)
    return out


def overtime_rank(importance: pd.DataFrame, value_col: str | None = None) -> int | None:
    """1-based rank of the first OverTime-related feature, if present."""
    del value_col  # kept for call-site clarity; ranking uses feature name order
    mask = importance["feature"].str.contains("over_time", case=False, regex=False)
    hits = importance.index[mask].tolist()
    if not hits:
        return None
    return int(hits[0]) + 1


def main():
    df = load_features(PROCESSED_DATA_PATH)
    print(f"Loaded {len(df)} rows from {PROCESSED_DATA_PATH}")
    print(f"Attrition rate: {(df[TARGET_COL] == 'Yes').mean():.2%}")

    X, y, ids = prepare_xy(df)
    X_train, X_test, y_train, y_test, ids_train, ids_test = train_test_split(
        X,
        y,
        ids,
        test_size=TEST_SIZE,
        stratify=y,
        random_state=RANDOM_STATE,
    )
    print(f"Train/test sizes: {len(X_train)} / {len(X_test)} (stratified)")

    lr_preprocessor = build_preprocessor(X_train)
    lr_model = train_baseline_model(X_train, y_train, lr_preprocessor)
    xgb_model = train_xgboost_model(X_train, y_train, lr_preprocessor)

    lr_metrics = evaluate_model(lr_model, X_test, y_test, name="Logistic Regression")
    xgb_metrics = evaluate_model(xgb_model, X_test, y_test, name="XGBoost")

    lr_importance = get_feature_importance(lr_model)
    xgb_importance = get_feature_importance(xgb_model)

    print("\n=== Top logistic regression drivers (|coefficient|) ===")
    print(lr_importance.to_string(index=False))
    print(f"OverTime rank (logistic): {overtime_rank(lr_importance, 'abs_coefficient')}")

    print("\n=== Top XGBoost drivers (feature importance) ===")
    print(xgb_importance.to_string(index=False))
    print(f"OverTime rank (XGBoost): {overtime_rank(xgb_importance, 'importance')}")

    # Score full population with the stronger / primary model (XGBoost)
    risk_scores = export_risk_scores(xgb_model, X, ids, RISK_SCORES_PATH)
    print(f"\nWrote {len(risk_scores)} risk scores to {RISK_SCORES_PATH}")
    print(risk_scores["risk_tier"].value_counts().to_string())
    print("\nSample:")
    print(risk_scores.head(5).to_string(index=False))

    return {
        "logistic": lr_metrics,
        "xgboost": xgb_metrics,
        "lr_importance": lr_importance,
        "xgb_importance": xgb_importance,
        "risk_scores": risk_scores,
    }


if __name__ == "__main__":
    main()
