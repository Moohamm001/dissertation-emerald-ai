"""Global + local explanations (proposal §5.11).

First cut uses sklearn-native explainers so the module has no extra deps:

  * `global_importance(model, X, y)` returns a per-feature ranking via
    permutation importance against PR-AUC (model-agnostic). Tree models
    additionally get `feature_importances_` as a fast secondary view.

  * `local_explanation(model, x_row, feature_names)` returns per-feature
    contributions:
      - linear models: coefficient × value (clean and exact);
      - tree models: scaled `feature_importances_` × |z-score(x_row)| as a
        cheap proxy for SHAP — flagged in the report as proxy-only;
      - SHAP/KernelSHAP swap-in lands when the `shap` dep is added.

The §5.11 commit acknowledges this is a *first cut*; TreeSHAP / KernelSHAP /
LIME / DiCE / Quantus land once the dep budget is approved.

References:
    lundberg2017shap.md, lundberg2020trees.md, aas2021explaining.md
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance


@dataclass
class FeatureContribution:
    name: str
    value: float        # the actual feature value for this row
    contribution: float # signed contribution to the prediction
    direction: str      # "increases" / "decreases" / "neutral"


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
    """Per-feature permutation importance ± std, sorted desc.

    Permutation importance is model-agnostic and produces stable rankings on
    the §5.7 imbalance-strategy regime where tree `feature_importances_` can
    be misleading on calibrated outputs.
    """
    if feature_names is None:
        feature_names = (list(X.columns) if hasattr(X, "columns")
                         else [f"f{i}" for i in range(np.asarray(X).shape[1])])
    Xv = X.to_numpy() if hasattr(X, "to_numpy") else np.asarray(X)
    yv = np.asarray(y).astype(int)
    result = permutation_importance(
        model, Xv, yv, scoring=scoring, n_repeats=n_repeats, random_state=random_state, n_jobs=-1
    )
    df = pd.DataFrame({
        "feature": feature_names,
        "importance_mean": result.importances_mean,
        "importance_std": result.importances_std,
    })
    return df.sort_values("importance_mean", ascending=False).reset_index(drop=True)


def local_explanation(
    model,
    x_row,
    feature_names: list[str],
    *,
    background_mean: np.ndarray | None = None,
    background_std: np.ndarray | None = None,
    top_k: int = 10,
) -> list[FeatureContribution]:
    """Per-feature contributions for a single applicant.

    Linear models use exact coefficient-times-deviation; tree-based models
    fall back to a proxy. The proxy is flagged in the report as such — the
    point is to surface *direction and magnitude*, not to claim Shapley
    additivity.
    """
    x = np.asarray(x_row, dtype=float).reshape(-1)
    names = list(feature_names)

    if hasattr(model, "coef_"):
        coef = np.asarray(model.coef_).reshape(-1)
        if background_mean is None:
            background_mean = np.zeros_like(x)
        dx = x - background_mean
        contribs = coef * dx
    elif hasattr(model, "feature_importances_"):
        imp = np.asarray(model.feature_importances_, dtype=float)
        if background_mean is None or background_std is None:
            background_mean = np.zeros_like(x)
            background_std = np.ones_like(x)
        z = (x - background_mean) / np.where(background_std > 1e-9, background_std, 1.0)
        contribs = imp * z  # proxy — see module docstring
    else:
        contribs = np.zeros_like(x)

    rows = []
    for i, c in enumerate(contribs):
        direction = "neutral"
        if c > 1e-9:
            direction = "increases"
        elif c < -1e-9:
            direction = "decreases"
        rows.append(FeatureContribution(
            name=names[i], value=float(x[i]), contribution=float(c), direction=direction,
        ))
    rows.sort(key=lambda r: abs(r.contribution), reverse=True)
    return rows[:top_k]
