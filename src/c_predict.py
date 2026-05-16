from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd

from c_preprocessing import EXPECTED_COLS, TARGET_COL, add_features, clean_data, load_raw_data
from c_utils import predict_scores


MODEL_PATH = Path("models/c_final_model.pkl")


def example_payload() -> dict:
    df = clean_data(load_raw_data())
    return df.drop(columns=[TARGET_COL]).iloc[0].to_dict()


def predict_one(payload: dict, threshold: float = 0.5) -> dict:
    if not MODEL_PATH.exists():
        raise FileNotFoundError("No existe models/c_final_model.pkl. Ejecuta python src/c_tune_models.py")
    missing = [col for col in EXPECTED_COLS if col != TARGET_COL and col not in payload]
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {missing}")
    model = joblib.load(MODEL_PATH)
    row = pd.DataFrame([payload])
    row[TARGET_COL] = 0
    clean = clean_data(row)
    X = add_features(clean.drop(columns=[TARGET_COL]))
    proba = float(predict_scores(model, X)[0])
    return {
        "purchase_probability": proba,
        "prediction": int(proba >= threshold),
        "threshold": threshold,
        "model_path": str(MODEL_PATH).replace("\\", "/"),
    }


def main() -> None:
    payload = example_payload()
    result = predict_one(payload)
    print("Payload de ejemplo:")
    print(json.dumps(payload, indent=2, default=str))
    print("\nPrediccion local:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
