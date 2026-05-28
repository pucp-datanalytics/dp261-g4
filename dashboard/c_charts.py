from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.metrics import confusion_matrix


FIELD_LABELS = {
    "Administrative": "Paginas administrativas visitadas",
    "Administrative_Duration": "Tiempo en paginas administrativas",
    "Informational": "Paginas informativas visitadas",
    "Informational_Duration": "Tiempo en paginas informativas",
    "ProductRelated": "Paginas de producto visitadas",
    "ProductRelated_Duration": "Tiempo en paginas de producto",
    "BounceRates": "Tasa de rebote",
    "ExitRates": "Tasa de salida",
    "PageValues": "Valor estimado de paginas",
    "SpecialDay": "Cercania a fecha especial",
    "Month": "Mes de visita",
    "OperatingSystems": "Sistema operativo",
    "Browser": "Navegador",
    "Region": "Region",
    "TrafficType": "Tipo de trafico",
    "VisitorType": "Tipo de visitante",
    "Weekend": "Visita en fin de semana",
}

MODEL_COLOR_MAP = {
    "XGBoost": "#2563eb",
    "LightGBM": "#64748b",
    "Random Forest": "#94a3b8",
    "Random Forest baseline": "#f97316",
    "Logistic Regression baseline": "#14b8a6",
    "Decision Tree baseline": "#22c55e",
    "SVM baseline": "#ef4444",
    "KNN baseline": "#eab308",
    "XGBoost inicial": "#7c3aed",
    "LightGBM inicial": "#cbd5e1",
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
        title="Comparacion de modelos por F1-score",
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
        title="Matriz de confusion",
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
        labels={"segment": dimension_label, "conversion_rate": "Tasa de conversion", "sessions": "Sesiones"},
        title=f"Conversion por {dimension_label.lower()}",
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
        labels={"feature_label": "Senal de comportamiento", "average_value": "Promedio"},
        title="Promedio de senales de intencion por resultado",
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
        title="Variables mas relevantes del modelo",
    )


def economic_value_bar(comparison: pd.DataFrame):
    if comparison.empty or "net_value_usd" not in comparison.columns:
        return None
    view = comparison.copy().sort_values("net_value_usd", ascending=False)
    view["color_group"] = view["model"].apply(lambda value: "XGBoost" if value == "XGBoost" else "Comparador")
    fig = px.bar(
        view,
        x="net_value_usd",
        y="model",
        color="color_group",
        orientation="h",
        text="net_value_usd",
        color_discrete_map={"XGBoost": "#2563eb", "Comparador": "#94a3b8"},
        labels={"net_value_usd": "Valor neto estimado USD", "model": "Modelo"},
        title="Ranking economico de modelos",
    )
    fig.update_traces(texttemplate="USD %{text:,.0f}", textposition="outside")
    fig.update_layout(showlegend=False, xaxis_tickprefix="USD ")
    fig.update_yaxes(categoryorder="array", categoryarray=view["model"].tolist(), autorange="reversed")
    return fig


def incremental_gain_chart(baseline_comparison: pd.DataFrame):
    if baseline_comparison.empty or "xgboost_incremental_usd" not in baseline_comparison.columns:
        return None
    view = baseline_comparison.copy().sort_values("xgboost_incremental_usd", ascending=True)
    fig = px.bar(
        view,
        x="xgboost_incremental_usd",
        y="model",
        orientation="h",
        text="xgboost_incremental_usd",
        color="xgboost_incremental_usd",
        color_continuous_scale=["#f97316", "#22c55e"],
        labels={"xgboost_incremental_usd": "Ganancia incremental USD", "model": "Comparador"},
        title="Ganancia incremental de XGBoost frente a comparadores",
    )
    fig.update_traces(texttemplate="USD %{text:,.0f}", textposition="outside")
    fig.update_layout(coloraxis_showscale=False, xaxis_tickprefix="USD ")
    return fig


