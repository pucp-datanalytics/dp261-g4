# Final Report - Proyecto 2

## Resumen ejecutivo

El proyecto aborda la conversion de visitantes online en compradores. El objetivo de negocio es identificar visitantes con alta probabilidad de compra para priorizar acciones comerciales como cupones, ofertas personalizadas, mensajes o chat prioritario.

El target oficial es `Revenue=True`, que indica compra realizada. El problema se resolvio como clasificacion binaria con clase positiva desbalanceada.

## Modelo final

El modelo final tecnico es XGBoost, seleccionado por F1-score y validado contra train, cross-validation y test. Los artefactos persistidos para despliegue son:

- `handoff/model/c_final_model.pkl`
- `handoff/model/c_preprocessing_pipeline.pkl`
- `models/c_final_model.pkl`
- `models/c_best_model.pkl`

## Valor de negocio

El dashboard ejecutivo estima valor economico en USD con una matriz costo-beneficio:

`Valor = TP * beneficio_TP + FP * costo_FP + FN * costo_FN + TN * valor_TN`

Los montos son estimaciones bajo supuestos configurables. El dataset no contiene monto real de compra, por lo que los valores sirven para comparar modelos, thresholds y escenarios bajo una misma logica economica.

## Dashboard

El dashboard `dashboard/c_app.py` permite:

- comparar modelos por valor economico,
- revisar impacto del tuning,
- analizar profit curve por modelo,
- cargar datasets nuevos,
- simular visitantes individuales,
- probar una muestra contra la API REST del Sprint 6,
- revisar segmentos y recomendaciones ejecutivas.

## Sprint 6 - Deployment

El Sprint 6 deja preparado y funcional el MVP:

- API FastAPI en `api/` con `/health`, `/version`, `/predict` y `/predict_batch`,
- Dockerfile de API en `api/Dockerfile`,
- workflow manual de API en `.github/workflows/cd-api.yml`,
- dashboard Docker en el `Dockerfile` raiz,
- contratos JSON en `handoff/contracts/`,
- runbook en `docs/runbook.md`,
- checklist Sprint 6 en `docs/sprint6_completion_checklist.md`,
- artefactos de monitoreo en `monitoring/`.

## Recomendaciones

1. Usar XGBoost como modelo tecnico base.
2. Seleccionar el modelo recomendado economicamente segun los supuestos vigentes del negocio.
3. No ofrecer descuentos indiscriminadamente; intervenir solo visitantes con probabilidad superior al threshold economico.
4. Monitorear falsos positivos, falsos negativos, latencia p95 y error rate 5xx.
5. Configurar `API_URL` y `API_KEY` mediante variables de entorno o GitHub Secrets, nunca en codigo.
6. Validar en demo el flujo completo: dashboard -> API -> prediccion -> logs CloudWatch.
