from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import sys

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from c_preprocessing import TARGET_COL
from c_utils import predict_scores


@dataclass(frozen=True)
class EconomicAssumptions:
    average_purchase_usd: float = 180.0
    gross_margin_pct: float = 0.45
    incentive_cost_usd: float = 8.0
    contact_cost_usd: float = 2.0
    uplift_pct: float = 0.40
    false_negative_cost_usd: float = 60.0
    true_negative_value_usd: float = 0.0

    @property
    def intervention_cost_usd(self) -> float:
        return float(self.incentive_cost_usd + self.contact_cost_usd)

    @property
    def benefit_tp_usd(self) -> float:
        incremental_margin = self.average_purchase_usd * self.gross_margin_pct * self.uplift_pct
        return float(incremental_margin - self.intervention_cost_usd)

    @property
    def cost_fp_usd(self) -> float:
        return float(-self.intervention_cost_usd)

    @property
    def cost_fn_usd(self) -> float:
        return float(-self.false_negative_cost_usd)

    @property
    def benefit_tn_usd(self) -> float:
        return float(self.true_negative_value_usd)


MODEL_REGISTRY = [
    {
        "model": "XGBoost",
        "model_id": "xgboost_tuned",
        "type": "tuned",
        "path": "models/c_final_model.pkl",
        "priority": 1,
        "recommended": True,
    },
    {
        "model": "LightGBM",
        "model_id": "lightgbm_tuned",
        "type": "tuned",
        "path": "models/c_tuned_lightgbm.pkl",
        "priority": 2,
        "recommended": False,
    },
    {
        "model": "Random Forest",
        "model_id": "random_forest_tuned",
        "type": "tuned",
        "path": "models/c_tuned_random_forest.pkl",
        "priority": 3,
        "recommended": False,
    },
    {
        "model": "Random Forest baseline",
        "model_id": "random_forest_baseline",
        "type": "baseline",
        "path": "models/c_baseline_random_forest.pkl",
        "priority": 10,
        "recommended": False,
    },
    {
        "model": "Logistic Regression baseline",
        "model_id": "logistic_regression_baseline",
        "type": "baseline",
        "path": "models/c_baseline_logistic_regression.pkl",
        "priority": 11,
        "recommended": False,
    },
    {
        "model": "Decision Tree baseline",
        "model_id": "decision_tree_baseline",
        "type": "baseline",
        "path": "models/c_baseline_decision_tree.pkl",
        "priority": 12,
        "recommended": False,
    },
    {
        "model": "SVM baseline",
        "model_id": "svm_baseline",
        "type": "baseline",
        "path": "models/c_baseline_svm.pkl",
        "priority": 13,
        "recommended": False,
    },
    {
        "model": "KNN baseline",
        "model_id": "knn_baseline",
        "type": "baseline",
        "path": "models/c_baseline_knn.pkl",
        "priority": 14,
        "recommended": False,
    },
    {
        "model": "XGBoost inicial",
        "model_id": "xgboost_initial",
        "type": "advanced_initial",
        "path": "models/c_baseline_xgboost_base.pkl",
        "priority": 20,
        "recommended": False,
    },
    {
        "model": "LightGBM inicial",
        "model_id": "lightgbm_initial",
        "type": "advanced_initial",
        "path": "models/c_baseline_lightgbm_base.pkl",
        "priority": 21,
        "recommended": False,
    },
]

MODEL_CURVE_IDS = tuple(item["model_id"] for item in MODEL_REGISTRY)


def load_test_data() -> tuple[pd.DataFrame, pd.Series]:
    test_path = ROOT / "data" / "processed" / "c_test.csv"
    if not test_path.exists():
        raise FileNotFoundError("No se encontro data/processed/c_test.csv")
    test = pd.read_csv(test_path)
    if TARGET_COL not in test.columns:
        raise ValueError(f"No se encontro el target {TARGET_COL} en c_test.csv")
    X = test.drop(columns=[TARGET_COL])
    y = test[TARGET_COL].astype(int)
    return X, y


def safe_auc(y_true: pd.Series, scores: np.ndarray) -> float:
    try:
        return float(roc_auc_score(y_true, scores))
    except ValueError:
        return 0.0


