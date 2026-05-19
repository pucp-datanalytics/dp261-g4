from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_validate


METRICS = ["accuracy", "precision", "recall", "f1", "roc_auc"]
SCORING = {metric: metric for metric in METRICS}


def cv_strategy(n_splits: int = 5) -> StratifiedKFold:
    return StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)


def predict_scores(model, X):
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)[:, 1]
    if hasattr(model, "decision_function"):
        raw = model.decision_function(X)
        return 1 / (1 + np.exp(-raw))
    return model.predict(X)


def metric_row(model_name: str, phase: str, y_true, y_score, threshold: float = 0.5) -> dict:
    y_pred = (y_score >= threshold).astype(int)
    return {
        "model": model_name,
        "phase": phase,
        "threshold": threshold,
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_true, y_score),
    }


def evaluate_cv(model, X, y, model_name: str, phase: str, n_splits: int = 5) -> dict:
    scores = cross_validate(
        model,
        X,
        y,
        scoring=SCORING,
        cv=cv_strategy(n_splits),
        n_jobs=-1,
        return_train_score=True,
        error_score="raise",
    )
    row = {"model": model_name, "phase": phase, "cv_folds": n_splits}
    for metric in METRICS:
        row[f"train_{metric}"] = float(scores[f"train_{metric}"].mean())
        row[f"train_{metric}_std"] = float(scores[f"train_{metric}"].std())
        row[f"cv_{metric}"] = float(scores[f"test_{metric}"].mean())
        row[f"cv_{metric}_std"] = float(scores[f"test_{metric}"].std())
    return row


def write_csv(rows: list[dict] | pd.DataFrame, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    df.to_csv(path, index=False)


def save_json(data: dict, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")


def save_model(model, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)


def best_by_f1(df: pd.DataFrame, prefix: str = "cv_") -> pd.Series:
    return df.sort_values([f"{prefix}f1", f"{prefix}recall", f"{prefix}roc_auc"], ascending=False).iloc[0]
