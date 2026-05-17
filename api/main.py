"""EMERALD-AI FastAPI application — production scoring + explanation endpoints.

Endpoints (planned, see proposal §5.14):
    GET  /healthz              liveness probe
    POST /score                single applicant → probability + risk band + conformal interval
    POST /batch_score          CSV upload → scored CSV
    POST /explain              applicant → SHAP waterfall + counterfactual
    GET  /portfolio            portfolio-level analytics + KPIs
    GET  /fairness_audit       group-fairness panel
    GET  /model_card           model + datasheet metadata

Run locally: ``uvicorn api.main:app --reload``
Or:          ``make api``
"""
from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from emerald_ai import __version__

app = FastAPI(
    title="EMERALD-AI",
    version=__version__,
    description="Explainable, calibrated, audit-ready green-loan credit scoring.",
)


class HealthResponse(BaseModel):
    """Liveness probe response."""

    status: str
    version: str


@app.get("/healthz", response_model=HealthResponse, tags=["ops"])
def healthz() -> HealthResponse:
    """Liveness probe — returns 200 + version when the service is up."""
    return HealthResponse(status="ok", version=__version__)


# TODO: /score, /batch_score, /explain, /portfolio, /fairness_audit, /model_card
#       wired in once the ML pipeline is implemented.
