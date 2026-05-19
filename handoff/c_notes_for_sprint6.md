# Handoff para Sprint 6

Sprint 6 no esta implementado en esta etapa.

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

## Trabajo futuro

1. Crear API FastAPI con `/health`, `/predict` y `/version`.
2. Cargar el modelo una sola vez al iniciar el servicio.
3. Validar entradas con los contratos de `handoff/contracts/`.
4. Crear Dockerfile y smoke tests locales.
5. Elegir arquitectura AWS despues de confirmar tamano del modelo, costos y requisitos de latencia.
6. Agregar secretos fuera del repositorio, logs estructurados, alertas y monitoreo de drift.

## Fuera de alcance actual

- No se crea carpeta `api/`.
- No se crea Dockerfile final.
- No se crea infraestructura AWS.
- No se configura CI/CD.
- No se despliega nada.