def compute_metrics(y_true: pd.Series, scores: np.ndarray, threshold: float) -> dict:
    pred = (scores >= threshold).astype(int)
    return {
        "accuracy": float(accuracy_score(y_true, pred)),
        "precision": float(precision_score(y_true, pred, zero_division=0)),
        "recall": float(recall_score(y_true, pred, zero_division=0)),
        "f1": float(f1_score(y_true, pred, zero_division=0)),
        "roc_auc": safe_auc(y_true, scores),
    }


def compute_economic_value(y_true: pd.Series, scores: np.ndarray, threshold: float, assumptions: EconomicAssumptions) -> dict:
    pred = (scores >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, pred, labels=[0, 1]).ravel()
    tp_value = tp * assumptions.benefit_tp_usd
    fp_value = fp * assumptions.cost_fp_usd
    fn_value = fn * assumptions.cost_fn_usd
    tn_value = tn * assumptions.benefit_tn_usd
    net_value = tp_value + fp_value + fn_value + tn_value
    visitors_impacted = int(tp + fp)
    intervention_cost = visitors_impacted * assumptions.intervention_cost_usd
    roi = (net_value / intervention_cost * 100.0) if intervention_cost > 0 else 0.0
    return {
        "threshold": float(threshold),
        "tp": int(tp),
        "fp": int(fp),
        "fn": int(fn),
        "tn": int(tn),
        "visitors_impacted": visitors_impacted,
        "benefit_tp_usd": float(tp_value),
        "cost_fp_usd": float(fp_value),
        "cost_fn_usd": float(fn_value),
        "value_tn_usd": float(tn_value),
        "intervention_cost_usd": float(intervention_cost),
        "net_value_usd": float(net_value),
        "roi_pct": float(roi),
    }


def load_available_model_scores() -> dict[str, dict]:
    X, y = load_test_data()
    return score_available_models(X, y)


def score_available_models(X: pd.DataFrame, y: pd.Series | None = None) -> dict[str, dict]:
    scores_by_model: dict[str, dict] = {}
    for spec in MODEL_REGISTRY:
        model_path = ROOT / spec["path"]
        if not model_path.exists():
            continue
        try:
            model = joblib.load(model_path)
            scores = np.asarray(predict_scores(model, X), dtype=float)
        except Exception as exc:  # noqa: BLE001 - dashboard artifact generation should be tolerant.
            print(f"No se pudo puntuar {spec['model']} ({spec['path']}): {exc}")
            continue
        scores_by_model[spec["model_id"]] = {**spec, "scores": scores, "y_true": y}
    return scores_by_model


def score_single_model(X: pd.DataFrame, model_id: str = "xgboost_tuned", y: pd.Series | None = None) -> dict:
    spec = next((item for item in MODEL_REGISTRY if item["model_id"] == model_id), None)
    if spec is None:
        return {}
    model_path = ROOT / spec["path"]
    if not model_path.exists():
        return {}
    model = joblib.load(model_path)
    scores = np.asarray(predict_scores(model, X), dtype=float)
    return {**spec, "scores": scores, "y_true": y}


def compute_model_economic_comparison(
    assumptions: EconomicAssumptions | None = None,
    threshold: float = 0.5,
    include_baselines: bool = True,
) -> pd.DataFrame:
    assumptions = assumptions or EconomicAssumptions()
    rows = []
    scores_by_model = load_available_model_scores()
    y_true = next(iter(scores_by_model.values()))["y_true"] if scores_by_model else pd.Series(dtype=int)
    for item in scores_by_model.values():
        economic = compute_economic_value(y_true, item["scores"], threshold, assumptions)
        metrics = compute_metrics(y_true, item["scores"], threshold)
        rows.append(
            {
                "model": item["model"],
                "model_id": item["model_id"],
                "type": item["type"],
                "artifact_path": item["path"],
                "recommended": bool(item["recommended"]),
                "priority": int(item["priority"]),
                **metrics,
                **economic,
                **asdict(assumptions),
            }
        )
    if include_baselines and not y_true.empty:
        rows.extend(compute_operational_baselines(y_true, scores_by_model, assumptions, threshold))
    if not rows:
        return pd.DataFrame()
    comparison = pd.DataFrame(rows)
    best_baseline_value = best_baseline_net_value(comparison)
    no_model_value = comparison.loc[comparison["model_id"].eq("baseline_no_model"), "net_value_usd"]
    no_model_value = float(no_model_value.iloc[0]) if not no_model_value.empty else 0.0
    xgb_value = comparison.loc[comparison["model_id"].eq("xgboost_tuned"), "net_value_usd"]
    xgb_value = float(xgb_value.iloc[0]) if not xgb_value.empty else 0.0
    comparison["incremental_vs_best_baseline_usd"] = comparison["net_value_usd"] - best_baseline_value
    comparison["incremental_vs_no_model_usd"] = comparison["net_value_usd"] - no_model_value
    comparison["difference_vs_xgboost_usd"] = comparison["net_value_usd"] - xgb_value
    comparison["recommendation"] = comparison.apply(recommendation_text, axis=1)
    return comparison.sort_values(["recommended", "net_value_usd", "priority"], ascending=[False, False, True]).reset_index(drop=True)


