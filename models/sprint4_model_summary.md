# Sprint 4 - Model Tracking Summary

## Objetivo del Sprint 4

El Sprint 4 tuvo como objetivo optimizar modelos candidatos, explorar modelos avanzados y validar el desempeno final sobre el conjunto de test real.

La conclusion actualizada es que no existe un unico modelo ganador universal. La seleccion depende del escenario de negocio, especialmente del costo de contacto y del tipo de visitante.

## Inputs principales

### Rol 2 - Hyperparameter Tuner

Responsable: Perla

Archivos principales:

- `notebooks/12_hyperparam_tuning.ipynb`
- `models/best_tuned_model.pkl`

Resultado:

- Se optimizaron modelos candidatos del Sprint 3: SVM, Decision Tree y Random Forest.
- El mejor modelo dentro de este bloque fue Random Forest tuneado.
- `models/best_tuned_model.pkl` corresponde al Random Forest tuneado.
- Este modelo es especialmente util cuando se prioriza recall y maxima captura de compradores.

### Rol 3 - Ensemble Engineer

Responsable: Julio

Archivos principales:

- `notebooks/13_ensembles.ipynb`
- `models/ensemble_results_xgb_lgbm.csv`
- `models/ensemble_results_by_visitor_type.csv`
- `models/xgboost_base.pkl`
- `models/lightgbm_base.pkl`
- `models/tuned_xgboost.pkl`
- `models/tuned_lightgbm.pkl`

Resultado:

- Se reentrenaron y evaluaron XGBoost y LightGBM usando el mismo esquema de datos que Random Forest.
- Los modelos se evaluaron sobre `data/processed/test_processed.csv`, manteniendo la distribucion real de compras cercana al 15%.
- XGBoost tuneado obtuvo el mejor desempeno global para ranking/campanas conservadoras por PR-AUC y ROC-AUC.
- LightGBM fue competitivo, pero no supero claramente a XGBoost ni a Random Forest en los escenarios clave.

### Rol 4 - Final Validator

Responsable: Nikol

Archivo principal:

- `notebooks/14_evaluacion final del Test.ipynb`

Outputs principales:

- `models/final_test_model_comparison.csv`
- `models/final_test_by_visitor_type.csv`

Resultado:

- Se validaron Random Forest, XGBoost y LightGBM sobre el mismo test real.
- Se compararon politicas con `threshold=0.50` y `threshold=0.25`.
- Se agrego evaluacion segmentada por `VisitorType`.
- La seleccion final se definio por escenario de negocio.

## Resultados principales en test real

Con `threshold=0.50`:

| Modelo | F1 | Precision | Recall | ROC-AUC | PR-AUC |
|---|---:|---:|---:|---:|---:|
| Random Forest final | 0.6751 | 0.6552 | 0.6963 | 0.9210 | 0.6940 |
| XGBoost tuned | 0.6720 | 0.6877 | 0.6571 | 0.9319 | 0.7438 |
| LightGBM base | 0.6684 | 0.6802 | 0.6571 | 0.9317 | 0.7361 |
| LightGBM tuned | 0.6676 | 0.6841 | 0.6518 | 0.9315 | 0.7412 |
| XGBoost base | 0.6649 | 0.6757 | 0.6545 | 0.9310 | 0.7368 |

Con `threshold=0.25`, Random Forest logra la mayor captura global de compradores:

- Recall: 0.8770
- Compradores detectados: 335 de 382
- Falsos positivos: 336

## Recomendacion final por escenario

| Escenario | Modelo recomendado | Threshold | Razon |
|---|---|---:|---|
| Global conservador / ranking de compradores | XGBoost tuned | 0.50 | Mayor PR-AUC y ROC-AUC en test real; util cuando el contacto tiene costo. |
| Maxima captura de compradores | Random Forest final | 0.25 | Mayor recall global; util si perder compradores es mas caro que contactar falsos positivos. |
| Usuarios nuevos | XGBoost base/tuned | 0.50 | Alta precision; contactar nuevos suele ser mas dificil y caro. |
| Usuarios recurrentes | Random Forest final | 0.25 | Alto recall; activar recurrentes suele ser mas barato. |

## Decision de negocio

El proyecto debe presentar la salida del modelo como una politica de decision:

- Para campanas globales o usuarios nuevos, usar XGBoost con politica conservadora.
- Para retencion o activacion de usuarios recurrentes, usar Random Forest con threshold mas bajo.
- Mantener LightGBM como benchmark competitivo, pero no como recomendacion principal.

## Uso esperado para Sprint 5

Sprint 5 debe enfocarse en Business Value:

- Definir costo de contacto para usuario nuevo y recurrente.
- Definir valor esperado o margen por compra.
- Evaluar beneficio esperado por politica:
  `beneficio = TP * valor_compra - FP * costo_contacto`.
- Convertir las probabilidades en segmentos accionables para marketing/retencion.
