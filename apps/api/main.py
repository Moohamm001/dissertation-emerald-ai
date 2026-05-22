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

# -----------------------------------------------------------------------------
# Plain-English copy: algorithm names and pipeline steps
# -----------------------------------------------------------------------------
ALGORITHM_LABEL: dict[str, str] = {
    "xgboost": "XGBoost — gradient-boosted decision trees",
    "lr_l1": "Logistic Regression (L1 / lasso penalty)",
    "lr_l2": "Logistic Regression (L2 / ridge penalty)",
    "rf": "Random Forest classifier",
    "svm_rbf": "Support Vector Machine (RBF kernel)",
    "lightgbm": "LightGBM — gradient-boosted decision trees",
    "catboost": "CatBoost — gradient-boosted decision trees",
}

ALGORITHM_PLAIN: dict[str, str] = {
    "xgboost": (
        "Imagine hundreds of small yes/no decision trees, each one trained to fix "
        "the mistakes of the ones before it. The final score is the average of all "
        "their votes. That ensemble of trees is what XGBoost is."
    ),
    "lr_l1": (
        "A weighted scorecard: each feature gets a number, the model adds them up "
        "and converts the total into a probability. L1 keeps the scorecard short by "
        "zeroing out features that don't help."
    ),
    "lr_l2": (
        "A weighted scorecard: each feature gets a number, the model adds them up "
        "and converts the total into a probability. L2 keeps the weights small so no "
        "single feature dominates."
    ),
    "rf": (
        "A committee of hundreds of decision trees, each trained on a different "
        "slice of the data; the final answer is their majority vote."
    ),
    "svm_rbf": (
        "Tries to draw the cleanest curved boundary between repaying and defaulting "
        "applicants in feature space."
    ),
    "lightgbm": (
        "Hundreds of small yes/no decision trees built one after another, each one "
        "fixing the mistakes of the previous trees. Similar to XGBoost but tuned for speed."
    ),
    "catboost": (
        "Hundreds of small yes/no decision trees built one after another, each one "
        "fixing the mistakes of the previous trees. CatBoost is especially good at "
        "categorical fields."
    ),
}


