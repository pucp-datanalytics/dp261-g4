from __future__ import annotations

import json
import logging
import time
import uuid
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from api.predict import (
    get_model_path,
    get_model_sha,
    get_model_version,
    get_preprocessor_path,
    get_threshold,
    load_model,
    model_is_pipeline,
    predict_purchase,
)
from api.schemas import HealthResponse, PredictionResponse, VersionResponse, VisitorFeatures


logging.basicConfig(level=logging.INFO, format="%(message)s")
LOGGER = logging.getLogger("sprint6_api")

PROJECT_NAME = "Proyecto 2 - Conversion de Visitantes Online"
API_VERSION = "1.0.0-pb19"

app = FastAPI(
    title="Sprint 6 PB-19 API",
    description="API REST para servir el modelo final de conversion de visitantes online.",
    version=API_VERSION,
)


def log_event(event: str, **fields: Any) -> None:
    payload = {
        "event": event,
        "timestamp": time.time(),
        "api_version": API_VERSION,
        **fields,
    }
    LOGGER.info(json.dumps(payload, ensure_ascii=False, default=str))


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception as exc:
        log_event(
            "request_error",
            request_id=request_id,
            endpoint=request.url.path,
            method=request.method,
            status_code=500,
            latency_ms=round((time.perf_counter() - start) * 1000, 3),
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            error=str(exc),
        )
        raise

    latency_ms = round((time.perf_counter() - start) * 1000, 3)
    response.headers["X-Request-ID"] = request_id
    log_event(
        "request",
        request_id=request_id,
        endpoint=request.url.path,
        method=request.method,
        status_code=response.status_code,
        latency_ms=latency_ms,
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return response


@app.on_event("startup")
def startup_event() -> None:
    try:
        load_model()
        log_event(
            "startup",
            status_code=200,
            model_path=get_model_path(),
            model_version=get_model_version(),
            model_sha=get_model_sha(),
            preprocessor_path=get_preprocessor_path(),
        )
    except Exception as exc:
        log_event("startup_error", status_code=500, error=str(exc))
        raise


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    log_event(
        "validation_error",
        endpoint=request.url.path,
        method=request.method,
        status_code=400,
        error_count=len(exc.errors()),
    )
    return JSONResponse(status_code=400, content={"detail": exc.errors()})


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    start = time.perf_counter()
    response = HealthResponse(status="ok", service="sprint6-pb19-api")
    log_event(
        "health",
        endpoint="/health",
        method="GET",
        status_code=200,
        latency_ms=round((time.perf_counter() - start) * 1000, 3),
    )
    return response


@app.get("/version", response_model=VersionResponse)
def version() -> VersionResponse:
    start = time.perf_counter()
    try:
        model = load_model()
        threshold = get_threshold()
        model_sha = get_model_sha()
    except Exception as exc:
        log_event(
            "version_error",
            endpoint="/version",
            method="GET",
            status_code=500,
            latency_ms=round((time.perf_counter() - start) * 1000, 3),
            error=str(exc),
        )
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    response = VersionResponse(
        project=PROJECT_NAME,
        api_version=API_VERSION,
        model_version=get_model_version(),
        model_sha=model_sha,
        model_path=get_model_path(),
        preprocessor_path=get_preprocessor_path(),
        model_is_pipeline=model_is_pipeline(model),
        threshold=threshold,
    )
    log_event(
        "version",
        endpoint="/version",
        method="GET",
        status_code=200,
        latency_ms=round((time.perf_counter() - start) * 1000, 3),
        model_path=response.model_path,
        model_version=response.model_version,
        model_sha=response.model_sha,
        model_is_pipeline=response.model_is_pipeline,
        threshold=response.threshold,
    )
    return response


@app.post("/predict", response_model=PredictionResponse)
def predict(features: VisitorFeatures) -> PredictionResponse:
    start = time.perf_counter()
    try:
        prediction = predict_purchase(features)
        response = PredictionResponse(**prediction)
        log_event(
            "predict",
            endpoint="/predict",
            method="POST",
            status_code=200,
            latency_ms=round((time.perf_counter() - start) * 1000, 3),
            proba=response.purchase_probability,
            prediction=response.prediction,
            threshold=response.threshold,
            model_version=response.model_version,
            model_sha=response.model_sha,
        )
        return response
    except ValueError as exc:
        log_event(
            "predict_validation_error",
            endpoint="/predict",
            method="POST",
            status_code=400,
            latency_ms=round((time.perf_counter() - start) * 1000, 3),
            error=str(exc),
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        log_event(
            "predict_error",
            endpoint="/predict",
            method="POST",
            status_code=500,
            latency_ms=round((time.perf_counter() - start) * 1000, 3),
            error=str(exc),
        )
        raise HTTPException(status_code=500, detail=str(exc)) from exc
