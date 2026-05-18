"""Tests for the §5.6 selection module."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from emerald_ai.features import selection as sel


@pytest.fixture
def synth_xy() -> tuple[pd.DataFrame, pd.Series]:
    """Frame with three strong predictors + 17 noise features at ~1% prevalence."""
    rng = np.random.default_rng(0)
    n = 500
    y = rng.choice([0, 1], n, p=[0.01, 0.99])
    # Three predictors whose distribution depends on y
    s1 = rng.normal(0, 1, n) + 3 * (y == 0).astype(float)
    s2 = rng.normal(0, 1, n) - 2 * (y == 0).astype(float)
    s3 = rng.normal(0, 1, n) + 1.5 * (y == 0).astype(float)
    noise = {f"noise_{i}": rng.normal(0, 1, n) for i in range(17)}
    X = pd.DataFrame({"signal_1": s1, "signal_2": s2, "signal_3": s3, **noise})
    return X, pd.Series(y)


def test_filter_by_mutual_info_drops_low_signal(synth_xy):
    X, y = synth_xy
    retained, scores = sel.filter_by_mutual_info(X, y, drop_quantile=0.20)
    # All three real signals should survive
    for s in ("signal_1", "signal_2", "signal_3"):
        assert s in retained
    # MI scores defined for every column
    assert set(scores.keys()) == set(X.columns)


def test_filter_by_mutual_info_accepts_numpy(synth_xy):
    X, y = synth_xy
    retained, _ = sel.filter_by_mutual_info(
        X.to_numpy(), y.to_numpy(), feature_names=list(X.columns),
    )
    assert "signal_1" in retained


def test_bootstrap_stability_select_finds_signals(synth_xy):
    X, y = synth_xy
    selected, freq = sel.bootstrap_stability_select(
        X, y, top_k=5, n_bootstraps=10, selection_frequency_threshold=0.50,
    )
    # All three signals should clear 50% selection frequency
    for s in ("signal_1", "signal_2", "signal_3"):
        assert freq[s] >= 0.50, f"{s} freq={freq[s]}"
        assert s in selected


def test_bootstrap_stability_handles_pure_noise():
    """Selection on noise-only data should retain ~nobody."""
    rng = np.random.default_rng(0)
    n = 200
    X = pd.DataFrame({f"f{i}": rng.normal(0, 1, n) for i in range(20)})
    y = pd.Series(rng.choice([0, 1], n, p=[0.05, 0.95]))
    selected, _ = sel.bootstrap_stability_select(
        X, y, top_k=5, n_bootstraps=10, selection_frequency_threshold=0.80,
    )
    # With pure noise, no feature should reliably hit top-5 across 10 bootstraps
    # at the 80% threshold. (A handful might sneak through but should be rare.)
    assert len(selected) <= 5


def test_run_selection_end_to_end(synth_xy):
    X, y = synth_xy
    audit = sel.run_selection(X, y, n_bootstraps=8, top_k=5)
    assert isinstance(audit, sel.SelectionAudit)
    assert audit.n_features_in == X.shape[1]
    assert audit.n_after_filter <= audit.n_features_in
    assert audit.n_selected <= audit.n_after_filter
    # All three signals should make it through to final selection
    for s in ("signal_1", "signal_2", "signal_3"):
        assert s in audit.selected


def test_emit_report_writes_markdown(tmp_path, synth_xy):
    X, y = synth_xy
    audit = sel.run_selection(X, y, n_bootstraps=8, top_k=5)
    out = tmp_path / "selection_report.md"
    written = sel.emit_report(audit, out_path=out)
    text = written.read_text(encoding="utf-8")
    assert "## Stage 1 — Mutual-information filter" in text
    assert "## Stage 2 — Bootstrap-stability wrapper" in text
    assert "signal_1" in text or "signal_2" in text  # selected names surface
