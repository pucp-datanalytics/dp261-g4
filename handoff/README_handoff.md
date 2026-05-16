# Sprint 6 Handoff

## Objetivo

Este paquete define los artefactos necesarios para iniciar Sprint 6 (Deployment MVP) sin ambiguedad sobre modelos, entradas, salidas y politicas de decision.

## Artefactos de Modelo

Los modelos permanecen versionados en `models/`:

- `models/tuned_xgboost.pkl`: recomendado para ranking global conservador.
- `models/best_tuned_model.pkl`: Random Forest, util para maxima captura.
- `models/tuned_lightgbm.pkl`: benchmark competitivo.
- `models/preprocessing_pipeline.pkl`: pipeline de preprocesamiento versionado por DVC.

La carpeta `handoff/model/` se deja como punto de montaje para copiar artefactos si Sprint 6 requiere empaquetado separado.

## Politicas Recomendadas

| Escenario | Modelo | Threshold inicial | Estado |
|---|---|---:|---|
| Global conservador | XGBoost tuned | 0.50 | Recomendado para piloto |
| Usuarios nuevos | XGBoost | 0.50 | Recomendado para contacto caro |
| Maxima captura | Random Forest | 0.25 | Requiere validar costo FP |
| Usuarios recurrentes | Random Forest / threshold bajo | 0.25 | Requiere validar costo FP |

Los thresholds economicos optimos del notebook 15 son simulaciones y deben validarse con sponsor antes de automatizar campanas reales.

## Contratos

Archivos en `handoff/contracts/`:

- `input_schema.json`: esquema de entrada esperado por la API.
- `output_schema.json`: esquema de respuesta.
- `example_request.json`: ejemplo de request procesado.
- `example_response.json`: ejemplo de response.

## Como Usar en Sprint 6

1. Crear API con FastAPI o Flask.
2. Cargar modelo seleccionado desde `models/`.
3. Validar input contra `handoff/contracts/input_schema.json`.
4. Calcular `probability_revenue`.
5. Aplicar threshold configurable.
6. Devolver output compatible con `output_schema.json`.
7. Registrar predicciones y resultados reales para monitoreo.

## Riesgos para Deployment

- Confirmar si `PageValues` esta disponible al momento de scoring.
- Confirmar costos reales de TP, FP y FN.
- Evitar hardcodear un unico threshold.
- Monitorear drift de conversion y distribucion de visitantes.
- Validar que el dashboard y API usen las mismas features.

## Decision de Handoff

El paquete esta listo para MVP tecnico. La activacion economica queda condicionada a validacion del sponsor.
