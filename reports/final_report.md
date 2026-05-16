# Sprint 5 Final Report

## 1. Resumen Ejecutivo

El Sprint 5 evaluo el valor de negocio de los modelos finales del Sprint 4. La conclusion principal es que no conviene desplegar un unico modelo y threshold para todos los usuarios. La estrategia recomendada es segmentada:

- **XGBoost tuned** para ranking global y campanas conservadoras.
- **XGBoost** para usuarios nuevos, donde se busca mayor precision.
- **Random Forest** o una politica de bajo threshold para maxima captura y usuarios recurrentes.

Los resultados economicos son provisionales porque el dataset contiene `Revenue` binario, no monto real de compra. Los costos y beneficios usados en la matriz costo-beneficio deben validarse con el sponsor antes del despliegue en Sprint 6.

## 2. Contexto de Negocio

El problema consiste en predecir si una sesion de e-commerce terminara en compra (`Revenue = True`). La clase positiva es minoritaria: en el test real, solo **15.65%** de sesiones terminaron en compra.

La decision de negocio no es solo "predecir bien", sino decidir a quien contactar, con que umbral y bajo que costo esperado.

## 3. Datos y Preparacion

Los modelos se evaluaron sobre:

- `data/processed/test_processed.csv`
- 2,441 sesiones en test.
- 382 compradores reales.
- 2,059 no compradores.

Se uso el test real desbalanceado para evitar conclusiones infladas por datasets balanceados.

## 4. Modelos Evaluados

Modelos comparados:

- Random Forest final (`models/best_tuned_model.pkl`)
- XGBoost base
- XGBoost tuned
- LightGBM base
- LightGBM tuned

Con threshold 0.50:

| Modelo | Precision | Recall | F1 | ROC-AUC | PR-AUC |
|---|---:|---:|---:|---:|---:|
| Random Forest | 0.6552 | 0.6963 | 0.6751 | 0.9210 | 0.6940 |
| XGBoost tuned | 0.6877 | 0.6571 | 0.6720 | 0.9319 | 0.7438 |
| LightGBM base | 0.6802 | 0.6571 | 0.6684 | 0.9317 | 0.7361 |

Interpretacion:

- Random Forest tiene mejor F1 global con threshold 0.50.
- XGBoost tuned tiene mejor PR-AUC y ROC-AUC, por lo que es mejor para ranking.
- LightGBM es competitivo, pero no lidera los escenarios clave.

## 5. Valor de Negocio

El notebook `notebooks/15_business_value.ipynb` construyo la matriz costo-beneficio y busco thresholds optimos bajo supuestos iniciales.

Supuestos usados:

| Escenario | TP | FP | FN | TN |
|---|---:|---:|---:|---:|
| Global conservador | 100 | -20 | -80 | 0 |
| Maxima captura | 100 | -10 | -120 | 0 |
| Usuarios nuevos | 120 | -35 | -90 | 0 |
| Usuarios recurrentes | 80 | -5 | -70 | 0 |

Resultados principales:

| Escenario | Modelo | Threshold | Valor incremental anual estimado |
|---|---|---:|---:|
| Global conservador | XGBoost base | 0.07 | 272,800 |
| Maxima captura | XGBoost base | 0.06 | 370,200 |
| Usuarios nuevos | XGBoost base | 0.06 | 85,050 |
| Usuarios recurrentes | LightGBM base | 0.05 | 191,250 |

Estos valores son simulaciones. Deben considerarse rangos de sensibilidad hasta que el sponsor confirme costos reales y margen por compra.

## 6. Gain/Lift

Con XGBoost tuned como ranking:

| Porcentaje contactado | Compradores capturados | Lift |
|---:|---:|---:|
| 10% | 49.2% | 4.92x |
| 20% | 76.7% | 3.84x |
| 30% | 89.3% | 2.98x |
| 50% | 98.4% | 1.97x |

Esto sugiere que el modelo es util para priorizar campanas con presupuesto limitado.

## 7. Recomendaciones

1. Usar **XGBoost tuned** para ranking global y campanas conservadoras.
2. Usar una politica conservadora para `New_Visitor`, priorizando precision.
3. Usar una politica mas agresiva para `Returning_Visitor` solo si el costo de contacto es bajo.
4. Validar costos reales con sponsor antes de fijar thresholds.
5. Incluir en Sprint 6 un mecanismo para cambiar thresholds sin reentrenar el modelo.

## 8. Riesgos y Limitaciones

- `Revenue` es binario y no representa monto real.
- Los costos de TP, FP y FN aun no estan validados.
- `PageValues` puede ser una variable sensible si no esta disponible antes de la decision operativa.
- El desempeno puede cambiar si cambia la distribucion de trafico.
- La estrategia segmentada requiere que `VisitorType` este disponible en produccion.

## 9. Decision de Despliegue

La recomendacion es avanzar a Sprint 6 con un MVP condicionado:

- Dashboard y API deben permitir seleccionar modelo y threshold.
- El sponsor debe validar costos antes de activar campanas reales.
- La primera version deberia operar en modo monitoreo o piloto, no automatizacion completa.
- El entorno de Sprint 6 debe incluir la dependencia de dashboard (`streamlit`) antes de la demo local.

## 10. Anexos

Artefactos generados:

- `notebooks/15_business_value.ipynb`
- `dashboard/app.py`
- `models/business_value_recommendations.csv`
- `models/business_value_threshold_search.csv`
- `models/business_value_gain_lift_curve.csv`
- `reports/executive_summary_sprint5.md`
- `reports/sponsor_validation_questions.md`
- `handoff/README_handoff.md`
- `handoff/KPIs_target_SLA.md`
- `handoff/contracts/`
