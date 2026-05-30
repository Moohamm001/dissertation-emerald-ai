"""Tests for §5.12/§5.14 percentile risk bands and the fairness audit at them."""

from __future__ import annotations

import numpy as np

from emerald_ai.eval.risk_bands import band_for, risk_band_thresholds


def test_thresholds_are_ordered_percentiles():
    rng = np.random.default_rng(0)
    scores = rng.beta(8, 2, size=5000)  # right-skewed, like the real model
    thr = risk_band_thresholds(scores)
    assert thr["high_risk_cut"] <= thr["watch_cut"]
    assert thr["high_risk_percentile"] == 5.0
    assert thr["watch_percentile"] == 20.0
    # ~5% below high_risk_cut, ~20% below watch_cut, by construction.
    assert abs((scores < thr["high_risk_cut"]).mean() - 0.05) < 0.02
    assert abs((scores < thr["watch_cut"]).mean() - 0.20) < 0.02


def test_band_for_maps_each_region():
    thr = {"high_risk_cut": 0.3, "watch_cut": 0.6}
    assert band_for(0.1, thr) == "high_risk"
    assert band_for(0.45, thr) == "watch"
    assert band_for(0.9, thr) == "approve"


def test_audit_at_risk_band_threshold_is_non_degenerate():
    """At a percentile cut-off the audit produces non-zero, informative gaps."""
    from emerald_ai.fairness import audit_predictions

    rng = np.random.default_rng(1)
    n = 4000
    # Two groups with genuinely different score distributions.
    group = rng.integers(0, 2, size=n)
    scores = np.clip(rng.normal(0.9 + 0.05 * group, 0.05), 0, 1)
    y = (rng.random(n) < scores).astype(int)
    thr = risk_band_thresholds(scores)
    audit = audit_predictions(y, scores, {"grp": group}, threshold=thr["watch_cut"])
    # Selection rate is no longer ~100% everywhere, so DP gap is meaningful.
    rates = [r.selection_rate for r in audit.axes["grp"]]
    assert max(rates) < 0.99
    assert audit.gaps["grp"]["dp_gap"] > 0.0
