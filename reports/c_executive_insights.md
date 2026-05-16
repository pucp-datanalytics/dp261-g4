# Executive Insights

## Lectura general

El modelo final identifica visitantes con mayor probabilidad de compra y permite priorizar acciones comerciales sobre sesiones de alto valor potencial.

## Insights principales

- La conversion historica es baja frente al total de sesiones, por lo que conviene focalizar incentivos.
- El F1-score es la metrica principal porque equilibra precision y recall en un contexto desbalanceado.
- El threshold de negocio recomendado puede ser menor a 0.5 porque perder compradores potenciales puede costar mas que activar una accion comercial adicional.
- Variables como el valor estimado de paginas, el tiempo en paginas de producto y las tasas de salida/rebote ayudan a interpretar la intencion.

## Acciones sugeridas

1. Activar ofertas o chat prioritario para visitantes de alta intencion.
2. Usar recomendaciones o recordatorios para visitantes de intencion media.
3. Evitar descuentos indiscriminados para visitantes de baja intencion.
4. Medir conversion incremental despues de aplicar acciones.
5. Revisar costos reales antes de llevar el modelo a produccion.

## Riesgos

- Los supuestos de costo-beneficio deben validarse con negocio.
- El comportamiento de usuarios puede cambiar por campanas, temporada o cambios de UX.
- Sprint 6 debe agregar API, seguridad, monitoreo y validacion productiva.