def compute_model_economic_comparison_for_dataset(
    X: pd.DataFrame,
    y: pd.Series,
    assumptions: EconomicAssumptions | None = None,
    threshold: float = 0.5,
    include_baselines: bool = True,
) -> pd.DataFrame:
    assumptions = assumptions or EconomicAssumptions()
    scores_by_model = score_available_models(X, y)
    rows = []
    for item in scores_by_model.values():
        scores = item["scores"]
        economic = compute_economic_value(y, scores, threshold, assumptions)
        metrics = compute_metrics(y, scores, threshold)
        rows.append(
            {
                "model": item["model"],
                "model_id": item["model_id"],
                "type": item["type"],
                "artifact_path": item["path"],
                "recommended": bool(item["recommended"]),
                "priority": int(item["priority"]),
                **metrics,
                **economic,
                **asdict(assumptions),
            }
        )
    if include_baselines and rows:
        rows.extend(compute_operational_baselines(y, scores_by_model, assumptions, threshold))
    if not rows:
        return pd.DataFrame()
    comparison = pd.DataFrame(rows)
    best_baseline_value = best_baseline_net_value(comparison)
    no_model_value = comparison.loc[comparison["model_id"].eq("baseline_no_model"), "net_value_usd"]
    no_model_value = float(no_model_value.iloc[0]) if not no_model_value.empty else 0.0
    xgb_value = comparison.loc[comparison["model_id"].eq("xgboost_tuned"), "net_value_usd"]
    xgb_value = float(xgb_value.iloc[0]) if not xgb_value.empty else 0.0
    comparison["incremental_vs_best_baseline_usd"] = comparison["net_value_usd"] - best_baseline_value
    comparison["incremental_vs_no_model_usd"] = comparison["net_value_usd"] - no_model_value
    comparison["difference_vs_xgboost_usd"] = comparison["net_value_usd"] - xgb_value
    comparison["recommendation"] = comparison.apply(recommendation_text, axis=1)
    return comparison.sort_values(["recommended", "net_value_usd", "priority"], ascending=[False, False, True]).reset_index(drop=True)


def compute_profit_curve_for_dataset(
    X: pd.DataFrame,
    y: pd.Series,
    assumptions: EconomicAssumptions | None = None,
    thresholds: np.ndarray | None = None,
    model_ids: tuple[str, ...] | None = None,
) -> pd.DataFrame:
    assumptions = assumptions or EconomicAssumptions()
    thresholds = thresholds if thresholds is not None else np.round(np.arange(0.05, 0.96, 0.01), 2)
    model_ids = model_ids or MODEL_CURVE_IDS
    scores_by_model = score_available_models(X, y)
    rows = []
    for model_id in model_ids:
        item = scores_by_model.get(model_id)
        if not item:
            continue
        for threshold in thresholds:
            economic = compute_economic_value(y, item["scores"], float(threshold), assumptions)
            metrics = compute_metrics(y, item["scores"], float(threshold))
            rows.append(
                {
                    "model": item["model"],
                    "model_id": item["model_id"],
                    "type": item["type"],
                    "recommended": bool(item["recommended"]),
                    **metrics,
                    **economic,
                    **asdict(assumptions),
                }
            )
    if not rows:
        return pd.DataFrame()
    curve = pd.DataFrame(rows)
    curve["is_best_value_threshold"] = curve.groupby("model_id")["net_value_usd"].transform("max").eq(curve["net_value_usd"])
    curve["is_best_f1_threshold"] = curve.groupby("model_id")["f1"].transform("max").eq(curve["f1"])
    return curve


