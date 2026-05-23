# Dashboard ejecutivo Sprint 5

El dashboard fue reforzado para responder la observacion del profesor: ahora muestra valor de negocio en USD, no solo metricas tecnicas.

## Secciones principales

- Resumen ejecutivo con modelo recomendado, valor estimado, ROI, threshold economico y costos de FP/FN.
- Carga de nuevo dataset con validacion de estructura.
- Ranking economico de modelos.
- Impacto economico del tuning: XGBoost tuneado vs inicial, LightGBM tuneado vs inicial y Random Forest tuneado vs baseline.
- Desempeno tecnico vs valor economico para Accuracy, Precision, Recall, F1-score y ROC-AUC.
- Profit curve con selector interno para analizar todas las curvas o un modelo especifico, incluyendo baseline, iniciales y tuneados.
- Simulador economico de visitante.
- Segmentos y senales de negocio.
- Recomendaciones ejecutivas.
- Sprint 6 readiness.

## Archivos economicos generados

- `models/c_model_economic_comparison.csv`
- `models/c_profit_curve_by_model.csv`
- `models/c_baseline_comparison_usd.csv`

## Lectura ejecutiva

El dashboard permite explicar que el modelo recomendado puede variar segun los supuestos economicos y el threshold. Tambien permite evaluar si el tuning agrego o redujo valor frente a la version inicial/baseline de cada familia de modelo.

Los montos son estimaciones configurables desde la barra lateral del dashboard.

## Dataset cargado por usuario

El dashboard ahora puede recibir un CSV/XLSX desde la interfaz. Si el archivo contiene `Revenue`, se recalculan metricas reales, matriz de confusion y valor economico. Si no contiene `Revenue`, se muestran predicciones, niveles de intencion y valor potencial estimado sin reportar metricas reales.

El dataset original `docs/dataset_pucp.csv` se mantiene como fallback reproducible.
