"""Counterfactual recourse (proposal §5.11).

First-cut implementation: greedy 1-D search over a configurable list of
actionable numeric features. Looks for the minimum signed change that flips
the model's predicted class. DiCE swap-in (proper multi-feature diverse
counterfactuals) lands when the `dice-ml` dep is approved.

The proposal's interpretation (proposal §5.11 + Wachter et al., 2017): a
counterfactual under GDPR Art. 22 should be (a) actionable, (b) sparse,
(c) plausible. This first cut handles (a) via the caller-supplied feature
list and (b) via the single-feature scan; (c) is checked manually for now.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class Counterfactual:
    feature: str
    original_value: float
    new_value: float
    delta: float
    original_prediction: float
    new_prediction: float
    flipped: bool


def nearest_counterfactual(
    model,
    x_row: np.ndarray,
    feature_names: list[str],
    *,
    actionable_features: list[str],
    feature_ranges: dict[str, tuple[float, float]] | None = None,
    n_steps: int = 50,
    target_class: int = 1,
    threshold: float = 0.5,
    minority_label: int = 0,
) -> Counterfactual | None:
    """Search each actionable feature for the smallest 1-D change that flips
    the decision toward ``target_class``.

    Returns the best (smallest |Δ|) flip found, or ``None`` if no actionable
    feature can flip the prediction within its configured range.
    """
    x = np.asarray(x_row, dtype=float).reshape(1, -1).copy()
    name_to_idx = {n: i for i, n in enumerate(feature_names)}

    proba0 = model.predict_proba(x)
    classes = model.classes_ if hasattr(model, "classes_") else np.array([0, 1])
    target_idx = int(np.where(classes == target_class)[0][0]) if target_class in classes else 1
    p0 = float(proba0[0, target_idx])
    if (target_class == 1 and p0 >= threshold) or (target_class == 0 and p0 < threshold):
        # Already on the target side — no recourse needed
        return Counterfactual(
            feature="__none__",
            original_value=float("nan"),
            new_value=float("nan"),
            delta=0.0,
            original_prediction=p0,
            new_prediction=p0,
            flipped=True,
        )

    best: Counterfactual | None = None
    for f in actionable_features:
        if f not in name_to_idx:
            continue
        idx = name_to_idx[f]
        orig = float(x[0, idx])
        if feature_ranges and f in feature_ranges:
            lo, hi = feature_ranges[f]
        else:
            lo, hi = orig - 3.0, orig + 3.0  # standardised-scale default
        sweep = np.linspace(lo, hi, n_steps)
        for v in sweep:
            x[0, idx] = v
            p = float(model.predict_proba(x)[0, target_idx])
            flipped = (p >= threshold) if target_class == 1 else (p < threshold)
            if flipped:
                cand = Counterfactual(
                    feature=f, original_value=orig, new_value=float(v),
                    delta=float(v - orig), original_prediction=p0, new_prediction=p,
                    flipped=True,
                )
                if best is None or abs(cand.delta) < abs(best.delta):
                    best = cand
                break
        # Restore the feature for the next iteration
        x[0, idx] = orig
    return best
