"""EMERALD-AI FastAPI application — production scoring + explanation endpoints.

Endpoints (proposal §5.14):
    GET  /healthz         — liveness probe.
    GET  /model_card      — model + datasheet + governance metadata.
    GET  /portfolio       — KPI aggregates over the supervisory pool.
    GET  /global_importance — top-k features by permutation importance.
    GET  /fairness_audit  — per-axis DP/EO/PP/ECE gaps as structured JSON.
    POST /score           — single applicant → P(Y=1) + risk band + conformal.
    POST /explain         — applicant → top-k local contributions + counterfactual.
    POST /batch_score     — CSV upload → scored CSV.

CORS is enabled for localhost dev so the React SPA in apps/web/ can hit this
service without a proxy. Tighten for production.

Run:
    python -m emerald_ai api
    uvicorn apps.api.main:app --reload
"""
from __future__ import annotations

import io
from typing import Any

import numpy as np
import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from emerald_ai import __version__
from emerald_ai.config import PATHS

app = FastAPI(
    title="EMERALD-AI",
    version=__version__,
    description="Explainable, calibrated, audit-ready green-loan credit scoring.",
)

# Permissive dev-only CORS — production should restrict allow_origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# Lazy model loading — keeps /healthz fast even when artefacts are missing
# -----------------------------------------------------------------------------
ARTEFACT_PATHS = {
    "model": PATHS.root / "models" / "current_model.joblib",
    "preprocessor": PATHS.root / "models" / "preprocessor.joblib",
    "conformal": PATHS.root / "models" / "conformal_marginal.joblib",
    "feature_names": PATHS.root / "models" / "feature_names.json",
}

_state: dict[str, Any] = {"loaded": False}


def _load_state() -> dict[str, Any]:
    if _state.get("loaded"):
        return _state

    import json
    try:
        import joblib
    except ImportError as exc:  # pragma: no cover
        raise HTTPException(503, f"joblib not available: {exc}") from exc

    missing = [n for n, p in ARTEFACT_PATHS.items() if not p.exists()]
    if missing:
        raise HTTPException(
            503,
            detail={
                "code": "artefacts_not_trained",
                "missing": missing,
                "remediation": "Run `python -m emerald_ai train` to produce model artefacts.",
            },
        )
    _state["model"] = joblib.load(ARTEFACT_PATHS["model"])
    _state["preprocessor"] = joblib.load(ARTEFACT_PATHS["preprocessor"])
    _state["conformal"] = joblib.load(ARTEFACT_PATHS["conformal"])
    _state["feature_names"] = json.loads(ARTEFACT_PATHS["feature_names"].read_text())
    _state["loaded"] = True
    return _state


# -----------------------------------------------------------------------------
# Schemas
# -----------------------------------------------------------------------------
class HealthResponse(BaseModel):
    status: str
    version: str
    artefacts_present: bool


class ModelCard(BaseModel):
    name: str = "EMERALD-AI"
    version: str
    proposal_version: str = "v0.4.1"
    primary_metrics: list[str] = Field(
        default_factory=lambda: ["PR-AUC (minority)", "within-minority ECE", "recall@top-decile"]
    )
    governance_artefacts: list[str] = Field(
        default_factory=lambda: [
            "data/governance/datasheet.md",
            "data/governance/feature_catalogue.yaml",
            "data/governance/eda_report.md",
            "data/governance/preprocess_report.md",
            "data/governance/selection_report.md",
            "data/governance/imbalance_report.md",
            "data/governance/training_report.md",
            "data/governance/explain_report.md",
            "data/governance/fairness_report.md",
        ]
    )
    regulatory_alignment: list[str] = Field(
        default_factory=lambda: [
            "EU AI Act Annex III (high-risk credit scoring)",
            "FCA Consumer Duty PS22/9",
            "EBA/GL/2020/06",
        ]
    )
    feature_names: list[str] = Field(default_factory=list)
    best_family: str | None = None


class ApplicantPayload(BaseModel):
    features: dict[str, float] = Field(..., description="Map of feature_name -> value")


class ScoreResponse(BaseModel):
    probability_creditworthy: float
    risk_band: str
    conformal_interval_alpha: float
    conformal_includes_creditworthy: bool
    conformal_includes_delinquent: bool


class ExplainResponse(BaseModel):
    top_contributions: list[dict]
    counterfactual: dict | None
    note: str = (
        "Local explanations use a coefficient/importance proxy until shap is "
        "added; counterfactual is a single-feature greedy search until DiCE "
        "is wired in."
    )


