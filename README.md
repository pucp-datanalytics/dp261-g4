# Proyecto 2: Conversion de Visitantes en Compradores Online

Reconstruccion individual limpia y reproducible hasta Sprint 5.

## Alcance

- Sprint 1: Business Understanding y Data Understanding.
- Sprint 2: Data Preparation con pipeline reproducible.
- Sprint 3: modelos baseline.
- Sprint 4: modelos avanzados, tuning y seleccion final.
- Sprint 5: evaluacion, Business Value, dashboard y recomendaciones.
- Sprint 6: API REST, integracion dashboard-API y despliegue MVP con Docker + EC2.

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

## Dashboard ejecutivo Sprint 5 / Sprint 6

Ejecutar desde la raiz:

```bash
streamlit run dashboard/c_app.py
```

Para la integracion PB-21 del Sprint 6, el simulador consume la API REST por HTTP:

```bash
API_URL=http://localhost:8000 streamlit run dashboard/c_app.py
```

En Windows PowerShell:

```powershell
$env:API_URL="http://localhost:8000"
streamlit run dashboard/c_app.py
```

Si PB-20 despliega la API en AWS, reemplazar `API_URL` por el endpoint entregado.
Si la API desplegada usa llave, configurar tambien `API_KEY`; el dashboard la enviara como header `x-api-key`.

## Despliegue MVP Sprint 6

El repositorio incluye un `Dockerfile` para publicar el dashboard Streamlit en el puerto `8080`, un `api/Dockerfile` para publicar la API FastAPI en el puerto `8000`, y un workflow en `.github/workflows/cd.yml` que construye ambas imagenes, las sube a ECR y actualiza ambos contenedores en EC2 cuando se hace push a `feat/PB-review3`.

Secretos requeridos en GitHub Actions:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_SESSION_TOKEN`
- `EC2_HOST`
- `EC2_USER`
- `EC2_SSH_KEY`
- `API_URL` con el endpoint de la API de prediccion. En EC2 con ambos contenedores, el workflow usa por defecto `http://sprint6-api:8000`.
- `API_KEY` opcional, solo si la API desplegada exige autenticacion.

Contenedores esperados en EC2:

- `sprint6-api`: FastAPI, puerto `8000`.
- `dp261-g4`: dashboard Streamlit, puerto `8080`.

Validacion rapida en EC2:

