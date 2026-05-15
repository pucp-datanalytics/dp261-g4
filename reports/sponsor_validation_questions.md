# Preguntas de Validacion para Sponsor

## Objetivo

Validar los supuestos economicos usados en `notebooks/15_business_value.ipynb` antes de tomar una decision de despliegue en Sprint 6.

El analisis actual es correcto como simulacion, pero los valores de negocio dependen de costos y beneficios que deben venir del sponsor o del area comercial.

## Preguntas Criticas

### 1. Valor de una compra

1. Cual es el ticket promedio por compra?
2. Cual es el margen promedio por compra, no solo el ingreso bruto?
3. El valor esperado cambia entre usuario nuevo y usuario recurrente?
4. Existe informacion historica de recompra o lifetime value?

### 2. Costo de contacto

1. Cuanto cuesta contactar a un usuario nuevo?
2. Cuanto cuesta contactar a un usuario recurrente?
3. El canal sera email, SMS, llamada, retargeting ads, push notification u otro?
4. Existe un limite diario/semanal de usuarios que se pueden contactar?
5. Hay penalizacion por contactar a usuarios que no compran, por ejemplo baja de suscripcion o queja?

### 3. Costo de oportunidad

1. Que tan grave es no contactar a un comprador potencial?
2. Una compra perdida se considera perdida total o puede ocurrir igual sin intervencion?
3. Hay promociones o descuentos asociados que reduzcan el margen?
4. El objetivo principal es maximizar ventas, margen o eficiencia de campana?

### 4. Politica por segmento

1. Tiene sentido tratar distinto a `New_Visitor` y `Returning_Visitor`?
2. Contactar usuarios nuevos es realmente mas caro que contactar recurrentes?
3. Para recurrentes, se acepta mayor cantidad de falsos positivos?
4. Para usuarios nuevos, se prefiere alta precision aunque se pierdan algunos compradores?

### 5. Disponibilidad operacional de variables

1. `PageValues` esta disponible antes de decidir contactar al usuario?
2. Si `PageValues` se calcula despues de una compra, puede usarse en produccion?
3. En que momento se ejecutara el modelo: durante la sesion, al cierre de sesion o al dia siguiente?
4. Las variables de navegacion se capturan en tiempo real o batch?

### 6. Umbral de decision

1. El negocio prefiere una politica conservadora o agresiva?
2. Cual es el minimo de precision aceptable?
3. Cual es el minimo de recall aceptable?
4. Se quiere un umbral global o umbrales distintos por segmento?
5. Debe priorizarse top-k usuarios por presupuesto de campana en vez de threshold fijo?

## Supuestos Actuales del Analisis

| Escenario | TP | FP | FN | TN |
|---|---:|---:|---:|---:|
| Global conservador | 100 | -20 | -80 | 0 |
| Maxima captura | 100 | -10 | -120 | 0 |
| Usuarios nuevos | 120 | -35 | -90 | 0 |
| Usuarios recurrentes | 80 | -5 | -70 | 0 |

Donde:

- TP: comprador correctamente identificado.
- FP: usuario contactado que no compra.
- FN: comprador no detectado.
- TN: no comprador correctamente ignorado.

## Decisiones que el Sponsor Debe Confirmar

1. Valores finales para TP, FP, FN y TN.
2. Si se aprueba estrategia segmentada por tipo de visitante.
3. Si se permite usar `PageValues` en produccion.
4. Si la campana se ejecutara por threshold o por top-k.
5. Si se continua a Sprint 6 con MVP.

## Recomendacion Provisional para Validar

| Escenario | Recomendacion provisional |
|---|---|
| Ranking global | XGBoost tuned |
| Usuarios nuevos | XGBoost con politica conservadora |
| Usuarios recurrentes | Random Forest o politica de bajo threshold |
| Maxima captura | Bajo threshold, sujeto a costo de falsos positivos |

## Resultado Esperado de la Reunion

Al finalizar la validacion con sponsor se debe poder completar esta decision:

```text
Se aprueba / no se aprueba avanzar a Sprint 6 con el MVP.

Modelo/politica aprobada:
Segmentos incluidos:
Thresholds aprobados:
Canal de contacto:
Costo FP validado:
Valor TP validado:
Costo FN validado:
Restricciones operativas:
```

## Pendientes si No Hay Validacion

Si no se logra validar con sponsor, el reporte final debe declarar:

- Los resultados economicos son simulaciones.
- Los thresholds optimos son provisionales.
- La decision de despliegue queda condicionada a validar costos y margen.
- Se puede avanzar con dashboard y handoff tecnico, pero no con recomendacion economica cerrada.
