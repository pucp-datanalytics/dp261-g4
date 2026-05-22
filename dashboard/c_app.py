from __future__ import annotations

import os
from pathlib import Path
import sys

import pandas as pd
import requests
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "dashboard"))

from c_business_insights import business_recommendations, classify_intention, executive_summary, performance_status
from c_dashboard_data import model_feature_importance
from c_charts import (
    business_value_chart,
    confusion_matrix_chart,
    feature_importance_chart,
    feature_summary_chart,
    model_f1_chart,
    precision_recall_chart,
    segment_conversion_chart,
)
from c_components import business_note, explain_metric, missing_warning, status_box
from c_data_loader import load_dashboard_bundle, load_dataset, load_model, score_dataset


st.set_page_config(page_title="Dashboard Ejecutivo - Conversion Online", layout="wide")


DEFAULT_API_URL = "http://localhost:8000"
API_TIMEOUT_SECONDS = 10


FIELD_LABELS = {
    "Administrative": "Páginas administrativas visitadas",
    "Administrative_Duration": "Tiempo en páginas administrativas",
    "Informational": "Páginas informativas visitadas",
    "Informational_Duration": "Tiempo en páginas informativas",
    "ProductRelated": "Páginas de producto visitadas",
    "ProductRelated_Duration": "Tiempo en páginas de producto",
    "BounceRates": "Tasa de rebote",
    "ExitRates": "Tasa de salida",
    "PageValues": "Valor estimado de páginas",
    "SpecialDay": "Cercanía a fecha especial",
    "Month": "Mes de visita",
    "OperatingSystems": "Sistema operativo",
    "Browser": "Navegador",
    "Region": "Región",
    "TrafficType": "Tipo de tráfico",
    "VisitorType": "Tipo de visitante",
    "Weekend": "Visita en fin de semana",
}


def field_label(name: str) -> str:
    return FIELD_LABELS.get(name, name)


def get_api_url() -> str:
    return os.getenv("API_URL", DEFAULT_API_URL).rstrip("/")