def tuned_model_waterfall(comparison: pd.DataFrame):
    if comparison.empty:
        return None
    view = comparison[comparison["model"].isin(["XGBoost", "LightGBM", "Random Forest"])].copy()
    if view.empty:
        return None
    fig = px.bar(
        view.sort_values("net_value_usd", ascending=False),
        x="model",
        y="net_value_usd",
        color="model",
        text="net_value_usd",
        color_discrete_map=MODEL_COLOR_MAP,
        labels={"net_value_usd": "Valor neto estimado USD", "model": "Modelo"},
        title="Comparativa de modelos tuneados principales",
    )
    fig.update_traces(texttemplate="USD %{text:,.0f}", textposition="outside")
    fig.update_layout(showlegend=False, yaxis_tickprefix="USD ")
    return fig


def tuning_pair_bar(tuning: pd.DataFrame):
    if tuning.empty:
        return None
    view = tuning.melt(
        id_vars=["family"],
        value_vars=["base_value_usd", "tuned_value_usd"],
        var_name="version",
        value_name="net_value_usd",
    )
    view["version"] = view["version"].map({"base_value_usd": "Base / inicial", "tuned_value_usd": "Tuneado"})
    fig = px.bar(
        view,
        x="family",
        y="net_value_usd",
        color="version",
        barmode="group",
        text="net_value_usd",
        color_discrete_map={"Base / inicial": "#94a3b8", "Tuneado": "#2563eb"},
        labels={"family": "Familia de modelo", "net_value_usd": "Valor neto estimado USD", "version": "Version"},
        title="Valor economico antes vs despues del tuning",
    )
    fig.update_traces(texttemplate="USD %{text:,.0f}", textposition="outside")
    fig.update_layout(yaxis_tickprefix="USD ")
    return fig


def tuning_delta_bar(tuning: pd.DataFrame):
    if tuning.empty:
        return None
    view = tuning.sort_values("delta_value_usd")
    fig = px.bar(
        view,
        x="delta_value_usd",
        y="family",
        orientation="h",
        color="delta_value_usd",
        text="delta_value_usd",
        color_continuous_scale=["#ef4444", "#f59e0b", "#22c55e"],
        labels={"delta_value_usd": "Incremento economico USD", "family": "Familia de modelo"},
        title="Impacto economico incremental del tuning",
    )
    fig.update_traces(texttemplate="USD %{text:,.0f}", textposition="outside")
    fig.update_layout(coloraxis_showscale=False, xaxis_tickprefix="USD ")
    return fig


def tuning_technical_delta_bar(tuning: pd.DataFrame):
    if tuning.empty:
        return None
    view = tuning.melt(
        id_vars=["family"],
        value_vars=["delta_f1", "delta_recall", "delta_precision"],
        var_name="metric",
        value_name="delta",
    )
    view["metric"] = view["metric"].map({"delta_f1": "F1", "delta_recall": "Recall", "delta_precision": "Precision"})
    return px.bar(
        view,
        x="family",
        y="delta",
        color="metric",
        barmode="group",
        labels={"family": "Familia de modelo", "delta": "Cambio tecnico", "metric": "Metrica"},
        title="Cambio tecnico del tuning",
    )


def profit_curve_chart(curve: pd.DataFrame):
    if curve.empty or not {"threshold", "net_value_usd", "model"}.issubset(curve.columns):
        return None
    model_count = curve["model"].nunique()
    line_width = 3 if model_count <= 3 else 2
    fig = px.line(
        curve,
        x="threshold",
        y="net_value_usd",
        color="model",
        markers=False,
        color_discrete_map={"XGBoost": "#2563eb", "LightGBM": "#64748b", "Random Forest": "#94a3b8"},
        labels={"threshold": "Threshold", "net_value_usd": "Valor neto estimado USD", "model": "Modelo"},
        title="Profit curve: valor economico por threshold",
    )
    fig.update_traces(line={"width": line_width})
    if "is_best_value_threshold" in curve.columns:
        is_best = curve["is_best_value_threshold"].astype(str).str.lower().eq("true")
        best_points = (
            curve[is_best]
            .sort_values(["model", "net_value_usd", "threshold"], ascending=[True, False, True])
            .groupby("model", as_index=False)
            .first()
        )
        if not best_points.empty:
            fig.add_trace(
                go.Scatter(
                    x=best_points["threshold"],
                    y=best_points["net_value_usd"],
                    mode="markers",
                    customdata=best_points[["model", "threshold", "net_value_usd"]],
                    hovertemplate="<b>%{customdata[0]}</b><br>Threshold optimo: %{customdata[1]:.2f}<br>Valor: USD %{customdata[2]:,.0f}<extra></extra>",
                    marker={"size": 10, "symbol": "diamond", "color": "#16a34a", "line": {"width": 1, "color": "white"}},
                    name="Threshold optimo",
                )
            )
    fig.update_layout(
        height=620 if model_count > 3 else 520,
        yaxis_tickprefix="USD ",
        legend_title_text="Modelo",
        hovermode="x unified" if model_count <= 3 else "closest",
        margin={"l": 20, "r": 20, "t": 70, "b": 30},
    )
    return fig


