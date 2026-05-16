from __future__ import annotations

from pathlib import Path
import sys

import joblib
import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.metrics import confusion_matrix


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from c_preprocessing import TARGET_COL, add_features, clean_data, load_raw_data
from c_utils import predict_scores


st.set_page_config(page_title="Conversion Online Sprint 5", layout="wide")
st.title("Conversion de Visitantes en Compradores Online")

MODEL_PATH = ROOT / "models" / "c_final_model.pkl"
METRICS_PATH = ROOT / "models" / "c_validation_test_comparison.csv"
BUSINESS_PATH = ROOT / "models" / "c_threshold_analysis.csv"


@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


@st.cache_data
def load_data():
    df = clean_data(load_raw_data(ROOT / "docs" / "dataset_pucp.csv"))
    X = add_features(df.drop(columns=[TARGET_COL]))
    return df, X, df[TARGET_COL]


model = load_model()
df, X, y = load_data()
business = pd.read_csv(BUSINESS_PATH) if BUSINESS_PATH.exists() else pd.DataFrame()
threshold = float(business.sort_values("expected_value", ascending=False).iloc[0]["threshold"]) if not business.empty else 0.5
scores = predict_scores(model, X)
pred = (scores >= threshold).astype(int)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Sesiones", f"{len(df):,}")
c2.metric("Conversion real", f"{y.mean():.1%}")
c3.metric("Umbral negocio", f"{threshold:.2f}")
c4.metric("Modelo", type(model.named_steps["classifier"]).__name__)

left, right = st.columns(2)
with left:
    cm = confusion_matrix(y, pred, labels=[0, 1])
    fig_cm = px.imshow(
        cm,
        text_auto=True,
        x=["No compra", "Compra"],
        y=["No compra", "Compra"],
        labels={"x": "Prediccion", "y": "Real", "color": "Sesiones"},
        color_continuous_scale="Blues",
    )
    st.plotly_chart(fig_cm, width="stretch")

with right:
    if METRICS_PATH.exists():
        metrics = pd.read_csv(METRICS_PATH)
        st.dataframe(metrics.tail(8), width="stretch", hide_index=True)

if not business.empty:
    st.subheader("Valor de negocio por umbral")
    fig_value = px.line(business, x="threshold", y="expected_value", markers=True)
    st.plotly_chart(fig_value, width="stretch")

st.subheader("Prediccion de ejemplo")
sample = df.drop(columns=[TARGET_COL]).iloc[0].to_dict()
payload = {}
cols = st.columns(3)
for idx, (col, value) in enumerate(sample.items()):
    with cols[idx % 3]:
        if str(df[col].dtype) in ["string", "object", "category"]:
            options = sorted(df[col].astype(str).unique().tolist())
            payload[col] = st.selectbox(col, options, index=options.index(str(value)))
        elif col == "Weekend":
            payload[col] = st.checkbox(col, value=bool(value))
        else:
            payload[col] = st.number_input(col, value=float(value))

input_df = pd.DataFrame([payload])
input_df[TARGET_COL] = 0
input_clean = clean_data(input_df)
input_X = add_features(input_clean.drop(columns=[TARGET_COL]))
input_score = float(predict_scores(model, input_X)[0])
input_pred = int(input_score >= threshold)

p1, p2 = st.columns(2)
p1.metric("Probabilidad de compra", f"{input_score:.1%}")
p2.metric("Accion sugerida", "Priorizar incentivo" if input_pred else "Flujo estandar")

st.subheader("Importancia simple de variables")
classifier = model.named_steps["classifier"]
preprocessor = model.named_steps["preprocessor"]
if hasattr(classifier, "feature_importances_"):
    imp = pd.DataFrame(
        {
            "feature": preprocessor.get_feature_names_out(),
            "importance": classifier.feature_importances_,
        }
    ).sort_values("importance", ascending=False).head(15)
    st.plotly_chart(px.bar(imp, x="importance", y="feature", orientation="h"), width="stretch")
elif hasattr(classifier, "coef_"):
    imp = pd.DataFrame(
        {
            "feature": preprocessor.get_feature_names_out(),
            "importance": abs(classifier.coef_[0]),
        }
    ).sort_values("importance", ascending=False).head(15)
    st.plotly_chart(px.bar(imp, x="importance", y="feature", orientation="h"), width="stretch")
else:
    st.info("El modelo final no expone importancia directa de variables.")
