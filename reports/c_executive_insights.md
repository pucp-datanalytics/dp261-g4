# Insights ejecutivos

## 1. Modelo recomendado

XGBoost es el modelo final/base del proyecto. El dashboard ahora recomienda economicamente el modelo que genera mayor valor neto bajo los supuestos actuales; por eso el recomendado puede variar al cambiar threshold, costos, margen o dataset.

## 2. Valor economico

La evaluacion economica permite estimar ganancia o perdida en USD para cada modelo. Esto responde mejor a una decision gerencial que mirar solo F1-score, precision, recall o ROC-AUC.

## 3. Baselines de negocio

El dashboard compara:

- Modelos tuneados frente a su version inicial o baseline.
- Modelos finales frente a escenarios operativos.
- Desempeno tecnico frente a valor economico.
- Sin modelo, intervenir a todos y seleccion aleatoria con misma cobertura.

## 4. Threshold economico

El threshold recomendado puede ser distinto de 0.5 porque los costos de FP y FN no son simetricos. Si el costo de oportunidad de perder compradores aumenta, conviene bajar el threshold y capturar mas visitantes con intencion de compra.

## 5. Accion recomendada

Usar el modelo recomendado economicamente bajo los supuestos actuales para activar acciones comerciales focalizadas: cupon, chat prioritario, oferta personalizada o recomendacion de productos. Evitar descuentos masivos porque elevan el costo de falsos positivos.

## 6. Limitacion

Los montos en USD dependen de supuestos configurables. Antes de produccion se deben reemplazar con margen real, costo real de incentivo y uplift observado en campanas.

## 7. Dataset dinamico

El dashboard dejo de ser estatico. Ahora puede recibir nuevos datasets desde la interfaz, validar la estructura esperada, generar predicciones con XGBoost y recalcular valor de negocio si el archivo incluye `Revenue`.

Si el archivo no incluye `Revenue`, el dashboard evita reportar metricas reales y muestra solo predicciones, segmentos e impacto potencial estimado.
