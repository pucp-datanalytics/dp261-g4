# Resumen de dataset cargado

Este reporte documenta la funcionalidad de carga dinamica desde el dashboard.

## Flujo

1. El usuario selecciona `Dataset cargado por usuario` en la barra lateral.
2. El usuario sube un CSV o XLSX.
3. El dashboard valida columnas, tipos, nulos y target opcional `Revenue`.
4. Si el archivo es valido, se generan predicciones con el modelo final.
5. Si existe `Revenue`, se recalculan metricas reales y valor economico.
6. Si no existe `Revenue`, se muestran predicciones y valor potencial estimado.

## Archivos locales

- `data/processed/c_uploaded_dataset_validated.csv`
- `data/processed/c_uploaded_predictions.csv`
- `models/c_uploaded_dataset_business_value.csv`, cuando aplica
- `models/c_uploaded_dataset_economic_comparison.csv`, cuando aplica

## Nota metodologica

El dashboard no reentrena el modelo con datasets cargados. La carga dinamica solo sirve para scoring, analisis ejecutivo y valor de negocio bajo supuestos configurables.
