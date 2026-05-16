# QA & Stakeholder Feedback - Sprint 5

## Estado de Revision

Revision tecnica interna completada. Validacion formal con sponsor pendiente.

## Artefactos Revisados

| Artefacto | Estado | Observacion |
|---|---|---|
| `notebooks/13_ensembles.ipynb` | Revisado | Compara modelos sobre test real y agrega segmentacion. |
| `notebooks/14_evaluacion final del Test.ipynb` | Revisado | Define recomendacion por escenario. |
| `notebooks/15_business_value.ipynb` | Revisado | Ejecuta matriz costo-beneficio, thresholds y gain/lift. |
| `dashboard/app.py` | Revisado parcialmente | Compila correctamente; ejecucion local pendiente porque `streamlit` no esta instalado en el entorno actual. |
| `reports/final_report.md` | Revisado | Listo para convertir a PDF. |
| `handoff/` | Revisado | Contratos iniciales listos para Sprint 6. |

## Checklist QA

| Criterio | Estado |
|---|---|
| Notebooks principales parsean sin errores de sintaxis | OK |
| Notebook BA ejecutado end-to-end | OK |
| CSVs de business value generados | OK |
| Reporte ejecutivo disponible | OK |
| Preguntas de validacion sponsor documentadas | OK |
| Dashboard creado | OK |
| Dashboard ejecutado localmente | Pendiente por dependencia `streamlit` ausente |
| Costos/beneficios validados por sponsor | Pendiente |
| Thresholds aprobados por sponsor | Pendiente |

## Evidencia de Verificacion Local

Validaciones ejecutadas en la rama `feat/PB-18-sprint5-pm-ba-documentation`:

- `python -m json.tool` sobre `handoff/contracts/input_schema.json`.
- `python -m json.tool` sobre `handoff/contracts/output_schema.json`.
- `python -m json.tool` sobre `handoff/contracts/example_request.json`.
- `python -m json.tool` sobre `handoff/contracts/example_response.json`.
- `python -m py_compile dashboard/app.py`.
- Parseo con `nbformat` de `notebooks/13_ensembles.ipynb`, `notebooks/14_evaluacion final del Test.ipynb` y `notebooks/15_business_value.ipynb`.

Nota: `nbformat` reporta warnings de `Cell is missing an id field` en notebooks antiguos. No bloquea la lectura actual, pero conviene normalizar notebooks antes de Sprint 6.

## Feedback Tecnico

- La comparacion final usa test real desbalanceado, lo cual mejora la consistencia de la evaluacion.
- La estrategia por escenario es mas defendible que seleccionar un unico modelo.
- Los resultados economicos deben presentarse como sensibilidad, no como valor financiero final.
- La dependencia de `PageValues` debe revisarse antes de produccion.

## Feedback Pendiente del Sponsor

Preguntas pendientes:

1. Costo real de contactar usuario nuevo.
2. Costo real de contactar usuario recurrente.
3. Margen promedio por compra.
4. Penalizacion por falsos positivos.
5. Tolerancia a falsos negativos.
6. Canal real de activacion.
7. Disponibilidad operacional de `PageValues`.

## Decision QA

Sprint 5 queda tecnicamente listo para review. La decision de despliegue economico queda condicionada a validacion del sponsor.

## Recomendacion para Sprint 6

Avanzar con MVP en modo piloto:

- API con modelo XGBoost tuned y Random Forest disponibles.
- Threshold configurable.
- Monitoreo de precision, recall, tasa de contacto y conversion real.
- Registro de decisiones para recalibrar costos y thresholds.
- Instalar `streamlit` o agregarlo al entorno antes de la demo del dashboard.
