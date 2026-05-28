# Consultas CloudWatch Logs Insights - Sprint 6

Usar estas consultas sobre el log group donde Docker/AWS capture el `stdout` de la API FastAPI.

## Latencia p50 / p95 / p99 de `/predict`

```sql
fields @timestamp, event, endpoint, latency_ms
| filter event = "predict" or endpoint = "/predict"
| stats pct(latency_ms, 50) as p50_ms,
        pct(latency_ms, 95) as p95_ms,
        pct(latency_ms, 99) as p99_ms,
        count(*) as requests
  by bin(5m)
| sort @timestamp desc
```

## Throughput por endpoint

```sql
fields @timestamp, event, endpoint, status_code
| filter event = "request"
| stats count(*) as requests by endpoint, bin(1m)
| sort @timestamp desc
```

## Error rate 5xx

```sql
fields @timestamp, event, endpoint, status_code, error
| filter status_code >= 500
| stats count(*) as errors_5xx by endpoint, bin(5m)
| sort @timestamp desc
```

## Distribucion de probabilidades para drift operativo

```sql
fields @timestamp, event, proba, prediction, model_version, model_sha
| filter event = "predict"
| stats avg(proba) as avg_proba,
        pct(proba, 50) as p50_proba,
        pct(proba, 95) as p95_proba,
        count(*) as predictions,
        sum(prediction) as positive_predictions
  by model_version, model_sha, bin(1h)
| sort @timestamp desc
```

## Trazabilidad por request

```sql
fields @timestamp, request_id, event, endpoint, status_code, latency_ms, error
| filter ispresent(request_id)
| sort @timestamp desc
| limit 50
```