def _training_pipeline_steps() -> list[dict[str, str]]:
    """Plain-English + technical narration of the seven training-pipeline stages."""
    return [
        {
            "step": "1. Inspect the data (EDA)",
            "plain": (
                "We open the 2019 funded green-loan spreadsheet (~14,000 loans) and "
                "look at every column: how often it's missing, what range it takes, "
                "and whether it differs between loans that repaid and loans that defaulted."
            ),
            "technical": (
                "Four-layer EDA over the 90 leakage-audit-permitted features: univariate "
                "summaries, bivariate association vs. Y (Pearson, Spearman, mutual "
                "information), segment-level conditional default rates with Wilson 95% CIs, "
                "and quarterly PSI drift diagnostics. Output: data/governance/eda_report.md."
            ),
        },
        {
            "step": "2. Clean and standardise (preprocess)",
            "plain": (
                "Drop columns that are mostly empty, fill in remaining blanks sensibly, "
                "turn text fields (e.g. industry) into numbers the model can read, and "
                "put every numeric column on the same scale."
            ),
            "technical": (
                "Four-stage ColumnTransformer: drop columns with >40% missingness and "
                "EDA-flagged time-leaking artefacts; median-impute numerics with appended "
                "missing-indicators; OneHot-encode categoricals with ≤10 levels and "
                "TargetEncode high-cardinality ones (Industry, Borrower State) with internal "
                "cross-fit; StandardScaler on all numerics."
            ),
        },
        {
            "step": "3. Pick the features that matter (selection)",
            "plain": (
                "Out of 90 fields, find the ~20 that actually carry information about "
                "whether a loan will be repaid. Anything irrelevant is dropped."
            ),
            "technical": (
                "Two-stage selection: Stage 1 mutual-information filter (drops the bottom "
                "decile). Stage 2 bootstrap-stability wrapper using RandomForest impurity "
                "importance — 10 stratified bootstraps, keep features with ≥60% selection "
                "frequency. Result: 20 features, master seed 42."
            ),
        },
        {
            "step": "4. Handle class imbalance",
            "plain": (
                "Only about 0.4% of loans defaulted, so the model could 'cheat' by always "
                "predicting repay. We compare strategies (no resampling, class-weighting, "
                "SMOTE) and pick the one that scores best on a fair test."
            ),
            "technical": (
                "5-fold stratified CV on a logistic-regression baseline; candidate "
                "strategies = {no_resample, class_weighted, SMOTE}; selection metric = "
                "PR-AUC × (1 − within-minority-ECE) joint score. The chosen strategy is "
                "applied inside each fold during training, never before selection."
            ),
        },
        {
            "step": "5. Train and tune (nested cross-validation)",
            "plain": (
                "Train five different algorithm families. For each family, we don't just "
                "train once — we train and test on different slices of the data many times "
                "to get an honest estimate of how it'll behave on new applicants. The "
                "best-scoring family is kept."
            ),
            "technical": (
                "Nested CV: 5 outer folds × 3 inner folds with RandomizedSearchCV "
                "(12 trial budget per family-fold). Families: lr_l1, lr_l2, svm_rbf, rf, "
                "xgboost. Selection metric: outer-fold mean PR-AUC against the minority "
                "class. Best estimator is refit on the full labelled supervisory pool."
            ),
        },
        {
            "step": "6. Calibrate the probabilities",
            "plain": (
                "When the model says '85% chance of repay', we want that to actually mean "
                "85% in the real world — not 60%, not 95%. We adjust the probability "
                "scale until that's true."
            ),
            "technical": (
                "Calibration is measured with within-minority ECE; isotonic / Platt scaling "
                "available under emerald_ai.calibration. The persisted classifier exposes "
                "predict_proba directly; conformal layer (next step) provides distribution-"
                "free guarantees on top."
            ),
        },
        {
            "step": "7. Add a confidence guarantee (conformal prediction)",
            "plain": (
                "On top of the probability we attach an honest confidence statement: "
                "either 'I'm 90% sure this applicant is creditworthy', or 'I'm 90% sure "
                "they will default', or 'I can't tell'. That last bucket is the one a "
                "human should look at."
            ),
            "technical": (
                "Split-conformal calibration at α=0.10. Produces prediction sets {0}, {1}, "
                "or {0,1}; the marginal-coverage guarantee is distribution-free under the "
                "exchangeability assumption. Persisted as models/conformal_marginal.joblib."
            ),
        },
        {
            "step": "8. Audit for fairness and explainability",
            "plain": (
                "Before trusting the model, check two things: (a) does it treat different "
                "groups (industries, regions) the same way? and (b) for any given decision, "
                "which inputs pushed the answer? Both reports are saved alongside the model."
            ),
            "technical": (
                "Fairness audit (§5.12): demographic-parity, TPR, FPR, precision and ECE "
                "gaps across Industry and Borrower-State axes. Explainability: permutation "
                "importance globally; coefficient/importance proxy locally; single-feature "
                "greedy counterfactual search. Outputs: fairness_report.md, explain_report.md."
            ),
        },
    ]