def compute_prediction_table(
    X: pd.DataFrame,
    assumptions: EconomicAssumptions,
    threshold: float = 0.5,
    model_id: str = "xgboost_tuned",
) -> pd.DataFrame:
    item = score_single_model(X, model_id=model_id)
    if not item:
        return pd.DataFrame()
    probabilities = np.asarray(item["scores"], dtype=float)
    predictions = (probabilities >= threshold).astype(int)
    table = pd.DataFrame(
        {
            "row_id": np.arange(len(probabilities)),
            "purchase_probability": probabilities,
            "prediction": predictions,
        }
    )
    table["intention_level"] = pd.cut(
        table["purchase_probability"],
        bins=[-0.01, 0.35, 0.70, 1.01],
        labels=["Baja", "Media", "Alta"],
    ).astype(str)
    table["recommended_action"] = table["intention_level"].map(
        {
            "Alta": "Cupon, chat prioritario u oferta personalizada",
            "Media": "Recomendacion de productos o recordatorio",
            "Baja": "Navegacion normal y retargeting posterior",
        }
    )
    table["estimated_impact_usd"] = np.where(
        table["prediction"].eq(1),
        table["purchase_probability"] * assumptions.benefit_tp_usd + (1 - table["purchase_probability"]) * assumptions.cost_fp_usd,
        table["purchase_probability"] * assumptions.cost_fn_usd,
    )
    return table


def compute_potential_value_without_target(predictions: pd.DataFrame, assumptions: EconomicAssumptions) -> dict:
    if predictions.empty:
        return {
            "visitors": 0,
            "recommended_interventions": 0,
            "high_intention": 0,
            "estimated_intervention_cost_usd": 0.0,
            "estimated_potential_value_usd": 0.0,
        }
    recommended = predictions[predictions["prediction"].eq(1)]
    return {
        "visitors": int(len(predictions)),
        "recommended_interventions": int(len(recommended)),
        "high_intention": int(predictions["intention_level"].eq("Alta").sum()),
        "estimated_intervention_cost_usd": float(len(recommended) * assumptions.intervention_cost_usd),
        "estimated_potential_value_usd": float(predictions["estimated_impact_usd"].sum()),
    }


def compute_operational_baselines(
    y_true: pd.Series,
    scores_by_model: dict[str, dict],
    assumptions: EconomicAssumptions,
    threshold: float,
) -> list[dict]:
    y_values = y_true.to_numpy(dtype=int)
    n = len(y_values)
    no_model_scores = np.zeros(n)
    intervene_all_scores = np.ones(n)
    rng = np.random.default_rng(42)
    xgb_scores = scores_by_model.get("xgboost_tuned", {}).get("scores", np.zeros(n))
    intervention_rate = float((xgb_scores >= threshold).mean()) if n else 0.0
    random_scores = rng.random(n)
    random_threshold = 1.0 - intervention_rate
    baselines = [
        ("Sin modelo", "baseline_no_model", "operational_baseline", no_model_scores, 0.5),
        ("Intervenir a todos", "baseline_intervene_all", "operational_baseline", intervene_all_scores, 0.5),
        ("Aleatorio misma cobertura", "baseline_random", "operational_baseline", random_scores, random_threshold),
    ]
    rows = []
    for model, model_id, model_type, scores, baseline_threshold in baselines:
        economic = compute_economic_value(y_true, scores, baseline_threshold, assumptions)
        metrics = compute_metrics(y_true, scores, baseline_threshold)
        rows.append(
            {
                "model": model,
                "model_id": model_id,
                "type": model_type,
                "artifact_path": "",
                "recommended": False,
                "priority": 99,
                **metrics,
                **economic,
                **asdict(assumptions),
            }
        )
    return rows


def best_baseline_net_value(comparison: pd.DataFrame) -> float:
    baseline = comparison[comparison["type"].eq("baseline")]
    if baseline.empty:
        baseline = comparison[comparison["type"].eq("operational_baseline")]
    if baseline.empty:
        return 0.0
    return float(baseline["net_value_usd"].max())


