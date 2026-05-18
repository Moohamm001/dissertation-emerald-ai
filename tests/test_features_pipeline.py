"""Tests for the preprocessing pipeline (proposal §5.5).

Synthetic frames let the tests run without the proprietary dataset; the
real-data end-to-end is covered by `python -m emerald_ai preprocess`.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from emerald_ai.features import pipeline as pp


@pytest.fixture
def synth_xy() -> tuple[pd.DataFrame, pd.Series]:
    rng = np.random.default_rng(0)
    n = 400
    X = pd.DataFrame({
        # numeric, sub-threshold missing
        "Credit Score": rng.normal(700, 50, n),
        "Revenue": rng.normal(50000, 15000, n),
        # numeric, missingness above 40% — should be dropped
        "HighMissingNum": [np.nan] * int(n * 0.6) + list(rng.normal(0, 1, n - int(n * 0.6))),
        # low-cardinality categorical
        "Borrower State": rng.choice(["TX", "CA", "NY", "FL"], n),
        # high-cardinality categorical (>10 levels)
        "Industry": rng.choice([f"sector_{i}" for i in range(15)], n),
        # time-leaking column flagged by EDA
        "Start Month": rng.integers(1, 13, n),
        # datetime — should be dropped (deferred to §5.6)
        "Contract Signed TS": pd.date_range("2019-01-01", periods=n, freq="D"),
    })
    y = pd.Series(rng.choice([0, 1], n, p=[0.05, 0.95]), name="Y")
    return X, y


def test_build_preprocessor_returns_transformer_and_audit(synth_xy):
    X, _ = synth_xy
    pre, audit = pp.build_preprocessor(X)
    assert pre is not None
    assert isinstance(audit, pp.PreprocessAudit)
    assert audit.n_input_columns == X.shape[1]
    assert audit.missingness_threshold == pp.DEFAULT_MISSINGNESS_THRESHOLD


def test_high_missingness_columns_are_dropped(synth_xy):
    X, _ = synth_xy
    _pre, audit = pp.build_preprocessor(X)
    assert "HighMissingNum" in audit.drop_high_missingness


def test_time_leaking_columns_are_dropped(synth_xy):
    X, _ = synth_xy
    _pre, audit = pp.build_preprocessor(X)
    assert "Start Month" in audit.drop_time_leaking


def test_datetime_columns_are_dropped(synth_xy):
    X, _ = synth_xy
    _pre, audit = pp.build_preprocessor(X)
    assert "Contract Signed TS" in audit.drop_datetime


def test_low_high_cardinality_split(synth_xy):
    X, _ = synth_xy
    _pre, audit = pp.build_preprocessor(X)
    # Borrower State has 4 levels → low-card; Industry has 15 → high-card
    assert "Borrower State" in audit.low_cardinality_cols
    assert "Industry" in audit.high_cardinality_cols


def test_numeric_columns_are_kept(synth_xy):
    X, _ = synth_xy
    _pre, audit = pp.build_preprocessor(X)
    assert "Credit Score" in audit.numeric_cols
    assert "Revenue" in audit.numeric_cols
    # The high-missingness numeric must NOT be in the retained list
    assert "HighMissingNum" not in audit.numeric_cols


def test_fit_transform_with_audit_runs_end_to_end(synth_xy):
    X, y = synth_xy
    X_t, fitted, audit = pp.fit_transform_with_audit(X, y)
    assert X_t.shape[0] == X.shape[0]
    # Output dim must exceed numeric count (one-hot + indicators inflate)
    assert X_t.shape[1] > len(audit.numeric_cols)
    assert audit.n_output_features == X_t.shape[1]
    # Numerics should be standardised (mean ~ 0 by column)
    n_num = len(audit.numeric_cols)
    if n_num:
        col_means = np.abs(X_t[:, :n_num].mean(axis=0))
        assert (col_means < 1e-6).all()


def test_drop_time_leaking_can_be_disabled(synth_xy):
    X, _ = synth_xy
    _pre, audit = pp.build_preprocessor(X, drop_time_leaking=False)
    assert audit.drop_time_leaking == []
    # Start Month is numeric so it'll fall into numeric_cols
    assert "Start Month" in audit.numeric_cols


def test_emit_report_writes_markdown(tmp_path, synth_xy):
    X, y = synth_xy
    _X_t, _fitted, audit = pp.fit_transform_with_audit(X, y)
    out = tmp_path / "preprocess_report.md"
    written = pp.emit_report(audit, out_path=out)
    assert written == out
    text = out.read_text(encoding="utf-8")
    # Section headers present
    assert "## Stage 1 — Drop list" in text
    assert "## Stage 2 — Missing-data treatment" in text
    assert "## Stage 3 — Encoding" in text
    assert "## Stage 4 — Scaling" in text
    # Empirical drops surface in the markdown
    assert "HighMissingNum" in text
    assert "Start Month" in text


def test_target_encoder_handles_unseen_categorical_levels(synth_xy):
    X, y = synth_xy
    _X_t, fitted, _audit = pp.fit_transform_with_audit(X, y)
    # Construct a new row whose Industry value never appeared at fit time
    new = X.iloc[:1].copy()
    new.loc[:, "Industry"] = "sector_unseen"
    new.loc[:, "Borrower State"] = "ZZ"  # unseen state too
    # Must not raise — OneHotEncoder configured with handle_unknown='ignore'
    out = fitted.transform(new)
    assert out.shape[0] == 1
    assert np.isfinite(out).all()
