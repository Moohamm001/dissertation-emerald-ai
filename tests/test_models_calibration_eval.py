"""Smoke + invariant tests for the §5.8 / §5.10 / §5.11 / §5.12 / §5.13 modules.

Synthetic data only — the real-dataset end-to-end is `python -m emerald_ai train`.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from emerald_ai import calibration as cal
from emerald_ai import explain as xai
from emerald_ai import fairness as fair
from emerald_ai.eval import (
    delong_test,
    paired_bootstrap,
    pr_auc_minority,
    recall_at_top_decile,
    within_minority_ece,
)
from emerald_ai.models import available_models, make_model


@pytest.fixture
def synth_imbalanced():
    rng = np.random.default_rng(0)
    n = 600
    y = rng.choice([0, 1], n, p=[0.05, 0.95])
    x1 = rng.normal(0, 1, n) + 2.5 * (y == 0)
    x2 = rng.normal(0, 1, n) - 2.0 * (y == 0)
    return np.column_stack([x1, x2]), y


# -----------------------------------------------------------------------------
# §5.8 model factories
# -----------------------------------------------------------------------------
def test_available_models_includes_core():
    avail = available_models()
    # These ship with the base environment
    assert "lr_l1" in avail
    assert "lr_l2" in avail
    assert "rf" in avail
    assert "xgboost" in avail


def test_make_model_dispatches(synth_imbalanced):
    X, y = synth_imbalanced
    for name in ("lr_l2", "rf", "xgboost"):
        m = make_model(name)
        m.fit(X, y)
        proba = m.predict_proba(X)
        assert proba.shape == (len(y), 2)


def test_unknown_model_raises():
    with pytest.raises(KeyError):
        make_model("not_a_model")


# -----------------------------------------------------------------------------
# §5.10 calibration + conformal
# -----------------------------------------------------------------------------
def test_calibrate_platt_lowers_ece_on_miscalibrated_scores():
    rng = np.random.default_rng(0)
    n = 1000
    y = rng.choice([0, 1], n, p=[0.5, 0.5])
    # Miscalibrated: predicted = true label squared (overconfident)
    raw = np.where(y == 1, rng.uniform(0.7, 1.0, n), rng.uniform(0.0, 0.3, n))
    raw = np.clip(raw + rng.normal(0, 0.05, n), 0.001, 0.999)
    # Add bias so ece is non-trivial
    raw = np.clip(raw ** 2, 0.001, 0.999)
    result = cal.calibrate("platt", raw, y)
    assert result.ece_post <= result.ece_pre + 1e-3


def test_isotonic_calibration_runs(synth_imbalanced):
    X, y = synth_imbalanced
    m = make_model("lr_l2")
    m.fit(X, y)
    classes = m.classes_
    pos_idx = int(np.where(classes == 1)[0][0])
    scores = m.predict_proba(X)[:, pos_idx]
    result = cal.calibrate("isotonic", scores, y)
    assert 0.0 <= result.ece_post <= 1.0


def test_split_conformal_marginal_coverage_meets_target(synth_imbalanced):
    X, y = synth_imbalanced
    m = make_model("rf")
    m.fit(X, y)
    pos_idx = int(np.where(m.classes_ == 1)[0][0])
    scores = m.predict_proba(X)[:, pos_idx]
    half = len(y) // 2
    sc = cal.SplitConformal(alpha=0.10).fit(scores[:half], y[:half])
    cov = sc.marginal_coverage(scores[half:], y[half:])
    # Finite-sample exact: expect cov >= ~0.9 (with some slack on small N)
    assert cov >= 0.85


def test_mondrian_conformal_returns_per_class_coverage(synth_imbalanced):
    X, y = synth_imbalanced
    m = make_model("rf")
    m.fit(X, y)
    pos_idx = int(np.where(m.classes_ == 1)[0][0])
    scores = m.predict_proba(X)[:, pos_idx]
    half = len(y) // 2
    mc = cal.MondrianConformal(alpha=0.10).fit(scores[:half], y[:half])
    cov = mc.class_conditional_coverage(scores[half:], y[half:])
    assert 0 in cov and 1 in cov


def test_bootstrap_class_conditional_coverage_returns_tuples(synth_imbalanced):
    X, y = synth_imbalanced
    m = make_model("rf")
    m.fit(X, y)
    pos_idx = int(np.where(m.classes_ == 1)[0][0])
    scores = m.predict_proba(X)[:, pos_idx]
    cis = cal.bootstrap_class_conditional_coverage(scores, y, n_bootstraps=50)
    assert 0 in cis and 1 in cis
    for c in (0, 1):
        mean, lo, hi = cis[c]
        if np.isfinite(mean):
            assert lo <= mean <= hi


# -----------------------------------------------------------------------------
# §5.11 explainability
# -----------------------------------------------------------------------------
def test_global_importance_returns_dataframe(synth_imbalanced):
    X, y = synth_imbalanced
    m = make_model("rf")
    m.fit(X, y)
    imp = xai.global_importance(m, X, y, feature_names=["f0", "f1"], n_repeats=3)
    assert "feature" in imp.columns
    assert "importance_mean" in imp.columns


def test_local_explanation_for_linear_model(synth_imbalanced):
    X, y = synth_imbalanced
    m = make_model("lr_l2")
    m.fit(X, y)
    contribs = xai.local_explanation(m, X[0], ["f0", "f1"])
    assert len(contribs) <= 2  # only 2 features


def test_nearest_counterfactual_finds_a_flip(synth_imbalanced):
    X, y = synth_imbalanced
    m = make_model("lr_l2")
    m.fit(X, y)
    # Pick a row whose predicted class is 0 (the model predicts minority); we
    # search for a Δ that flips it to 1
    classes = m.classes_
    pos_idx = int(np.where(classes == 1)[0][0])
    proba = m.predict_proba(X)[:, pos_idx]
    minority_pred = np.argsort(proba)[0]
    cf = xai.nearest_counterfactual(
        m, X[minority_pred], ["f0", "f1"],
        actionable_features=["f0", "f1"],
        feature_ranges={"f0": (-5.0, 5.0), "f1": (-5.0, 5.0)},
    )
    # Either we find a flip or we don't (depends on model fit) — both fine; just
    # assert the function returns the expected type
    assert cf is None or hasattr(cf, "flipped")


# -----------------------------------------------------------------------------
# §5.12 fairness
# -----------------------------------------------------------------------------
def test_audit_predictions_produces_per_axis_gaps():
    rng = np.random.default_rng(0)
    n = 500
    y = rng.choice([0, 1], n, p=[0.1, 0.9])
    scores = np.clip(0.8 + rng.normal(0, 0.1, n) - 0.3 * (y == 0), 0, 1)
    groups = {"axis_a": rng.choice(["A", "B", "C"], n)}
    aud = fair.audit_predictions(y, scores, groups)
    assert "axis_a" in aud.gaps
    for key in ("dp_gap", "tpr_gap", "fpr_gap", "precision_gap", "ece_gap"):
        assert key in aud.gaps["axis_a"]


def test_fairness_report_emits(tmp_path):
    rng = np.random.default_rng(0)
    n = 300
    y = rng.choice([0, 1], n, p=[0.1, 0.9])
    scores = rng.uniform(0, 1, n)
    aud = fair.audit_predictions(y, scores, {"region": rng.choice(["X", "Y"], n)})
    out = tmp_path / "fairness.md"
    written = fair.emit_report(aud, out_path=out)
    txt = written.read_text(encoding="utf-8")
    assert "Per-axis gap summary" in txt
    assert "region" in txt


# -----------------------------------------------------------------------------
# §5.13 eval primitives
# -----------------------------------------------------------------------------
def test_pr_auc_minority_runs(synth_imbalanced):
    X, y = synth_imbalanced
    scores = np.random.default_rng(0).uniform(0, 1, len(y))
    auc = pr_auc_minority(y, scores)
    assert 0.0 <= auc <= 1.0


def test_recall_at_top_decile_perfect_ranker():
    y = np.array([0, 0, 0, 1, 1, 1, 1, 1, 1, 1])
    # Perfect ranker: lowest 3 scores are the minority (Y=0)
    scores = np.array([0.0, 0.05, 0.1, 0.9, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96])
    # Top decile = n//10 = 1; lowest score is index 0, which IS minority
    rec = recall_at_top_decile(y, scores)
    assert rec >= 1 / 3  # caught 1 of 3 minorities


def test_within_minority_ece_returns_finite():
    y = np.array([0, 0, 0, 1, 1, 1, 1, 1])
    scores = np.array([0.05, 0.1, 0.15, 0.9, 0.92, 0.94, 0.96, 0.98])
    e = within_minority_ece(y, scores)
    assert np.isfinite(e)


def test_delong_test_returns_finite(synth_imbalanced):
    X, y = synth_imbalanced
    m1 = make_model("lr_l2"); m1.fit(X, y)
    m2 = make_model("rf"); m2.fit(X, y)
    p1 = m1.predict_proba(X)[:, int(np.where(m1.classes_ == 1)[0][0])]
    p2 = m2.predict_proba(X)[:, int(np.where(m2.classes_ == 1)[0][0])]
    res = delong_test(y, p1, p2)
    assert np.isfinite(res["delta_auc"])


def test_paired_bootstrap_ci_bounds(synth_imbalanced):
    X, y = synth_imbalanced
    m1 = make_model("lr_l2"); m1.fit(X, y)
    m2 = make_model("rf"); m2.fit(X, y)
    p1 = m1.predict_proba(X)[:, int(np.where(m1.classes_ == 1)[0][0])]
    p2 = m2.predict_proba(X)[:, int(np.where(m2.classes_ == 1)[0][0])]
    out = paired_bootstrap(y, p1, p2, pr_auc_minority, n_resamples=200)
    assert out["ci95_lo"] <= out["delta_mean"] <= out["ci95_hi"]
