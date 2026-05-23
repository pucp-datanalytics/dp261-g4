\# Runbook – API de Predicción (MVP)



\## Equipo Responsable y Contactos



| Rol | Responsable | Correo | Contacto |

|------|-------------|---------|-----------|

| \*\*SRE / Monitoreo Principal\*\* | Solanch Nikol Alexandra Solaligue Limache | f0556376@pucp.edu.pe | 944487921 |

| \*\*API Engineer\*\* | Julio Anthony Misari Rosales | f1276544@pucp.edu.pe | 962570825 |

| \*\*DevOps \& Infraestructura\*\* | Perla Doris Gavilano Zavala | f1237483@pucp.edu.pe | 978581469 |

| \*\*Integración y Dashboard\*\* | Juan Ramos Villavicencio | f0990541@pucp.edu.pe | 996083615 |



\### Flujo de Comunicación



Ante cualquier incidente o comportamiento inesperado del sistema, el primer punto de revisión será el área de monitoreo (SRE). Dependiendo de la naturaleza del problema, se escalará al responsable correspondiente:



\- Problemas relacionados con la API o modelos → \*\*Julio Misari\*\*

\- Incidentes de despliegue, contenedores o infraestructura AWS → \*\*Perla Gavilano\*\*

\- Errores en visualización o dashboard → \*\*Juan Ramos\*\*



\---



\# Monitoreo del Sistema



Los siguientes indicadores son monitoreados continuamente para garantizar la estabilidad y disponibilidad del servicio:



\- \*\*Latencia de la API (p95):\*\*  

&#x20; Se genera una alerta si supera los \*\*500 ms\*\*.



\- \*\*Tasa de errores HTTP 5xx:\*\*  

&#x20; Se considera crítico si excede el \*\*2% durante 5 minutos consecutivos\*\*.



\- \*\*Uso de CPU del contenedor:\*\*  

&#x20; Si el consumo supera el \*\*80% durante más de 10 minutos\*\*, se evalúa escalamiento o reinicio del servicio.



\---



\# Procedimiento ante Incremento de Errores (>2%)



\## 1. Revisión Inicial



\- Verificar logs en \*\*AWS CloudWatch\*\*

\- Revisar métricas y comportamiento general en el dashboard de monitoreo



> Nota: actualmente los logs aún no se encuentran estructurados en formato JSON.



\---



\## 2. Validación de Contenedor



Si se detectan timeouts o degradación del servicio, reiniciar el contenedor:



```bash

sudo docker restart dp261-g4

