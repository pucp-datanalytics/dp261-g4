from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

from c_preprocessing import TARGET_COL, add_features, clean_data, load_raw_data


def safe_read_csv(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def conversion_segments(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in ["VisitorType", "Month", "Weekend"]:
        seg = (
            df.groupby(col, dropna=False)[TARGET_COL]
            .agg(["count", "sum", "mean"])
            .reset_index()
            .rename(columns={col: "segment", "count": "sessions", "sum": "buyers", "mean": "conversion_rate"})
        )
        seg.insert(0, "dimension", col)
        rows.append(seg)
    return pd.concat(rows, ignore_index=True)


def feature_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in ["PageValues", "ProductRelated_Duration", "BounceRates", "ExitRates"]:
        tmp = df.groupby(TARGET_COL)[col].mean().reset_index()
        tmp["feature"] = col
        tmp = tmp.rename(columns={col: "average_value", TARGET_COL: "revenue"})
        rows.append(tmp[["feature", "revenue", "average_value"]])
    return pd.concat(rows, ignore_index=True)


def model_feature_importance(model_path: str | Path = "models/c_final_model.pkl") -> pd.DataFrame:
    path = Path(model_path)
    if not path.exists():
        return pd.DataFrame()
    model = joblib.load(path)
    if not hasattr(model, "named_steps"):
        return pd.DataFrame()
    classifier = model.named_steps.get("classifier")
    preprocessor = model.named_steps.get("preprocessor")
    if classifier is None or preprocessor is None:
        return pd.DataFrame()
    names = preprocessor.get_feature_names_out()
    if hasattr(classifier, "feature_importances_"):
        values = classifier.feature_importances_
    elif hasattr(classifier, "coef_"):
        values = abs(classifier.coef_[0])
    else:
        return pd.DataFrame()
    return pd.DataFrame({"feature": names, "importance": values}).sort_values("importance", ascending=False)


def dashboard_kpis() -> pd.DataFrame:
    df = clean_data(load_raw_data())
    validation = safe_read_csv("models/c_validation_test_comparison.csv")
    threshold = safe_read_csv("models/c_threshold_analysis.csv")
    final_test = validation[validation["phase"].eq("final_test_threshold_0_5")]
    best_value = threshold.sort_values("expected_value", ascending=False).head(1) if not threshold.empty else pd.DataFrame()
    row = {
        "sessions": len(df),
        "real_conversion_rate": df[TARGET_COL].mean(),
        "real_buyers": int(df[TARGET_COL].sum()),
        "f1": float(final_test.iloc[0]["f1"]) if not final_test.empty else None,
        "recall": float(final_test.iloc[0]["recall"]) if not final_test.empty else None,
        "precision": float(final_test.iloc[0]["precision"]) if not final_test.empty else None,
        "roc_auc": float(final_test.iloc[0]["roc_auc"]) if not final_test.empty else None,
        "recommended_threshold": float(best_value.iloc[0]["threshold"]) if not best_value.empty else 0.5,
        "expected_value": float(best_value.iloc[0]["expected_value"]) if not best_value.empty else 0.0,
        "detected_buyers": int(best_value.iloc[0]["tp"]) if not best_value.empty else None,
    }
    return pd.DataFrame([row])


def build_dashboard_artifacts() -> None:
    Path("models").mkdir(exist_ok=True)
    df = clean_data(load_raw_data())
    dashboard_kpis().to_csv("models/c_dashboard_kpis.csv", index=False)
    conversion_segments(df).to_csv("models/c_dashboard_segments.csv", index=False)
    feature_summary(df).to_csv("models/c_dashboard_feature_summary.csv", index=False)
    safe_read_csv("models/c_threshold_analysis.csv").to_csv("models/c_dashboard_threshold_summary.csv", index=False)


if __name__ == "__main__":
    build_dashboard_artifacts()