# Plain-English copy for the most common raw input fields. Used by /raw_schema
# so the React form can render sensible labels + hints without re-importing the
# proposal-side feature catalogue.
RAW_FIELD_COPY: dict[str, dict[str, str]] = {
    "Credit Score": {"label": "Credit Score", "hint": "FICO-style number; higher is safer (typical range 300–850).", "unit": "score"},
    "Revenue": {"label": "Annual Revenue", "hint": "Applicant's reported annual revenue.", "unit": "USD"},
    "Amount Funded": {"label": "Loan Amount (funded)", "hint": "Principal we are lending.", "unit": "USD"},
    "Payment Amount": {"label": "Scheduled Payment", "hint": "Size of each scheduled repayment.", "unit": "USD"},
    "Payback": {"label": "Payback Multiple", "hint": "Total repaid ÷ principal. 1.20 = 20% interest.", "unit": "×"},
    "Closed Max Term": {"label": "Loan Term", "hint": "Length of the accepted offer.", "unit": "days"},
    "# Offers Received": {"label": "# Offers Received", "hint": "How many lenders bid. More competition = healthier deal.", "unit": "count"},
    "Average Monthly Sales": {"label": "Average Monthly Sales", "hint": "Reported monthly revenue (cash-flow proxy).", "unit": "USD"},
    "Commission": {"label": "Broker Commission", "hint": "Commission paid on the deal.", "unit": "USD"},
    "Max Offer Received $": {"label": "Best Offer Received", "hint": "Highest competing offer.", "unit": "USD"},
    "Points": {"label": "Origination Points", "hint": "Origination fee in points.", "unit": "%"},
    "Prod Rank": {"label": "Product Rank", "hint": "Internal product ranking (1 = best).", "unit": "rank"},
    "Industry": {"label": "Industry", "hint": "Applicant's industry / NAICS sector."},
    "Borrower State": {"label": "Borrower State", "hint": "US state of the borrower."},
    "Lender": {"label": "Lender", "hint": "Lender that issued the loan."},
    "Product": {"label": "Loan Product", "hint": "Internal product name."},
    "Prod Type": {"label": "Product Type", "hint": "High-level product category."},
    "Payment Frequency": {"label": "Payment Frequency", "hint": "Daily / weekly / monthly schedule."},
    "Is Lender Renewal": {"label": "Lender Renewal?", "hint": "Is this a renewed loan with the same lender?"},
    "Is Borrower Renewal": {"label": "Borrower Renewal?", "hint": "Has the borrower had a loan with us before?"},
    "Is Product Renewal": {"label": "Product Renewal?", "hint": "Is this a renewal on the same product?"},
}

# Headline raw columns the simple form starts with (proposal §5.6 selection
# intersected with fields a non-technical user can plausibly fill in).
HEADLINE_RAW_COLUMNS: tuple[str, ...] = (
    "Credit Score",
    "Revenue",
    "Amount Funded",
    "Payment Amount",
    "Payback",
    "Closed Max Term",
    "# Offers Received",
    "Industry",
    "Borrower State",
)


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


class TrainingStep(BaseModel):
    step: str
    plain: str
    technical: str


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
    algorithm_label: str | None = None
    algorithm_plain: str | None = None
    headline_raw_features: list[str] = Field(default_factory=list)
    training_pipeline: list[TrainingStep] = Field(default_factory=list)
    risk_band_thresholds: dict[str, float] = Field(
        default_factory=dict,
        description="Score cut-offs derived from the training-pool percentile distribution.",
    )


class RawColumnSchema(BaseModel):
    name: str
    kind: str  # "numeric" | "categorical"
    default: Any
    headline: bool
    label: str
    hint: str | None = None
    unit: str | None = None
    p25: float | None = None
    p75: float | None = None
    p05: float | None = None
    p95: float | None = None
    top_values: list[str] | None = None


class RawSchemaResponse(BaseModel):
    columns: list[RawColumnSchema]


class RawApplicantPayload(BaseModel):
    raw: dict[str, Any] = Field(..., description="Raw column-name -> value (string/number/null).")


class ApplicantPayload(BaseModel):
    features: dict[str, float] = Field(..., description="Map of feature_name -> value")


class ScoreResponse(BaseModel):
    probability_creditworthy: float
    risk_band: str
    score_percentile: float | None = None
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

    algo_label = ALGORITHM_LABEL.get(best) if best else None
    algo_plain = ALGORITHM_PLAIN.get(best) if best else None
    headline_raw = list(HEADLINE_RAW_COLUMNS)
    steps = [TrainingStep(**s) for s in _training_pipeline_steps()]

    # Risk-band thresholds are only computable once artefacts are loaded;
    # silently omit them if the model isn't trained yet.
    bands: dict[str, float] = {}
    try:
        bands = _risk_band_thresholds()
    except HTTPException:
        bands = {}

    return ModelCard(
        version=__version__,
        feature_names=feature_names,
        best_family=best,
        algorithm_label=algo_label,
        algorithm_plain=algo_plain,
        headline_raw_features=headline_raw,
        training_pipeline=steps,
        risk_band_thresholds=bands,
    )


