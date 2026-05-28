# Contrato API PB-19

Base local:

```text
http://localhost:8000
```

Variable para PB-21:

```text
API_URL=http://localhost:8000
API_KEY=<solo si PB-20 habilita autenticacion>
```

En AWS, PB-20 debera reemplazar este valor por el endpoint publico/privado desplegado.
Si PB-20 define `API_KEY`, el cliente debe enviarla en el header `x-api-key`.

## GET /health

Verifica que la API esta viva.

```powershell
curl.exe http://localhost:8000/health
```

Respuesta esperada:

```json
{
  "status": "ok",
  "service": "sprint6-pb19-api"
}
```

## GET /version

Devuelve informacion de version, modelo y threshold.

```powershell
curl.exe http://localhost:8000/version
```

Respuesta esperada:

```json
{
  "project": "Proyecto 2 - Conversion de Visitantes Online",
  "api_version": "1.0.0-pb19",
  "model_version": "c_final_model",
  "model_sha": "abc123def456",
  "model_path": "handoff/model/c_final_model.pkl",
  "preprocessor_path": "handoff/model/c_preprocessing_pipeline.pkl",
  "model_is_pipeline": true,
  "threshold": 0.5
}
```

## POST /predict

Recibe las variables de una sesion online y devuelve probabilidad de compra y clase predicha.

```powershell
curl.exe -X POST "http://localhost:8000/predict" -H "Content-Type: application/json" --data-binary "@handoff/contracts/c_example_request.json"
```

Con API key:

```powershell
curl.exe -X POST "http://localhost:8000/predict" -H "Content-Type: application/json" -H "x-api-key: <API_KEY>" --data-binary "@handoff/contracts/c_example_request.json"
```

Request esperado:

```json
{
  "Administrative": 0,
  "Administrative_Duration": 0.0,
  "Informational": 0,
  "Informational_Duration": 0.0,
  "ProductRelated": 1,
  "ProductRelated_Duration": 0.0,
  "BounceRates": 0.2,
  "ExitRates": 0.2,
  "PageValues": 0.0,
  "SpecialDay": 0.0,
  "Month": "Feb",
  "OperatingSystems": 1,
  "Browser": 1,
  "Region": 1,
  "TrafficType": 1,
  "VisitorType": "Returning_Visitor",
  "Weekend": false
}
```

Response esperado:

```json
{
  "purchase_probability": 0.12,
  "prediction": 0,
  "threshold": 0.5,
  "model_path": "handoff/model/c_final_model.pkl",
  "model_version": "c_final_model",
  "model_sha": "abc123def456"
}
```

El valor exacto de `purchase_probability` depende del modelo final y del threshold configurado.

## Codigos de error

| Codigo | Caso |
|---|---|
| 400 | JSON invalido, columnas faltantes, tipos invalidos o variables extra no permitidas |
| 401 | API key faltante o invalida cuando `API_KEY` esta configurada en el servidor |
| 500 | Error cargando modelo, error inesperado de prediccion o configuracion invalida |

## POST /predict_batch

Permite que PB-21 valide datasets cargados desde el dashboard sin hacer una llamada manual por fila. El limite por request es 500 registros.

```powershell
curl.exe -X POST "http://localhost:8000/predict_batch" -H "Content-Type: application/json" --data-binary "@handoff/contracts/c_example_batch_request.json"
```

Request esperado:

```json
{
  "records": [
    {
      "Administrative": 0,
      "Administrative_Duration": 0.0,
      "Informational": 0,
      "Informational_Duration": 0.0,
      "ProductRelated": 1,
      "ProductRelated_Duration": 0.0,
      "BounceRates": 0.2,
      "ExitRates": 0.2,
      "PageValues": 0.0,
      "SpecialDay": 0.0,
      "Month": "Feb",
      "OperatingSystems": 1,
      "Browser": 1,
      "Region": 1,
      "TrafficType": 1,
      "VisitorType": "Returning_Visitor",
      "Weekend": false
    }
  ]
}
```

Response esperado:

```json
{
  "records": [
    {
      "row_id": 0,
      "purchase_probability": 0.12,
      "prediction": 0,
      "threshold": 0.5,
      "model_path": "handoff/model/c_final_model.pkl",
      "model_version": "c_final_model",
      "model_sha": "abc123def456"
    }
  ],
  "count": 1
}
```

## Logs estructurados para monitoring

La API escribe logs JSON por `stdout`. AWS/Docker/CloudWatch puede capturarlos sin cambiar el contrato de respuesta.

Ejemplo de log exitoso de `/predict`:

```json
{
  "event": "predict",
  "timestamp": 1779497501.08,
  "endpoint": "/predict",
  "method": "POST",
  "status_code": 200,
  "latency_ms": 108.451,
  "proba": 0.014604109339416027,
  "prediction": 0,
  "threshold": 0.5,
  "model_version": "c_final_model",
  "model_sha": "abc123def456"
}
```

Campos para Rol 5:

- `latency_ms`: base para p50, p95 y p99.
- `event`: base para throughput por tipo de evento.
- `status_code`: base para error rate 4xx/5xx.
- `proba`: base para distribucion de probabilidades y monitoreo de drift.
- `prediction`: base para conteo de predicciones positivas/negativas.
- `request_id`: trazabilidad de una llamada especifica.
- `model_version` y `model_sha`: versionado para debugging y rollback.

La API tambien emite eventos `request` por cada endpoint. Rol 5 puede calcular throughput contando logs con
`event="request"` agrupados por minuto y filtrar error rate con `status_code >= 500`.

## Entrega para PB-20

PB-20 debe tomar:

- `api/Dockerfile`;
- `api/requirements.txt`;
- codigo de `api/`;
- artefactos de `handoff/model/`;
- endpoint `/health` para health checks;
- variables `MODEL_PATH`, `PREPROCESSOR_PATH` y `THRESHOLD`;
- variable opcional `API_KEY` si el endpoint se expone publicamente;
- este contrato para smoke tests en AWS.

## Entrega para PB-21

PB-21 debe usar:

- `API_URL` como variable de entorno;
- `API_KEY` como variable de entorno solo si PB-20 protege la API;
- `POST {API_URL}/predict`;
- `POST {API_URL}/predict_batch` para datasets cargados desde el dashboard;
- payload compatible con `handoff/contracts/c_example_request.json`;
- respuesta compatible con `handoff/contracts/c_output_schema.json`;
- manejo de timeouts, errores 400/500 y API no disponible.
