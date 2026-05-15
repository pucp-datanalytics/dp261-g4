# Resumen Ejecutivo - Sprint 5

## Decision Principal

El modelo no debe desplegarse como una unica regla universal. La evidencia del Sprint 5 recomienda una politica por escenario:

- **Campanas globales / ranking conservador:** usar **XGBoost tuned** con threshold 0.50.
- **Maxima captura de compradores:** usar **Random Forest** con threshold bajo.
- **Usuarios nuevos:** usar **XGBoost** con politica conservadora.
- **Usuarios recurrentes:** usar una politica mas agresiva, porque la activacion suele ser menos costosa.

Esta estrategia conecta mejor con el negocio que elegir solo el modelo con mayor F1 global.

## Contexto

El proyecto busca predecir si una sesion de e-commerce terminara en compra (`Revenue = True`). El dataset esta desbalanceado: en el test real solo **15.65%** de las sesiones terminaron en compra.

Durante Sprint 4 se validaron Random Forest, XGBoost y LightGBM. En Sprint 5 se tradujeron esas metricas a valor de negocio mediante:

- matriz costo-beneficio,
- busqueda de umbral optimo,
- evaluacion por segmento de visitante,
- curva gain/lift,
- estimacion anual bajo supuestos.

## Hallazgos Tecnicos Clave

Con threshold 0.50 sobre test real:

| Modelo | Precision | Recall | F1 | ROC-AUC | PR-AUC |
|---|---:|---:|---:|---:|---:|
| Random Forest | 0.6552 | 0.6963 | 0.6751 | 0.9210 | 0.6940 |
| XGBoost tuned | 0.6877 | 0.6571 | 0.6720 | 0.9319 | 0.7438 |
| LightGBM base | 0.6802 | 0.6571 | 0.6684 | 0.9317 | 0.7361 |

Interpretacion:

- **Random Forest** captura mas compradores con threshold estandar.
- **XGBoost tuned** ordena mejor los clientes por probabilidad de compra, con mayor PR-AUC y ROC-AUC.
- **LightGBM** es competitivo, pero no lidera los escenarios clave.

## Hallazgo por Segmento

Para usuarios nuevos (`New_Visitor`), XGBoost base con threshold 0.50 obtiene:

- Precision: **0.9048**
- Recall: **0.7835**
- F1: **0.8398**
- Falsos positivos: **8**
- Compradores detectados: **76 de 97**

Esto es adecuado cuando contactar usuarios nuevos es mas caro.

Para usuarios recurrentes, una politica mas agresiva aumenta la captura. El analisis tecnico previo muestra que Random Forest con threshold 0.25 logra:

- Recall alto para recurrentes.
- Mayor captura de compradores.
- Mas falsos positivos, aceptables solo si el costo de activacion es bajo.

## Business Value Provisional

El notebook `15_business_value.ipynb` estima valor economico usando supuestos iniciales. Estos supuestos deben ser validados con el sponsor.

Resultados bajo supuestos actuales:

| Escenario | Modelo | Threshold | Valor incremental test | Valor incremental anual estimado |
|---|---|---:|---:|---:|
| Global conservador | XGBoost base | 0.07 | 54,560 | 272,800 |
| Maxima captura | XGBoost base | 0.06 | 74,040 | 370,200 |
| Usuarios nuevos | XGBoost base | 0.06 | 17,010 | 85,050 |
| Usuarios recurrentes | LightGBM base | 0.05 | 38,250 | 191,250 |

Lectura importante:

- Los umbrales economicos optimos son bajos porque los supuestos penalizan mucho perder compradores (`FN`).
- Si el sponsor confirma que contactar falsos positivos es mas caro, los umbrales optimos deberian subir.
- Estos valores no son revenue real observado; son estimaciones basadas en una matriz costo-beneficio.

## Curva Gain/Lift

Usando XGBoost tuned como modelo de ranking:

| Porcentaje contactado | Compradores capturados | Lift vs aleatorio |
|---:|---:|---:|
| 10% | 49.2% | 4.92x |
| 20% | 76.7% | 3.84x |
| 30% | 89.3% | 2.98x |
| 50% | 98.4% | 1.97x |

Esto indica que el modelo es util para priorizar campanas: contactando el top 20% se podria capturar alrededor del 76.7% de compradores del test.

## Riesgos y Limitaciones

- `Revenue` es binario; no representa monto real de compra.
- Los costos y beneficios economicos son supuestos no validados.
- `PageValues` tiene alta importancia y debe confirmarse si esta disponible al momento real de decision.
- La distribucion futura de visitantes puede cambiar.
- No se recomienda desplegar Sprint 6 sin validar costos, margen y politica de contacto con sponsor.

## Recomendacion Ejecutiva

Avanzar hacia Sprint 6 solo si el sponsor valida los supuestos economicos. Mientras tanto, la recomendacion provisional es:

1. Usar **XGBoost tuned** para ranking global y priorizacion de campanas.
2. Usar **XGBoost con threshold conservador** para usuarios nuevos.
3. Usar **Random Forest o una politica de bajo threshold** para recurrentes si el costo de contacto es bajo.
4. Presentar el dashboard y reporte final con escenarios de sensibilidad, no como una unica decision fija.

## Estado

Sprint 5 queda preparado para revision con sponsor. La validacion pendiente no bloquea el analisis tecnico, pero si bloquea la decision final de despliegue economico.