# -----------------------------------------------------------------------------
# Raw-input schema + scoring (runs the persisted preprocessor server-side so
# the UI no longer has to ask users for post-standardisation z-scores).
# -----------------------------------------------------------------------------
def _raw_input_columns(state: dict[str, Any]) -> list[str]:
    pre = state["preprocessor"]
    names = getattr(pre, "feature_names_in_", None)
    if names is None:
        raise HTTPException(500, "Preprocessor has no feature_names_in_; refit required.")
    return [str(n) for n in names]


def _build_raw_schema(state: dict[str, Any]) -> list[RawColumnSchema]:
    """Inspect the labelled dataset once to derive defaults + categorical levels."""
    if "raw_schema" in state:
        return state["raw_schema"]

    from emerald_ai.data.eda import split_xy
    from emerald_ai.data.load import load_labelled

    df = load_labelled()
    X, _ = split_xy(df)
    cols = _raw_input_columns(state)

    out: list[RawColumnSchema] = []
    for c in cols:
        if c not in X.columns:
            continue
        series = X[c]
        copy = RAW_FIELD_COPY.get(c, {})
        label = copy.get("label", c)
        hint = copy.get("hint")
        unit = copy.get("unit")
        headline = c in HEADLINE_RAW_COLUMNS
        if pd.api.types.is_numeric_dtype(series):
            valid = series.dropna()
            default = float(valid.median()) if len(valid) else 0.0
            out.append(RawColumnSchema(
                name=c,
                kind="numeric",
                default=round(default, 4),
                headline=headline,
                label=label,
                hint=hint,
                unit=unit,
                p05=float(valid.quantile(0.05)) if len(valid) else None,
                p25=float(valid.quantile(0.25)) if len(valid) else None,
                p75=float(valid.quantile(0.75)) if len(valid) else None,
                p95=float(valid.quantile(0.95)) if len(valid) else None,
            ))
        else:
            counts = series.astype("string").value_counts(dropna=True).head(40)
            top_values = [str(v) for v in counts.index]
            default = top_values[0] if top_values else ""
            out.append(RawColumnSchema(
                name=c,
                kind="categorical",
                default=default,
                headline=headline,
                label=label,
                hint=hint,
                unit=None,
                top_values=top_values,
            ))
    state["raw_schema"] = out
    return out


def _raw_payload_to_frame(raw: dict[str, Any], state: dict[str, Any]) -> pd.DataFrame:
    """Build a single-row DataFrame aligned to the preprocessor's expected columns."""
    cols = _raw_input_columns(state)
    schema = {c.name: c for c in _build_raw_schema(state)}
    row: dict[str, Any] = {}
    for c in cols:
        meta = schema.get(c)
        v = raw.get(c, None)
        if v is None or v == "":
            v = meta.default if meta is not None else None
        if meta and meta.kind == "numeric":
            try:
                row[c] = float(v) if v is not None else float("nan")
            except (TypeError, ValueError):
                row[c] = float("nan")
        else:
            row[c] = str(v) if v is not None else None
    return pd.DataFrame([row], columns=cols)


@app.get("/raw_schema", response_model=RawSchemaResponse, tags=["scoring"])
def raw_schema() -> RawSchemaResponse:
    state = _load_state()
    return RawSchemaResponse(columns=_build_raw_schema(state))


@app.post("/score_raw", response_model=ScoreResponse, tags=["scoring"])
def score_raw(payload: RawApplicantPayload) -> ScoreResponse:
    state = _load_state()
    df = _raw_payload_to_frame(payload.raw, state)
    X_t = state["preprocessor"].transform(df)
    model = state["model"]
    conf = state["conformal"]
    proba = model.predict_proba(X_t)[0]
    classes = getattr(model, "classes_", np.array([0, 1]))
    pos_idx = int(np.where(classes == 1)[0][0]) if 1 in classes else 1
    p1 = float(proba[pos_idx])
    cset = conf.predict(np.array([p1]))
    return ScoreResponse(
        probability_creditworthy=p1,
        risk_band=_band_for(p1),
        score_percentile=_percentile_rank(p1),
        conformal_interval_alpha=getattr(conf, "alpha", 0.1),
        conformal_includes_creditworthy=bool(cset.include_1[0]),
        conformal_includes_delinquent=bool(cset.include_0[0]),
    )


