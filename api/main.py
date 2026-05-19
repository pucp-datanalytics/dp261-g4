from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from api.predict import get_model_path, get_preprocessor_path, get_threshold, load_model, model_is_pipeline, predict_purchase
from api.schemas import HealthResponse, PredictionResponse, VersionResponse, VisitorFeatures


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
LOGGER = logging.getLogger("sprint6_api")

PROJECT_NAME = "Proyecto 2 - Conversion de Visitantes Online"
API_VERSION = "1.0.0-pb19"

app = FastAPI(
    title="Sprint 6 PB-19 API",
    description="API REST para servir el modelo final de conversion de visitantes online.",
    version=API_VERSION,
)


@app.on_event("startup")
def startup_event() -> None:
    try:
        load_model()
        LOGGER.info("API inicializada correctamente con modelo %s", get_model_path())
    except Exception:
        LOGGER.exception("Error cargando el modelo al iniciar la API")
        raise


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    LOGGER.warning("Input invalido en %s: %s", request.url.path, exc.errors())
    return JSONResponse(status_code=400, content={"detail": exc.errors()})


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    LOGGER.info("Consulta /health")
    return HealthResponse(status="ok", service="sprint6-pb19-api")


@app.get("/version", response_model=VersionResponse)
def version() -> VersionResponse:
    LOGGER.info("Consulta /version")
    try:
        model = load_model()
        threshold = get_threshold()
    except Exception as exc:
        LOGGER.exception("Error obteniendo version de API/modelo")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return VersionResponse(
        project=PROJECT_NAME,
        api_version=API_VERSION,
        model_path=get_model_path(),
        preprocessor_path=get_preprocessor_path(),
        model_is_pipeline=model_is_pipeline(model),
        threshold=threshold,
    )


@app.post("/predict", response_model=PredictionResponse)
def predict(features: VisitorFeatures) -> PredictionResponse:
    LOGGER.info("Request /predict recibido")
    try:
        prediction = predict_purchase(features)
        return PredictionResponse(**prediction)
    except ValueError as exc:
        LOGGER.warning("Error de validacion en prediccion: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        LOGGER.exception("Error ejecutando prediccion")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