```bash
sudo docker ps
curl http://localhost:8000/health
curl http://localhost:8000/version
curl -X POST "http://localhost:8000/predict" -H "Content-Type: application/json" --data-binary "@handoff/contracts/c_example_request.json"
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

El simulador del dashboard esta integrado con `POST {API_URL}/predict` y maneja errores de API no disponible, timeouts y respuestas HTTP invalidas.
La vista de carga de datasets puede probar una muestra contra `POST {API_URL}/predict_batch`, lo que permite validar el flujo Sprint 6 usuario -> dashboard -> API -> predicciones.

## Dashboard ejecutivo y valor de negocio

El dashboard fue reforzado para mostrar valor economico, no solo metricas tecnicas. Se ejecuta con:

```bash
streamlit run dashboard/c_app.py
```

Secciones principales:

- Resumen ejecutivo con modelo recomendado dinamico segun mayor valor economico.
- Ranking economico de modelos en USD.
- Impacto economico del tuning: tuneado vs inicial/baseline.
- Desempeno tecnico vs valor economico para Accuracy, Precision, Recall, F1-score y ROC-AUC.
- Profit curve con selector interno para ver todas las curvas o un modelo especifico, incluyendo baseline, iniciales y tuneados.
- Simulador economico con supuestos editables.
- Segmentos y senales de negocio.
- Recomendaciones ejecutivas.
- Compatibilidad Sprint 6.

Supuestos configurables desde la barra lateral:

- Ingreso promedio por compra.
- Margen bruto.
- Costo de incentivo/descuento.
- Costo de contacto o chat.
- Uplift esperado por intervencion.
- Costo de oportunidad de falso negativo.
- Valor/costo de true negative.
- Threshold de decision.

Interpretacion:

- `Valor esperado USD` estima ganancia o perdida neta con la matriz costo-beneficio.
- `Ganancia incremental vs baseline` muestra cuanto mejora XGBoost frente a modelos o escenarios de referencia.
- `ROI %` compara el valor neto contra el costo de intervenir visitantes.
- Los montos son estimaciones bajo supuestos configurables porque el dataset no contiene monto real de compra.

Archivos economicos usados:

- `models/c_model_economic_comparison.csv`
- `models/c_profit_curve_by_model.csv`
- `models/c_baseline_comparison_usd.csv`

Esta mejora corresponde al Sprint 5 y mantiene compatibilidad con Sprint 6. No cambia el modelo final, no reentrena modelos, no cambia la API y no modifica Docker.

## Uso de dataset cargado por usuario en el dashboard

Ejecutar:

```bash
streamlit run dashboard/c_app.py
```

En la barra lateral se puede elegir:

- `Dataset original`: usa `docs/dataset_pucp.csv` como demo reproducible.
- `Dataset cargado por usuario`: permite subir un archivo CSV o XLSX desde el dashboard.

Columnas requeridas:

- `Administrative`
- `Administrative_Duration`
- `Informational`
- `Informational_Duration`
- `ProductRelated`
- `ProductRelated_Duration`
- `BounceRates`
- `ExitRates`
- `PageValues`
- `SpecialDay`
- `Month`
- `OperatingSystems`
- `Browser`
- `Region`
- `TrafficType`
- `VisitorType`
- `Weekend`

Columna opcional:

- `Revenue`

Si el dataset contiene `Revenue`, el dashboard puede calcular metricas reales, matriz de confusion, valor economico, ROI y comparacion de modelos sobre el archivo cargado.

Si el dataset no contiene `Revenue`, el dashboard no calcula F1, recall, precision, ROC-AUC ni matriz de confusion real. En ese caso muestra predicciones, probabilidades, nivel de intencion, acciones sugeridas y valor potencial estimado bajo supuestos configurables.

El modelo no se reentrena desde el dashboard. La carga dinamica usa el modelo final `models/c_final_model.pkl` y los modelos existentes para scoring/comparacion. Las predicciones pueden descargarse desde la interfaz como `c_uploaded_predictions.csv`.

Archivos locales generados cuando se carga un dataset valido:

- `data/processed/c_uploaded_dataset_validated.csv`
- `data/processed/c_uploaded_predictions.csv`
- `models/c_uploaded_dataset_business_value.csv`, si aplica
- `models/c_uploaded_dataset_economic_comparison.csv`, si aplica

La carpeta `data/user_uploads/` queda preparada para cargas locales, pero los archivos de usuario no se versionan. No subir datos sensibles.

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
- `models/c_model_economic_comparison.csv`
- `models/c_profit_curve_by_model.csv`
- `models/c_baseline_comparison_usd.csv`
- `reports/c_model_validation_report.md`
- `reports/c_business_value_summary.md`
- `reports/c_recommendations.md`
- `handoff/c_notes_for_sprint6.md`

## Prevencion de data leakage

El split train/test se hace antes de cualquier `fit` con `train_test_split(..., stratify=y, random_state=42)`. El preprocesamiento se encapsula con `ColumnTransformer`. El balanceo se integra en `imblearn.pipeline.Pipeline`, por lo que SMOTE se aplica solo sobre train durante entrenamiento y cross-validation. El test set solo se usa para evaluacion final.

## Seleccion del modelo

El criterio principal es F1-score. Accuracy, precision, recall y ROC-AUC se reportan como soporte. Si dos modelos tienen F1 similar, se revisan recall, ROC-AUC, estabilidad y facilidad de despliegue futuro.

## Sprint 6

La API FastAPI vive en `api/`, el dashboard consume `POST {API_URL}/predict` desde el simulador y puede consumir `POST {API_URL}/predict_batch` para datasets cargados. El despliegue principal usa Docker + EC2 mediante GitHub Actions y levanta ambos contenedores en la red Docker `sprint6-net`.

Artefactos operativos agregados para Sprint 6:

- `docs/sprint6_completion_checklist.md`
- `docs/runbook.md`
- `monitoring/cloudwatch-log-insights.md`
- `monitoring/cloudwatch-alarms.json`
- `.github/workflows/cd-api.yml`

El endpoint final de API debe configurarse como `API_URL` cuando PB-20 entregue o actualice el servicio desplegado. Si la IP o las credenciales temporales de AWS cambian, se actualizan los GitHub Secrets, no el codigo.