class PortfolioKPIs(BaseModel):
    n_rows: int
    n_labelled: int
    prevalence: float
    mean_score: float
    approve_rate_at_threshold: dict[str, float]
    top_industries_by_volume: list[dict]


class FairnessGapJSON(BaseModel):
    axis: str
    gaps: dict[str, float]
    groups: list[dict]


class GlobalImportanceRow(BaseModel):
    feature: str
    importance_mean: float
    importance_std: float


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------
@app.get("/healthz", response_model=HealthResponse, tags=["ops"])
def healthz() -> HealthResponse:
    artefacts_present = all(p.exists() for p in ARTEFACT_PATHS.values())
    return HealthResponse(status="ok", version=__version__, artefacts_present=artefacts_present)


@app.get("/model_card", response_model=ModelCard, tags=["governance"])
def model_card() -> ModelCard:
    # Best family is optional — loaded if present
    best_family_path = PATHS.root / "models" / "best_family.txt"
    best = best_family_path.read_text().strip() if best_family_path.exists() else None
    feature_names: list[str] = []
    fn_path = ARTEFACT_PATHS["feature_names"]
    if fn_path.exists():
        import json
        feature_names = json.loads(fn_path.read_text())
    return ModelCard(version=__version__, feature_names=feature_names, best_family=best)


def _row_from_payload(payload: ApplicantPayload, feature_names: list[str]) -> np.ndarray:
    return np.asarray([float(payload.features.get(n, 0.0)) for n in feature_names], dtype=float)


def _scores_full_dataset() -> tuple[np.ndarray, pd.Series, pd.DataFrame]:
    """Compute predictions on the entire labelled supervisory pool."""
    from emerald_ai.data.eda import split_xy
    from emerald_ai.data.load import load_labelled

    state = _load_state()
    df = load_labelled()
    X, y = split_xy(df)
    X_t = state["preprocessor"].transform(X)
    classes = getattr(state["model"], "classes_", np.array([0, 1]))
    pos_idx = int(np.where(classes == 1)[0][0]) if 1 in classes else 1
    scores = state["model"].predict_proba(X_t)[:, pos_idx]
    return scores, y, X


@app.post("/score", response_model=ScoreResponse, tags=["scoring"])
def score(payload: ApplicantPayload) -> ScoreResponse:
    state = _load_state()
    feature_names: list[str] = state["feature_names"]
    model = state["model"]
    conf = state["conformal"]
    x = _row_from_payload(payload, feature_names).reshape(1, -1)
    proba = model.predict_proba(x)[0]
    classes = getattr(model, "classes_", np.array([0, 1]))
    pos_idx = int(np.where(classes == 1)[0][0]) if 1 in classes else 1
    p1 = float(proba[pos_idx])
    band = "high_risk" if p1 < 0.5 else ("watch" if p1 < 0.8 else "approve")
    cset = conf.predict(np.array([p1]))
    return ScoreResponse(
        probability_creditworthy=p1,
        risk_band=band,
        conformal_interval_alpha=getattr(conf, "alpha", 0.1),
        conformal_includes_creditworthy=bool(cset.include_1[0]),
        conformal_includes_delinquent=bool(cset.include_0[0]),
    )


@app.post("/explain", response_model=ExplainResponse, tags=["explainability"])
def explain(payload: ApplicantPayload) -> ExplainResponse:
    from emerald_ai.explain import local_explanation, nearest_counterfactual

    state = _load_state()
    feature_names: list[str] = state["feature_names"]
    model = state["model"]
    x = _row_from_payload(payload, feature_names)

    contribs = local_explanation(model, x, feature_names, top_k=10)
    actionable = [c.name for c in contribs[:5]]
    cf = nearest_counterfactual(model, x, feature_names, actionable_features=actionable)
    return ExplainResponse(
        top_contributions=[
            {"feature": c.name, "value": c.value, "contribution": c.contribution, "direction": c.direction}
            for c in contribs
        ],
        counterfactual={
            "feature": cf.feature,
            "original_value": cf.original_value,
            "new_value": cf.new_value,
            "delta": cf.delta,
            "original_prediction": cf.original_prediction,
            "new_prediction": cf.new_prediction,
            "flipped": cf.flipped,
        } if cf is not None else None,
    )


