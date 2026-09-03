"""
model_training.py
==================
Trains and evaluates classification models to predict employee attrition.

STATUS: placeholder stub — logic to be filled in.

Planned approach:
    1. Baseline: Logistic Regression (interpretable, good benchmark)
    2. Main model: XGBoost classifier
    3. Evaluate with ROC-AUC, precision/recall (attrition is imbalanced ~16% positive class)
    4. Extract feature importance to identify key attrition drivers

Usage (once implemented):
    python src/model_training.py
"""

import pandas as pd
from pathlib import Path

# from sklearn.model_selection import train_test_split
# from sklearn.linear_model import LogisticRegression
# from sklearn.metrics import roc_auc_score, classification_report
# from xgboost import XGBClassifier

PROCESSED_DATA_PATH = Path("data/processed/employee_attrition_clean.csv")


def load_features(path: Path) -> pd.DataFrame:
    """Load the cleaned dataset ready for modeling."""
    return pd.read_csv(path)


def train_baseline_model(X_train, y_train):
    """Train a logistic regression baseline."""
    # TODO
    raise NotImplementedError


def train_xgboost_model(X_train, y_train):
    """Train the main XGBoost classifier."""
    # TODO
    raise NotImplementedError


def evaluate_model(model, X_test, y_test):
    """Evaluate a trained model: ROC-AUC, precision/recall, confusion matrix."""
    # TODO
    raise NotImplementedError


def get_feature_importance(model, feature_names):
    """Extract and rank feature importance to identify attrition drivers."""
    # TODO
    raise NotImplementedError


def main():
    print("TODO: implement full training pipeline")
    # df = load_features(PROCESSED_DATA_PATH)
    # ... train/test split, train models, evaluate, print feature importance


if __name__ == "__main__":
    main()
