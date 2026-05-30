"""Empirical explanation-fidelity validation (proposal §5.11).

An attribution method is not trustworthy *because* it produced a number — it
has to be validated. This module reports a **faithfulness correlation**: if we
ablate the features an explanation says matter most, a faithful explanation's
attribution mass should track the resulting drop in the model's prediction.

The metric is the Bhatt et al. (2020) faithfulness correlation, implemented in
pure NumPy so it has no extra dependency. If the ``quantus`` package is
installed, ``quantus_faithfulness`` exposes its richer battery as well.

Reference: literature/papers/hedstrom2023quantus.md
"""

from __future__ import annotations

import numpy as np


def faithfulness_correlation(
    model,
    X: np.ndarray,
    attributions: np.ndarray,
    *,
    n_subsets: int = 50,
    subset_size: int = 3,
    baseline: np.ndarray | None = None,
    random_state: int = 0,
) -> float:
    """Mean per-instance correlation between attribution mass and prediction drop.

    For each instance we repeatedly (a) replace a random subset of features with
    a baseline value, (b) record the drop in P(Y=1), and (c) record the summed
    attribution of the ablated features. A faithful explanation yields a high
    positive correlation between (b) and (c). Returns the mean over instances in
    [-1, 1]; higher is better.
    """
    rng = np.random.default_rng(random_state)
    X = np.asarray(X, dtype=float)
    attributions = np.asarray(attributions, dtype=float)
    n, d = X.shape
    subset_size = min(subset_size, d)
    classes = getattr(model, "classes_", np.array([0, 1]))
    pos = int(np.where(classes == 1)[0][0]) if 1 in classes else 1
    base = baseline if baseline is not None else X.mean(axis=0)

    base_pred = model.predict_proba(X)[:, pos]
    correlations: list[float] = []
    for i in range(n):
        attr_sums = np.empty(n_subsets)
        pred_drops = np.empty(n_subsets)
        for s in range(n_subsets):
            idx = rng.choice(d, size=subset_size, replace=False)
            x_pert = X[i].copy()
            x_pert[idx] = base[idx]
            pred_drops[s] = base_pred[i] - model.predict_proba(x_pert.reshape(1, -1))[0, pos]
            attr_sums[s] = attributions[i, idx].sum()
        if np.std(attr_sums) < 1e-12 or np.std(pred_drops) < 1e-12:
            continue
        correlations.append(float(np.corrcoef(attr_sums, pred_drops)[0, 1]))
    return float(np.mean(correlations)) if correlations else float("nan")


def quantus_faithfulness(model, X: np.ndarray, attributions: np.ndarray) -> dict[str, float] | None:
    """Optional: run Quantus' FaithfulnessCorrelation if the package is present.

    Returns ``None`` when ``quantus`` is not installed, so callers can fall back
    to :func:`faithfulness_correlation`.
    """
    try:
        import quantus
    except ImportError:
        return None
    metric = quantus.FaithfulnessCorrelation(return_aggregate=True, disable_warnings=True)
    classes = getattr(model, "classes_", np.array([0, 1]))
    pos = int(np.where(classes == 1)[0][0]) if 1 in classes else 1
    y = (model.predict_proba(X)[:, pos] >= 0.5).astype(int)
    score = metric(model=model, x_batch=X, y_batch=y, a_batch=attributions)
    return {"quantus_faithfulness_correlation": float(np.mean(score))}
