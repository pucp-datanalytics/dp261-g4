# QA Validation Checklist - Sprint 5

## Objetivo

Este checklist documenta la revision del rol QA & Stakeholder Reviewer para cerrar Sprint 5 y preparar el handoff a Sprint 6.

## Alcance Revisado

| Entregable | Archivo | Estado QA | Comentario |
|---|---|---|---|
| Business value | `notebooks/15_business_value.ipynb` | OK con observacion | Debe presentarse como simulacion basada en supuestos. |
| Comparacion final test | `models/final_test_model_comparison.csv` | OK | Usa test real desbalanceado. |
| Evaluacion por segmento | `models/final_test_by_visitor_type.csv` | OK | Soporta estrategia por `VisitorType`. |
| Recomendaciones economicas | `models/business_value_recommendations.csv` | OK con condicion | Requiere validacion sponsor para costos y thresholds. |
| Dashboard | `dashboard/app.py` | Pendiente operativo | Compila, pero faltan dependencias para ejecucion local. |
| Reporte final | `reports/final_report.md` | OK | Listo para revision y conversion a PDF. |
| Feedback QA | `reports/feedback.md` | OK | Incluye riesgos, pendientes y decision QA. |
| Handoff | `handoff/README_handoff.md` | OK | Define artefactos para Sprint 6. |
| Contratos API | `handoff/contracts/` | OK | Incluye input, output y ejemplos. |
| KPIs/SLA | `handoff/KPIs_target_SLA.md` | OK | Define targets iniciales y Go/No-Go. |

## Validaciones Minimas

| Control QA | Estado | Evidencia |
|---|---|---|
| Repositorio en rama de trabajo separada | OK | `feat/QA-sprint5-rol5` |
| Reporte final disponible | OK | `reports/final_report.md` |
| Handoff disponible | OK | `handoff/` |
| Dashboard creado | OK | `dashboard/app.py` |
| Dashboard compila | OK | `python -m py_compile dashboard/app.py` |
| Dashboard ejecutado localmente | Pendiente | Faltan `streamlit`, `plotly` y `shap` en entorno actual. |
| JSON contracts validos | Pendiente de revalidar antes del PR | Usar `python -m json.tool`. |
| Sponsor valida costos | Pendiente | Requiere reunion o respuesta formal. |
| Sponsor aprueba thresholds | Pendiente | No bloquear review tecnica, pero si despliegue economico. |

## Riesgos QA

| Riesgo | Impacto | Recomendacion |
|---|---|---|
| Costos TP/FP/FN no validados | Puede cambiar el threshold optimo. | Presentar resultados como sensibilidad, no como valor final. |
| `PageValues` no disponible en scoring real | Puede invalidar el modelo para produccion temprana. | Confirmar disponibilidad o preparar modelo alternativo. |
| Dependencias dashboard ausentes | Puede fallar la demo. | Instalar/agregar `streamlit`, `plotly` y `shap` antes de presentar. |
| Diferencia entre input crudo y procesado | Puede generar errores en API/dashboard. | Definir si Sprint 6 recibira datos crudos + pipeline o features procesadas. |
| Thresholds economicos muy bajos | Aumentan falsos positivos. | Usarlos solo si el costo FP es realmente bajo. |

## Decision QA

Sprint 5 esta listo para revision tecnica y presentacion de resultados, pero no para despliegue economico automatico.

La recomendacion QA es avanzar a Sprint 6 como MVP piloto condicionado a:

- validacion de costos y margen con sponsor,
- confirmacion de disponibilidad de `PageValues`,
- instalacion de dependencias del dashboard,
- threshold configurable,
- trazabilidad de predicciones,
- monitoreo semanal de precision, recall, tasa de contacto y conversion real.

## Mensaje para Stakeholder

El modelo muestra valor para priorizar usuarios y campanas, especialmente usando ranking. Sin embargo, la decision final de contacto debe validarse con informacion economica real. El Sprint 6 debe iniciar como piloto controlado, no como automatizacion definitiva.