def predict_with_api(payload: dict) -> dict:
    api_url = get_api_url()
    response = requests.post(f"{api_url}/predict", json=payload, timeout=API_TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json()


def render_api_status() -> None:
    api_url = get_api_url()
    st.caption(f"API configurada: `{api_url}`")
    try:
        response = requests.get(f"{api_url}/health", timeout=3)
        response.raise_for_status()
    except requests.RequestException as exc:
        st.warning(f"API no disponible para integracion en vivo: {exc}")
        return
    st.success("API disponible: el simulador enviara predicciones por REST.")


def render_sidebar(default_threshold: float) -> tuple[str, float, bool]:
    st.sidebar.title("Panel ejecutivo")
    view = st.sidebar.selectbox(
        "Selector de vista",
        [
            "Resumen ejecutivo",
            "Desempeño del modelo",
            "Valor de negocio",
            "Simulador",
            "Segmentos",
            "Recomendaciones",
            "Handoff Sprint 6",
        ],
    )
    default_threshold = min(max(float(default_threshold), 0.05), 0.95)
    threshold = float(
        st.sidebar.slider(
            "Threshold de decisión",
            min_value=0.05,
            max_value=0.95,
            value=default_threshold,
            step=0.01,
            format="%.2f",
        )
    )
    show_technical = st.sidebar.checkbox("Mostrar detalles técnicos", value=False)
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Ficha del proyecto**")
    st.sidebar.markdown("- Proyecto 2")
    st.sidebar.markdown("- Target: `Revenue=True`")
    st.sidebar.markdown("- Sprint 5")
    st.sidebar.markdown("- Estado: prototipo ejecutivo")
    return view, threshold, show_technical


def get_final_metrics(validation: pd.DataFrame, metrics: pd.DataFrame) -> dict:
    final = validation[validation["phase"].eq("final_test_threshold_0_5")] if not validation.empty else pd.DataFrame()
    if not final.empty:
        row = final.iloc[0]
        return {k: float(row[k]) for k in ["accuracy", "precision", "recall", "f1", "roc_auc"]}
    tuned = metrics[metrics["phase"].eq("tuned")] if not metrics.empty else pd.DataFrame()
    if not tuned.empty:
        row = tuned.sort_values("cv_f1", ascending=False).iloc[0]
        return {
            "accuracy": float(row.get("cv_accuracy", 0)),
            "precision": float(row.get("cv_precision", 0)),
            "recall": float(row.get("cv_recall", 0)),
            "f1": float(row.get("cv_f1", 0)),
            "roc_auc": float(row.get("cv_roc_auc", 0)),
        }
    return {"accuracy": 0, "precision": 0, "recall": 0, "f1": 0, "roc_auc": 0}


def build_dashboard_kpis(df: pd.DataFrame, y: pd.Series, scores: pd.Series, threshold: float, final_metrics: dict, thresholds: pd.DataFrame) -> dict:
    pred = (scores >= threshold).astype(int)
    best_business = thresholds.sort_values("expected_value", ascending=False).head(1) if not thresholds.empty else pd.DataFrame()
    expected_value = float(best_business.iloc[0]["expected_value"]) if not best_business.empty else 0.0
    recommended_threshold = float(best_business.iloc[0]["threshold"]) if not best_business.empty else threshold
    return {
        **final_metrics,
        "real_conversion_rate": float(y.mean()),
        "recommended_threshold": recommended_threshold,
        "selected_threshold": threshold,
        "expected_value": expected_value,
        "sessions": int(len(df)),
        "real_buyers": int(y.sum()),
        "detected_buyers": int(((pred == 1) & (y == 1)).sum()),
        "predicted_positive": int(pred.sum()),
    }


def render_header() -> None:
    st.title("Dashboard Ejecutivo - Conversión de Visitantes Online")
    st.subheader("Modelo predictivo para identificar visitantes con alta probabilidad de compra")
    st.markdown(
        "Proyecto 2: Conversión de Visitantes en Compradores Online. "
        "El target es `Revenue=True`, que indica una sesión que terminó en compra."
    )
    st.success("El modelo permite priorizar acciones comerciales sobre visitantes con mayor intención de compra.")


def render_kpis(kpis: dict) -> None:
    rows = [
        [("F1-score", f"{kpis['f1']:.3f}", "Balance entre precisión y recall."), ("Recall", f"{kpis['recall']:.1%}", "Compradores reales detectados."), ("Precision", f"{kpis['precision']:.1%}", "Predicciones de compra que fueron correctas."), ("ROC-AUC", f"{kpis['roc_auc']:.3f}", "Capacidad de separar compradores y no compradores.")],
        [("Conversión real", f"{kpis['real_conversion_rate']:.1%}", "Porcentaje histórico de sesiones con compra."), ("Umbral recomendado", f"{kpis['recommended_threshold']:.2f}", "Threshold que maximiza valor esperado."), ("Valor esperado", f"{kpis['expected_value']:,.0f}", "Impacto bajo supuestos actuales."), ("Visitantes evaluados", f"{kpis['sessions']:,}", "Sesiones disponibles para análisis.")],
        [("Compradores reales", f"{kpis['real_buyers']:,}", "Sesiones que terminaron en compra."), ("Compradores detectados", f"{kpis['detected_buyers']:,}", "Compradores capturados con el threshold seleccionado."), ("Visitantes priorizados", f"{kpis['predicted_positive']:,}", "Sesiones que recibirían acción comercial."), ("Threshold actual", f"{kpis['selected_threshold']:.2f}", "Controlado desde la barra lateral.")],
    ]
    for row in rows:
        cols = st.columns(4)
        for col, (label, value, caption) in zip(cols, row):
            col.metric(label, value)
            with col:
                explain_metric(label, caption)


def render_executive_summary(kpis: dict, validation: pd.DataFrame) -> None:
    render_header()
    render_kpis(kpis)
    status, message = performance_status(validation)
    status_box(status, message)
    summary = executive_summary(kpis)
    tab1, tab2, tab3, tab4 = st.tabs(["Qué significa", "Acción sugerida", "Riesgo", "Confiabilidad"])
    tab1.markdown(summary["meaning"])
    tab2.markdown(summary["action"])
    tab3.markdown(summary["risk"])
    tab4.markdown(summary["confidence"])


def render_model_performance(bundle: dict, y: pd.Series, scores: pd.Series, threshold: float, show_technical: bool) -> None:
    st.header("Desempeño del modelo")
    metrics = bundle["metrics"]
    validation = bundle["validation"]
    pred = (scores >= threshold).astype(int)
    status, message = performance_status(validation)
    status_box(status, message)
    cols = st.columns(2)
    fig_f1 = model_f1_chart(metrics)
    fig_pr = precision_recall_chart(metrics)
    if fig_f1:
        cols[0].plotly_chart(fig_f1, width="stretch")
    else:
        cols[0].warning("No hay métricas suficientes para comparar F1.")
    if fig_pr:
        cols[1].plotly_chart(fig_pr, width="stretch")
    else:
        cols[1].warning("No hay métricas suficientes para Precision vs Recall.")
    st.plotly_chart(confusion_matrix_chart(y, pred), width="stretch")
    business_note("La matriz indica cuántos compradores reales se capturan y cuántos visitantes recibirían acciones sin comprar.")
    if show_technical:
        with st.expander("Tabla técnica de validación"):
            st.dataframe(validation, width="stretch")


def render_business_value(bundle: dict, threshold: float, show_technical: bool) -> None:
    st.header("Valor de negocio")
    thresholds = bundle["thresholds"]
    if thresholds.empty:
        missing_warning("models/c_threshold_analysis.csv")
        return
    best = thresholds.sort_values("expected_value", ascending=False).iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("Umbral recomendado", f"{best['threshold']:.2f}")
    c2.metric("Valor esperado", f"{best['expected_value']:,.0f}")
    c3.metric("Valor por sesión", f"{best['value_per_session']:.2f}")
    fig = business_value_chart(thresholds)
    if fig:
        st.plotly_chart(fig, width="stretch")
    st.info("El threshold puede ser distinto de 0.5 porque el negocio no valora igual un falso positivo y un falso negativo.")
    st.success(f"Recomendación: usar el umbral {best['threshold']:.2f} para maximizar valor esperado bajo los supuestos actuales.")
    if show_technical:
        st.dataframe(thresholds, width="stretch", hide_index=True)


def render_prediction_simulator(model, df: pd.DataFrame, threshold: float) -> None:
    st.header("Simulador interactivo de visitante")
    render_api_status()
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
    with st.expander("Características de la sesión", expanded=True):
        cols = st.columns(3)
        for idx, col_name in enumerate(available_numeric_cols):
            values = pd.to_numeric(df[col_name], errors="coerce").dropna()
            if values.empty:
                min_value, max_value, default = 0.0, 1.0, 0.0
            else:
                min_value = float(values.min())
                max_value = float(values.quantile(0.99))
                if min_value == max_value:
                    max_value = min_value + 1.0
                default = float(defaults.get(col_name, min_value))
            default = float(defaults.get(col_name, min_value))
            payload[col_name] = cols[idx % 3].slider(
                field_label(col_name),
                min_value=min_value,
                max_value=max_value,
                value=min(max(default, min_value), max_value),
                key=f"sim_{col_name}",
            )
        for col_name in available_categorical_cols:
            options = sorted(df[col_name].dropna().astype(str).unique().tolist())
            if not options:
                options = [""]
            payload[col_name] = st.selectbox(field_label(col_name), options, key=f"sim_{col_name}")
        payload["Weekend"] = st.checkbox(field_label("Weekend"), key="sim_Weekend")
    if st.button("Calcular probabilidad de compra"):
        try:
            result = predict_with_api(payload)
            proba = float(result["purchase_probability"])
            api_threshold = float(result.get("threshold", threshold))
            st.caption(f"Prediccion servida por API REST. Modelo: `{result.get('model_path', 'no informado')}`")
        except requests.HTTPError as exc:
            detail = exc.response.text if exc.response is not None else str(exc)
            st.error(f"La API rechazo el request: {detail}")
            return
        except (requests.RequestException, KeyError, ValueError) as exc:
            st.error(f"No se pudo obtener prediccion desde la API: {exc}")
            return
        level, action, tone = classify_intention(proba)
        st.progress(min(max(proba, 0.0), 1.0), text=f"Probabilidad de compra: {proba:.1%}")
        st.metric("Nivel de intención", level)
        st.metric("Decisión", "Activar acción comercial" if proba >= api_threshold else "No priorizar todavía")
        st.metric("Threshold API", f"{api_threshold:.2f}")
        if tone == "success":
            st.success(action)
        elif tone == "warning":
            st.warning(action)
        else:
            st.info(action)


def render_segments(bundle: dict, show_technical: bool) -> None:
    st.header("Análisis de segmentos")
    segments = bundle["segments"]
    features = bundle["feature_summary"]
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
    business_note("Los segmentos y señales de navegación ayudan a enfocar incentivos donde hay mayor intención de compra.")
    if show_technical:
        st.dataframe(segments, width="stretch", hide_index=True)


def render_recommendations() -> None:
    st.header("Recomendaciones de negocio")
    for recommendation in business_recommendations():
        st.markdown(f"- {recommendation}")
    st.success("Prioridad ejecutiva: aplicar acciones focalizadas, medir resultados reales y ajustar costos antes de producción.")


def render_sprint6_handoff() -> None:
    st.header("Handoff para Sprint 6")
    st.markdown("**Artefactos listos**")
    for item in ["Modelo final", "Pipeline de preprocesamiento", "Métricas", "Script de predicción", "Dashboard ejecutivo", "Notas de handoff"]:
        st.markdown(f"- {item}")
    st.markdown("**Pendiente para Sprint 6**")
    for item in ["API FastAPI", "Docker", "AWS", "Integración productiva", "Monitoreo y seguridad"]:
        st.markdown(f"- {item}")
    st.warning("Sprint 6 no está implementado todavía. Este dashboard es un prototipo ejecutivo de Sprint 5.")


def main() -> None:
    df, X, y = load_dataset()
    model, model_path = load_model()
    bundle = load_dashboard_bundle()
    if bundle["thresholds"].empty:
        default_threshold = 0.5
    else:
        default_threshold = float(bundle["thresholds"].sort_values("expected_value", ascending=False).iloc[0]["threshold"])
    view, threshold, show_technical = render_sidebar(default_threshold)
    if model is None:
        st.warning("No se encontró `models/c_final_model.pkl` ni `models/c_best_model.pkl`.")
        scores = pd.Series([0.0] * len(df), index=df.index)
    else:
        scores = score_dataset(model, X)
    final_metrics = get_final_metrics(bundle["validation"], bundle["metrics"])
    kpis = build_dashboard_kpis(df, y, scores, threshold, final_metrics, bundle["thresholds"])
    if model_path:
        st.caption(f"Modelo cargado: `{model_path}`")
    if view == "Resumen ejecutivo":
        render_executive_summary(kpis, bundle["validation"])
    elif view == "Desempeño del modelo":
        render_model_performance(bundle, y, scores, threshold, show_technical)
    elif view == "Valor de negocio":
        render_business_value(bundle, threshold, show_technical)
    elif view == "Simulador":
        render_prediction_simulator(model, df, threshold)
    elif view == "Segmentos":
        render_segments(bundle, show_technical)
    elif view == "Recomendaciones":
        render_recommendations()
    else:
        render_sprint6_handoff()


if __name__ == "__main__":
    main()
