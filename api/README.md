# `api/` — FastAPI Backend

Production scoring + explanation service for EMERALD-AI. Hosts the REST endpoints consumed by the React frontend (`../web/`) and any external integration.

## Run locally

```bash
make api
# or directly:
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Then visit:
- http://localhost:8000/docs — interactive Swagger UI
- http://localhost:8000/healthz — liveness probe

## Planned endpoints

| Method | Path | Purpose |
|---|---|---|
| GET  | `/healthz` | Liveness probe |
| POST | `/score` | Single applicant → probability + risk band + conformal interval |
| POST | `/batch_score` | CSV upload → scored CSV with per-row top-3 SHAP features |
| POST | `/explain` | Applicant → SHAP waterfall + counterfactual |
| GET  | `/portfolio` | Portfolio-level KPIs and distributions |
| GET  | `/fairness_audit` | Group-fairness panel (proxy axes) |
| GET  | `/model_card` | Active model + datasheet metadata |

## Architecture notes

- All requests validated by Pydantic v2 models.
- Structured JSON logging for post-market monitoring (EU AI Act Article 61).
- Prometheus metrics exposed at `/metrics` (planned).
- Model + preprocessor loaded once at startup from MLflow registry.
