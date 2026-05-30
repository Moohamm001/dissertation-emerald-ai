"""Percentile-based risk bands (proposal §5.12 + §5.14).

Because the dataset is extremely imbalanced (~0.36% defaults), the model's
predicted P(Y=1) values are heavily right-skewed: a hard 0.5 / 0.8 cut-off
classifies ~99.7% of applicants as "approve", so the decision — and any
fairness audit run on it — carries almost no information.

These percentile bands restore the decision's information value by cutting the
score distribution at fixed percentiles of the training pool:

    score <  p5   → high_risk   (decline / adverse action)
    p5 ≤ score < p20 → watch     (manual review)
    score ≥ p20   → approve

The trade-off (documented for the audit): the bands are *relative* to the
training-pool distribution rather than absolute probabilities. Both the API
(scoring badges) and the fairness audit consume this single source of truth so
the deployed decision and the audited decision are identical.
"""

from __future__ import annotations

import numpy as np

# Percentile of the training-pool score distribution at each band boundary.
RISK_BAND_PERCENTILES: dict[str, float] = {"high_risk": 5.0, "watch": 20.0}


def risk_band_thresholds(scores: np.ndarray) -> dict[str, float]:
    """Return the score cut-offs for each band from a pool of model scores.

    Keys: ``high_risk_cut`` (p5), ``watch_cut`` (p20), and the percentiles used.
    """
    s = np.asarray(scores, dtype=float)
    return {
        "high_risk_cut": float(np.percentile(s, RISK_BAND_PERCENTILES["high_risk"])),
        "watch_cut": float(np.percentile(s, RISK_BAND_PERCENTILES["watch"])),
        "high_risk_percentile": RISK_BAND_PERCENTILES["high_risk"],
        "watch_percentile": RISK_BAND_PERCENTILES["watch"],
    }


def band_for(p: float, thresholds: dict[str, float]) -> str:
    """Map a single probability to {high_risk, watch, approve} given cut-offs."""
    if p < thresholds["high_risk_cut"]:
        return "high_risk"
    if p < thresholds["watch_cut"]:
        return "watch"
    return "approve"
