# Sprint 4 - Model Tracking Summary

## Objetivo del Sprint 4

El Sprint 4 tuvo como objetivo optimizar los modelos candidatos del Sprint 3, explorar técnicas avanzadas de modelado y validar un modelo final en el conjunto de test.

## Inputs principales

### Rol 2 - Hyperparameter Tuner

Responsable: Perla

Archivos principales:

- `notebooks/12_hyperparam_tuning.ipynb`
- `models/best_tuned_model.pkl`

Resultado:

- Se optimizaron modelos candidatos del Sprint 3: SVM, Decision Tree y Random Forest.
- El mejor modelo tuneado fue Random Forest.
- El archivo `models/best_tuned_model.pkl` corresponde al Random Forest tuneado.

### Rol 3 - Ensemble Engineer

Responsable: Julio

Archivos principales:

- `notebooks/13_ensembles.ipynb`
- `models/ensemble_results_xgb_lgbm.csv`
- `models/xgboost_base.pkl`
- `models/lightgbm_base.pkl`
- `models/tuned_xgboost.pkl`
- `models/tuned_lightgbm.pkl`

Resultado:

- Se entrenaron y optimizaron modelos avanzados de Gradient Boosting: XGBoost y LightGBM.
- El mejor modelo de este bloque fue XGBoost tuneado.
- XGBoost tuneado obtuvo un F1 CV de 0.9450, Recall CV de 0.9516 y ROC-AUC CV de 0.9885.

### Rol 4 - Final Validator

Responsable: Nikol

Archivo principal:

- `notebooks/14_evaluacion final del Test.ipynb`

Resultado:

- Se validó el modelo final en el conjunto de test.
- El modelo final validado fue el Random Forest tuneado generado en el Rol 2.

## Modelo final seleccionado

- Modelo: Random Forest tuneado
- Archivo original: `models/best_tuned_model.pkl`
- Archivo final del Sprint 4: `models/final_model.pkl`
- Responsable del tuning: Perla
- Responsable de la validación final: Nikol

## Comparación con modelos avanzados

En el PB-14 se entrenaron y optimizaron XGBoost y LightGBM como modelos avanzados de Gradient Boosting.

Aunque XGBoost tuneado obtuvo un desempeño alto en validación cruzada, el modelo final seleccionado para validación en test fue el Random Forest tuneado.

## Uso esperado para Sprint 5

El archivo `models/final_model.pkl` queda como insumo principal para el Sprint 5, donde se evaluará el valor de negocio del modelo seleccionado.