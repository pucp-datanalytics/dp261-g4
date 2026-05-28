# Checklist Sprint 6 - Deployment MVP

Este checklist resume lo que debe validarse para cerrar el Sprint 6 segun el PDF del curso.

## Rol 1 - Project Manager

- Issues PB-19, PB-20, PB-21 y monitoreo creados en GitHub Projects.
- Secuencia validada: API -> AWS -> dashboard -> monitoreo.
- Demo en vivo planificada con URL de dashboard y URL de API.
- Riesgos documentados: credenciales temporales AWS, endpoint variable y expiracion de sesion.

## Rol 2 - API Engineer

- API FastAPI en `api/`.
- Endpoints disponibles:
  - `GET /health`
  - `GET /version`
  - `POST /predict`
  - `POST /predict_batch`
- Dockerfile de API en `api/Dockerfile`.
- Contratos JSON en `handoff/contracts/`.
- Logs JSON con `latency_ms`, `event`, `status_code`, `request_id`, `proba`, `model_version` y `model_sha`.
- `API_KEY` opcional via variable de entorno y header `x-api-key`.

## Rol 3 - Cloud / DevOps

- Crear o confirmar repositorio ECR para la API.
- Configurar secrets de GitHub:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_SESSION_TOKEN`
  - `AWS_REGION`
  - `ECR_REGISTRY`
  - `ECR_REPOSITORY_API`
  - `EC2_HOST`
  - `EC2_USER`
  - `EC2_SSH_KEY`
  - `API_URL`
  - `API_KEY` si se habilita seguridad
- Ejecutar workflow manual `Deploy Sprint 6 API`.
- Verificar que la API responda en el puerto 8000 o detras de API Gateway/ALB.
- Actualizar `API_URL` para que el dashboard desplegado consuma la API real.
- En el workflow principal `.github/workflows/cd.yml`, confirmar que queden vivos dos contenedores:
  - `sprint6-api` en puerto `8000`;
  - `dp261-g4` en puerto `8080`.
- Si dashboard y API corren en la misma EC2 dentro de Docker, usar `API_URL=http://sprint6-api:8000` dentro del contenedor del dashboard.

## Rol 4 - Integration Engineer

- Verificar dashboard desplegado en puerto 8080 o servicio equivalente.
- Confirmar que `API_URL` apunta al endpoint real de la API.
- Si existe `API_KEY`, confirmar que el dashboard la recibe por variable de entorno.
- Probar:
  - Simulador economico individual.
  - Dataset cargado por usuario.
  - Boton de prueba contra `POST /predict_batch`.
- Validar mensajes amigables ante timeout, 400, 401 y 500.

## Rol 5 - SRE / Monitoring

- Confirmar log group de CloudWatch para la API.
- Ejecutar consultas de `monitoring/cloudwatch-log-insights.md`.
- Crear metric filters o widgets para:
  - latencia p50/p95/p99,
  - throughput,
  - error rate 5xx,
  - distribucion de probabilidades.
- Crear alarmas descritas en `monitoring/cloudwatch-alarms.json`.
- Completar runbook con endpoint final, log group, alarmas y responsable de escalamiento.

## Comandos minimos de demo

```powershell
curl.exe $env:API_URL/health
curl.exe $env:API_URL/version
curl.exe -X POST "$env:API_URL/predict" -H "Content-Type: application/json" --data-binary "@handoff/contracts/c_example_request.json"
curl.exe -X POST "$env:API_URL/predict_batch" -H "Content-Type: application/json" --data-binary "@handoff/contracts/c_example_batch_request.json"
```

En la EC2 tambien debe funcionar:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/version
curl -X POST "http://localhost:8000/predict" -H "Content-Type: application/json" --data-binary "@handoff/contracts/c_example_request.json"
```

Si la API usa llave:

```powershell
curl.exe -X POST "$env:API_URL/predict" -H "Content-Type: application/json" -H "x-api-key: $env:API_KEY" --data-binary "@handoff/contracts/c_example_request.json"
```
