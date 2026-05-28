from __future__ import annotations

import os
from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "dashboard"))

from c_business_insights import business_recommendations, classify_intention, executive_summary, performance_status
from c_charts import (
    business_label,
    confusion_matrix_chart,
    confusion_value_chart,
    economic_value_bar,
    feature_importance_chart,
    feature_summary_chart,
    incremental_gain_chart,
    precision_recall_chart,
    profit_curve_chart,
    segment_conversion_chart,
    technical_vs_value_scatter,
    tuning_delta_bar,
    tuning_pair_bar,
    tuning_technical_delta_bar,
    tuned_model_waterfall,
)
from c_components import business_note, explain_metric, missing_warning, status_box
from c_dashboard_data import model_feature_importance
from c_data_loader import load_dashboard_bundle, load_dataset, load_model, score_dataset
from c_data_validation import read_uploaded_dataset, validate_dataset, validation_summary, write_uploaded_outputs
from c_input_schema import REQUIRED_INPUT_COLUMNS, schema_as_dataframe_rows
from c_model_economic_comparison import (
    EconomicAssumptions,
    compute_model_economic_comparison_for_dataset,
    compute_prediction_table,
    compute_potential_value_without_target,
    compute_baseline_comparison_usd,
    compute_model_economic_comparison,
    compute_profit_curve_for_dataset,
    compute_profit_curve_by_model,
)


st.set_page_config(page_title="Dashboard Ejecutivo - Conversion Online", layout="wide")


DEFAULT_API_URL = "http://localhost:8000"
API_TIMEOUT_SECONDS = 10
PRIMARY_MODEL = "XGBoost"
ECONOMIC_CACHE_VERSION = 2


def fmt_usd(value: float) -> str:
    prefix = "-" if value < 0 else ""
    return f"{prefix}USD {abs(value):,.0f}"


def fmt_pct(value: float) -> str:
    return f"{value:.1f}%"


def get_api_url() -> str:
    return os.getenv("API_URL", DEFAULT_API_URL).rstrip("/")


def get_api_headers() -> dict:
    headers = {"Content-Type": "application/json"}
    api_key = os.getenv("API_KEY")
    if api_key:
        headers["x-api-key"] = api_key
    return headers


