from __future__ import annotations

import pandas as pd
import plotly.express as px
from sklearn.metrics import confusion_matrix


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


def business_label(name: str) -> str:
    clean_name = str(name)
    for prefix in ["num__", "cat__"]:
        clean_name = clean_name.replace(prefix, "")
    for field, label in sorted(FIELD_LABELS.items(), key=lambda item: len(item[0]), reverse=True):
        if clean_name == field:
            return label
        if clean_name.startswith(f"{field}_"):
            return f"{label}: {clean_name.removeprefix(f'{field}_')}"
    return clean_name


def model_f1_chart(metrics: pd.DataFrame):
    if metrics.empty or "cv_f1" not in metrics.columns:
        return None
    view = metrics.dropna(subset=["cv_f1"]).sort_values("cv_f1", ascending=False).head(10)
    return px.bar(
        view,
        x="cv_f1",
        y="model",
        color="phase",
        orientation="h",
        labels={"cv_f1": "F1-score CV", "model": "Modelo"},
        title="Comparación de modelos por F1-score",
    )


def precision_recall_chart(metrics: pd.DataFrame):
    if metrics.empty or not {"cv_precision", "cv_recall"}.issubset(metrics.columns):
        return None
    view = metrics.dropna(subset=["cv_precision", "cv_recall"])
    return px.scatter(
        view,
        x="cv_recall",
        y="cv_precision",
        color="phase",
        text="model",
        labels={"cv_recall": "Recall", "cv_precision": "Precision"},
        title="Trade-off Precision vs Recall",
    )


def confusion_matrix_chart(y_true, y_pred):
    matrix = confusion_matrix(y_true, y_pred, labels=[0, 1])
    return px.imshow(
        matrix,
        text_auto=True,
        x=["Predice no compra", "Predice compra"],
        y=["Real no compra", "Real compra"],
        labels={"color": "Sesiones"},
        color_continuous_scale="Blues",
        title="Matriz de confusión",
    )


def business_value_chart(thresholds: pd.DataFrame):
    if thresholds.empty:
        return None
    return px.line(
        thresholds,
        x="threshold",
        y="expected_value",
        markers=True,
        labels={"threshold": "Umbral", "expected_value": "Valor esperado"},
        title="Valor esperado por umbral",
    )


def segment_conversion_chart(segments: pd.DataFrame, dimension: str):
    if segments.empty:
        return None
    view = segments[segments["dimension"].eq(dimension)].sort_values("conversion_rate", ascending=False)
    dimension_label = business_label(dimension)
    return px.bar(
        view,
        x="segment",
        y="conversion_rate",
        text="sessions",
        labels={"segment": dimension_label, "conversion_rate": "Tasa de conversión", "sessions": "Sesiones"},
        title=f"Conversión por {dimension_label.lower()}",
    )


def feature_summary_chart(feature_summary: pd.DataFrame):
    if feature_summary.empty:
        return None
    view = feature_summary.copy()
    view["feature_label"] = view["feature"].map(business_label)
    view["Revenue"] = view["revenue"].map({0: "No compra", 1: "Compra"})
    return px.bar(
        view,
        x="feature_label",
        y="average_value",
        color="Revenue",
        barmode="group",
        labels={"feature_label": "Señal de comportamiento", "average_value": "Promedio"},
        title="Promedio de señales de intención por resultado",
    )


def feature_importance_chart(importances: pd.DataFrame):
    if importances.empty:
        return None
    view = importances.head(15).copy()
    view["feature_label"] = view["feature"].map(business_label)
    view = view.sort_values("importance")
    return px.bar(
        view,
        x="importance",
        y="feature_label",
        orientation="h",
        labels={"importance": "Importancia", "feature_label": "Variable"},
        title="Variables más relevantes del modelo",
    )
