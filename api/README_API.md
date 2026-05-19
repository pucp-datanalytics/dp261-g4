# PB-19 - API REST del modelo final

Esta carpeta implementa PB-19 del Sprint 6: empaquetar el modelo final como una API REST con FastAPI y Docker.

La rama de trabajo es `feat/PB-19-api`, creada desde `feat/PB-review3`, que funciona como base limpia del proyecto hasta Sprint 5.

## Alineacion con Sprint 6

El PDF de Sprint 6 pide que PB-19 entregue:

- servicio FastAPI/Flask con `/health`, `/predict` y `/version`;
- schemas de entrada/salida con Pydantic segun `handoff/contracts/`;
- carga del modelo y pipeline una sola vez al iniciar el proceso;
- manejo de errores con codigos HTTP claros;
- Dockerfile con imagen `python:3.10-slim`;
- pruebas locales con `docker build`, `docker run` y `curl`.

Esta implementacion usa el modelo final real de Sprint 4/5 y los contratos de `handoff/contracts/`.

## Estructura

```text
api/
  main.py
  schemas.py
  predict.py
  requirements.txt
  Dockerfile
  README_API.md
```

## Artefactos usados

- Modelo: `handoff/model/c_final_model.pkl`
- Pipeline/preprocesador disponible: `handoff/model/c_preprocessing_pipeline.pkl`
- Request ejemplo: `handoff/contracts/c_example_request.json`
- Output schema: `handoff/contracts/c_output_schema.json`

Nota tecnica: `c_final_model.pkl` ya es un pipeline completo con preprocesador interno. Por eso la API no aplica doble preprocesamiento; solo normaliza tipos, crea las features derivadas igual que entrenamiento y llama al modelo final.

## Variables de entorno

| Variable | Default | Uso |
|---|---|---|
| `MODEL_PATH` | `handoff/model/c_final_model.pkl` | Ruta del modelo final |
| `PREPROCESSOR_PATH` | `handoff/model/c_preprocessing_pipeline.pkl` | Ruta informativa/opcional del preprocesador |
| `THRESHOLD` | `0.5` | Umbral para convertir probabilidad en clase |

## Ejecucion local en Windows PowerShell

Instalar dependencias:

```powershell
python -m pip install -r api/requirements.txt
```

Levantar la API:

```powershell
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Probar `/health`:

```powershell
curl http://localhost:8000/health
```

Resultado esperado:

```json
{"status":"ok","service":"sprint6-pb19-api"}
```

Probar `/version`:

```powershell
curl http://localhost:8000/version
```

Probar `/predict`:

```powershell
curl -X POST "http://localhost:8000/predict" -H "Content-Type: application/json" --data-binary "@handoff/contracts/c_example_request.json"
```

Resultado esperado:

```json
{
  "purchase_probability": 0.0,
  "prediction": 0,
  "threshold": 0.5,
  "model_path": "handoff/model/c_final_model.pkl"
}
```

El valor exacto de `purchase_probability` puede variar si cambia el modelo o el threshold.

## Docker

Construir imagen:

```powershell
docker build -t sprint6-api -f api/Dockerfile .
```

Correr contenedor:

```powershell
docker run --rm -p 8000:8000 sprint6-api
```

Probar contenedor:

```powershell
curl http://localhost:8000/health
curl http://localhost:8000/version
curl -X POST "http://localhost:8000/predict" -H "Content-Type: application/json" --data-binary "@handoff/contracts/c_example_request.json"
```

## Entrega para PB-20 AWS

PB-20 debe tomar:

- `api/Dockerfile`;
- `api/requirements.txt`;
- codigo `api/`;
- artefactos `handoff/model/`;
- contratos `handoff/contracts/`;
- variables `MODEL_PATH`, `PREPROCESSOR_PATH`, `THRESHOLD`;
- endpoint `/health` para health checks de AWS.

Para AWS, se recomienda mantener secretos fuera del repo y definir variables sensibles en AWS Secrets Manager, Parameter Store o GitHub Secrets.

## Entrega para PB-21 Dashboard

PB-21 debe usar:

- URL base de la API via variable `API_URL`;
- `POST /predict` con payload compatible con `handoff/contracts/c_example_request.json`;
- response compatible con `handoff/contracts/c_output_schema.json`;
- manejo de errores de red, timeouts y respuestas 4xx/5xx.

## Riesgos y supuestos

- El modelo final es un pipeline completo; aplicar el preprocesador aparte duplicaria transformaciones.
- El repositorio usa prefijo `c_` en artefactos de reconstruccion. La API referencia esos nombres reales y funcionales.
- Docker copia `src/` porque el pickle requiere clases/funciones importables del proyecto.
- No se incluyen credenciales, llaves, tokens ni archivos `.pem`.
