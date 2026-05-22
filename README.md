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

# Caracterización de Delegación de Roles — Sprint 5 (Evaluation)

## Enfoque del Sprint 5

El Sprint 5 estuvo orientado a la fase **Evaluation** dentro de la metodología CRISP-DM. El objetivo principal fue traducir las métricas técnicas del modelo en valor de negocio, construir herramientas de visualización para stakeholders y generar documentación ejecutiva que sustente la decisión de despliegue del MVP.

La distribución de roles se realizó considerando las capacidades técnicas, organizacionales y de comunicación de cada integrante, buscando además fomentar el aprendizaje colaborativo y la participación activa en distintas áreas del proyecto.

---

# Delegación de Roles — Sprint 5

| Rol | Responsable | Función Principal |
|---|---|---|
| **Project Manager** | Perla Gavilano | Coordinación general del Sprint, seguimiento de tareas y gestión del Kanban |
| **Business Analyst** | Perla Gavilano | Evaluación del Business Value del modelo seleccionado (PB-16) |
| **Dashboard Developer** | Juan Ramos | Construcción del dashboard interactivo de resultados (PB-17) |
| **Documentation Lead** | Solanch Nikol Solaligue | Documentación de hallazgos y recomendaciones de negocio (PB-18) |
| **QA & Stakeholder Reviewer** | Julio Misari | Validación de calidad y preparación del handoff al Sprint 6 |

---

# Justificación de las Delegaciones

## Project Manager — Perla Gavilano

Se asignó el rol de Project Manager a Perla Gavilano debido a su capacidad de organización y coordinación del flujo de trabajo del Sprint. Entre sus principales responsabilidades estuvieron:

- Gestión y actualización del tablero Kanban.
- Supervisión del avance de tareas.
- Coordinación entre roles y seguimiento de entregables.
- Preparación del Sprint Review y control del cumplimiento del cronograma.

Además, asumió simultáneamente el rol de **Business Analyst**, permitiendo mantener alineada la evaluación técnica con los objetivos de negocio.

---

## Business Analyst — Perla Gavilano (PB-16)

La tarea PB-16 consistió en evaluar el valor de negocio del modelo seleccionado mediante análisis costo–beneficio, definición de umbrales óptimos y estimación de impacto económico.

La asignación de este rol permitió:

- Traducir métricas técnicas a indicadores de negocio comprensibles para stakeholders.
- Analizar escenarios de costo y beneficio asociados a falsos positivos y falsos negativos.
- Definir criterios para justificar el despliegue del MVP en el Sprint 6.

---

## Dashboard Developer — Juan Ramos (PB-17)

Juan Ramos asumió el rol de Dashboard Developer, siendo responsable de la construcción del dashboard interactivo orientado a stakeholders.

Sus responsabilidades incluyeron:

- Diseño de visualizaciones interactivas.
- Implementación de KPIs y métricas del modelo.
- Integración de simulaciones de predicción.
- Incorporación de explicabilidad mediante SHAP.

La delegación se enfocó en fortalecer la presentación visual y comprensión de resultados para usuarios no técnicos.

---

## Documentation Lead — Solanch Nikol Solaligue (PB-18)

El rol de Documentation Lead fue asignado a Solanch Nikol Solaligue para liderar la elaboración del reporte ejecutivo y las recomendaciones estratégicas del proyecto.

Entre sus responsabilidades estuvieron:

- Redacción del resumen ejecutivo.
- Documentación de hallazgos, riesgos y limitaciones.
- Elaboración de recomendaciones de negocio.
- Organización del reporte final orientado a stakeholders.

Esta función permitió consolidar técnicamente los resultados obtenidos durante los Sprint anteriores y preparar la documentación necesaria para el handoff hacia Deployment.

---

## QA & Stakeholder Reviewer — Julio Misari

Julio Misari asumió el rol de QA & Stakeholder Reviewer, encargado de validar la calidad general de los entregables y preparar la transición hacia el Sprint 6.

Sus funciones principales fueron:

- Verificar consistencia entre notebooks, dashboard y reporte.
- Validar funcionamiento del dashboard de extremo a extremo.
- Revisar claridad del lenguaje utilizado para stakeholders.
- Preparar el paquete de handoff técnico para Deployment.

Este rol fue fundamental para asegurar que los entregables del Sprint 5 estuvieran correctamente documentados, validados y listos para la siguiente fase del proyecto.

---

# Conclusión

La delegación de roles del Sprint 5 permitió distribuir responsabilidades de manera equilibrada entre análisis de negocio, visualización, documentación y validación de calidad.

Esta organización facilitó el cumplimiento de los objetivos de la fase Evaluation, asegurando que el proyecto no solo alcance métricas técnicas satisfactorias, sino también valor de negocio, interpretabilidad y preparación adecuada para el despliegue del MVP en el Sprint 6.

# Caracterización de Delegación de Roles — Sprint 6 (Deployment)

## Enfoque del Sprint 6

El Sprint 6 estuvo orientado a la fase **Deployment** dentro de la metodología CRISP-DM. El objetivo principal fue desplegar el MVP del modelo en un entorno operativo, integrando la API, el dashboard y las herramientas de monitoreo necesarias para garantizar disponibilidad, observabilidad y continuidad operativa.

