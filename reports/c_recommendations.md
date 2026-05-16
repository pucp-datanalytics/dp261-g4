# Recomendaciones

## Hallazgos

- `Revenue=True` representa cerca de 15.5% de las sesiones, por lo que F1, recall y ROC-AUC son mas informativos que accuracy.
- El objetivo de negocio es priorizar visitantes con alta probabilidad de compra para acciones de conversion.
- El test set conserva la distribucion real y no recibe SMOTE.

## Recomendaciones de negocio

- Usar el umbral recomendado en `models/c_threshold_analysis.csv` para campanas de personalizacion.
- Validar los costos y beneficios supuestos con el sponsor antes de Sprint 6.
- Monitorear drift de variables de comportamiento, conversion real y distribucion de probabilidades.
- Empezar con acciones de bajo riesgo: pop-ups de descuento, soporte priorizado o ofertas segmentadas.

## Riesgos

- Los costos reales de FP/FN no estan disponibles; los valores actuales son supuestos modificables.
- La conducta de compra puede cambiar por temporada, campanas, precios o experiencia de usuario.
- En Sprint 6 se debe agregar validacion estricta de payloads y observabilidad.
