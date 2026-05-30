"""Global + local explanations (proposal §5.11).

Two tiers, with graceful degradation:

  * **SHAP tier** (when the ``shap`` package is installed) — the headline
    explainer of the dissertation. Tree models use exact, fast **TreeSHAP**
    (Lundberg et al., 2020); linear models use exact coefficient Shapley
    values; anything else falls back to model-agnostic **KernelSHAP** on a
    sampled background. SHAP values are additive (Σφ + φ₀ = f(x)), which is
    what makes them defensible under the EU AI Act transparency requirement.

  * **Fallback tier** (when ``shap`` is absent) — permutation importance for
    the global view and a coefficient/importance proxy for the local view, so
    the package still runs in a minimal install. The proxy is *flagged as
    such* in every report; it surfaces direction and magnitude but does not
    claim Shapley additivity.

Public API (stable; the FastAPI backend depends on it):
    global_importance        — permutation-importance ranking (model-agnostic)
    shap_global_importance   — mean(|SHAP|) ranking (preferred when available)
    local_explanation        — per-row contributions (SHAP when possible)
    HAS_SHAP                  — capability flag

References:
    lundberg2017shap.md, lundberg2020trees.md, aas2021explaining.md
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance

try:  # optional, gated dependency — see pyproject [xai] extra
    import shap as _shap

    HAS_SHAP = True
except ImportError:  # pragma: no cover - exercised only in minimal installs
    _shap = None
    HAS_SHAP = False


@dataclass
class FeatureContribution:
    name: str
    value: float  # the actual feature value for this row
    contribution: float  # signed contribution to the prediction
    direction: str  # "increases" / "decreases" / "neutral"
    method: str = "proxy"  # "treeshap" | "linearshap" | "kernelshap" | "proxy"


def _is_tree_model(model) -> bool:
    """Heuristic: tree ensembles expose ``feature_importances_`` and no ``coef_``."""
    name = type(model).__name__.lower()
    tree_markers = ("forest", "xgb", "lgbm", "lightgbm", "catboost", "gradientboosting", "tree")
    return (hasattr(model, "feature_importances_") and not hasattr(model, "coef_")) or any(
        m in name for m in tree_markers
    )


def _positive_class_index(model) -> int:
    classes = getattr(model, "classes_", np.array([0, 1]))
    return int(np.where(classes == 1)[0][0]) if 1 in classes else 1


def _to_matrix(X) -> np.ndarray:
    return X.to_numpy() if hasattr(X, "to_numpy") else np.asarray(X, dtype=float)


# --------------------------------------------------------------------------- #
# Global explanations
# --------------------------------------------------------------------------- #
def global_importance(
    model,
    X,
    y,
    *,
    feature_names: list[str] | None = None,
    n_repeats: int = 5,
    random_state: int = 0,
    scoring: str = "average_precision",
) -> pd.DataFrame:
    """Per-feature permutation importance ± std, sorted desc (model-agnostic).

    Permutation importance is robust on the §5.7 imbalance regime where tree
    ``feature_importances_`` can mislead on calibrated outputs. This is the
    fallback global view; ``shap_global_importance`` is preferred when SHAP is
    available.
    """
    if feature_names is None:
        feature_names = (
            list(X.columns)
            if hasattr(X, "columns")
            else [f"f{i}" for i in range(_to_matrix(X).shape[1])]
        )
    Xv = _to_matrix(X)
    yv = np.asarray(y).astype(int)
    result = permutation_importance(
        model, Xv, yv, scoring=scoring, n_repeats=n_repeats, random_state=random_state, n_jobs=-1
    )
    df = pd.DataFrame(
        {
            "feature": feature_names,
            "importance_mean": result.importances_mean,
            "importance_std": result.importances_std,
        }
    )
    return df.sort_values("importance_mean", ascending=False).reset_index(drop=True)


def _shap_values_matrix(
    model, X: np.ndarray, *, background: np.ndarray | None = None
) -> np.ndarray:
    """Return a (n_samples, n_features) array of SHAP values for the positive class.

    Picks the cheapest correct explainer: TreeSHAP for tree ensembles, exact
    Shapley for linear models, KernelSHAP otherwise. Raises if SHAP is absent.
    """
    if not HAS_SHAP:  # pragma: no cover
        raise RuntimeError("shap is not installed")
    pos = _positive_class_index(model)

    if _is_tree_model(model):
        explainer = _shap.TreeExplainer(model)
        vals = explainer.shap_values(X)
    elif hasattr(model, "coef_"):
        bg = background if background is not None else X
        explainer = _shap.LinearExplainer(model, bg)
        vals = explainer.shap_values(X)
    else:
        bg = (
            background
            if background is not None
            else _shap.sample(X, min(100, len(X)), random_state=0)
        )
        explainer = _shap.KernelExplainer(lambda d: model.predict_proba(d)[:, pos], bg)
        vals = explainer.shap_values(X, silent=True)

    # Normalise the several shapes SHAP returns across versions/models.
    arr = np.asarray(vals)
    if isinstance(vals, list):  # [class0, class1]
        arr = np.asarray(vals[pos if pos < len(vals) else -1])
    elif arr.ndim == 3:  # (n_samples, n_features, n_classes)
        arr = arr[:, :, pos if pos < arr.shape[2] else -1]
    return arr.reshape(len(X), -1)


def shap_global_importance(
    model,
    X,
    *,
    feature_names: list[str] | None = None,
    max_samples: int = 500,
    random_state: int = 0,
) -> pd.DataFrame:
    """Global ranking by mean(|SHAP|) over a sample of rows.

    This is the dissertation's headline global explanation: it aggregates the
    same exact local attributions served to the lending officer, so the global
    and local stories are guaranteed consistent.
    """
    Xv = _to_matrix(X)
    if feature_names is None:
        feature_names = (
            list(X.columns) if hasattr(X, "columns") else [f"f{i}" for i in range(Xv.shape[1])]
        )
    if len(Xv) > max_samples:
        rng = np.random.default_rng(random_state)
        idx = rng.choice(len(Xv), size=max_samples, replace=False)
        Xv = Xv[idx]
    sv = _shap_values_matrix(model, Xv)
    mean_abs = np.abs(sv).mean(axis=0)
    mean_signed = sv.mean(axis=0)
    df = pd.DataFrame(
        {
            "feature": feature_names,
            "mean_abs_shap": mean_abs,
            "mean_signed_shap": mean_signed,
        }
    )
    return df.sort_values("mean_abs_shap", ascending=False).reset_index(drop=True)


# --------------------------------------------------------------------------- #
# Local explanations
# --------------------------------------------------------------------------- #
def local_explanation(
    model,
    x_row,
    feature_names: list[str],
    *,
    background_mean: np.ndarray | None = None,
    background_std: np.ndarray | None = None,
    background: np.ndarray | None = None,
    top_k: int = 10,
) -> list[FeatureContribution]:
    """Per-feature contributions for a single applicant.

    Prefers exact SHAP (TreeSHAP for the tree winner, linear Shapley for linear
    models) when the ``shap`` package is installed; otherwise falls back to the
    coefficient/importance proxy. The ``method`` field on each contribution
    records which path was taken so the UI/report can be honest about it.
    """
    x = np.asarray(x_row, dtype=float).reshape(-1)
    names = list(feature_names)

    contribs: np.ndarray | None = None
    method = "proxy"

    if HAS_SHAP:
        try:
            sv = _shap_values_matrix(model, x.reshape(1, -1), background=background)
            contribs = sv.reshape(-1)
            if _is_tree_model(model):
                method = "treeshap"
            elif hasattr(model, "coef_"):
                method = "linearshap"
            else:
                method = "kernelshap"
        except Exception:  # pragma: no cover - never let explanation crash a request
            contribs = None

    if contribs is None:
        # ---- fallback proxy (no shap, or shap failed) ----
        if hasattr(model, "coef_"):
            coef = np.asarray(model.coef_).reshape(-1)
            bm = background_mean if background_mean is not None else np.zeros_like(x)
            contribs = coef * (x - bm)
        elif hasattr(model, "feature_importances_"):
            imp = np.asarray(model.feature_importances_, dtype=float)
            bm = background_mean if background_mean is not None else np.zeros_like(x)
            bs = background_std if background_std is not None else np.ones_like(x)
            z = (x - bm) / np.where(bs > 1e-9, bs, 1.0)
            contribs = imp * z
        else:
            contribs = np.zeros_like(x)

    rows = []
    for i, c in enumerate(contribs):
        c = float(c)
        direction = "increases" if c > 1e-9 else "decreases" if c < -1e-9 else "neutral"
        rows.append(
            FeatureContribution(
                name=names[i],
                value=float(x[i]),
                contribution=c,
                direction=direction,
                method=method,
            )
        )
    rows.sort(key=lambda r: abs(r.contribution), reverse=True)
    return rows[:top_k]
