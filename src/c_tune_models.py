from __future__ import annotations

import shutil
import warnings
from pathlib import Path

import joblib
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RandomizedSearchCV, train_test_split
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
from c_utils import cv_strategy, evaluate_cv, metric_row, predict_scores, save_json, save_model, write_csv


warnings.filterwarnings("ignore")


def search_space(model_name: str):
    if model_name.startswith("random_forest"):
        return RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1), {
            "classifier__n_estimators": [160, 240, 320],
            "classifier__max_depth": [None, 8, 12, 16],
            "classifier__min_samples_leaf": [1, 2, 4],
            "classifier__class_weight": [None, "balanced"],
        }
    if model_name.startswith("xgboost") and XGBClassifier is not None:
        return XGBClassifier(eval_metric="logloss", random_state=RANDOM_STATE, n_jobs=-1), {
            "classifier__n_estimators": [160, 240, 320],
            "classifier__max_depth": [3, 4, 5],
            "classifier__learning_rate": [0.03, 0.06, 0.1],
            "classifier__subsample": [0.8, 0.9, 1.0],
            "classifier__colsample_bytree": [0.8, 0.9, 1.0],
        }
    if model_name.startswith("lightgbm") and LGBMClassifier is not None:
        return LGBMClassifier(random_state=RANDOM_STATE, n_jobs=-1, verbose=-1), {
            "classifier__n_estimators": [160, 240, 320],
            "classifier__num_leaves": [15, 31, 63],
            "classifier__learning_rate": [0.03, 0.06, 0.1],
            "classifier__min_child_samples": [10, 20, 40],
        }
    if model_name.startswith("svm"):
        return SVC(probability=True, random_state=RANDOM_STATE), {
            "classifier__C": [0.5, 1.0, 2.0],
            "classifier__gamma": ["scale", 0.05, 0.1],
        }
    if model_name.startswith("logistic_regression"):
        return LogisticRegression(max_iter=1600, random_state=RANDOM_STATE), {
            "classifier__C": [0.1, 0.5, 1.0, 2.0],
            "classifier__class_weight": [None, "balanced"],
        }
    if model_name.startswith("decision_tree"):
        return DecisionTreeClassifier(random_state=RANDOM_STATE), {
            "classifier__max_depth": [4, 6, 8, 12, None],
            "classifier__min_samples_leaf": [1, 5, 10, 20],
            "classifier__class_weight": [None, "balanced"],
        }
    return None, None


def choose_candidates(baseline: pd.DataFrame) -> list[str]:
    ranked = baseline.sort_values(["cv_f1", "cv_recall", "cv_roc_auc"], ascending=False)
    candidates = ranked["model"].head(3).tolist()
    for required in ["xgboost_initial", "lightgbm_initial"]:
        if required in ranked["model"].values and required not in candidates:
            candidates.append(required)
    return candidates[:4]


def threshold_from_train_validation(model, X_train, y_train) -> tuple[float, pd.DataFrame]:
    X_fit, X_val, y_fit, y_val = train_test_split(
        X_train,
        y_train,
        test_size=0.25,
        stratify=y_train,
        random_state=RANDOM_STATE,
    )
    candidate = clone(model)
    candidate.fit(X_fit, y_fit)
    scores = predict_scores(candidate, X_val)
    rows = []
    for threshold in [round(x / 100, 2) for x in range(10, 91, 2)]:
        rows.append(metric_row("threshold_candidate", "train_validation_threshold", y_val, scores, threshold))
    df = pd.DataFrame(rows)
    best = df.sort_values(["f1", "recall", "roc_auc"], ascending=False).iloc[0]
    return float(best["threshold"]), df


