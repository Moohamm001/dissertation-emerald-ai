"""scikit-learn ColumnTransformer pipeline (proposal §5.5).

Stages (mirroring the proposal):
    1. Drop columns           — >40% missing + time-leaking artefacts surfaced by EDA.
    2. Missing-data treatment — median imputation for numerics + 'missing' category
                                for categoricals; missing-indicator binaries appended
                                where informative.
    3. Encoding               — OneHotEncoder for low-cardinality categoricals (≤10
                                levels); TargetEncoder with internal CV for high-
                                cardinality categoricals (Industry, Borrower State).
    4. Scaling                — StandardScaler on numerics (harmless for trees,
                                necessary for distance-based learners — keeps the
                                same preprocessor reusable across all six model
                                families).
    Stage 5 (feature interactions) is deferred; the §5.6 selection stage will
    add domain ratios.

The orchestrator `build_preprocessor()` returns a ColumnTransformer plus an
audit dictionary describing every decision so the dissertation can show its
work. `fit_transform_with_audit()` wraps fit + transform and persists the
audit. `emit_report()` writes data/governance/preprocess_report.md.

Run:
    python -m emerald_ai preprocess
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, TargetEncoder

from emerald_ai.config import MODEL, PATHS

# -----------------------------------------------------------------------------
# Constants surfaced by upstream artefacts
# -----------------------------------------------------------------------------
# EDA flagged these as pure-time encodings whose PSI ~16 across quarters is by
# construction, not by business drift. They must be dropped before modelling
# to avoid leaking the partition into X.
TIME_LEAKING_COLUMNS: tuple[str, ...] = (
    "Start Month",
    "Start Annual Day",
)

DEFAULT_MISSINGNESS_THRESHOLD: float = 0.40
DEFAULT_HIGH_CARDINALITY_THRESHOLD: int = 10

GOVERNANCE_DIR = PATHS.root / "data" / "governance"
PREPROCESS_REPORT_PATH = GOVERNANCE_DIR / "preprocess_report.md"


# -----------------------------------------------------------------------------
# Audit record
# -----------------------------------------------------------------------------
@dataclass
class PreprocessAudit:
    """Trace of every preprocessing decision — written to governance/."""

    drop_high_missingness: list[str] = field(default_factory=list)
    drop_time_leaking: list[str] = field(default_factory=list)
    drop_datetime: list[str] = field(default_factory=list)
    numeric_cols: list[str] = field(default_factory=list)
    low_cardinality_cols: list[str] = field(default_factory=list)
    high_cardinality_cols: list[str] = field(default_factory=list)
    missingness_threshold: float = DEFAULT_MISSINGNESS_THRESHOLD
    high_cardinality_threshold: int = DEFAULT_HIGH_CARDINALITY_THRESHOLD
    n_input_columns: int = 0
    n_output_features: int | None = None
    per_column_missingness: dict[str, float] = field(default_factory=dict)
    n_rows_in: int = 0
    n_rows_out: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "drop_high_missingness": self.drop_high_missingness,
            "drop_time_leaking": self.drop_time_leaking,
            "drop_datetime": self.drop_datetime,
            "numeric_cols": self.numeric_cols,
            "low_cardinality_cols": self.low_cardinality_cols,
            "high_cardinality_cols": self.high_cardinality_cols,
            "missingness_threshold": self.missingness_threshold,
            "high_cardinality_threshold": self.high_cardinality_threshold,
            "n_input_columns": self.n_input_columns,
            "n_output_features": self.n_output_features,
            "n_rows_in": self.n_rows_in,
            "n_rows_out": self.n_rows_out,
        }


# -----------------------------------------------------------------------------
# Core builder
# -----------------------------------------------------------------------------
def build_preprocessor(
    X: pd.DataFrame,
    *,
    missingness_threshold: float = DEFAULT_MISSINGNESS_THRESHOLD,
    high_cardinality_threshold: int = DEFAULT_HIGH_CARDINALITY_THRESHOLD,
    drop_time_leaking: bool = True,
    add_missing_indicators: bool = True,
    random_state: int = MODEL.random_seed,
) -> tuple[ColumnTransformer, PreprocessAudit]:
    """Construct an unfitted ColumnTransformer + audit record for ``X``.

    Parameters
    ----------
    X : pd.DataFrame
        Permitted-feature frame produced by ``emerald_ai.data.eda.split_xy`` or
        equivalent (i.e., post-leakage-audit, post-label-drop).
    missingness_threshold : float
        Columns with proportion of NA above this are dropped at Stage 1.
    high_cardinality_threshold : int
        Categorical columns with more unique levels than this go to the
        TargetEncoder branch; the rest go to OneHotEncoder.
    drop_time_leaking : bool
        Strip the EDA-flagged pure-time columns (default: yes).
    add_missing_indicators : bool
        Append a binary indicator per numeric column whose value is 1 where the
        original was NA. Useful where missingness is itself informative
        (proposal §5.5 Stage 1).
    random_state : int
        Forwarded to TargetEncoder's internal CV.

    Returns
    -------
    (preprocessor, audit) : tuple
        ``preprocessor`` is unfitted; call ``fit`` or use
        :func:`fit_transform_with_audit`. ``audit`` is a ``PreprocessAudit``
        capturing the decisions made.
    """
    audit = PreprocessAudit(
        missingness_threshold=missingness_threshold,
        high_cardinality_threshold=high_cardinality_threshold,
        n_input_columns=int(X.shape[1]),
        n_rows_in=int(X.shape[0]),
        per_column_missingness={c: float(X[c].isna().mean()) for c in X.columns},
    )

    # ------------------------------------------------------------------
    # Stage 1: drop list
    # ------------------------------------------------------------------
    missing_rates = X.isna().mean()
    audit.drop_high_missingness = sorted(
        missing_rates[missing_rates > missingness_threshold].index.tolist()
    )
    if drop_time_leaking:
        audit.drop_time_leaking = [c for c in TIME_LEAKING_COLUMNS if c in X.columns]

    drop_set = set(audit.drop_high_missingness) | set(audit.drop_time_leaking)
    kept = [c for c in X.columns if c not in drop_set]

    # Datetime columns: drop for now; §5.6 feature engineering will revisit
    # them (e.g. days-since-start, day-of-week features).
    audit.drop_datetime = [c for c in kept if pd.api.types.is_datetime64_any_dtype(X[c])]
    drop_set.update(audit.drop_datetime)
    kept = [c for c in kept if c not in drop_set]

    # ------------------------------------------------------------------
    # Stage 2-4: per-type transformer pipelines
    # ------------------------------------------------------------------
    numeric_cols = [c for c in kept if pd.api.types.is_numeric_dtype(X[c])]
    cat_cols_raw = [c for c in kept if c not in numeric_cols]
    low_card = [
        c for c in cat_cols_raw
        if X[c].nunique(dropna=True) <= high_cardinality_threshold
    ]
    high_card = [c for c in cat_cols_raw if c not in low_card]

    audit.numeric_cols = numeric_cols
    audit.low_cardinality_cols = low_card
    audit.high_cardinality_cols = high_card

    # Numeric branch — impute median + add indicator + scale
    numeric_steps = [("impute", SimpleImputer(strategy="median", add_indicator=add_missing_indicators))]
    numeric_steps.append(("scale", StandardScaler()))
    numeric_tx = Pipeline(numeric_steps)

    # Low-cardinality categorical branch — fill 'missing' + one-hot
    low_card_tx = Pipeline([
        ("impute", SimpleImputer(strategy="constant", fill_value="__missing__")),
        ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])

    # High-cardinality categorical branch — fill 'missing' + cross-fitted target
    high_card_tx = Pipeline([
        ("impute", SimpleImputer(strategy="constant", fill_value="__missing__")),
        ("target", TargetEncoder(target_type="binary", random_state=random_state)),
    ])

    transformers: list[tuple[str, Pipeline, list[str]]] = []
    if numeric_cols:
        transformers.append(("num", numeric_tx, numeric_cols))
    if low_card:
        transformers.append(("low_card", low_card_tx, low_card))
    if high_card:
        transformers.append(("high_card", high_card_tx, high_card))

    preprocessor = ColumnTransformer(
        transformers=transformers,
        remainder="drop",
        verbose_feature_names_out=False,
    )
    return preprocessor, audit


# -----------------------------------------------------------------------------
# Fit + transform helper
# -----------------------------------------------------------------------------
def fit_transform_with_audit(
    X: pd.DataFrame,
    y: pd.Series,
    *,
    missingness_threshold: float = DEFAULT_MISSINGNESS_THRESHOLD,
    high_cardinality_threshold: int = DEFAULT_HIGH_CARDINALITY_THRESHOLD,
    drop_time_leaking: bool = True,
    random_state: int = MODEL.random_seed,
) -> tuple[np.ndarray, ColumnTransformer, PreprocessAudit]:
    """Build, fit, transform — returns (X_transformed, fitted_pipeline, audit).

    ``y`` is required for the TargetEncoder branch's cross-fitting.
    """
    pre, audit = build_preprocessor(
        X,
        missingness_threshold=missingness_threshold,
        high_cardinality_threshold=high_cardinality_threshold,
        drop_time_leaking=drop_time_leaking,
        random_state=random_state,
    )
    X_t = pre.fit_transform(X, y)
    audit.n_output_features = int(X_t.shape[1])
    audit.n_rows_out = int(X_t.shape[0])
    return X_t, pre, audit


# -----------------------------------------------------------------------------
# Report writer
# -----------------------------------------------------------------------------
def _fmt_list(items: list[str], cap: int = 12) -> str:
    if not items:
        return "_(none)_"
    if len(items) <= cap:
        return ", ".join(f"`{c}`" for c in items)
    head = ", ".join(f"`{c}`" for c in items[:cap])
    return f"{head}, … (+{len(items) - cap} more)"


def emit_report(
    audit: PreprocessAudit,
    *,
    out_path: Path = PREPROCESS_REPORT_PATH,
) -> Path:
    """Write data/governance/preprocess_report.md."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    today = pd.Timestamp.utcnow().date().isoformat()

    miss = sorted(audit.per_column_missingness.items(), key=lambda kv: kv[1], reverse=True)
    miss_rows = [
        f"| `{name}` | {rate*100:.2f}% |" for name, rate in miss[:20]
    ]

    body = f"""# Preprocessing Report — proposal §5.5

_Companion to `datasheet.md`, `feature_catalogue.yaml`, and `eda_report.md`.
Operates on the post-EDA permitted-feature frame; rows with missing labels
have already been dropped upstream._

Version: 0.1 · Generated: {today}

## Stage 1 — Drop list

| Reason | Threshold | Count | Columns |
|---|---|---:|---|
| Missingness > {audit.missingness_threshold*100:.0f}% | hard drop | {len(audit.drop_high_missingness)} | {_fmt_list(audit.drop_high_missingness)} |
| Time-leaking (EDA PSI ≫ 0.25 by construction) | hard drop | {len(audit.drop_time_leaking)} | {_fmt_list(audit.drop_time_leaking)} |
| Datetime (deferred to §5.6 feature engineering) | typed drop | {len(audit.drop_datetime)} | {_fmt_list(audit.drop_datetime)} |

## Stage 2 — Missing-data treatment

- Numeric features: median imputation + missing-indicator binary appended per feature.
- Categorical features: explicit `__missing__` level added before encoding.

## Stage 3 — Encoding

- **Low-cardinality categoricals (≤{audit.high_cardinality_threshold} unique levels):** OneHotEncoder with `handle_unknown='ignore'`.
  Columns ({len(audit.low_cardinality_cols)}): {_fmt_list(audit.low_cardinality_cols)}
- **High-cardinality categoricals:** TargetEncoder (binary target, internal cross-fit, random_state=42).
  Columns ({len(audit.high_cardinality_cols)}): {_fmt_list(audit.high_cardinality_cols)}
  Master seed: {MODEL.random_seed} (from `emerald_ai.config.MODEL.random_seed`).

## Stage 4 — Scaling

- All surviving numerics → StandardScaler. Tree-based learners are scale-invariant; the same fitted preprocessor is reused across all six model families (proposal §5.8) to keep comparisons identical.

## Shape summary

| | Value |
|---|---:|
| Input columns (after EDA permitted-set) | {audit.n_input_columns} |
| Output features (post-encoding + indicators) | {audit.n_output_features if audit.n_output_features is not None else '—'} |
| Numeric retained | {len(audit.numeric_cols)} |
| Low-cardinality categoricals | {len(audit.low_cardinality_cols)} |
| High-cardinality categoricals | {len(audit.high_cardinality_cols)} |
| Rows in | {audit.n_rows_in} |
| Rows out | {audit.n_rows_out if audit.n_rows_out is not None else '—'} |

## Top-20 input-column missingness (for traceability)

| Column | Missing % |
|---|---:|
{chr(10).join(miss_rows)}
"""
    out_path.write_text(body, encoding="utf-8")
    return out_path


# -----------------------------------------------------------------------------
# Orchestrator
# -----------------------------------------------------------------------------
def run_preprocess(
    path: Path | None = None,
    *,
    out_path: Path = PREPROCESS_REPORT_PATH,
) -> tuple[Path, PreprocessAudit]:
    """End-to-end: load → split X/Y → fit preprocessor → emit governance report.

    The fitted preprocessor itself is returned via the audit-bound function
    rather than persisted here; a future commit will pickle it under
    ``data/processed/`` once the train/test split design is locked.
    """
    # Local imports keep eda / load lazy for fast test imports
    from emerald_ai.data.eda import split_xy
    from emerald_ai.data.load import load_labelled

    df = load_labelled(path)
    X, y = split_xy(df)
    _X_t, _pre, audit = fit_transform_with_audit(X, y)
    written = emit_report(audit, out_path=out_path)
    return written, audit


def main() -> None:  # pragma: no cover
    written, audit = run_preprocess()
    print(f"OK: {written}")
    print(
        f"  in={audit.n_input_columns} cols / {audit.n_rows_in} rows "
        f"-> out={audit.n_output_features} features / {audit.n_rows_out} rows"
    )


if __name__ == "__main__":  # pragma: no cover
    main()
