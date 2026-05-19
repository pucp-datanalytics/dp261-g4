from __future__ import annotations

import logging
import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from c_preprocessing import TARGET_COL, add_features, clean_data  # noqa: E402
from c_utils import predict_scores  # noqa: E402
from api.schemas import VisitorFeatures  # noqa: E402


LOGGER = logging.getLogger(__name__)
DEFAULT_MODEL_PATH = "handoff/model/c_final_model.pkl"
DEFAULT_PREPROCESSOR_PATH = "handoff/model/c_preprocessing_pipeline.pkl"
DEFAULT_THRESHOLD = 0.5


def get_model_path() -> str:
    return os.getenv("MODEL_PATH", DEFAULT_MODEL_PATH)


def get_preprocessor_path() -> str | None:
    return os.getenv("PREPROCESSOR_PATH", DEFAULT_PREPROCESSOR_PATH)


def get_threshold() -> float:
    raw = os.getenv("THRESHOLD", str(DEFAULT_THRESHOLD))
    try:
        threshold = float(raw)
    except ValueError as exc:
        raise ValueError(f"THRESHOLD debe ser numerico, recibido: {raw}") from exc
    if not 0 <= threshold <= 1:
        raise ValueError(f"THRESHOLD debe estar entre 0 y 1, recibido: {threshold}")
    return threshold


@lru_cache(maxsize=1)
def load_model() -> Any:
    model_path = Path(get_model_path())
    if not model_path.exists():
        raise FileNotFoundError(f"No se encontro el modelo: {model_path}")
    LOGGER.info("Cargando modelo desde %s", model_path)
    return joblib.load(model_path)


@lru_cache(maxsize=1)
def load_preprocessor() -> Any | None:
    preprocessor_path = get_preprocessor_path()
    if not preprocessor_path:
        return None
    path = Path(preprocessor_path)
    if not path.exists():
        LOGGER.warning("No se encontro preprocesador opcional: %s", path)
        return None
    LOGGER.info("Cargando preprocesador opcional desde %s", path)
    return joblib.load(path)


def model_is_pipeline(model: Any | None = None) -> bool:
    model = model if model is not None else load_model()
    return hasattr(model, "named_steps") and "preprocessor" in getattr(model, "named_steps", {})


def build_model_input(features: VisitorFeatures) -> pd.DataFrame:
    input_df = pd.DataFrame([features.model_dump()])
    input_df[TARGET_COL] = 0
    clean = clean_data(input_df)
    return add_features(clean.drop(columns=[TARGET_COL]))


def predict_purchase(features: VisitorFeatures) -> dict:
    model = load_model()
    threshold = get_threshold()
    X_input = build_model_input(features)

    if model_is_pipeline(model):
        scores = predict_scores(model, X_input)
    else:
        preprocessor = load_preprocessor()
        if preprocessor is not None:
            X_input = preprocessor.transform(X_input)
        scores = predict_scores(model, X_input)

    probability = float(scores[0])
    prediction = int(probability >= threshold)
    return {
        "purchase_probability": probability,
        "prediction": prediction,
        "threshold": threshold,
        "model_path": get_model_path(),
    }
