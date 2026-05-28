# Resumen de valor de negocio

El dashboard ejecutivo incorpora una evaluacion economica de los modelos usando una matriz costo-beneficio configurable. Como el dataset no contiene monto real de compra, los valores en USD son estimaciones para comparar escenarios bajo los mismos supuestos.

## Matriz costo-beneficio

Valor del modelo =

`TP * beneficio_TP + FP * costo_FP + FN * costo_FN + TN * beneficio_TN`

- TP: comprador real detectado; representa una oportunidad aprovechada.
- FP: visitante que no compra pero recibe accion comercial; representa costo innecesario.
- FN: comprador real no detectado; representa oportunidad perdida.
- TN: no comprador correctamente ignorado; normalmente valor 0.

## Modelos comparados

- XGBoost tuneado: modelo final recomendado.
- LightGBM tuneado.
- Random Forest tuneado.
- Baselines del Sprint 3.
- Escenarios operativos: sin modelo, intervenir a todos y aleatorio con la misma cobertura.

## Insight principal

XGBoost se mantiene como modelo recomendado porque combina desempeno tecnico, valor economico estimado y compatibilidad con los artefactos preparados para Sprint 6. La decision final no depende solo del F1-score: tambien se evalua ROI, costo de falsos positivos, costo de falsos negativos y ganancia incremental contra baselines.

## Recomendacion

Usar el threshold economico sugerido en el dashboard y ajustar los supuestos con datos reales de margen, costo de campana y uplift observado antes de pasar a produccion.
