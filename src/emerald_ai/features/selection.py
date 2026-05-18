"""Two-stage feature selection (proposal §5.6).

Stage 1 — **Filter**: mutual information of each candidate feature against Y;
the bottom decile is dropped as low-signal. This is fast, model-agnostic, and
robust to extreme imbalance.

Stage 2 — **Wrapper with bootstrap stability**: a Random-Forest mean-decrease-
impurity ranking is repeated across `n_bootstraps` stratified resamples; a
feature is retained iff it lands in the top-K importance positions in at least
`selection_frequency_threshold` of bootstraps. This is a lightweight Boruta-
analogue: it captures the "stable importance under resampling" intent without
adding the boruta-py / shap dependencies for this dissertation stage. The
proposal explicitly allows substituting a SHAP-importance variant once the
modelling pipeline lands a tuned XGBoost; this module is the §5.6 first cut.

Outputs are governance-grade: every step is logged in
``data/governance/selection_report.md`` so the supervisor can verify which
features the dissertation's modelling stage actually consumes.

Run:
    python -m emerald_ai select
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import mutual_info_classif
from sklearn.model_selection import StratifiedKFold

from emerald_ai.config import MODEL, PATHS

DEFAULT_FILTER_DROP_QUANTILE = 0.10
DEFAULT_TOP_K = 25
DEFAULT_N_BOOTSTRAPS = 30
DEFAULT_SELECTION_FREQUENCY = 0.60

GOVERNANCE_DIR = PATHS.root / "data" / "governance"
SELECTION_REPORT_PATH = GOVERNANCE_DIR / "selection_report.md"


@dataclass
class SelectionAudit:
    """Trace of every selection decision."""

    n_features_in: int = 0
    n_after_filter: int = 0
    n_selected: int = 0
    filter_drop_quantile: float = DEFAULT_FILTER_DROP_QUANTILE
    top_k: int = DEFAULT_TOP_K
    n_bootstraps: int = DEFAULT_N_BOOTSTRAPS
    selection_frequency_threshold: float = DEFAULT_SELECTION_FREQUENCY
    mi_scores: dict[str, float] = field(default_factory=dict)
    filter_dropped: list[str] = field(default_factory=list)
    selection_frequency: dict[str, float] = field(default_factory=dict)
    selected: list[str] = field(default_factory=list)
    random_state: int = MODEL.random_seed


# -----------------------------------------------------------------------------
# Stage 1 — mutual-information filter
# -----------------------------------------------------------------------------
def filter_by_mutual_info(
    X: pd.DataFrame | np.ndarray,
    y: pd.Series | np.ndarray,
    *,
    drop_quantile: float = DEFAULT_FILTER_DROP_QUANTILE,
    feature_names: list[str] | None = None,
    random_state: int = MODEL.random_seed,
) -> tuple[list[str], dict[str, float]]:
    """Drop the bottom-``drop_quantile`` features by MI against Y.

    Accepts either a DataFrame (column names used as feature names) or a numpy
    matrix (``feature_names`` required). Returns the names of *retained*
    features and the full MI score dict for audit.
    """
    if isinstance(X, pd.DataFrame):
        names = list(X.columns)
        X_arr = X.to_numpy()
    else:
        if feature_names is None:
            feature_names = [f"f{i}" for i in range(X.shape[1])]
        names = list(feature_names)
        X_arr = np.asarray(X)
    y_arr = np.asarray(y).astype(int)

    mi = mutual_info_classif(X_arr, y_arr, random_state=random_state, n_neighbors=3)
    scores = {n: float(s) for n, s in zip(names, mi)}
    cutoff = float(np.quantile(mi, drop_quantile))
    retained = [n for n in names if scores[n] > cutoff]
    return retained, scores


# -----------------------------------------------------------------------------
# Stage 2 — bootstrap-stability wrapper
# -----------------------------------------------------------------------------
def _topk_features_from_rf(
    X: np.ndarray,
    y: np.ndarray,
    feature_names: list[str],
    *,
    top_k: int,
    random_state: int,
) -> set[str]:
    """One bootstrap round: fit an RF, return its top-``top_k`` features.

    Uses class_weight='balanced_subsample' to handle the 0.36% prevalence
    inside each bootstrap fold without resampling — Santos et al. (2018)'s
    in-fold-only constraint is preserved trivially because no resampling
    happens here at all (§5.6 stays separate from §5.7 imbalance strategy).
    """
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        min_samples_leaf=5,
        class_weight="balanced_subsample",
        n_jobs=-1,
        random_state=random_state,
    )
    rf.fit(X, y)
    order = np.argsort(rf.feature_importances_)[::-1]
    return {feature_names[i] for i in order[:top_k]}


def bootstrap_stability_select(
    X: pd.DataFrame | np.ndarray,
    y: pd.Series | np.ndarray,
    *,
    top_k: int = DEFAULT_TOP_K,
    n_bootstraps: int = DEFAULT_N_BOOTSTRAPS,
    selection_frequency_threshold: float = DEFAULT_SELECTION_FREQUENCY,
    feature_names: list[str] | None = None,
    random_state: int = MODEL.random_seed,
) -> tuple[list[str], dict[str, float]]:
    """Stage-2 wrapper: select features that are stable under resampling.

    For each of ``n_bootstraps`` stratified resamples, fit a Random Forest
    and record the top-``top_k`` features by mean-decrease-impurity. A feature
    is retained iff its selection frequency across bootstraps clears
    ``selection_frequency_threshold``.

    Returns (selected_features, selection_frequency_per_feature).
    """
    if isinstance(X, pd.DataFrame):
        names = list(X.columns)
        X_arr = X.to_numpy()
    else:
        if feature_names is None:
            feature_names = [f"f{i}" for i in range(X.shape[1])]
        names = list(feature_names)
        X_arr = np.asarray(X)
    y_arr = np.asarray(y).astype(int)

    rng = np.random.default_rng(random_state)
    counts: dict[str, int] = {n: 0 for n in names}
    n_rows = X_arr.shape[0]

    for b in range(n_bootstraps):
        # Stratified bootstrap: resample within each class so the minority is
        # always represented. Critical at 0.36% prevalence — uniform bootstrap
        # would leave minority-free draws.
        seed = int(rng.integers(0, 2**31 - 1))
        rng_b = np.random.default_rng(seed)
        idx_pos = np.where(y_arr == 1)[0]
        idx_neg = np.where(y_arr == 0)[0]
        boot_pos = rng_b.choice(idx_pos, size=len(idx_pos), replace=True) if len(idx_pos) else np.array([], dtype=int)
        boot_neg = rng_b.choice(idx_neg, size=len(idx_neg), replace=True) if len(idx_neg) else np.array([], dtype=int)
        boot_idx = np.concatenate([boot_pos, boot_neg])
        if boot_idx.size == 0:
            continue
        topk = _topk_features_from_rf(
            X_arr[boot_idx], y_arr[boot_idx], names,
            top_k=top_k, random_state=seed,
        )
        for n in topk:
            counts[n] += 1

    freq = {n: counts[n] / max(n_bootstraps, 1) for n in names}
    selected = [n for n, f in freq.items() if f >= selection_frequency_threshold]
    return selected, freq


# -----------------------------------------------------------------------------
# Orchestrator
# -----------------------------------------------------------------------------
def run_selection(
    X: pd.DataFrame,
    y: pd.Series,
    *,
    drop_quantile: float = DEFAULT_FILTER_DROP_QUANTILE,
    top_k: int = DEFAULT_TOP_K,
    n_bootstraps: int = DEFAULT_N_BOOTSTRAPS,
    selection_frequency_threshold: float = DEFAULT_SELECTION_FREQUENCY,
    random_state: int = MODEL.random_seed,
) -> SelectionAudit:
    """Two-stage selection end-to-end. Returns the audit; emit_report() writes it."""
    audit = SelectionAudit(
        n_features_in=int(X.shape[1]),
        filter_drop_quantile=drop_quantile,
        top_k=top_k,
        n_bootstraps=n_bootstraps,
        selection_frequency_threshold=selection_frequency_threshold,
        random_state=random_state,
    )
    retained, mi_scores = filter_by_mutual_info(
        X, y, drop_quantile=drop_quantile, random_state=random_state,
    )
    audit.mi_scores = mi_scores
    audit.filter_dropped = sorted(set(X.columns) - set(retained))
    audit.n_after_filter = len(retained)

    X_filtered = X[retained]
    selected, freq = bootstrap_stability_select(
        X_filtered, y,
        top_k=top_k,
        n_bootstraps=n_bootstraps,
        selection_frequency_threshold=selection_frequency_threshold,
        random_state=random_state,
    )
    audit.selection_frequency = freq
    audit.selected = sorted(selected)
    audit.n_selected = len(selected)
    return audit


# -----------------------------------------------------------------------------
# Report writer
# -----------------------------------------------------------------------------
def _fmt_list(items: list[str], cap: int = 12) -> str:
    if not items:
        return "_(none)_"
    if len(items) <= cap:
        return ", ".join(f"`{c}`" for c in items)
    return ", ".join(f"`{c}`" for c in items[:cap]) + f", … (+{len(items) - cap} more)"


def emit_report(audit: SelectionAudit, *, out_path: Path = SELECTION_REPORT_PATH) -> Path:
    """Write data/governance/selection_report.md."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    today = pd.Timestamp.utcnow().date().isoformat()

    # Top-15 by selection frequency (sorted desc)
    freq_rows = sorted(audit.selection_frequency.items(), key=lambda kv: kv[1], reverse=True)
    freq_table = "\n".join(
        f"| `{name}` | {audit.mi_scores.get(name, float('nan')):.4f} | {freq*100:.1f}% |"
        for name, freq in freq_rows[:30]
    )

    body = f"""# Feature Selection Report — proposal §5.6

_Companion to `datasheet.md`, `eda_report.md`, `preprocess_report.md`. Two-stage
selection: MI filter (Stage 1) + bootstrap-stability RF importance (Stage 2)._

Version: 0.1 · Generated: {today}

## Stage 1 — Mutual-information filter

| | Value |
|---|---:|
| Drop quantile (bottom) | {audit.filter_drop_quantile:.2f} |
| Features in | {audit.n_features_in} |
| Features retained after filter | {audit.n_after_filter} |
| Features dropped | {len(audit.filter_dropped)} |

**Filter-dropped features:** {_fmt_list(audit.filter_dropped)}

## Stage 2 — Bootstrap-stability wrapper

| | Value |
|---|---:|
| Top-K per bootstrap | {audit.top_k} |
| Bootstrap rounds | {audit.n_bootstraps} |
| Selection-frequency threshold | {audit.selection_frequency_threshold*100:.0f}% |
| Final selected features | **{audit.n_selected}** |
| Master seed | {audit.random_state} |

Bootstraps are stratified within each class so the minority (0.36% prevalence)
is always represented; the in-fold-only constraint from Santos et al. (2018)
is moot here because no resampling-then-relabelling happens in this stage.

**Selected features:** {_fmt_list(audit.selected, cap=40)}

## Top-30 features by selection frequency

| Feature | MI(Y) [nats] | Selection freq |
|---|---:|---:|
{freq_table}

## Notes

- This is the §5.6 first cut. A SHAP-importance variant on a tuned XGBoost is
  the documented next step once the modelling stage lands; the present
  RandomForest-based ranking provides the bootstrap-stability invariant the
  proposal calls out without adding the boruta-py / shap dependencies prematurely.
- The selection is independent of any imbalance strategy choice — that
  decision lives in §5.7 (`imbalance.py`) and is applied **inside** each
  cross-validation fold during modelling, never before selection.
"""
    out_path.write_text(body, encoding="utf-8")
    return out_path


def main() -> None:  # pragma: no cover
    # Load preprocessed X via the orchestrator; we re-fit the preprocessor
    # here to keep selection deterministic w.r.t. config.
    from emerald_ai.data.eda import split_xy
    from emerald_ai.data.load import load_labelled
    from emerald_ai.features.pipeline import fit_transform_with_audit

    df = load_labelled()
    X, y = split_xy(df)
    X_t, _pre, pre_audit = fit_transform_with_audit(X, y)
    # Re-attach feature names — sklearn's get_feature_names_out gives us the
    # post-encoding column space.
    fnames = list(_pre.get_feature_names_out())
    X_df = pd.DataFrame(X_t, columns=fnames, index=X.index)
    audit = run_selection(X_df, y)
    written = emit_report(audit)
    print(f"OK: {written}")
    print(f"  in={audit.n_features_in} -> filter-kept={audit.n_after_filter} -> selected={audit.n_selected}")


if __name__ == "__main__":  # pragma: no cover
    main()