def main() -> None:
    baseline_path = Path("models/c_baseline_metrics.csv")
    if not baseline_path.exists():
        raise FileNotFoundError("Ejecuta primero: python src/c_train_baselines.py")

    X_train, X_test, y_train, y_test = prepare_data()
    baseline = pd.read_csv(baseline_path)
    candidates = choose_candidates(baseline)
    print("Candidatos para tuning:", ", ".join(candidates))

    tuned_rows = []
    validation_rows = []
    tuned_models = {}
    for original_name in candidates:
        estimator, params = search_space(original_name)
        if estimator is None:
            continue
        model_name = original_name.replace("_initial", "").replace("_base", "")
        print(f"\nTuning {model_name} con scoring='f1'")
        pipe = build_model_pipeline(estimator, use_smote=True)
        search = RandomizedSearchCV(
            pipe,
            params,
            n_iter=10,
            scoring="f1",
            cv=cv_strategy(3),
            random_state=RANDOM_STATE,
            n_jobs=-1,
            error_score="raise",
            return_train_score=True,
        )
        search.fit(X_train, y_train)
        best_estimator = search.best_estimator_
        cv_row = evaluate_cv(best_estimator, X_train, y_train, model_name, "tuned", n_splits=5)
        cv_row["best_params"] = search.best_params_
        tuned_rows.append(cv_row)
        model_path = Path("models") / f"c_tuned_{model_name}.pkl"
        save_model(best_estimator, model_path)
        tuned_models[model_name] = best_estimator

        train_row = metric_row(model_name, "train_fit", y_train, predict_scores(best_estimator, X_train), 0.5)
        test_row = metric_row(model_name, "test_0_5", y_test, predict_scores(best_estimator, X_test), 0.5)
        validation_rows.extend([train_row, test_row])
        print(pd.Series(cv_row)[["cv_accuracy", "cv_precision", "cv_recall", "cv_f1", "cv_roc_auc"]].round(4).to_string())
        print(pd.Series(test_row)[["accuracy", "precision", "recall", "f1", "roc_auc"]].round(4).to_string())

    tuned_df = pd.DataFrame(tuned_rows).sort_values(["cv_f1", "cv_recall", "cv_roc_auc"], ascending=False)
    if tuned_df.empty:
        raise RuntimeError("No se pudo tunear ningun candidato.")

    winner = tuned_df.iloc[0]
    winner_name = winner["model"]
    final_model = tuned_models[winner_name]
    best_threshold, threshold_df = threshold_from_train_validation(final_model, X_train, y_train)
    threshold_df.to_csv("models/c_f1_threshold_analysis.csv", index=False)

    final_model.fit(X_train, y_train)
    final_scores_train = predict_scores(final_model, X_train)
    final_scores_test = predict_scores(final_model, X_test)
    final_rows = [
        metric_row(winner_name, "final_train_threshold_0_5", y_train, final_scores_train, 0.5),
        metric_row(winner_name, "final_test_threshold_0_5", y_test, final_scores_test, 0.5),
        metric_row(winner_name, "final_train_threshold_f1", y_train, final_scores_train, best_threshold),
        metric_row(winner_name, "final_test_threshold_f1", y_test, final_scores_test, best_threshold),
    ]
    validation_rows.extend(final_rows)

    save_model(final_model, "models/c_best_model.pkl")
    save_model(final_model, "models/c_final_model.pkl")
    shutil.copyfile("models/c_final_model.pkl", "handoff/model/c_final_model.pkl")
    shutil.copyfile("models/c_preprocessing_pipeline.pkl", "handoff/model/c_preprocessing_pipeline.pkl")

    experiments = pd.concat(
        [baseline.assign(stage="baseline_or_initial"), tuned_df.assign(stage="tuned")],
        ignore_index=True,
        sort=False,
    )
    write_csv(experiments, "models/c_experiments_log.csv")
    write_csv(experiments, "models/c_metrics_summary.csv")
    write_csv(pd.DataFrame(validation_rows), "models/c_validation_test_comparison.csv")
    save_json(
        {
            "winner": winner_name,
            "selection_criterion": "highest cross-validation F1-score; test set used only for final evaluation",
            "f1_threshold_selected_on_train_validation": best_threshold,
            "cv_metrics": winner.to_dict(),
            "test_metrics_threshold_f1": final_rows[-1],
        },
        "models/c_best_model_metadata.json",
    )

    print("\nModelo ganador por F1 CV:", winner_name)
    print("Umbral F1 seleccionado sin usar test:", best_threshold)
    print(pd.DataFrame(final_rows).round(4).to_string(index=False))


if __name__ == "__main__":
    main()
