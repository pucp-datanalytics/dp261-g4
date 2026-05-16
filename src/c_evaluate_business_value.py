from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix

from c_preprocessing import prepare_data
from c_utils import predict_scores, save_json


BENEFIT_TP = 100.0
COST_FP = -10.0
COST_FN = -80.0
BENEFIT_TN = 0.0


def value_at_threshold(y_true, y_score, threshold: float) -> dict:
    y_pred = (y_score >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    expected_value = tp * BENEFIT_TP + fp * COST_FP + fn * COST_FN + tn * BENEFIT_TN
    return {
        "threshold": threshold,
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "expected_value": float(expected_value),
        "value_per_session": float(expected_value / len(y_true)),
    }


def gain_lift(y_true, y_score, bins: int = 10) -> pd.DataFrame:
    df = pd.DataFrame({"target": y_true.to_numpy(), "score": y_score}).sort_values("score", ascending=False)
    df = df.reset_index(drop=True)
    df["decile"] = pd.qcut(df.index + 1, q=bins, labels=False, duplicates="drop") + 1
    base_rate = df["target"].mean()
    total_pos = df["target"].sum()
    rows = []
    cum_pos = 0
    cum_n = 0
    for decile, group in df.groupby("decile", sort=True):
        positives = int(group["target"].sum())
        cum_pos += positives
        cum_n += len(group)
        rows.append(
            {
                "decile": int(decile),
                "sessions": int(len(group)),
                "positives": positives,
                "response_rate": positives / len(group),
                "cumulative_gain": cum_pos / total_pos if total_pos else 0.0,
                "cumulative_lift": (cum_pos / cum_n) / base_rate if base_rate else 0.0,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    _, X_test, _, y_test = prepare_data()
    model_path = Path("models/c_final_model.pkl")
    if not model_path.exists():
        raise FileNotFoundError("Ejecuta primero: python src/c_tune_models.py")
    model = joblib.load(model_path)
    scores = predict_scores(model, X_test)

    thresholds = np.round(np.arange(0.05, 0.96, 0.05), 2)
    threshold_df = pd.DataFrame([value_at_threshold(y_test, scores, float(t)) for t in thresholds])
    threshold_df.to_csv("models/c_threshold_analysis.csv", index=False)
    threshold_df.to_csv("models/c_business_value_results.csv", index=False)
    threshold_df.to_csv("reports/c_business_value_threshold_analysis.csv", index=False)

    lift_df = gain_lift(y_test, scores)
    lift_df.to_csv("models/c_gain_lift.csv", index=False)
    best = threshold_df.sort_values(["expected_value", "tp"], ascending=False).iloc[0]
    summary = {
        "assumptions": {
            "benefit_true_positive": BENEFIT_TP,
            "cost_false_positive": COST_FP,
            "cost_false_negative": COST_FN,
            "benefit_true_negative": BENEFIT_TN,
            "note": "Supuestos razonables y modificables ante falta de costos reales.",
        },
        "recommended_business_threshold": best.to_dict(),
        "default_threshold": value_at_threshold(y_test, scores, 0.5),
    }
    save_json(summary, "models/c_business_value_summary.json")

    Path("reports/c_business_value_summary.md").write_text(
        "# Business Value Summary\n\n"
        "Sprint 5 usa el modelo final del Sprint 4; no entrena modelos nuevos.\n\n"
        "## Supuestos\n\n"
        f"- Beneficio TP: {BENEFIT_TP}\n"
        f"- Costo FP: {COST_FP}\n"
        f"- Costo FN: {COST_FN}\n"
        f"- Beneficio/costo TN: {BENEFIT_TN}\n\n"
        "## Resultado\n\n"
        f"- Umbral recomendado de negocio: {best['threshold']:.2f}\n"
        f"- Valor esperado: {best['expected_value']:.2f}\n"
        f"- Valor por sesion: {best['value_per_session']:.4f}\n\n"
        "Estos supuestos deben validarse con negocio antes de Sprint 6.\n",
        encoding="utf-8",
    )
    print(threshold_df.round(4).to_string(index=False))
    print("\nUmbral recomendado de negocio:")
    print(best.round(4).to_string())


if __name__ == "__main__":
    main()