@app.post("/batch_score", tags=["scoring"])
async def batch_score(file: UploadFile = File(...)) -> StreamingResponse:
    """Accept a CSV with one applicant per row, return the same CSV plus score columns."""
    state = _load_state()
    feature_names: list[str] = state["feature_names"]

    content = await file.read()
    try:
        df_in = pd.read_csv(io.BytesIO(content))
    except Exception as exc:
        raise HTTPException(400, f"Could not parse CSV: {exc}") from exc

    # Align columns to the post-preprocessing feature space; missing → 0.0
    matrix = np.zeros((len(df_in), len(feature_names)), dtype=float)
    for j, name in enumerate(feature_names):
        if name in df_in.columns:
            matrix[:, j] = pd.to_numeric(df_in[name], errors="coerce").fillna(0.0).to_numpy()

    model = state["model"]
    classes = getattr(model, "classes_", np.array([0, 1]))
    pos_idx = int(np.where(classes == 1)[0][0]) if 1 in classes else 1
    probas = model.predict_proba(matrix)[:, pos_idx]

    conf = state["conformal"]
    sets = conf.predict(probas)

    df_out = df_in.copy()
    df_out["probability_creditworthy"] = probas
    df_out["risk_band"] = np.where(probas < 0.5, "high_risk",
                                    np.where(probas < 0.8, "watch", "approve"))
    df_out["conformal_includes_creditworthy"] = sets.include_1
    df_out["conformal_includes_delinquent"] = sets.include_0

    buf = io.StringIO()
    df_out.to_csv(buf, index=False)
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=scored_{file.filename}"},
    )


@app.get("/portfolio", response_model=PortfolioKPIs, tags=["governance"])
def portfolio() -> PortfolioKPIs:
    scores, y, X = _scores_full_dataset()
    y_arr = y.to_numpy().astype(int)
    n_rows = int(len(y_arr))
    n_labelled = int(np.isfinite(y_arr).sum())
    prevalence = float((y_arr == 0).mean())
    mean_score = float(scores.mean())
    thresholds = [0.5, 0.7, 0.9]
    approve = {f"thr_{t:.1f}": float((scores >= t).mean()) for t in thresholds}

    if "Industry" in X.columns:
        top = (
            X.assign(_score=scores)
            .groupby("Industry", dropna=True)
            .agg(volume=("_score", "size"), mean_score=("_score", "mean"))
            .sort_values("volume", ascending=False)
            .head(10)
            .reset_index()
            .to_dict(orient="records")
        )
    else:
        top = []
    return PortfolioKPIs(
        n_rows=n_rows,
        n_labelled=n_labelled,
        prevalence=prevalence,
        mean_score=mean_score,
        approve_rate_at_threshold=approve,
        top_industries_by_volume=top,
    )


@app.get("/global_importance", response_model=list[GlobalImportanceRow], tags=["explainability"])
def global_importance_endpoint(top_k: int = 20, n_repeats: int = 3) -> list[GlobalImportanceRow]:
    from emerald_ai.explain import global_importance

    state = _load_state()
    scores, y, X = _scores_full_dataset()
    X_t = state["preprocessor"].transform(X)
    imp = global_importance(
        state["model"], X_t, y,
        feature_names=state["feature_names"],
        n_repeats=n_repeats,
    )
    return [
        GlobalImportanceRow(
            feature=r["feature"],
            importance_mean=float(r["importance_mean"]),
            importance_std=float(r["importance_std"]),
        )
        for _, r in imp.head(top_k).iterrows()
    ]


@app.get("/fairness_audit", response_model=list[FairnessGapJSON], tags=["governance"])
def fairness_audit_endpoint() -> list[FairnessGapJSON]:
    from emerald_ai.fairness import audit_predictions

    scores, y, X = _scores_full_dataset()
    sensitive = {}
    for axis in ("Industry", "Borrower State"):
        if axis in X.columns:
            sensitive[axis] = X[axis].fillna("__missing__").to_numpy()
    aud = audit_predictions(np.asarray(y), scores, sensitive)
    out: list[FairnessGapJSON] = []
    for axis_name, rows in aud.axes.items():
        groups = [
            {
                "group": str(r.group),
                "n": r.n,
                "selection_rate": r.selection_rate,
                "tpr": r.tpr,
                "fpr": r.fpr,
                "precision": r.precision,
                "ece": r.ece,
            }
            for r in sorted(rows, key=lambda r: r.n, reverse=True)[:15]
        ]
        out.append(FairnessGapJSON(
            axis=axis_name,
            gaps=aud.gaps[axis_name],
            groups=groups,
        ))
    return out
