# Sprint 5 - PM Plan

## Objetivo del Sprint

Evaluar el valor de negocio de la estrategia de modelos validada en Sprint 4, construir los insumos para dashboard/reporte y preparar la decision de despliegue para Sprint 6.

## Alcance

Sprint 5 cubre la fase Evaluation de CRISP-DM:

- PB-16: Evaluar Business Value del modelo seleccionado.
- PB-17: Construir dashboard interactivo de resultados.
- PB-18: Documentar hallazgos y recomendaciones de negocio.

Este sprint no entrena modelos nuevos. Usa los artefactos finales de Sprint 4:

- `notebooks/13_ensembles.ipynb`
- `notebooks/14_evaluacion final del Test.ipynb`
- `models/final_test_model_comparison.csv`
- `models/final_test_by_visitor_type.csv`
- `models/best_tuned_model.pkl`
- `models/tuned_xgboost.pkl`
- `models/tuned_lightgbm.pkl`

## Issues Sugeridos

| Issue | Rol | Responsable | Descripcion | Entregable |
|---|---|---|---|---|
| PB-16a | BA | Business Analyst | Construir matriz costo-beneficio por modelo, threshold y segmento. | `notebooks/15_business_value.ipynb` |
| PB-16b | BA | Business Analyst | Identificar umbral optimo y estimar impacto economico anual. | `notebooks/15_business_value.ipynb` |
| PB-17a | DD | Dashboard Developer | Definir layout, KPIs y tabla de predicciones. | `dashboard/app.py` |
| PB-17b | DD | Dashboard Developer | Integrar explicabilidad y visualizaciones principales. | `dashboard/app.py` |
| PB-18 | DL | Documentation Lead | Redactar reporte ejecutivo, riesgos y recomendaciones. | `reports/final_report.pdf` o `reports/final_report.md` |
| QA-S5 | QA | QA Reviewer | Validar notebook, dashboard, reporte y handoff a Sprint 6. | `handoff/` + `reports/feedback.md` |

## Flujo Kanban

Cada issue debe moverse por:

1. To Do
2. In Progress
3. In Review
4. Done

Reglas de gestion:

- Una rama por issue: `feat/PB-16`, `feat/PB-17`, `feat/PB-18`, `feat/QA-sprint5`.
- Pull Request obligatorio para cada entregable.
- Revisor cruzado asignado antes de mover a In Review.
- El PM valida que el entregable tenga evidencia reproducible antes de mover a Done.

## Dependencias

| Orden | Actividad | Depende de |
|---:|---|---|
| 1 | PM crea issues, roles y tablero Sprint 5 | Cierre Sprint 4 |
| 2 | BA calcula Business Value y umbral optimo | Resultados finales Sprint 4 |
| 3 | Dashboard Developer construye KPIs y simulador | Inputs del BA |
| 4 | Documentation Lead redacta reporte ejecutivo | Inputs de BA y dashboard |
| 5 | QA valida y arma handoff | Reporte + dashboard completos |

## Asignacion de Roles

| Rol | Responsabilidad principal |
|---|---|
| Project Manager | Coordinar tablero, dependencias, revisiones y Sprint Review. |
| Business Analyst | Traducir metricas tecnicas a impacto economico y umbral de negocio. |
| Dashboard Developer | Construir dashboard interactivo con KPIs, predicciones y explicabilidad. |
| Documentation Lead | Documentar hallazgos, riesgos y recomendacion de despliegue. |
| QA & Stakeholder Reviewer | Validar calidad, feedback y paquete handoff para Sprint 6. |

## Agenda Sprint Review

1. Contexto: objetivo de negocio y problema de conversion.
2. Recap Sprint 4: modelos validados y resultado tecnico.
3. Business Value: matriz costo-beneficio, umbral optimo e impacto anual.
4. Segmentacion: nuevos vs recurrentes y politica recomendada.
5. Dashboard: demo de KPIs y simulador.
6. Riesgos: supuestos, PageValues, drift y costos no confirmados.
7. Decision: desplegar MVP, iterar o requerir datos adicionales.
8. Handoff Sprint 6: modelo, contratos, dashboard y SLAs.

## Definition of Done

| Criterio | Estado |
|---|---|
| Issues PB-16, PB-17, PB-18 creados y asignados | Pendiente en GitHub |
| Roles y revisores cruzados definidos | Pendiente en GitHub |
| `15_business_value.ipynb` ejecuta de inicio a fin | En progreso |
| Umbral optimo justificado con valor esperado | En progreso |
| Dashboard ejecutable localmente | Pendiente |
| Reporte ejecutivo con resumen de 1 pagina | Pendiente |
| Riesgos y supuestos documentados | En progreso |
| Paquete handoff listo para Sprint 6 | Pendiente |

## Riesgos de Gestion

- Los costos de contacto y beneficio por compra son supuestos hasta ser validados con sponsor.
- Un unico umbral global puede no ser adecuado: los resultados sugieren politica por segmento.
- Si `PageValues` no esta disponible al momento de decision, puede requerirse una variante de modelo sin esa variable.
- Los modelos deben evaluarse con test real desbalanceado; las metricas CV balanceadas no deben usarse como conclusion final.

## Decision PM Recomendada

Continuar Sprint 5 con una estrategia por escenario:

- XGBoost tuned para ranking global y campanas conservadoras.
- XGBoost con threshold alto para usuarios nuevos.
- Random Forest con threshold bajo para usuarios recurrentes o maxima captura.
- Validar costos reales con sponsor antes de convertir esta politica en despliegue Sprint 6.