@app.post("/explain_raw", response_model=ExplainResponse, tags=["explainability"])
def explain_raw(payload: RawApplicantPayload) -> ExplainResponse:
    from emerald_ai.explain import local_explanation, nearest_counterfactual

    state = _load_state()
    feature_names: list[str] = state["feature_names"]
    model = state["model"]
    df = _raw_payload_to_frame(payload.raw, state)
    X_t = state["preprocessor"].transform(df)
    x = np.asarray(X_t[0], dtype=float)
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


def _row_from_payload(payload: ApplicantPayload, feature_names: list[str]) -> np.ndarray:
    return np.asarray([float(payload.features.get(n, 0.0)) for n in feature_names], dtype=float)


def _scores_full_dataset() -> tuple[np.ndarray, pd.Series, pd.DataFrame]:
    """Compute predictions on the entire labelled supervisory pool."""
    from emerald_ai.data.eda import split_xy
    from emerald_ai.data.load import load_labelled

    state = _load_state()
    if "full_scores" in state:
        return state["full_scores"], state["full_y"], state["full_X"]
    df = load_labelled()
    X, y = split_xy(df)
    X_t = state["preprocessor"].transform(X)
    classes = getattr(state["model"], "classes_", np.array([0, 1]))
    pos_idx = int(np.where(classes == 1)[0][0]) if 1 in classes else 1
    scores = state["model"].predict_proba(X_t)[:, pos_idx]
    state["full_scores"] = scores
    state["full_y"] = y
    state["full_X"] = X
    return scores, y, X


# Percentile cut-offs that translate a raw model probability into a risk band.
# Because the dataset is extremely imbalanced (~0.36% defaults) the model's
# probabilities are heavily right-skewed and the legacy 0.5 / 0.8 cut-offs
# classify ~99.7% of applicants as "approve". These percentile-based bands
# preserve the badge's information value at the cost of being relative to the
# training pool rather than absolute.
RISK_BAND_PERCENTILES = {"high_risk": 5.0, "watch": 20.0}


def _risk_band_thresholds() -> dict[str, float]:
    """Return {'high_risk_cut': p5, 'watch_cut': p20} from the training pool."""
    state = _load_state()
    if "risk_band_thresholds" in state:
        return state["risk_band_thresholds"]
    scores, _, _ = _scores_full_dataset()
    out = {
        "high_risk_cut": float(np.percentile(scores, RISK_BAND_PERCENTILES["high_risk"])),
        "watch_cut": float(np.percentile(scores, RISK_BAND_PERCENTILES["watch"])),
        "high_risk_percentile": RISK_BAND_PERCENTILES["high_risk"],
        "watch_percentile": RISK_BAND_PERCENTILES["watch"],
    }
    state["risk_band_thresholds"] = out
    return out


def _band_for(p: float) -> str:
    """Map a model probability to {high_risk, watch, approve} using percentile cut-offs."""
    thr = _risk_band_thresholds()
    if p < thr["high_risk_cut"]:
        return "high_risk"
    if p < thr["watch_cut"]:
        return "watch"
    return "approve"


def _percentile_rank(p: float) -> float:
    """Return the empirical percentile of ``p`` in the training-pool score distribution."""
    scores, _, _ = _scores_full_dataset()
    return float((scores <= p).mean() * 100.0)


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
    cset = conf.predict(np.array([p1]))
    return ScoreResponse(
        probability_creditworthy=p1,
        risk_band=_band_for(p1),
        score_percentile=_percentile_rank(p1),
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

    thr = _risk_band_thresholds()
    df_out = df_in.copy()
    df_out["probability_creditworthy"] = probas
    df_out["risk_band"] = np.where(
        probas < thr["high_risk_cut"], "high_risk",
        np.where(probas < thr["watch_cut"], "watch", "approve"),
    )
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
