# Handoff para Sprint 6

Sprint 6 ya cuenta con la API PB-19, despliegue MVP PB-20 con Docker + EC2 y la integracion PB-21 del dashboard via REST.

## Artefactos listos

- `models/c_final_model.pkl`
- `models/c_best_model.pkl`
- `models/c_preproc.pkl`
- `models/c_preprocessing_pipeline.pkl`
- `models/c_metrics_summary.csv`
- `models/c_validation_test_comparison.csv`
- `src/c_predict.py`
- `handoff/contracts/c_input_schema.json`
- `handoff/contracts/c_output_schema.json`
- `handoff/contracts/c_example_request.json`
- `handoff/contracts/c_example_response.json`
- `api/` con endpoints `/health`, `/version` y `/predict`
- `Dockerfile` para publicar el dashboard Streamlit en el puerto `8080`
- `.github/workflows/cd.yml` para build, push a ECR y deploy en EC2

## Trabajo futuro

1. Confirmar el endpoint final de la API desplegada y guardarlo como secreto `API_URL`.
2. Ejecutar smoke tests contra `/health`, `/version` y `/predict`.
3. Validar el dashboard desplegado en EC2 consumiendo `POST {API_URL}/predict`.
4. Agregar logs estructurados, alertas y monitoreo de drift.

## Fuera de alcance actual

- No se configuran secretos reales ni credenciales.
- No se publica el valor real de `EC2_HOST`, llaves ni tokens.
- No se implementa monitoreo productivo en CloudWatch desde este entregable.