def predict_with_api(payload: dict) -> dict:
    response = requests.post(f"{get_api_url()}/predict", json=payload, headers=get_api_headers(), timeout=API_TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json()


def predict_batch_with_api(records: list[dict]) -> dict:
    response = requests.post(
        f"{get_api_url()}/predict_batch",
        json={"records": records},
        headers=get_api_headers(),
        timeout=API_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def render_api_status() -> bool:
    api_url = get_api_url()
    st.caption(f"API configurada: `{api_url}`")
    try:
        response = requests.get(f"{api_url}/health", timeout=3)
        response.raise_for_status()
    except requests.RequestException as exc:
        st.info(f"API no disponible. El simulador usara el modelo local como respaldo. Detalle: {exc}")
        return False
    st.success("API disponible: el simulador enviara predicciones por REST.")
    return True


def get_default_economic_threshold(bundle: dict) -> float:
    curve = bundle.get("profit_curve", pd.DataFrame())
    if not curve.empty and {"model", "is_best_value_threshold", "threshold"}.issubset(curve.columns):
        is_best = curve["is_best_value_threshold"].astype(str).str.lower().eq("true")
        xgb_best = curve[(curve["model"].eq(PRIMARY_MODEL)) & is_best]
        if not xgb_best.empty:
            return float(xgb_best.iloc[0]["threshold"])
    return 0.15


def render_sidebar(default_threshold: float):
    st.sidebar.title("Panel ejecutivo")
    view = st.sidebar.selectbox(
        "Selector de vista",
        [
            "Acerca del proyecto",
            "Resumen ejecutivo",
            "Cargar nuevo dataset",
            "Ranking economico",
            "Impacto economico del tuning",
            "Desempeno tecnico vs valor economico",
            "Profit curve",
            "Simulador economico",
            "Segmentos",
            "Recomendaciones",
        ],
    )
    dataset_mode = st.sidebar.radio("Dataset de trabajo", ["Dataset original", "Dataset cargado por usuario"], index=0)
    uploaded_file = None
    if dataset_mode == "Dataset cargado por usuario":
        uploaded_file = st.sidebar.file_uploader("Subir CSV o XLSX", type=["csv", "xlsx", "xls"])
    threshold = float(
        st.sidebar.slider(
            "Threshold de decision",
            min_value=0.05,
            max_value=0.95,
            value=min(max(float(default_threshold), 0.05), 0.95),
            step=0.01,
            format="%.2f",
        )
    )
    st.sidebar.markdown("**Supuestos economicos**")
    average_purchase = float(st.sidebar.number_input("Ingreso promedio por compra (USD)", 10.0, 1000.0, 180.0, 10.0))
    margin = float(st.sidebar.slider("Margen bruto", 0.05, 0.95, 0.45, 0.01))
    incentive = float(st.sidebar.number_input("Costo incentivo/descuento (USD)", 0.0, 200.0, 8.0, 1.0))
    contact = float(st.sidebar.number_input("Costo contacto/chat (USD)", 0.0, 100.0, 2.0, 1.0))
    uplift = float(st.sidebar.slider("Uplift esperado por intervencion", 0.01, 1.00, 0.40, 0.01))
    false_negative = float(st.sidebar.number_input("Costo oportunidad falso negativo (USD)", 0.0, 500.0, 60.0, 5.0))
    true_negative = float(st.sidebar.number_input("Valor/costo true negative (USD)", -100.0, 100.0, 0.0, 1.0))
    with st.sidebar.expander("Como se calcula el valor economico"):
        st.markdown(
            """
            **Formula general**

            `Valor = TP * beneficio_TP + FP * costo_FP + FN * costo_FN + TN * valor_TN`

            **Variables**

            - `TP`: comprador detectado correctamente.
            - `FP`: visitante intervenido que no compra.
            - `FN`: comprador no detectado, oportunidad perdida.
            - `TN`: no comprador correctamente no intervenido.

            **Beneficio por TP**

            `ingreso promedio * margen bruto * uplift - costo incentivo - costo contacto`

            El `uplift` representa el efecto adicional esperado por aplicar la accion comercial.
            Los valores en USD son estimaciones bajo estos supuestos, no ingresos reales observados.
            """
        )
    show_technical = st.sidebar.checkbox("Mostrar detalles tecnicos", value=False)
    assumptions = EconomicAssumptions(
        average_purchase_usd=average_purchase,
        gross_margin_pct=margin,
        incentive_cost_usd=incentive,
        contact_cost_usd=contact,
        uplift_pct=uplift,
        false_negative_cost_usd=false_negative,
        true_negative_value_usd=true_negative,
    )
    return view, threshold, assumptions, show_technical, dataset_mode, uploaded_file


@st.cache_data(show_spinner=False)
def build_economic_views(
    threshold: float,
    average_purchase_usd: float,
    gross_margin_pct: float,
    incentive_cost_usd: float,
    contact_cost_usd: float,
    uplift_pct: float,
    false_negative_cost_usd: float,
    true_negative_value_usd: float,
    cache_version: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    assumptions = EconomicAssumptions(
        average_purchase_usd=average_purchase_usd,
        gross_margin_pct=gross_margin_pct,
        incentive_cost_usd=incentive_cost_usd,
        contact_cost_usd=contact_cost_usd,
        uplift_pct=uplift_pct,
        false_negative_cost_usd=false_negative_cost_usd,
        true_negative_value_usd=true_negative_value_usd,
    )
    comparison = compute_model_economic_comparison(assumptions=assumptions, threshold=threshold)
    curve = compute_profit_curve_by_model(assumptions=assumptions)
    baseline = compute_baseline_comparison_usd(assumptions=assumptions, threshold=threshold)
    return comparison, curve, baseline


@st.cache_data(show_spinner=False)
def parse_uploaded_file(file_name: str, file_bytes: bytes) -> pd.DataFrame:
    return read_uploaded_dataset(file_name, file_bytes)


def baseline_from_comparison(comparison: pd.DataFrame) -> pd.DataFrame:
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
    candidates["xgboost_improvement_pct"] = candidates["xgboost_incremental_usd"] / candidates["net_value_usd"].abs().replace(0, pd.NA) * 100.0
    return candidates.sort_values("xgboost_incremental_usd", ascending=False)


def build_prediction_context(
    dataset_mode: str,
    uploaded_file,
    original_df: pd.DataFrame,
    original_X: pd.DataFrame,
    original_y: pd.Series,
    assumptions: EconomicAssumptions,
    threshold: float,
) -> dict:
    context = {
        "source": "Dataset original",
        "df": original_df,
        "X": original_X,
        "y": original_y,
        "has_target": True,
        "validation": None,
        "predictions": pd.DataFrame(),
        "is_uploaded": False,
        "is_valid": True,
    }
    if dataset_mode != "Dataset cargado por usuario":
        return context
    if uploaded_file is None:
        context["source"] = "Dataset original (fallback: no se cargo archivo)"
        return context
    try:
        raw_df = parse_uploaded_file(uploaded_file.name, uploaded_file.getvalue())
        validation = validate_dataset(raw_df)
    except Exception as exc:  # noqa: BLE001 - Streamlit debe mostrar error amigable.
        st.error(f"No se pudo leer el archivo cargado: {exc}")
        context["source"] = "Dataset original (fallback por error de lectura)"
        return context
    if not validation.is_valid:
        context.update(
            {
                "source": "Dataset cargado invalido",
                "validation": validation,
                "is_uploaded": True,
                "is_valid": False,
            }
        )
        return context
    predictions = compute_prediction_table(validation.model_input, assumptions=assumptions, threshold=threshold)
    validated_with_predictions = validation.validated_df.copy()
    if not predictions.empty:
        validated_with_predictions = pd.concat([validated_with_predictions.reset_index(drop=True), predictions.drop(columns=["row_id"]).reset_index(drop=True)], axis=1)
    write_uploaded_outputs(validation.validated_df, validated_with_predictions)
    context.update(
        {
            "source": f"Dataset cargado: {uploaded_file.name}",
            "df": validation.validated_df,
            "X": validation.model_input,
            "y": validation.target if validation.has_target and validation.target is not None and len(validation.target) == len(validation.validated_df) else None,
            "has_target": validation.has_target and validation.target is not None and len(validation.target) == len(validation.validated_df),
            "validation": validation,
            "predictions": validated_with_predictions,
            "is_uploaded": True,
            "is_valid": True,
        }
    )
    return context


def build_dynamic_economic_views(context: dict, assumptions: EconomicAssumptions, threshold: float):
    if context["is_uploaded"] and context["is_valid"] and context["has_target"]:
        comparison = compute_model_economic_comparison_for_dataset(context["X"], context["y"], assumptions=assumptions, threshold=threshold)
        curve = compute_profit_curve_for_dataset(context["X"], context["y"], assumptions=assumptions)
        baseline = baseline_from_comparison(comparison)
        Path("models").mkdir(exist_ok=True)
        comparison.to_csv("models/c_uploaded_dataset_economic_comparison.csv", index=False)
        curve.to_csv("models/c_uploaded_dataset_business_value.csv", index=False)
        return comparison, curve, baseline
    comparison, curve, baseline = build_economic_views(
        threshold,
        assumptions.average_purchase_usd,
        assumptions.gross_margin_pct,
        assumptions.incentive_cost_usd,
        assumptions.contact_cost_usd,
        assumptions.uplift_pct,
        assumptions.false_negative_cost_usd,
        assumptions.true_negative_value_usd,
        ECONOMIC_CACHE_VERSION,
    )
    return comparison, curve, baseline


def build_dynamic_segments(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()
    segments = []
    if "Revenue" in df.columns:
        target = pd.to_numeric(df["Revenue"], errors="coerce")
        for dimension in ["VisitorType", "Month", "Weekend"]:
            if dimension in df.columns:
                grouped = df.assign(Revenue=target).groupby(dimension, dropna=False)["Revenue"].agg(["count", "mean"]).reset_index()
                grouped.columns = ["segment", "sessions", "conversion_rate"]
                grouped["dimension"] = dimension
                segments.append(grouped)
    else:
        for dimension in ["VisitorType", "Month", "Weekend"]:
            if dimension in df.columns and "purchase_probability" in df.columns:
                grouped = df.groupby(dimension, dropna=False)["purchase_probability"].agg(["count", "mean"]).reset_index()
                grouped.columns = ["segment", "sessions", "conversion_rate"]
                grouped["dimension"] = dimension
                segments.append(grouped)
    feature_rows = []
    value_column = "Revenue" if "Revenue" in df.columns else "prediction" if "prediction" in df.columns else None
    for feature in ["PageValues", "ProductRelated_Duration", "BounceRates", "ExitRates"]:
        if feature in df.columns and value_column in df.columns:
            grouped = df.groupby(value_column, dropna=False)[feature].mean().reset_index()
            grouped.columns = ["revenue", "average_value"]
            grouped["feature"] = feature
            feature_rows.append(grouped)
    return (
        pd.concat(segments, ignore_index=True) if segments else pd.DataFrame(),
        pd.concat(feature_rows, ignore_index=True) if feature_rows else pd.DataFrame(),
    )


def get_row(comparison: pd.DataFrame, model_name: str = PRIMARY_MODEL) -> pd.Series:
    if comparison.empty:
        return pd.Series(dtype=object)
    match = comparison[comparison["model"].eq(model_name)]
    if match.empty:
        return pd.Series(dtype=object)
    return match.iloc[0]


def get_recommended_model_row(comparison: pd.DataFrame) -> pd.Series:
    if comparison.empty or "net_value_usd" not in comparison.columns:
        return pd.Series(dtype=object)
    candidates = comparison[~comparison["type"].eq("operational_baseline")].copy()
    if candidates.empty:
        candidates = comparison.copy()
    return candidates.sort_values(["net_value_usd", "f1", "recall"], ascending=False).iloc[0]


def get_best_baseline_row(comparison: pd.DataFrame) -> pd.Series:
    if comparison.empty:
        return pd.Series(dtype=object)
    baseline = comparison[comparison["type"].eq("baseline")]
    if baseline.empty:
        return pd.Series(dtype=object)
    return baseline.sort_values("net_value_usd", ascending=False).iloc[0]


def model_delta(comparison: pd.DataFrame, selected: pd.Series, comparator: str) -> float:
    if comparison.empty or selected.empty:
        return 0.0
    row = comparison[comparison["model"].eq(comparator)]
    if row.empty:
        return 0.0
    return float(selected.get("net_value_usd", 0.0)) - float(row.iloc[0].get("net_value_usd", 0.0))


def get_incremental(baseline: pd.DataFrame, comparator: str) -> float:
    if baseline.empty:
        return 0.0
    row = baseline[baseline["model"].eq(comparator)]
    if row.empty:
        return 0.0
    return float(row.iloc[0].get("xgboost_incremental_usd", 0.0))


def build_tuning_impact_table(comparison: pd.DataFrame) -> pd.DataFrame:
    pairs = [
        ("XGBoost", "XGBoost inicial", "XGBoost"),
        ("LightGBM", "LightGBM inicial", "LightGBM"),
        ("Random Forest", "Random Forest baseline", "Random Forest"),
    ]
    rows = []
    for family, base_name, tuned_name in pairs:
        base = get_row(comparison, base_name)
        tuned = get_row(comparison, tuned_name)
        if base.empty or tuned.empty:
            continue
        base_value = float(base.get("net_value_usd", 0.0))
        tuned_value = float(tuned.get("net_value_usd", 0.0))
        delta_value = tuned_value - base_value
        rows.append(
            {
                "family": family,
                "base_model": base_name,
                "tuned_model": tuned_name,
                "base_value_usd": base_value,
                "tuned_value_usd": tuned_value,
                "delta_value_usd": delta_value,
                "delta_value_pct": (delta_value / abs(base_value) * 100.0) if base_value else 0.0,
                "base_f1": float(base.get("f1", 0.0)),
                "tuned_f1": float(tuned.get("f1", 0.0)),
                "delta_f1": float(tuned.get("f1", 0.0)) - float(base.get("f1", 0.0)),
                "delta_precision": float(tuned.get("precision", 0.0)) - float(base.get("precision", 0.0)),
                "delta_recall": float(tuned.get("recall", 0.0)) - float(base.get("recall", 0.0)),
                "conclusion": "El tuning agrego valor economico." if delta_value > 0 else "El tuning redujo valor economico bajo estos supuestos.",
            }
        )
    return pd.DataFrame(rows)


def render_header() -> None:
    st.title("Dashboard Ejecutivo - Conversion de Visitantes Online")
    st.subheader("Modelo predictivo para priorizar visitantes con mayor probabilidad de compra")
    st.info(
        "Los valores en dolares son estimaciones basadas en supuestos configurables. "
        "Sirven para comparar escenarios y modelos bajo una misma matriz costo-beneficio, "
        "no para afirmar ingresos reales observados."
    )


def render_economic_kpis(comparison: pd.DataFrame, baseline: pd.DataFrame, curve: pd.DataFrame, threshold: float) -> None:
    recommended = get_recommended_model_row(comparison)
    if recommended.empty:
        missing_warning("models/c_final_model.pkl")
        return
    if not curve.empty and "is_best_value_threshold" in curve.columns:
        is_best = curve["is_best_value_threshold"].astype(str).str.lower().eq("true")
        best_curve = curve[(curve["model"].eq(recommended["model"])) & is_best]
    else:
        best_curve = pd.DataFrame()
    economic_threshold = float(best_curve.iloc[0]["threshold"]) if not best_curve.empty else threshold
    best_baseline = get_best_baseline_row(comparison)
    incremental_baseline = (
        float(recommended["net_value_usd"]) - float(best_baseline["net_value_usd"])
        if not best_baseline.empty
        else 0.0
    )
    best_alternative = comparison[
        (~comparison["type"].eq("operational_baseline")) & (~comparison["model"].eq(recommended["model"]))
    ].sort_values("net_value_usd", ascending=False)
    alternative_delta = (
        float(recommended["net_value_usd"]) - float(best_alternative.iloc[0]["net_value_usd"])
        if not best_alternative.empty
        else 0.0
    )
    alternative_label = f"Incremental vs {best_alternative.iloc[0]['model']}" if not best_alternative.empty else "Incremental vs alternativa"
    cols = st.columns(5)
    cols[0].metric("Modelo recomendado", str(recommended["model"]))
    cols[1].metric("Valor modelo", fmt_usd(float(recommended["net_value_usd"])))
    cols[2].metric("ROI estimado", fmt_pct(float(recommended["roi_pct"])))
    cols[3].metric("Threshold economico", f"{economic_threshold:.2f}")
    cols[4].metric("Visitantes impactados", f"{int(recommended['visitors_impacted']):,}")
    cols = st.columns(5)
    cols[0].metric("Incremental vs baseline", fmt_usd(incremental_baseline))
    cols[1].metric(alternative_label, fmt_usd(alternative_delta))
    cols[2].metric("Incremental vs XGBoost", fmt_usd(model_delta(comparison, recommended, PRIMARY_MODEL)))
    cols[3].metric("Costo falsos positivos", fmt_usd(float(recommended["cost_fp_usd"])))
    cols[4].metric("Costo falsos negativos", fmt_usd(float(recommended["cost_fn_usd"])))


def render_executive_summary(comparison: pd.DataFrame, baseline: pd.DataFrame, curve: pd.DataFrame, bundle: dict, threshold: float) -> None:
    render_header()
    render_economic_kpis(comparison, baseline, curve, threshold)
    recommended = get_recommended_model_row(comparison)
    status, message = performance_status(bundle.get("validation", pd.DataFrame()))
    status_box(status, message)
    st.success(
        f"Recomendacion ejecutiva: usar {recommended.get('model', 'el modelo con mayor valor')} como modelo recomendado bajo los supuestos actuales y activar acciones comerciales "
        "solo sobre visitantes cuya probabilidad supere el threshold economico."
    )
    if not recommended.empty:
        st.markdown(
            f"**Lectura de negocio:** bajo los supuestos actuales, {recommended['model']} genera {fmt_usd(float(recommended['net_value_usd']))} "
            f"en valor neto estimado, impactando {int(recommended['visitors_impacted']):,} visitantes. "
            "El recomendado puede variar cuando cambian threshold, costos, margen, uplift o dataset activo."
        )
    summary = executive_summary(
        {
            "f1": float(recommended.get("f1", 0.0)) if not recommended.empty else 0.0,
            "recall": float(recommended.get("recall", 0.0)) if not recommended.empty else 0.0,
            "precision": float(recommended.get("precision", 0.0)) if not recommended.empty else 0.0,
            "roc_auc": float(recommended.get("roc_auc", 0.0)) if not recommended.empty else 0.0,
            "real_conversion_rate": 0.0,
            "expected_value": float(recommended.get("net_value_usd", 0.0)) if not recommended.empty else 0.0,
            "recommended_threshold": threshold,
        }
    )
    tabs = st.tabs(["Que significa", "Accion sugerida", "Riesgo", "Confiabilidad"])
    tabs[0].markdown(summary["meaning"])
    tabs[1].markdown("Priorizar cupon, chat o recomendacion personalizada en visitantes de alta probabilidad.")
    tabs[2].markdown("Monitorear falsos positivos porque representan gasto comercial; monitorear falsos negativos porque son ventas perdidas.")
    tabs[3].markdown(summary["confidence"])


def render_economic_ranking(comparison: pd.DataFrame, baseline: pd.DataFrame, show_technical: bool) -> None:
    st.header("Ranking economico de modelos")
    fig = economic_value_bar(comparison)
    if fig:
        st.plotly_chart(fig, width="stretch")
    st.caption("Lectura ejecutiva: el ranking traduce TP, FP, FN y TN a valor neto estimado en USD.")
    columns = [
        "model",
        "type",
        "f1",
        "precision",
        "recall",
        "roc_auc",
        "threshold",
        "tp",
        "fp",
        "fn",
        "tn",
        "net_value_usd",
        "incremental_vs_best_baseline_usd",
        "incremental_vs_no_model_usd",
        "roi_pct",
        "recommendation",
    ]
    available_columns = [col for col in columns if col in comparison.columns]
    st.dataframe(
        comparison[available_columns],
        width="stretch",
        hide_index=True,
        column_config={
            "net_value_usd": st.column_config.NumberColumn("Valor esperado USD", format="USD %.0f"),
            "incremental_vs_best_baseline_usd": st.column_config.NumberColumn("Incremental vs baseline USD", format="USD %.0f"),
            "incremental_vs_no_model_usd": st.column_config.NumberColumn("Incremental vs sin modelo USD", format="USD %.0f"),
            "roi_pct": st.column_config.NumberColumn("ROI %", format="%.1f%%"),
        },
    )
    fig_incremental = incremental_gain_chart(baseline)
    if fig_incremental:
        st.plotly_chart(fig_incremental, width="stretch")
    if show_technical:
        with st.expander("Detalle tecnico completo"):
            st.dataframe(comparison, width="stretch", hide_index=True)


def render_uploaded_dataset_view(context: dict, assumptions: EconomicAssumptions, threshold: float) -> None:
    st.header("Cargar nuevo dataset")
    st.markdown(
        "Sube un archivo CSV o XLSX con las variables de navegacion del dataset Online Shoppers. "
        "Si incluye `Revenue`, el dashboard calcula metricas reales y valor economico observado; "
        "si no lo incluye, genera predicciones y valor potencial estimado."
    )
    with st.expander("Columnas requeridas", expanded=False):
        st.dataframe(pd.DataFrame(schema_as_dataframe_rows()), width="stretch", hide_index=True)
    validation = context.get("validation")
    if not context.get("is_uploaded"):
        st.info("No hay dataset cargado. El dashboard esta usando el dataset original como demo reproducible.")
        return
    if validation is None:
        st.warning("No se pudo construir el resultado de validacion del archivo.")
        return
    summary = validation_summary(validation)
    cols = st.columns(4)
    cols[0].metric("Filas", f"{summary['rows']:,}")
    cols[1].metric("Columnas", f"{summary['columns']:,}")
    cols[2].metric("Contiene Revenue", "Si" if summary["has_target"] else "No")
    cols[3].metric("Nulos totales", f"{summary['total_nulls']:,}")
    if not validation.is_valid:
        st.error("El dataset cargado no tiene la estructura minima requerida.")
        st.markdown("**Columnas faltantes:**")
        st.write(validation.missing_columns)
        if validation.extra_columns:
            st.info(f"Columnas extra detectadas: {validation.extra_columns}")
        return
    st.success("Dataset validado correctamente. Se genero una copia local validada en `data/processed/c_uploaded_dataset_validated.csv`.")
    if validation.extra_columns:
        st.info(f"Columnas extra detectadas y conservadas solo como referencia: {validation.extra_columns}")
    for warning in validation.warnings:
        st.warning(warning)
    predictions = context.get("predictions", pd.DataFrame())
    if predictions.empty:
        st.warning("No se pudieron generar predicciones con el modelo final.")
        return
    st.subheader("Predicciones generadas")
    top_columns = [
        "purchase_probability",
        "prediction",
        "intention_level",
        "recommended_action",
        "estimated_impact_usd",
    ]
    available = [col for col in top_columns if col in predictions.columns]
    st.dataframe(
        predictions.reset_index(names="row_id")[["row_id"] + available].head(50),
        width="stretch",
        hide_index=True,
        column_config={
            "purchase_probability": st.column_config.NumberColumn("Probabilidad compra", format="%.2f"),
            "estimated_impact_usd": st.column_config.NumberColumn("Impacto estimado USD", format="USD %.2f"),
        },
    )
    st.download_button(
        "Descargar predicciones",
        data=predictions.to_csv(index=False).encode("utf-8"),
        file_name="c_uploaded_predictions.csv",
        mime="text/csv",
    )
    with st.expander("Validacion Sprint 6: probar dataset contra API REST", expanded=False):
        st.caption(
            "Esta prueba envia una muestra del dataset cargado a `POST {API_URL}/predict_batch`. "
            "Si la API desplegada requiere llave, define `API_KEY` como variable de entorno."
        )
        api_sample_size = st.slider("Filas a enviar a la API", 1, min(100, len(validation.model_input)), min(10, len(validation.model_input)))
        if st.button("Probar muestra contra API"):
            records = validation.model_input.head(api_sample_size).to_dict(orient="records")
            try:
                result = predict_batch_with_api(records)
                api_predictions = pd.DataFrame(result.get("records", []))
                st.success(f"API respondio correctamente para {result.get('count', len(api_predictions))} registros.")
                st.dataframe(api_predictions.head(20), width="stretch", hide_index=True)
                st.download_button(
                    "Descargar respuesta API",
                    data=api_predictions.to_csv(index=False).encode("utf-8"),
                    file_name="c_api_batch_predictions_sample.csv",
                    mime="text/csv",
                )
            except requests.HTTPError as exc:
                detail = exc.response.text if exc.response is not None else str(exc)
                st.error(f"La API rechazo la muestra: {detail}")
            except requests.RequestException as exc:
                st.warning(f"No se pudo conectar con la API configurada en `{get_api_url()}`. Detalle: {exc}")
    left, right = st.columns(2)
    left.plotly_chart(
        px.histogram(
            predictions,
            x="purchase_probability",
            nbins=25,
            title="Distribucion de probabilidades de compra",
            labels={"purchase_probability": "Probabilidad de compra"},
        ),
        width="stretch",
    )
    right.plotly_chart(
        px.bar(
            predictions["intention_level"].value_counts().rename_axis("Nivel").reset_index(name="Visitantes"),
            x="Nivel",
            y="Visitantes",
            color="Nivel",
            title="Visitantes por nivel de intencion",
            color_discrete_map={"Alta": "#22c55e", "Media": "#f59e0b", "Baja": "#94a3b8"},
        ),
        width="stretch",
    )
    if context["has_target"]:
        st.success("El dataset incluye `Revenue`: se pueden calcular metricas reales, matriz de confusion y valor economico.")
    else:
        potential = compute_potential_value_without_target(predictions, assumptions)
        st.warning(
            "El dataset cargado no contiene Revenue, por lo que no es posible calcular metricas reales ni matriz de confusion. "
            "Se muestran predicciones y valor economico potencial bajo supuestos."
        )
        cols = st.columns(4)
        cols[0].metric("Visitantes cargados", f"{potential['visitors']:,}")
        cols[1].metric("Alta intencion", f"{potential['high_intention']:,}")
        cols[2].metric("Intervenciones sugeridas", f"{potential['recommended_interventions']:,}")
        cols[3].metric("Valor potencial", fmt_usd(potential["estimated_potential_value_usd"]))
        st.caption(f"Costo estimado de intervencion: {fmt_usd(potential['estimated_intervention_cost_usd'])} con threshold {threshold:.2f}.")


def render_tuning_impact(comparison: pd.DataFrame, show_technical: bool) -> None:
    st.header("Impacto economico del tuning")
    tuning = build_tuning_impact_table(comparison)
    if tuning.empty:
        st.warning("No hay suficientes pares base/tuneado para comparar el impacto del tuning.")
        return
    best_delta = tuning.sort_values("delta_value_usd", ascending=False).iloc[0]
    worst_delta = tuning.sort_values("delta_value_usd", ascending=True).iloc[0]
    improved_count = int((tuning["delta_value_usd"] > 0).sum())
    best_tuned = comparison[comparison["model"].isin(tuning["tuned_model"])].sort_values("net_value_usd", ascending=False).iloc[0]
    cols = st.columns(4)
    cols[0].metric("Mayor mejora por tuning", str(best_delta["family"]), fmt_usd(float(best_delta["delta_value_usd"])))
    cols[1].metric("Mayor perdida por tuning", str(worst_delta["family"]), fmt_usd(float(worst_delta["delta_value_usd"])))
    cols[2].metric("Tuneados que mejoraron", f"{improved_count}/{len(tuning)}")
    cols[3].metric("Tuneado con mayor valor", str(best_tuned["model"]), fmt_usd(float(best_tuned["net_value_usd"])))
    left, right = st.columns(2)
    fig_pair = tuning_pair_bar(tuning)
    fig_delta = tuning_delta_bar(tuning)
    if fig_pair:
        left.plotly_chart(fig_pair, width="stretch")
    if fig_delta:
        right.plotly_chart(fig_delta, width="stretch")
    fig_technical = tuning_technical_delta_bar(tuning)
    if fig_technical:
        st.plotly_chart(fig_technical, width="stretch")
    st.dataframe(
        tuning[
            [
                "family",
                "base_model",
                "base_value_usd",
                "tuned_model",
                "tuned_value_usd",
                "delta_value_usd",
                "delta_value_pct",
                "base_f1",
                "tuned_f1",
                "delta_f1",
                "conclusion",
            ]
        ],
        width="stretch",
        hide_index=True,
        column_config={
            "base_value_usd": st.column_config.NumberColumn("Valor base USD", format="USD %.0f"),
            "tuned_value_usd": st.column_config.NumberColumn("Valor tuneado USD", format="USD %.0f"),
            "delta_value_usd": st.column_config.NumberColumn("Diferencia USD", format="USD %.0f"),
            "delta_value_pct": st.column_config.NumberColumn("Cambio %", format="%.1f%%"),
        },
    )
    st.info(
        "Lectura ejecutiva: el tuning no siempre aumenta valor economico. "
        "Puede mejorar una metrica tecnica y aun asi reducir utilidad si cambia el balance entre TP, FP y FN."
    )
    if show_technical:
        with st.expander("Detalle completo de modelos usados en la comparacion"):
            st.dataframe(comparison, width="stretch", hide_index=True)


def render_technical_vs_economic(comparison: pd.DataFrame) -> None:
    st.header("Desempeno tecnico vs valor economico")
    recommended = get_recommended_model_row(comparison)
    highlight = str(recommended.get("model", PRIMARY_MODEL)) if not recommended.empty else PRIMARY_MODEL
    best_value = fmt_usd(float(recommended.get("net_value_usd", 0.0))) if not recommended.empty else "USD 0"
    st.markdown(
        "Estos graficos comparan metricas tecnicas contra valor economico estimado. "
        "Sirven para detectar si el modelo con mejor metrica tecnica tambien es el que genera mas valor de negocio."
    )
    st.info(
        f"Lectura rapida: el punto destacado corresponde al modelo recomendado economicamente ({highlight}, {best_value}). "
        "Los puntos por encima de USD 0 generan valor neto positivo bajo los supuestos actuales; los puntos por debajo implican perdida estimada."
    )
    metric_options = [
        ("accuracy", "Accuracy"),
        ("precision", "Precision"),
        ("recall", "Recall"),
        ("f1", "F1-score"),
        ("roc_auc", "ROC-AUC"),
    ]
    tabs = st.tabs([label for _, label in metric_options])
    for tab, (metric, label) in zip(tabs, metric_options):
        fig = technical_vs_value_scatter(comparison, metric, highlight_model=highlight)
        if fig:
            tab.plotly_chart(fig, width="stretch")
            tab.caption(
                f"Lectura ejecutiva: eje X = {label}; eje Y = valor neto estimado USD. "
                f"El punto destacado es el recomendado economico actual: {highlight}."
            )
        else:
            tab.warning(f"No hay datos suficientes para graficar {label}.")


def render_profit_curve(comparison: pd.DataFrame, curve: pd.DataFrame) -> None:
    st.header("Profit curve y threshold economico")
    if curve.empty or "model" not in curve.columns:
        st.warning("No hay datos suficientes para mostrar la profit curve.")
        return

    available_models = set(curve["model"].dropna().unique().tolist())
    if not comparison.empty and "model" in comparison.columns:
        model_options = [model for model in comparison["model"].dropna().tolist() if model in available_models]
        model_options += sorted(available_models.difference(model_options))
    else:
        model_options = sorted(available_models)

    st.markdown("**Modelos a mostrar en la curva**")
    if "profit_curve_show_all_previous" not in st.session_state:
        st.session_state["profit_curve_show_all_previous"] = True
    show_all = st.checkbox("Todos", value=True, help="Marca o desmarca todos los modelos disponibles.")
    if st.session_state["profit_curve_show_all_previous"] and not show_all:
        for model_name in model_options:
            st.session_state[f"profit_curve_model_{model_name}"] = False
    st.session_state["profit_curve_show_all_previous"] = show_all
    selected_curve_models = []
    checkbox_columns = st.columns(3)
    for index, model_name in enumerate(model_options):
        checkbox_key = f"profit_curve_model_{model_name}"
        if show_all:
            st.session_state[checkbox_key] = True
        with checkbox_columns[index % 3]:
            if st.checkbox(model_name, value=False, disabled=show_all, key=checkbox_key):
                selected_curve_models.append(model_name)

    if show_all:
        selected_curve_models = model_options
    if not selected_curve_models:
        st.warning("Selecciona al menos un modelo para mostrar la profit curve.")
        return

    curve_view = curve[curve["model"].isin(selected_curve_models)].copy()
    detail_default = PRIMARY_MODEL if PRIMARY_MODEL in model_options else selected_curve_models[0]
    if detail_default not in selected_curve_models:
        detail_default = selected_curve_models[0]
    detail_candidates = selected_curve_models
    selected_model = st.selectbox(
        "Ver detalle",
        detail_candidates,
        index=detail_candidates.index(detail_default),
        help="Este selector controla el resumen inferior y la matriz en USD. Las curvas visibles se controlan con los checkboxes.",
    )

    fig = profit_curve_chart(curve_view)
    if fig:
        st.plotly_chart(fig, width="stretch")
    selected_curve = curve[curve["model"].eq(selected_model)] if not curve.empty else pd.DataFrame()
    if not selected_curve.empty:
        best_value = selected_curve.sort_values("net_value_usd", ascending=False).iloc[0]
        best_f1 = selected_curve.sort_values("f1", ascending=False).iloc[0]
        cols = st.columns(3)
        cols[0].metric("Modelo", selected_model)
        cols[1].metric("Threshold economico", f"{float(best_value['threshold']):.2f}", fmt_usd(float(best_value["net_value_usd"])))
        cols[2].metric("Threshold max F1", f"{float(best_f1['threshold']):.2f}", f"F1 {float(best_f1['f1']):.3f}")
        st.info(
            "El threshold economico puede diferir de 0.5 y del threshold que maximiza F1 porque el negocio no valora igual "
            "un comprador detectado, una falsa intervencion y una oportunidad perdida."
        )
    selected = get_row(comparison, selected_model)
    fig_conf = confusion_value_chart(selected)
    if fig_conf:
        st.plotly_chart(fig_conf, width="stretch")
    st.caption("Lectura ejecutiva: TP crea valor, FP consume presupuesto, FN representa oportunidad perdida y TN normalmente no requiere accion.")


def predict_with_local_model(model, payload: dict) -> float:
    if model is None:
        raise ValueError("No se encontro modelo local cargado.")
    validation = validate_dataset(pd.DataFrame([payload]))
    if not validation.is_valid:
        raise ValueError(f"Input invalido para prediccion local. Faltan columnas: {validation.missing_columns}")
    return float(score_dataset(model, validation.model_input).iloc[0])


def render_economic_simulator(comparison: pd.DataFrame, df: pd.DataFrame, threshold: float, assumptions: EconomicAssumptions, model=None) -> None:
    st.header("Simulador economico de visitante")
    st.markdown("Simula una sesion individual y estima si conviene activar una accion comercial.")
    api_available = render_api_status()
    numeric_cols = [
        "Administrative",
        "Administrative_Duration",
        "Informational",
        "Informational_Duration",
        "ProductRelated",
        "ProductRelated_Duration",
        "BounceRates",
        "ExitRates",
        "PageValues",
        "SpecialDay",
    ]
    categorical_cols = ["Month", "OperatingSystems", "Browser", "Region", "TrafficType", "VisitorType"]
    available_numeric_cols = [col for col in numeric_cols if col in df.columns]
    available_categorical_cols = [col for col in categorical_cols if col in df.columns]
    defaults = df[available_numeric_cols].apply(pd.to_numeric, errors="coerce").median().to_dict()
    payload = {}
    with st.expander("Caracteristicas de la sesion", expanded=True):
        cols = st.columns(3)
        for idx, col_name in enumerate(available_numeric_cols):
            values = pd.to_numeric(df[col_name], errors="coerce").dropna()
            min_value = float(values.min()) if not values.empty else 0.0
            max_value = float(values.quantile(0.99)) if not values.empty else 1.0
            if min_value == max_value:
                max_value = min_value + 1.0
            default = min(max(float(defaults.get(col_name, min_value)), min_value), max_value)
            payload[col_name] = cols[idx % 3].slider(
                business_label(col_name),
                min_value=min_value,
                max_value=max_value,
                value=default,
                key=f"sim_{col_name}",
            )
        for col_name in available_categorical_cols:
            options = sorted(df[col_name].dropna().astype(str).unique().tolist()) or [""]
            payload[col_name] = st.selectbox(business_label(col_name), options, key=f"sim_{col_name}")
        payload["Weekend"] = st.checkbox(business_label("Weekend"), key="sim_Weekend")
    if st.button("Calcular probabilidad e impacto"):
        source = "modelo local"
        proba = None
        try:
            if api_available:
                result = predict_with_api(payload)
                proba = float(result["purchase_probability"])
                source = f"API REST (`{result.get('model_path', 'no informado')}`)"
            else:
                proba = predict_with_local_model(model, payload)
        except requests.HTTPError as exc:
            detail = exc.response.text if exc.response is not None else str(exc)
            st.warning(f"La API rechazo el request: {detail}. Se usara el modelo local.")
            try:
                proba = predict_with_local_model(model, payload)
            except Exception as local_exc:  # noqa: BLE001
                st.error(f"No se pudo predecir con el modelo local: {local_exc}")
                return
        except (requests.RequestException, KeyError, ValueError) as exc:
            if api_available:
                st.warning(f"No se pudo obtener prediccion desde la API: {exc}. Se usara el modelo local.")
            try:
                proba = predict_with_local_model(model, payload)
            except Exception as local_exc:  # noqa: BLE001
                st.error(f"No se pudo predecir con el modelo local: {local_exc}")
                return
        if proba is None:
            st.error("No se pudo calcular la probabilidad de compra.")
            return
        st.caption(f"Prediccion servida por: {source}")
        level, action, tone = classify_intention(proba)
        decision = proba >= threshold
        estimated_impact = assumptions.benefit_tp_usd if decision else -assumptions.cost_fn_usd * proba
        st.progress(min(max(proba, 0.0), 1.0), text=f"Probabilidad de compra: {proba:.1%}")
        cols = st.columns(4)
        cols[0].metric("Nivel de intencion", level)
        cols[1].metric("Decision", "Intervenir" if decision else "No intervenir")
        cols[2].metric("Threshold dashboard", f"{threshold:.2f}")
        cols[3].metric("Impacto estimado", fmt_usd(float(estimated_impact)))
        if tone == "success":
            st.success(action)
        elif tone == "warning":
            st.warning(action)
        else:
            st.info(action)
    xgb = get_row(comparison, PRIMARY_MODEL)
    if not xgb.empty:
        st.caption(
            f"Con los supuestos actuales, cada TP aporta {fmt_usd(assumptions.benefit_tp_usd)}, "
            f"cada FP cuesta {fmt_usd(assumptions.cost_fp_usd)} y cada FN cuesta {fmt_usd(assumptions.cost_fn_usd)}."
        )


def render_segments(bundle: dict, show_technical: bool, context: dict | None = None) -> None:
    st.header("Segmentos y senales de negocio")
    if context and context.get("is_uploaded") and context.get("is_valid"):
        segments, features = build_dynamic_segments(context.get("predictions", context.get("df", pd.DataFrame())))
        st.caption(f"Segmentos calculados sobre: {context.get('source', 'dataset cargado')}")
    else:
        segments = bundle.get("segments", pd.DataFrame())
        features = bundle.get("feature_summary", pd.DataFrame())
    cols = st.columns(3)
    for col, dimension in zip(cols, ["VisitorType", "Month", "Weekend"]):
        fig = segment_conversion_chart(segments, dimension)
        if fig:
            col.plotly_chart(fig, width="stretch")
    fig_features = feature_summary_chart(features)
    if fig_features:
        st.plotly_chart(fig_features, width="stretch")
    importances = model_feature_importance()
    fig_importance = feature_importance_chart(importances)
    if fig_importance:
        st.plotly_chart(fig_importance, width="stretch")
    business_note("Lectura ejecutiva: PageValues, duracion en productos y tasas de salida ayudan a priorizar visitantes con senales claras de compra.")
    if show_technical:
        st.dataframe(segments, width="stretch", hide_index=True)


def render_recommendations() -> None:
    st.header("Recomendaciones ejecutivas")
    recommendations = [
        "Usar el modelo con mayor valor economico bajo los supuestos actuales para priorizacion comercial.",
        "Aplicar incentivos solo cuando la probabilidad supere el threshold economico.",
        "Evitar descuentos indiscriminados: los falsos positivos consumen margen.",
        "Monitorear falsos negativos: representan compradores potenciales no atendidos.",
        "Ajustar el threshold segun presupuesto, margen y costo real de campanas.",
        "Medir resultados reales despues de activar acciones comerciales.",
        "Usar la API del Sprint 6 para exponer predicciones en tiempo real cuando el despliegue avance.",
    ]
    for recommendation in recommendations + business_recommendations():
        st.markdown(f"- {recommendation}")
    st.success("Decision sugerida: focalizar acciones comerciales, medir conversion incremental y recalibrar supuestos economicos.")


def render_project_about() -> None:
    st.header("Acerca del proyecto")
    st.markdown(
        "**Proyecto 2: Conversion de Visitantes Online** busca ayudar a una tienda e-commerce a decidir, en tiempo casi real, "
        "que visitantes merecen una accion comercial prioritaria antes de que abandonen la sesion."
    )
    st.info(
        "Idea central: no intervenir a todos. El modelo permite focalizar cupones, ofertas, recomendaciones o chat "
        "prioritario en visitantes con mayor probabilidad de compra."
    )

    cols = st.columns(4)
    cols[0].metric("Tipo de problema", "Clasificacion")
    cols[1].metric("Target", "Revenue=True")
    cols[2].metric("Modelo tecnico final", PRIMARY_MODEL)
    cols[3].metric("Criterio principal", "F1-score")

    st.subheader("1. Problema de negocio")
    st.markdown(
        """
        En una tienda online, muchas sesiones no terminan en compra. El reto no es solamente predecir quien comprara,
        sino decidir **donde conviene invertir una accion comercial**. Intervenir a todos puede destruir margen; intervenir
        tarde puede perder ventas; no intervenir deja oportunidades sobre la mesa.
        """
    )

    st.subheader("2. Solucion analitica")
    st.markdown(
        """
        El proyecto usa el dataset **Online Shoppers Purchasing Intention** y modela la variable `Revenue` como una
        clasificacion binaria: compra (`True`) o no compra (`False`). La clase compradora esta desbalanceada, por eso
        el desempeno tecnico se evalua principalmente con **F1-score**, complementado con Precision, Recall, Accuracy y ROC-AUC.
        """
    )

    st.subheader("3. Modelo final y decision economica")
    st.markdown(
        """
        El modelo final tecnico es **XGBoost**. Sin embargo, el dashboard tambien calcula un **modelo recomendado
        economicamente**, que puede cambiar segun los supuestos del negocio: costo de incentivo, costo de contacto,
        margen, uplift esperado y threshold de decision.

        El valor economico se estima con la matriz de confusion:
        `TP * beneficio_TP + FP * costo_FP + FN * costo_FN + TN * valor_TN`.
        """
    )

    st.subheader("4. Que permite hacer este dashboard")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            """
            - Comparar modelos por valor economico en USD.
            - Analizar el impacto del tuning.
            - Buscar el threshold que maximiza valor de negocio.
            - Simular visitantes individuales.
            """
        )
    with c2:
        st.markdown(
            """
            - Cargar nuevos datasets para prediccion.
            - Revisar segmentos con mayor conversion.
            - Evaluar costos de falsos positivos y falsos negativos.
            - Preparar la integracion futura con API.
            """
        )

def render_sprint6_readiness() -> None:
    st.header("Preparacion para Sprint 6")
    ready = [
        "Modelo final disponible: models/c_final_model.pkl y models/c_best_model.pkl.",
        "Pipeline/preprocesamiento disponible para consumo del modelo.",
        "API PB-19, contratos y Docker se mantienen sin cambios en esta mejora del dashboard.",
        "Dashboard consume artefactos existentes y agrega tablas economicas para analisis ejecutivo.",
        "Validacion de datasets disponible para dashboard y reutilizable como contrato de entrada.",
        "Las nuevas tablas pueden ser reutilizadas por PB-21 o por monitoreo si el equipo las necesita.",
    ]
    pending = ["Despliegue AWS productivo", "URL publica definitiva", "Monitoreo en ambiente real", "Seguridad y gestion de credenciales"]
    st.success("Sprint 6 sigue compatible: esta tarea no modifica entrenamiento, API ni Docker.")
    st.markdown("**Listo / compatible**")
    for item in ready:
        st.markdown(f"- {item}")
    st.markdown("**Pendiente de Sprint 6 operativo**")
    for item in pending:
        st.markdown(f"- {item}")


def main() -> None:
    original_df, original_X, original_y = load_dataset()
    model, model_path = load_model()
    bundle = load_dashboard_bundle()
    default_threshold = get_default_economic_threshold(bundle)
    view, threshold, assumptions, show_technical, dataset_mode, uploaded_file = render_sidebar(default_threshold)
    context = build_prediction_context(
        dataset_mode,
        uploaded_file,
        original_df,
        original_X,
        original_y,
        assumptions,
        threshold,
    )
    df = context["df"]
    X = context["X"]
    y = context["y"]
    comparison, curve, baseline = build_dynamic_economic_views(context, assumptions, threshold)
    if model_path:
        st.caption(f"Modelo final cargado para referencia local: `{model_path}`")
    st.caption(f"Dataset activo: `{context['source']}`")
    if model is not None:
        scores = score_dataset(model, X)
        pred = (scores >= threshold).astype(int)
    else:
        scores = pd.Series([0.0] * len(df), index=df.index)
        pred = pd.Series([0] * len(df), index=df.index)

    if view == "Acerca del proyecto":
        render_project_about()
    elif view == "Resumen ejecutivo":
        render_executive_summary(comparison, baseline, curve, bundle, threshold)
    elif view == "Cargar nuevo dataset":
        render_uploaded_dataset_view(context, assumptions, threshold)
    elif view == "Ranking economico":
        render_economic_ranking(comparison, baseline, show_technical)
    elif view == "Impacto economico del tuning":
        render_tuning_impact(comparison, show_technical)
    elif view == "Desempeno tecnico vs valor economico":
        render_technical_vs_economic(comparison)
    elif view == "Profit curve":
        render_profit_curve(comparison, curve)
        if show_technical and y is not None:
            st.plotly_chart(confusion_matrix_chart(y, pred), width="stretch")
    elif view == "Simulador economico":
        render_economic_simulator(comparison, df, threshold, assumptions, model)
    elif view == "Segmentos":
        render_segments(bundle, show_technical, context)
    elif view == "Recomendaciones":
        render_recommendations()
    else:
        render_project_about()


if __name__ == "__main__":
    main()
