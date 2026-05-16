from __future__ import annotations

from pathlib import Path
import sys

import joblib
import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from c_preprocessing import TARGET_COL, add_features, clean_data, load_raw_data
from c_utils import predict_scores


def path(name: str) -> Path:
    return ROOT / name


@st.cache_data
def load_dataset() -> tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    df = clean_data(load_raw_data(path("docs/dataset_pucp.csv")))
    X = add_features(df.drop(columns=[TARGET_COL]))
    return df, X, df[TARGET_COL]


@st.cache_data
def load_csv(relative_path: str) -> pd.DataFrame:
    file_path = path(relative_path)
    if file_path.exists():
        return pd.read_csv(file_path)
    return pd.DataFrame()


@st.cache_resource
def load_model():
    for relative_path in ["models/c_final_model.pkl", "models/c_best_model.pkl"]:
        file_path = path(relative_path)
        if file_path.exists():
            return joblib.load(file_path), relative_path
    return None, ""


@st.cache_data
def load_dashboard_bundle() -> dict:
    return {
        "metrics": load_csv("models/c_metrics_summary.csv"),
        "validation": load_csv("models/c_validation_test_comparison.csv"),
        "thresholds": load_csv("models/c_threshold_analysis.csv"),
        "kpis": load_csv("models/c_dashboard_kpis.csv"),
        "segments": load_csv("models/c_dashboard_segments.csv"),
        "feature_summary": load_csv("models/c_dashboard_feature_summary.csv"),
        "dashboard_thresholds": load_csv("models/c_dashboard_threshold_summary.csv"),
    }


def score_dataset(model, X: pd.DataFrame) -> pd.Series:
    return pd.Series(predict_scores(model, X), index=X.index, name="purchase_probability")
