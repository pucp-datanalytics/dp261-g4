# Handoff para Sprint 6

Sprint 6 ya cuenta con la API PB-19 y la integracion PB-21 del dashboard via REST.

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

1. Desplegar la API en AWS y entregar el endpoint final para `API_URL`.
2. Ejecutar smoke tests contra `/health`, `/version` y `/predict`.
3. Validar el dashboard con el endpoint desplegado.
4. Agregar secretos fuera del repositorio, logs estructurados, alertas y monitoreo de drift.

## Fuera de alcance actual

- No se crea infraestructura AWS desde este entregable.
- No se configuran secretos reales ni credenciales.
- No se configura CI/CD productivo.
- No se despliega nada.
