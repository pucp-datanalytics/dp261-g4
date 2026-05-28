# PB-19 Handoff - Rol 2 API Engineer

Este archivo resume los insumos que PB-19 entrega a los demas roles del Sprint 6.

## Estado del rol 2

- API FastAPI disponible en `api/main.py`.
- Endpoints requeridos por el PDF: `/health`, `/version`, `/predict`.
- Endpoint adicional para PB-21: `/predict_batch`, pensado para datasets cargados desde el dashboard.
- Schemas Pydantic en `api/schemas.py`.
- Logica de carga y prediccion en `api/predict.py`.
- Docker reproducible en `api/Dockerfile`.
- Dependencias en `api/requirements.txt`.
- Smoke test local en `api/smoke_test.py`.
- Seguridad opcional con `API_KEY` via variable de entorno y header `x-api-key`.

## Artefactos usados

| PDF Sprint 6 | Repo actual |
|---|---|
| `handoff/model/final_model.pkl` | `handoff/model/c_final_model.pkl` |
| `handoff/model/preproc_pipeline.pkl` | `handoff/model/c_preprocessing_pipeline.pkl` |
| `handoff/contracts/input_schema.json` | `handoff/contracts/c_input_schema.json` |
| `handoff/contracts/output_schema.json` | `handoff/contracts/c_output_schema.json` |
| `handoff/contracts/example_request.json` | `handoff/contracts/c_example_request.json` |

## Entrega a Rol 3 - Cloud / DevOps

- Usar `api/Dockerfile` para construir la imagen.
- Configurar variables `MODEL_PATH`, `PREPROCESSOR_PATH`, `THRESHOLD` y `MODEL_VERSION`.
- Configurar `API_KEY` si el endpoint queda expuesto publicamente.
- Usar `/health` como health check.
- Usar `/version` para diagnosticar version de API/modelo.
- Capturar logs JSON de stdout en CloudWatch.

## Entrega a Rol 4 - Integration Engineer

- Usar `handoff/contracts/api_contract.md`.
- Configurar `API_URL` con la URL que entregue Rol 3.
- Configurar `API_KEY` si Rol 3 protege la API.
- Enviar payload compatible con `handoff/contracts/c_example_request.json`.
- Para datasets cargados, enviar payload compatible con `handoff/contracts/c_example_batch_request.json`.
- Esperar respuesta compatible con `handoff/contracts/c_output_schema.json`.
- Manejar errores 400, 401, 500, timeouts y API no disponible.

## Entrega a Rol 5 - SRE / Monitoring

La API emite logs JSON con campos listos para CloudWatch:

- `event`
- `request_id`
- `endpoint`
- `method`
- `status_code`
- `latency_ms`
- `proba`
- `prediction`
- `threshold`
- `model_version`
- `model_sha`
- `error`

Con estos campos se pueden calcular:

- latencia p50/p95/p99 con `latency_ms`;
- throughput contando `event="request"` por ventana de tiempo;
- error rate 5xx filtrando `status_code >= 500`;
- distribucion de probabilidades con `proba`;
- trazabilidad de incidentes con `request_id`, `model_version` y `model_sha`.

## Validacion local minima

```powershell
python -m pip install -r api/requirements.txt
python api/smoke_test.py
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
curl http://localhost:8000/health
curl http://localhost:8000/version
curl -X POST "http://localhost:8000/predict" -H "Content-Type: application/json" --data-binary "@handoff/contracts/c_example_request.json"
curl -X POST "http://localhost:8000/predict_batch" -H "Content-Type: application/json" --data-binary "@handoff/contracts/c_example_batch_request.json"
```

## Validacion Docker minima

```powershell
docker build -t sprint6-api -f api/Dockerfile .
docker run --rm -p 8000:8000 sprint6-api
curl http://localhost:8000/health
curl http://localhost:8000/version
curl -X POST "http://localhost:8000/predict" -H "Content-Type: application/json" --data-binary "@handoff/contracts/c_example_request.json"
curl -X POST "http://localhost:8000/predict_batch" -H "Content-Type: application/json" --data-binary "@handoff/contracts/c_example_batch_request.json"
```
