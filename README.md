# Proyecto 2: Conversion de Visitantes en Compradores Online

Reconstruccion individual limpia y reproducible hasta Sprint 5.

## Alcance

- Sprint 1: Business Understanding y Data Understanding.
- Sprint 2: Data Preparation con pipeline reproducible.
- Sprint 3: modelos baseline.
- Sprint 4: modelos avanzados, tuning y seleccion final.
- Sprint 5: evaluacion, Business Value, dashboard y recomendaciones.
- Sprint 6: solo referencia para handoff futuro. No hay API, Docker, AWS ni CI/CD.

## Dataset

- Oficial: `docs/dataset_pucp.csv`
- Copia de trabajo: `data/raw/c_dataset_pucp.csv`
- Target: `Revenue`
- Clase positiva: `Revenue=True`
- Problema: clasificacion binaria desbalanceada.

## Instalacion

```bash
pip install -r requirements.txt
```

## Ejecucion

Desde la raiz del repositorio:

```bash
python src/c_train_baselines.py
python src/c_tune_models.py
python src/c_evaluate_business_value.py
python src/c_predict.py
streamlit run dashboard/c_app.py
```

## Notebooks academicos

Los notebooks son entregables de apoyo por sprint. La logica principal se mantiene en scripts `src/c_*.py` y los notebooks documentan/ejecutan el flujo con rutas relativas:

- Sprint 1: `notebooks/c_01_business.ipynb`, `notebooks/c_02_data_loading.ipynb`, `notebooks/c_03_eda.ipynb`, `notebooks/c_04_prototype.ipynb`
- Sprint 2: `notebooks/c_05_data_cleaning.ipynb`, `notebooks/c_06_feature_eng.ipynb`, `notebooks/c_07_class_balance.ipynb`, `notebooks/c_08_pipeline.ipynb`
- Sprint 3: `notebooks/c_09_baseline_models.ipynb`, `notebooks/c_10_evaluation.ipynb`, `notebooks/c_11_model_comparison.ipynb`
- Sprint 4: `notebooks/c_12_hyperparam_tuning.ipynb`, `notebooks/c_13_ensembles.ipynb`, `notebooks/c_14_final_validation.ipynb`
- Sprint 5: `notebooks/c_15_business_value.ipynb`, `notebooks/c_16_dashboard_prototype.ipynb`, `notebooks/c_17_findings_report.ipynb`

## Dashboard ejecutivo Sprint 5

Ejecutar desde la raiz:

```bash
streamlit run dashboard/c_app.py
```

El dashboard muestra una vista ejecutiva para stakeholders de e-commerce:

- problema de negocio y target `Revenue=True`
- KPIs del modelo final: F1-score, recall, precision y ROC-AUC
- conversion real, visitantes evaluados y compradores detectados
- comparacion visual de modelos por F1-score
- matriz de confusion explicada en lenguaje de negocio
- sensibilidad de valor esperado por threshold
- simulador interactivo de visitante
- analisis por tipo de visitante, mes de visita, fin de semana y variables de intencion
- recomendaciones accionables
- handoff preparado para Sprint 6

Archivos principales que lee:

- `docs/dataset_pucp.csv`
- `models/c_final_model.pkl`
- `models/c_metrics_summary.csv`
- `models/c_validation_test_comparison.csv`
- `models/c_threshold_analysis.csv`
- `models/c_dashboard_kpis.csv`
- `models/c_dashboard_segments.csv`
- `models/c_dashboard_feature_summary.csv`

Interpretacion rapida:

- F1-score resume el equilibrio entre detectar compradores y evitar falsas alarmas.
- Recall indica cuantos compradores reales captura el modelo.
- Precision indica que porcentaje de visitantes priorizados realmente compra.
- ROC-AUC mide la capacidad general de separar compradores de no compradores.
- El threshold de negocio puede ser distinto de 0.5 porque depende de costos y beneficios.

Este dashboard no implementa API, AWS ni Docker; es un prototipo ejecutivo local de Sprint 5.

## Artefactos principales

- `models/c_baseline_*.pkl`
- `models/c_tuned_*.pkl`
- `models/c_best_model.pkl`
- `models/c_final_model.pkl`
- `models/c_preproc.pkl`
- `models/c_preprocessing_pipeline.pkl`
- `models/c_metrics_summary.csv`
- `models/c_experiments_log.csv`
- `models/c_validation_test_comparison.csv`
- `models/c_threshold_analysis.csv`
- `reports/c_model_validation_report.md`
- `reports/c_business_value_summary.md`
- `reports/c_recommendations.md`
- `handoff/c_notes_for_sprint6.md`

## Prevencion de data leakage

El split train/test se hace antes de cualquier `fit` con `train_test_split(..., stratify=y, random_state=42)`. El preprocesamiento se encapsula con `ColumnTransformer`. El balanceo se integra en `imblearn.pipeline.Pipeline`, por lo que SMOTE se aplica solo sobre train durante entrenamiento y cross-validation. El test set solo se usa para evaluacion final.

## Seleccion del modelo

El criterio principal es F1-score. Accuracy, precision, recall y ROC-AUC se reportan como soporte. Si dos modelos tienen F1 similar, se revisan recall, ROC-AUC, estabilidad y facilidad de despliegue futuro.

## Sprint 6 futuro

El Sprint 6 puede usar `models/c_final_model.pkl`, `models/c_preprocessing_pipeline.pkl`, `src/c_predict.py` y `handoff/contracts/` como punto de partida para una API FastAPI. Esta reconstruccion no crea API, Dockerfile, infraestructura AWS ni CI/CD.
