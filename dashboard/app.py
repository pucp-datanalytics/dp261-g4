import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
from sklearn.metrics import confusion_matrix, roc_curve, auc
import shap
import matplotlib.pyplot as plt

# ==========================================
# CONFIGURACIÓN
# ==========================================

st.set_page_config(
    page_title="Dashboard Sprint 5",
    layout="wide"
)

st.title("Dashboard de Predicciones - Sprint 5")

# RUTAS RELATIVAS (IMPORTANTES PARA GITHUB)
MODEL_PATH = "models/best_tuned_model.pkl"
DATA_PATH = "data/processed/train_balanced.csv"

TARGET_COL = "Revenue"

# ==========================================
# CARGA DE MODELO Y DATOS
# ==========================================

@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

model = load_model()
df = load_data()

# ==========================================
# PREPARACIÓN DE DATOS
# ==========================================

X_raw = df.drop(columns=[TARGET_COL])
y = df[TARGET_COL]

expected_features = list(model.feature_names_in_)

def prepare_features(data):

    X = data.copy()

    num_cols = [
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
        "total_paginas",
        "duration_total"
    ]

    cat_cols = [
        "Month",
        "OperatingSystems",
        "Browser",
        "Region",
        "TrafficType",
        "VisitorType"
    ]

    bool_cols = [
        "Weekend"
    ]

    parts = []

    # NUMÉRICAS
    for col in num_cols:
        if col in X.columns:
            parts.append(
                pd.DataFrame({
                    f"num__{col}": X[col]
                })
            )

    # BOOLEANAS
    for col in bool_cols:
        if col in X.columns:
            parts.append(
                pd.DataFrame({
                    f"bool__{col}": X[col].astype(int)
                })
            )

    # CATEGÓRICAS
    for col in cat_cols:
        if col in X.columns:

            dummies = pd.get_dummies(
                X[col],
                prefix=f"cat__{col}"
            )

            parts.append(dummies)

    X_out = pd.concat(parts, axis=1)

    # AGREGAR FEATURES FALTANTES
    for col in expected_features:
        if col not in X_out.columns:
            X_out[col] = 0

    # MISMO ORDEN DEL MODELO
    X_out = X_out[expected_features]

    return X_out

X = prepare_features(X_raw)

# ==========================================
# KPIs
# ==========================================

st.subheader("KPIs principales")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Registros", len(df))
c2.metric("Variables originales", X_raw.shape[1])
c3.metric("Features modelo", X.shape[1])
c4.metric("Modelo", type(model).__name__)

# ==========================================
# TABLA
# ==========================================

st.subheader("Tabla de datos")

st.dataframe(
    df.head(100),
    use_container_width=True
)

# ==========================================
# SIMULADOR DE PREDICCIÓN
# ==========================================

st.sidebar.header("Simulador de predicción")

input_data = {}

for col in X_raw.columns:

    if X_raw[col].dtype == "object":

        input_data[col] = st.sidebar.selectbox(
            col,
            X_raw[col].dropna().unique()
        )

    else:

        input_data[col] = st.sidebar.number_input(
            col,
            value=float(X_raw[col].median())
        )

input_raw = pd.DataFrame([input_data])

input_model = prepare_features(input_raw)

st.subheader("Simulador de predicción")

if st.button("Predecir"):

    pred = model.predict(input_model)[0]

    if pred == 1:
        st.success("Predicción: Compra / Revenue = 1")
    else:
        st.warning("Predicción: No compra / Revenue = 0")

    # PROBABILIDAD
    if hasattr(model, "predict_proba"):

        prob = model.predict_proba(input_model)[0][1]

        st.metric(
            "Probabilidad de compra",
            f"{prob:.2%}"
        )

# ==========================================
# MATRIZ DE CONFUSIÓN
# ==========================================

st.subheader("Confusion Matrix")

y_pred = model.predict(X)

cm = confusion_matrix(y, y_pred)

fig_cm = px.imshow(
    cm,
    text_auto=True,
    labels=dict(
        x="Predicción",
        y="Valor real"
    ),
    title="Confusion Matrix"
)

st.plotly_chart(
    fig_cm,
    use_container_width=True
)

# ==========================================
# CURVA ROC
# ==========================================

st.subheader("ROC Curve")

if hasattr(model, "predict_proba"):

    y_score = model.predict_proba(X)[:, 1]

    fpr, tpr, _ = roc_curve(y, y_score)

    roc_auc = auc(fpr, tpr)

    roc_df = pd.DataFrame({
        "False Positive Rate": fpr,
        "True Positive Rate": tpr
    })

    fig_roc = px.line(
        roc_df,
        x="False Positive Rate",
        y="True Positive Rate",
        title=f"ROC Curve - AUC = {roc_auc:.3f}"
    )

    st.plotly_chart(
        fig_roc,
        use_container_width=True
    )

# ==========================================
# SHAP
# ==========================================

st.subheader("Explicabilidad SHAP")

try:

    explainer = shap.TreeExplainer(model)

    sample_size = min(100, len(X))

    X_sample = X.sample(
        sample_size,
        random_state=42
    )

    shap_values = explainer.shap_values(X_sample)

    # RANDOM FOREST
    if isinstance(shap_values, list):

        shap_values_to_plot = shap_values[1]

        expected_value = explainer.expected_value[1]

    else:

        shap_values_to_plot = shap_values

        expected_value = explainer.expected_value

    # ======================================
    # IMPORTANCIA GLOBAL
    # ======================================

    st.write("### Importancia global")

    fig_summary = plt.figure(figsize=(10, 6))

    shap.summary_plot(
        shap_values_to_plot,
        X_sample,
        show=False
    )

    st.pyplot(fig_summary)

    # ======================================
    # EXPLICACIÓN INDIVIDUAL
    # ======================================

    st.write("### Explicación individual")

    idx = st.slider(
        "Selecciona una fila",
        0,
        len(X_sample) - 1,
        0
    )

    explanation = shap.Explanation(
        values=shap_values_to_plot[idx],
        base_values=expected_value,
        data=X_sample.iloc[idx],
        feature_names=X_sample.columns
    )

    fig_waterfall = plt.figure(figsize=(10, 6))

    shap.plots.waterfall(
        explanation,
        show=False
    )

    st.pyplot(fig_waterfall)

except Exception as e:

    st.warning(
        f"No se pudo generar SHAP: {e}"
    )