def recommendation_text(row: pd.Series) -> str:
    if bool(row.get("recommended", False)):
        return "Modelo recomendado: combina desempeno tecnico, valor economico y facilidad de despliegue."
    if row.get("type") == "operational_baseline":
        return "Referencia operativa para comparar decisiones sin modelo."
    if row.get("net_value_usd", 0.0) > 0:
        return "Alternativa viable, pero debe compararse contra XGBoost y el costo de intervencion."
    return "No recomendado bajo los supuestos actuales por bajo valor neto o exceso de costo."


def compute_profit_curve_by_model(
    assumptions: EconomicAssumptions | None = None,
    thresholds: np.ndarray | None = None,
    model_ids: tuple[str, ...] | None = None,
) -> pd.DataFrame:
    assumptions = assumptions or EconomicAssumptions()
    thresholds = thresholds if thresholds is not None else np.round(np.arange(0.05, 0.96, 0.01), 2)
    model_ids = model_ids or MODEL_CURVE_IDS
    rows = []
    scores_by_model = load_available_model_scores()
    for model_id in model_ids:
        item = scores_by_model.get(model_id)
        if not item:
            continue
        y_true = item["y_true"]
        for threshold in thresholds:
            economic = compute_economic_value(y_true, item["scores"], float(threshold), assumptions)
            metrics = compute_metrics(y_true, item["scores"], float(threshold))
            rows.append(
                {
                    "model": item["model"],
                    "model_id": item["model_id"],
                    "type": item["type"],
                    "recommended": bool(item["recommended"]),
                    **metrics,
                    **economic,
                    **asdict(assumptions),
                }
            )
    if not rows:
        return pd.DataFrame()
    curve = pd.DataFrame(rows)
    curve["is_best_value_threshold"] = curve.groupby("model_id")["net_value_usd"].transform("max").eq(curve["net_value_usd"])
    curve["is_best_f1_threshold"] = curve.groupby("model_id")["f1"].transform("max").eq(curve["f1"])
    return curve


def compute_baseline_comparison_usd(assumptions: EconomicAssumptions | None = None, threshold: float = 0.5) -> pd.DataFrame:
    comparison = compute_model_economic_comparison(assumptions=assumptions, threshold=threshold)
    if comparison.empty or "xgboost_tuned" not in set(comparison["model_id"]):
        return pd.DataFrame()
    xgb = comparison[comparison["model_id"].eq("xgboost_tuned")].iloc[0]
    candidates = comparison[
        comparison["model_id"].isin(
            [
                "lightgbm_tuned",
                "random_forest_tuned",
                "random_forest_baseline",
                "baseline_no_model",
                "baseline_intervene_all",
                "baseline_random",
            ]
        )
    ].copy()
    candidates["xgboost_value_usd"] = float(xgb["net_value_usd"])
    candidates["xgboost_incremental_usd"] = float(xgb["net_value_usd"]) - candidates["net_value_usd"]
    candidates["xgboost_improvement_pct"] = np.where(
        candidates["net_value_usd"].abs() > 0,
        candidates["xgboost_incremental_usd"] / candidates["net_value_usd"].abs() * 100.0,
        0.0,
    )
    return candidates.sort_values("xgboost_incremental_usd", ascending=False)


def write_dashboard_economic_artifacts() -> dict[str, Path]:
    output_dir = ROOT / "models"
    output_dir.mkdir(exist_ok=True)
    assumptions = EconomicAssumptions()
    dashboard_threshold = 0.15
    comparison = compute_model_economic_comparison(assumptions=assumptions, threshold=dashboard_threshold)
    curve = compute_profit_curve_by_model(assumptions=assumptions)
    baseline = compute_baseline_comparison_usd(assumptions=assumptions, threshold=dashboard_threshold)
    outputs = {
        "comparison": output_dir / "c_model_economic_comparison.csv",
        "profit_curve": output_dir / "c_profit_curve_by_model.csv",
        "baseline": output_dir / "c_baseline_comparison_usd.csv",
    }
    comparison.to_csv(outputs["comparison"], index=False)
    curve.to_csv(outputs["profit_curve"], index=False)
    baseline.to_csv(outputs["baseline"], index=False)
    return outputs


def main() -> None:
    outputs = write_dashboard_economic_artifacts()
    for label, path in outputs.items():
        print(f"{label}: {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