def technical_vs_value_scatter(comparison: pd.DataFrame, metric: str = "f1", highlight_model: str = "XGBoost"):
    if comparison.empty or metric not in comparison.columns:
        return None
    view = comparison[~comparison["type"].eq("operational_baseline")].copy()
    view["highlight"] = view["model"].apply(lambda value: "Modelo recomendado" if value == highlight_model else "Otros modelos")
    top_value_model = view.sort_values("net_value_usd", ascending=False).head(1)["model"].tolist()
    best_metric_model = view.sort_values(metric, ascending=False).head(1)["model"].tolist()
    labeled_models = set([highlight_model] + top_value_model + best_metric_model)
    view["label"] = view["model"].where(view["model"].isin(labeled_models), "")
    view["model_type_label"] = view["type"].map(
        {
            "tuned": "Tuneado",
            "baseline": "Baseline",
            "advanced_initial": "Inicial avanzado",
        }
    ).fillna(view["type"])
    fig = px.scatter(
        view,
        x=metric,
        y="net_value_usd",
        color="highlight",
        size="visitors_impacted",
        hover_name="model",
        text="label",
        symbol="model_type_label",
        color_discrete_map={"Modelo recomendado": "#2563eb", "Otros modelos": "#94a3b8"},
        labels={metric: metric.upper(), "net_value_usd": "Valor neto estimado USD", "highlight": "Grupo", "model_type_label": "Tipo"},
        title=f"Desempeno tecnico vs valor economico ({metric.upper()})",
        hover_data={
            "model": False,
            metric: ":.3f",
            "net_value_usd": ":,.0f",
            "visitors_impacted": ":,",
            "model_type_label": True,
            "highlight": False,
            "label": False,
        },
    )
    fig.update_traces(
        textposition="top center",
        marker={"line": {"width": 1, "color": "white"}, "opacity": 0.88},
    )
    fig.add_hline(y=0, line_dash="dash", line_color="#64748b", annotation_text="Punto de equilibrio USD 0")
    fig.update_layout(
        height=560,
        yaxis_tickprefix="USD ",
        legend_title_text="Lectura",
        margin={"l": 20, "r": 20, "t": 70, "b": 35},
    )
    fig.update_xaxes(showgrid=True, gridcolor="#e5e7eb")
    fig.update_yaxes(showgrid=True, gridcolor="#e5e7eb")
    return fig


def confusion_value_chart(row: pd.Series):
    if row.empty:
        return None
    labels = ["Compradores detectados", "Falsas intervenciones", "Oportunidades perdidas", "No compradores ignorados"]
    values = [
        float(row.get("benefit_tp_usd", 0.0)),
        float(row.get("cost_fp_usd", 0.0)),
        float(row.get("cost_fn_usd", 0.0)),
        float(row.get("value_tn_usd", 0.0)),
    ]
    colors = ["#22c55e", "#f97316", "#ef4444", "#94a3b8"]
    fig = go.Figure(go.Bar(x=labels, y=values, marker_color=colors, text=values, texttemplate="USD %{text:,.0f}"))
    fig.update_layout(title="Matriz de confusion expresada en USD", yaxis_tickprefix="USD ")
    return fig
