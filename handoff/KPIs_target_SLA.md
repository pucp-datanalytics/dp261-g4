# KPIs, Targets and SLA - Sprint 6 MVP

## KPIs de Negocio

| KPI | Target inicial | Fuente |
|---|---:|---|
| Conversion capturada en top 20% | >= 70% de compradores | Gain curve Sprint 5 |
| Precision usuarios nuevos | >= 80% | Evaluacion por VisitorType |
| Recall recurrentes | >= 80% si costo FP bajo | Evaluacion por VisitorType |
| Incremental value | Positivo bajo supuestos validados | Business Value Sprint 5 |

## KPIs Tecnicos

| KPI | Target inicial |
|---|---:|
| Latencia por prediccion | < 500 ms en MVP local/API simple |
| Disponibilidad MVP | >= 95% durante demo/piloto |
| Error rate API | < 1% requests invalidos no controlados |
| Validacion schema | 100% requests validados |
| Trazabilidad de predicciones | 100% de predicciones registradas |
| Threshold configurable | Disponible sin reentrenar modelo |

## Monitoreo Recomendado

- Numero de sesiones scoreadas.
- Distribucion de probabilidades.
- Porcentaje de usuarios contactados.
- Conversion real posterior a contacto.
- Precision y recall recalculados semanalmente.
- Drift en `VisitorType`, `PageValues`, `BounceRates`, `ExitRates`.
- Threshold usado en cada decision.
- Modelo/version usado en cada prediccion.
- Motivo de rechazo para requests invalidos.

## Criterios Go / No-Go

Go:

- Sponsor valida costos y margen.
- API respeta contratos de `handoff/contracts/`.
- Dashboard muestra KPIs principales.
- Threshold configurable.

No-Go:

- `PageValues` no disponible en produccion y no hay modelo alternativo.
- Costos de contacto no validados.
- No existe trazabilidad de predicciones.
- Dashboard/API usan features distintas.
- No se puede cambiar threshold sin modificar codigo.
- El dashboard no puede ejecutarse por dependencias ausentes antes de la demo.

## Evidencia Minima para Cierre QA

| Evidencia | Responsable | Estado esperado |
|---|---|---|
| Dashboard ejecutado localmente o limitacion documentada | Dashboard Developer / QA | OK o pendiente justificado |
| Contratos JSON validados | QA | OK |
| Reporte final revisado | Documentation Lead / QA | OK |
| Preguntas sponsor preparadas | QA & Stakeholder Reviewer | OK |
| Decision Go/No-Go documentada | QA & Stakeholder Reviewer | OK |
