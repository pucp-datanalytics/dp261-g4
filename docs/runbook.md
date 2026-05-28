# Runbook Sprint 6 - API, Dashboard y Monitoreo

## Objetivo

Mantener operativo el MVP del Sprint 6: API FastAPI, dashboard Streamlit desplegado y monitoreo basico en AWS.

## Roles de escalamiento

| Area | Responsable | Accion principal |
|---|---|---|
| API Engineer | Responsable PB-19 | Revisar API, contratos, modelo, Docker y errores de prediccion. |
| Cloud / DevOps | Responsable PB-20 | Revisar EC2/ECR/API Gateway/secrets/CI-CD. |
| Integration Engineer | Responsable PB-21 | Revisar dashboard, `API_URL`, `API_KEY` y flujo usuario -> API. |
| SRE / Monitoring | Rol 5 | Revisar CloudWatch, alarmas, latencia, throughput y error rate. |

## Variables operativas

Nunca guardar estos valores en el repositorio. Deben configurarse como variables de entorno o GitHub Secrets.

- `API_URL`: endpoint base de la API.
- `API_KEY`: llave opcional enviada por el dashboard en header `x-api-key`.
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_SESSION_TOKEN`
- `AWS_REGION`
- `EC2_HOST`
- `EC2_USER`
- `EC2_SSH_KEY`
- `ECR_REGISTRY`
- `ECR_REPOSITORY_API`

## Health checks

```powershell
curl.exe $env:API_URL/health
curl.exe $env:API_URL/version
```

En la EC2, si el workflow levanto ambos contenedores, tambien se puede probar la API desde el host:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/version
```

Respuesta esperada de `/health`:

```json
{
  "status": "ok",
  "service": "sprint6-pb19-api"
}
```

## Prediccion de prueba

Sin API key:

```powershell
curl.exe -X POST "$env:API_URL/predict" -H "Content-Type: application/json" --data-binary "@handoff/contracts/c_example_request.json"
```

Con API key:

```powershell
curl.exe -X POST "$env:API_URL/predict" -H "Content-Type: application/json" -H "x-api-key: $env:API_KEY" --data-binary "@handoff/contracts/c_example_request.json"
```

## Prediccion batch para dashboard

```powershell
curl.exe -X POST "$env:API_URL/predict_batch" -H "Content-Type: application/json" --data-binary "@handoff/contracts/c_example_batch_request.json"
```

## Logs esperados

La API emite logs JSON por `stdout`. CloudWatch debe capturar campos como:

- `event`
- `endpoint`
- `status_code`
- `latency_ms`
- `request_id`
- `proba`
- `prediction`
- `model_version`
- `model_sha`

Eventos principales:

- `startup`
- `health`
- `version`
- `predict`
- `predict_batch`
- `request`
- `request_error`
- `predict_error`
- `auth_error`

## Metricas minimas

Usar `monitoring/cloudwatch-log-insights.md` para calcular:

- latencia p50/p95/p99,
- throughput por endpoint,
- error rate 5xx,
- distribucion de probabilidades,
- trazabilidad por `request_id`.

## Alarmas minimas

Ver `monitoring/cloudwatch-alarms.json`.

Alarmas recomendadas:

- error rate 5xx alto,
- latencia p95 mayor al SLA,
- caida de throughput durante ventana de demo,
- CPU/memoria alta del contenedor o EC2.

## Procedimiento ante incidente

1. Validar `/health` y `/version`.
2. Revisar si el dashboard tiene `API_URL` correcto.
3. Revisar si la API requiere `API_KEY` y si el dashboard la tiene configurada.
4. Revisar logs CloudWatch filtrando por `request_id`, `predict_error`, `request_error` o `auth_error`.
5. Revisar estado del contenedor en EC2:

```bash
sudo docker ps
sudo docker logs --tail 100 dp261-g4
sudo docker logs --tail 100 sprint6-api
```

6. Reiniciar contenedor si el servicio esta caido:

```bash
sudo docker restart sprint6-api
sudo docker restart dp261-g4
```

7. Si el despliegue nuevo falla, volver a la imagen anterior en ECR o relanzar el ultimo commit estable.

## Riesgos conocidos

- En AWS Academy las credenciales y tokens pueden cambiar por sesion.
- La IP publica de EC2 puede cambiar si la instancia se reinicia sin Elastic IP.
- El dashboard puede seguir funcionando con fallback local aunque la API no este disponible; para demo Sprint 6 debe mostrarse la integracion REST real.
- No exponer secretos en codigo, notebooks, README ni capturas publicas.