La delegación de roles se realizó buscando fortalecer competencias relacionadas con MLOps, despliegue en la nube, integración de servicios y monitoreo de sistemas en producción.

---

# Delegación de Roles — Sprint 6

| Rol | Responsable | Función Principal |
|---|---|---|
| **Project Manager** | Solanch Nikol Solaligue | Coordinación general del Sprint 6 y seguimiento del Deployment |
| **API Engineer** | Julio Misari | Empaquetar el modelo como API REST (PB-19) |
| **Docker & Container Support** | Perla Gavilano | Configuración y validación del Dockerfile |
| **Cloud / DevOps Engineer** | Perla Gavilano | Despliegue del MVP en AWS y configuración de infraestructura |
| **CI/CD Support** | Juan Ramos | Configuración de automatización con GitHub Actions |
| **Integration Engineer** | Juan Ramos | Integración del dashboard con la API desplegada (PB-21) |
| **Site Reliability & Monitoring (SRE)** | Todo el equipo | Monitoreo, observabilidad y soporte operativo del MVP |

---

# Justificación de las Delegaciones

## Project Manager — Solanch Nikol Solaligue

El rol de Project Manager fue asumido por Solanch Nikol Solaligue, quien estuvo a cargo de coordinar las actividades del Sprint 6 y supervisar el cumplimiento de los objetivos relacionados con Deployment.

Sus principales responsabilidades incluyeron:

- Organización y seguimiento del Sprint.
- Supervisión del avance técnico del MVP.
- Coordinación entre API, DevOps, integración y monitoreo.
- Gestión del flujo de trabajo y validación de entregables.
- Preparación de la Sprint Review final.

La asignación permitió mantener una visión integral del despliegue y asegurar la comunicación entre todos los componentes del sistema.

---

## API Engineer — Julio Misari (PB-19)

Julio Misari asumió el rol de API Engineer, siendo responsable de empaquetar el modelo como un servicio API REST utilizando FastAPI.

Entre sus funciones estuvieron:

- Implementación de endpoints como `/health`, `/predict` y `/version`.
- Integración del modelo entrenado dentro de la API.
- Validación de respuestas y pruebas locales.
- Preparación de la estructura base para despliegue.

La asignación de este rol permitió transformar el modelo analítico en un servicio consumible por aplicaciones externas y dashboards.

---

## Docker & Container Support — Perla Gavilano

Perla Gavilano participó en la configuración y validación del Dockerfile utilizado para contenerizar la aplicación.

Sus responsabilidades incluyeron:

- Construcción de imágenes Docker reproducibles.
- Validación del entorno de ejecución.
- Configuración de dependencias necesarias para producción.
- Soporte en pruebas de ejecución local del contenedor.

Este soporte fue clave para garantizar portabilidad y reproducibilidad del MVP.

---

## Cloud / DevOps Engineer — Perla Gavilano

Además del soporte en Docker, Perla Gavilano asumió el rol de Cloud / DevOps Engineer, liderando las tareas relacionadas con despliegue e infraestructura.

Sus funciones incluyeron:

- Configuración de despliegue en AWS.
- Gestión de repositorios ECR.
- Configuración de infraestructura para el MVP.
- Validación del endpoint público HTTPS.
- Supervisión de la automatización de despliegue.

La asignación permitió asegurar un entorno de despliegue funcional y alineado con buenas prácticas de MLOps.

---

## CI/CD Support — Juan Ramos

Juan Ramos colaboró en la configuración de automatización mediante GitHub Actions para facilitar procesos de integración y despliegue continuo.

Sus tareas incluyeron:

- Configuración del pipeline CI/CD.
- Automatización de build y deployment.
- Validación de workflows en GitHub Actions.
- Soporte en pruebas automatizadas del despliegue.

Esta delegación permitió mejorar la reproducibilidad y automatización del ciclo de despliegue.

---

## Integration Engineer — Juan Ramos (PB-21)

Juan Ramos también asumió el rol de Integration Engineer, encargado de conectar el dashboard desarrollado en Sprint 5 con la API desplegada en producción.

Entre sus responsabilidades estuvieron:

- Modificación del dashboard para consumir la API real.
- Validación de comunicación entre frontend y backend.
- Pruebas end-to-end del MVP.
- Verificación del flujo completo de predicción.

Este rol fue esencial para consolidar el funcionamiento integrado del sistema.

---

## Site Reliability & Monitoring (SRE) — Todo el Equipo

Las actividades de monitoreo y observabilidad fueron desarrolladas de manera colaborativa por todo el equipo.

Las responsabilidades incluyeron:

- Configuración de logs estructurados.
- Implementación de métricas y alarmas en CloudWatch.
- Supervisión de latencia y tasa de errores.
- Elaboración del runbook operativo.
- Validación de estabilidad del MVP en producción.

La participación conjunta permitió que todos los integrantes comprendieran aspectos básicos de operación y mantenimiento del sistema desplegado.

---

# Conclusión

La delegación de roles del Sprint 6 permitió distribuir las responsabilidades relacionadas con Deployment, integración y monitoreo del MVP de manera organizada y colaborativa.

La participación del equipo en actividades de API, Docker, AWS, CI/CD y observabilidad fortaleció las competencias prácticas en MLOps y permitió completar exitosamente el despliegue funcional del proyecto, alineado con los objetivos de la fase Deployment de CRISP-DM.





