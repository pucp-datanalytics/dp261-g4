# QA & Stakeholder Feedback - Sprint 5

## Estado de Revision

Revision tecnica interna completada desde el rol QA & Stakeholder Reviewer. La validacion formal con sponsor sigue pendiente y condiciona cualquier decision economica de despliegue.

El objetivo de esta revision fue comprobar que los entregables del Sprint 5 sean consistentes con la fase Evaluation de CRISP-DM: valor de negocio, dashboard, reporte ejecutivo, feedback y handoff para Sprint 6.

## Artefactos Revisados

| Artefacto | Estado | Observacion |
|---|---|---|
| `notebooks/13_ensembles.ipynb` | Revisado | Compara modelos sobre test real y agrega segmentacion. |
| `notebooks/14_evaluacion final del Test.ipynb` | Revisado | Define recomendacion por escenario. |
| `notebooks/15_business_value.ipynb` | Revisado | Ejecuta matriz costo-beneficio, thresholds y gain/lift. |
| `dashboard/app.py` | Revisado parcialmente | Compila correctamente; ejecucion local pendiente porque `streamlit` no esta instalado en el entorno actual. |
| `reports/final_report.md` | Revisado | Listo para convertir a PDF. |
| `handoff/` | Revisado | Contratos iniciales listos para Sprint 6. |

## Matriz de Validacion QA

| Dimension | Resultado | Evidencia | Observacion QA |
|---|---|---|---|
| Alineacion Sprint 5 | OK | `reports/final_report.md`, `notebooks/15_business_value.ipynb` | El sprint se enfoca en evaluacion, valor de negocio y decision de despliegue. |
| Metricas en test real | OK | `models/final_test_model_comparison.csv` | Se usa test desbalanceado, evitando conclusiones infladas por datos balanceados. |
| Valor de negocio | OK con condicion | `models/business_value_recommendations.csv` | Los valores dependen de supuestos TP/FP/FN no validados por sponsor. |
| Segmentacion | OK | `models/final_test_by_visitor_type.csv` | La estrategia por `VisitorType` es defendible, pero requiere disponibilidad en produccion. |
| Dashboard | Pendiente operativo | `dashboard/app.py` | El script compila, pero faltan dependencias del entorno para demo local. |
| Explicabilidad | Pendiente operativo | `dashboard/app.py` | SHAP esta implementado, pero la dependencia no esta instalada en el entorno actual. |
| Handoff Sprint 6 | OK | `handoff/README_handoff.md`, `handoff/contracts/` | Hay contratos iniciales, KPIs y riesgos documentados. |
| Decision sponsor | Pendiente | `reports/sponsor_validation_questions.md` | Faltan costos reales, margen, canal de contacto y aprobacion de thresholds. |

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
| Handoff tecnico documentado | OK |
| Criterios Go/No-Go definidos | OK |
| Riesgos operativos documentados | OK |

## Evidencia de Verificacion Local

Validaciones ejecutadas en la rama `feat/PB-18-sprint5-pm-ba-documentation`:

- `python -m json.tool` sobre `handoff/contracts/input_schema.json`.
- `python -m json.tool` sobre `handoff/contracts/output_schema.json`.
- `python -m json.tool` sobre `handoff/contracts/example_request.json`.
- `python -m json.tool` sobre `handoff/contracts/example_response.json`.
- `python -m py_compile dashboard/app.py`.
- Parseo con `nbformat` de `notebooks/13_ensembles.ipynb`, `notebooks/14_evaluacion final del Test.ipynb` y `notebooks/15_business_value.ipynb`.

Nota: `nbformat` reporta warnings de `Cell is missing an id field` en notebooks antiguos. No bloquea la lectura actual, pero conviene normalizar notebooks antes de Sprint 6.

## Observaciones QA Detalladas

1. Las metricas finales deben comunicarse desde test real. El mejor F1 a threshold 0.50 es Random Forest, pero XGBoost tuned tiene mejor ROC-AUC y PR-AUC, por lo que es mas fuerte como ranking para campanas.
2. Los thresholds economicos bajos son coherentes con los supuestos actuales porque se penaliza fuerte el falso negativo. Sin validacion de costos reales, no deben presentarse como thresholds finales de produccion.
3. El dashboard implementa KPIs, matriz de confusion, ROC y SHAP, pero depende de `streamlit`, `plotly` y `shap`. Estas dependencias deben agregarse al entorno o instalarse antes de la demo.
4. El contrato de API usa features procesadas. El dashboard, en cambio, parte de datos crudos y reconstruye features. Para Sprint 6 debe decidirse una unica fuente de verdad: input crudo con pipeline o input ya procesado.
5. `PageValues` debe validarse con negocio/operaciones. Si no esta disponible antes del scoring, se necesita un modelo alternativo sin esa variable o un scoring posterior a la sesion.

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

## Criterios de Aprobacion QA

Se considera que Sprint 5 esta listo para review si:

- El equipo presenta metricas sobre test real, no solo validacion cruzada.
- El reporte aclara que el valor economico es una simulacion.
- La recomendacion final es condicionada a validacion sponsor.
- El dashboard compila y se documentan dependencias pendientes.
- El handoff incluye contratos de entrada/salida, KPIs y riesgos.

No se considera listo para despliegue productivo si:

- No se validan costos TP/FP/FN con sponsor.
- No se confirma disponibilidad de `PageValues`.
- No se define si la decision usara threshold fijo o top-k.
- No se garantiza que API, dashboard y modelo usen las mismas features.

## Decision QA

Sprint 5 queda tecnicamente listo para review. La decision de despliegue economico queda condicionada a validacion del sponsor.

## Recomendacion para Sprint 6

Avanzar con MVP en modo piloto:

- API con modelo XGBoost tuned y Random Forest disponibles.
- Threshold configurable.
- Monitoreo de precision, recall, tasa de contacto y conversion real.
- Registro de decisiones para recalibrar costos y thresholds.
- Instalar `streamlit` o agregarlo al entorno antes de la demo del dashboard.
