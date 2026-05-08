import os
from datetime import datetime

import joblib
import pandas as pd
from sklearn.model_selection import cross_validate


DEFAULT_DATA_PATH = "data/processed/X_train_balanced_final.csv"
DEFAULT_PREPROCESSING_PATH = "models/preprocessing_pipeline.pkl"
DEFAULT_LOG_PATH = "models/experiments_log.csv"


def load_processed_data(data_path=DEFAULT_DATA_PATH, target_col="Revenue"):
    """
    Carga el dataset procesado y separa variables predictoras y target.
    """
    df = pd.read_csv(data_path)

    if target_col not in df.columns:
        raise ValueError(
            f"La columna target '{target_col}' no existe en {data_path}."
        )

    X = df.drop(columns=[target_col])
    y = df[target_col]

    return X, y, df


def load_preprocessing_pipeline(preprocessing_path=DEFAULT_PREPROCESSING_PATH):
    """
    Carga el pipeline de preprocesamiento persistido.
    """
    if not os.path.exists(preprocessing_path):
        raise FileNotFoundError(
            f"No se encontró el pipeline de preprocesamiento en: {preprocessing_path}"
        )

    return joblib.load(preprocessing_path)


def train_baseline(pipe, X, y, name, models_dir="models"):
    """
    Entrena un modelo baseline y lo guarda en disco.
    """
    os.makedirs(models_dir, exist_ok=True)

    pipe.fit(X, y)

    model_filename = f"baseline_{name}.pkl"
    model_path = os.path.join(models_dir, model_filename)

    joblib.dump(pipe, model_path)

    return pipe, model_path


def evaluate_model(pipe, X, y, cv, scoring):
    """
    Evalúa un modelo con cross-validation.
    """
    results = cross_validate(
        pipe,
        X,
        y,
        cv=cv,
        scoring=scoring,
        return_train_score=True,
        n_jobs=-1
    )
    return results


def summarize_cv_results(results, metrics=None):
    """
    Resume resultados de cross-validation en media y desviación estándar.
    """
    if metrics is None:
        metrics = ["accuracy", "f1", "precision", "recall", "roc_auc"]

    summary = {}

    for metric in metrics:
        test_key = f"test_{metric}"
        train_key = f"train_{metric}"

        if test_key in results:
            summary[f"{metric}_cv_mean"] = results[test_key].mean()
            summary[f"{metric}_cv_std"] = results[test_key].std()

        if train_key in results:
            summary[f"{metric}_train_mean"] = results[train_key].mean()
            summary[f"{metric}_train_std"] = results[train_key].std()

    return summary


def validate_saved_model(model_path, X_sample):
    """
    Valida que un modelo guardado cargue correctamente y pueda predecir.
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"No se encontró el modelo en: {model_path}")

    model = joblib.load(model_path)
    predictions = model.predict(X_sample)

    return model, predictions


def build_experiment_row(
    model_name,
    params,
    metrics,
    selected=False,
    notes="",
    extra_fields=None
):
    """
    Construye una fila de experimento lista para guardarse en CSV.
    """
    row = {
        "model": model_name,
        "params": str(params),
        **metrics,
        "selected": selected,
        "notes": notes,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    if extra_fields:
        row.update(extra_fields)

    return row


def log_experiment(row, log_path=DEFAULT_LOG_PATH):
    """
    Registra una fila de experimento en el CSV.
    """
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    row_df = pd.DataFrame([row])

    if os.path.exists(log_path):
        row_df.to_csv(log_path, mode="a", header=False, index=False)
    else:
        row_df.to_csv(log_path, index=False)


def save_experiments_dataframe(df, log_path=DEFAULT_LOG_PATH):
    """
    Guarda un DataFrame completo de experimentos en CSV.
    """
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    df.to_csv(log_path, index=False)


def get_default_scoring():
    """
    Retorna el conjunto estándar de métricas del Sprint 3.
    """
    return {
        "accuracy": "accuracy",
        "f1": "f1",
        "precision": "precision",
        "recall": "recall",
        "roc_auc": "roc_auc",
    }