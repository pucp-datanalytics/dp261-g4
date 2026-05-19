from __future__ import annotations

import warnings
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

try:
    from xgboost import XGBClassifier
except Exception:
    XGBClassifier = None

try:
    from lightgbm import LGBMClassifier
except Exception:
    LGBMClassifier = None

from c_preprocessing import RANDOM_STATE, build_model_pipeline, prepare_data
from c_utils import evaluate_cv, save_model, write_csv


warnings.filterwarnings("ignore")


def baseline_models() -> dict:
    return {
        "logistic_regression": LogisticRegression(max_iter=1200, random_state=RANDOM_STATE),
        "decision_tree": DecisionTreeClassifier(random_state=RANDOM_STATE),
        "random_forest": RandomForestClassifier(n_estimators=160, random_state=RANDOM_STATE, n_jobs=-1),
        "svm": SVC(probability=True, random_state=RANDOM_STATE),
        "knn": KNeighborsClassifier(n_neighbors=5),
    }


def advanced_initial_models() -> dict:
    models = {}
    if XGBClassifier is not None:
        models["xgboost_initial"] = XGBClassifier(
            n_estimators=160,
            max_depth=4,
            learning_rate=0.08,
            subsample=0.9,
            colsample_bytree=0.9,
            eval_metric="logloss",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )
    if LGBMClassifier is not None:
        models["lightgbm_initial"] = LGBMClassifier(
            n_estimators=160,
            learning_rate=0.08,
            random_state=RANDOM_STATE,
            n_jobs=-1,
            verbose=-1,
        )
    return models


def main() -> None:
    X_train, X_test, y_train, y_test = prepare_data()
    print(f"Train: {X_train.shape}; Test: {X_test.shape}")
    print("Distribucion Revenue en train:")
    print(y_train.value_counts(normalize=True).round(4).to_string())

    rows = []
    all_models = {**baseline_models(), **advanced_initial_models()}
    for name, estimator in all_models.items():
        phase = "advanced_initial" if name.endswith("_initial") else "baseline"
        print(f"\nEntrenando {name}")
        pipe = build_model_pipeline(estimator, use_smote=True)
        row = evaluate_cv(pipe, X_train, y_train, name, phase, n_splits=5)
        rows.append(row)
        pipe.fit(X_train, y_train)
        save_name = name.replace("_initial", "_base")
        save_model(pipe, Path("models") / f"c_baseline_{save_name}.pkl")
        print(pd.Series(row)[["cv_accuracy", "cv_precision", "cv_recall", "cv_f1", "cv_roc_auc"]].round(4).to_string())

    df = pd.DataFrame(rows).sort_values(["cv_f1", "cv_recall", "cv_roc_auc"], ascending=False)
    write_csv(df, "models/c_baseline_metrics.csv")
    write_csv(df, "models/c_metrics_summary.csv")
    write_csv(df.assign(stage="sprint3_baseline"), "models/c_experiments_log.csv")
    print("\nTabla comparativa:")
    print(df[["model", "phase", "cv_accuracy", "cv_precision", "cv_recall", "cv_f1", "cv_roc_auc"]].round(4).to_string(index=False))
    print("\nTop candidatos por F1:")
    print(df.head(3)[["model", "cv_f1", "cv_recall", "cv_roc_auc"]].round(4).to_string(index=False))


if __name__ == "__main__":
    main()
