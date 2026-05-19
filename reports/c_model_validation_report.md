# Model Validation Report

## Modelo final

El modelo seleccionado fue `xgboost`, elegido por mayor F1-score promedio en validacion cruzada estratificada.

## Metricas principales

| Evaluacion | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Train final, threshold 0.50 | 0.9049 | 0.6720 | 0.7641 | 0.7151 | 0.9470 |
| Cross-validation final | 0.8973 | 0.6524 | 0.7352 | 0.6910 | 0.9305 |
| Test final, threshold 0.50 | 0.8951 | 0.6445 | 0.7356 | 0.6870 | 0.9336 |
| Test final, threshold F1 train-validation 0.54 | 0.8959 | 0.6553 | 0.7068 | 0.6801 | 0.9336 |

## Diagnostico

No se observa una brecha fuerte entre cross-validation y test. El F1 de test con threshold 0.50 es 0.6870 frente a F1 CV 0.6910, por lo que el desempeno es coherente.

El threshold 0.54 fue seleccionado sin usar test, mediante train-validation, pero no mejoro el F1 en test. Por transparencia, el reporte tecnico conserva threshold 0.50 como referencia principal y Sprint 5 evalua un umbral separado de negocio.

## Overfitting / underfitting

- Overfitting: leve y esperable. Train F1 0.7151, CV F1 0.6910 y test F1 0.6870.
- Underfitting: no hay evidencia fuerte; el modelo captura senal razonable del dataset.
- Modelos con mayor sobreajuste: Random Forest entrenado completo mostro train perfecto, pero test menor; por eso no fue seleccionado.

## Data leakage

El split train/test se realiza antes de cualquier `fit`. Imputacion, escalado, one-hot encoding y SMOTE viven dentro de `imblearn.pipeline.Pipeline`. El test set no se usa para fit, tuning, balanceo ni seleccion de features.

## Limitaciones

La clase positiva representa cerca de 15.5%, por lo que precision y recall deben interpretarse junto con el costo de negocio. El umbral optimo operativo depende de costos reales no provistos por el sponsor.
