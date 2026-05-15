import streamlit as st
import pandas as pd
import joblib

st.set_page_config(page_title="Dashboard ML", layout="wide")

st.title("Dashboard de Predicciones")

MODEL_PATH = "models/tuned_xgboost.pkl"
DATA_PATH = "data/processed/train_balanced.csv"
TARGET_COL = "Revenue"

@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

model = load_model()
df = load_data()

X = df.drop(columns=[TARGET_COL])
y = df[TARGET_COL]

st.subheader("KPIs principales")

c1, c2, c3 = st.columns(3)

c1.metric("Registros", len(df))
c2.metric("Variables", X.shape[1])
c3.metric("Modelo", type(model).__name__)

st.sidebar.title("Simulador de predicción")

input_data = {}

for col in X.columns:
    if X[col].dtype == "object":
        input_data[col] = st.sidebar.selectbox(
            col,
            X[col].dropna().unique()
        )
    else:
        input_data[col] = st.sidebar.number_input(
            col,
            value=float(X[col].median())
        )

input_df = pd.DataFrame([input_data])

st.subheader("Predicción individual")

if st.button("Predecir"):
    try:
        pred = model.predict(input_df)[0]
        st.metric("Predicción", pred)

        if hasattr(model, "predict_proba"):
            prob = model.predict_proba(input_df)[0].max()
            st.metric("Confianza", f"{prob:.2%}")

    except Exception as e:
        st.error("No se pudo realizar la predicción.")
        st.write(
            "El modelo fue entrenado con variables transformadas "
            "que no están todas disponibles en el dataset actual."
        )
        st.code(str(e))

st.subheader("Vista del dataset")

st.dataframe(df.head(100))

st.subheader("Evaluación del modelo")

st.warning(
    "Confusion Matrix y ROC Curve quedan pendientes porque el modelo fue "
    "entrenado con variables transformadas/feature engineering que no están "
    "presentes en este dataset base."
)

st.subheader("Explicabilidad SHAP")

st.info(
    "SHAP por instancia queda pendiente hasta cargar el dataset con las mismas "
    "features usadas en el entrenamiento del modelo."
)