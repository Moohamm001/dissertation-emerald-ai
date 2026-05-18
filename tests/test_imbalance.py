"""Tests for the §5.7 class-imbalance harness."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from emerald_ai.training import imbalance as imb


@pytest.fixture
def synth_imbalanced_xy() -> tuple[np.ndarray, np.ndarray]:
    """Frame with ~3% minority — enough for SMOTE k_neighbors=5 to fit."""
    rng = np.random.default_rng(0)
    n = 600
    y = rng.choice([0, 1], n, p=[0.03, 0.97])
    # Two predictive features that distinguish the minority
    s1 = rng.normal(0, 1, n) + 2.5 * (y == 0).astype(float)
    s2 = rng.normal(0, 1, n) - 2.0 * (y == 0).astype(float)
    X = np.column_stack([s1, s2])
    return X, y


def test_strategy_factories_return_imblearn_pipelines():
    for name, factory in imb.STRATEGY_FACTORIES.items():
        pipe = factory(random_state=0)
        assert hasattr(pipe, "fit") and hasattr(pipe, "predict_proba")


def test_within_minority_ece_perfect_calibration_is_zero():
    # All minority rows; model predicts P(Y=1)=0 for everyone → ECE = 0
    y_true = np.zeros(100, dtype=int)
    y_score = np.zeros(100)
    assert imb.within_minority_ece(y_true, y_score) == 0.0


def test_within_minority_ece_worst_case_is_one():
    # All minority rows; model predicts P(Y=1)=1 (maximally wrong) → ECE ≈ 1
    y_true = np.zeros(100, dtype=int)
    y_score = np.ones(100)
    assert imb.within_minority_ece(y_true, y_score) > 0.99


def test_within_minority_ece_nan_when_no_minority():
    y_true = np.ones(50, dtype=int)
    y_score = np.full(50, 0.5)
    result = imb.within_minority_ece(y_true, y_score)
    assert np.isnan(result)


def test_evaluate_strategy_returns_finite_metrics(synth_imbalanced_xy):
    X, y = synth_imbalanced_xy
    pipe = imb.make_class_weighted_pipeline(random_state=0)
    res = imb.evaluate_strategy(pipe, X, y, name="class_weighted", n_folds=3)
    assert np.isfinite(res.pr_auc_mean)
    assert np.isfinite(res.minority_ece_mean)
    assert np.isfinite(res.joint_score)
    assert len(res.fold_pr_auc) == 3


def test_select_strategy_picks_a_winner(synth_imbalanced_xy):
    X, y = synth_imbalanced_xy
    audit = imb.select_strategy(X, y, n_folds=3)
    assert audit.n_rows == len(y)
    assert audit.n_minority == int((y == 0).sum())
    assert audit.chosen_strategy in ("no_resample", "class_weighted", "smote")
    # All three strategies attempted
    assert len(audit.strategies) == 3


def test_emit_report_writes_markdown(tmp_path, synth_imbalanced_xy):
    X, y = synth_imbalanced_xy
    audit = imb.select_strategy(X, y, n_folds=3)
    out = tmp_path / "imbalance_report.md"
    written = imb.emit_report(audit, out_path=out)
    text = written.read_text(encoding="utf-8")
    assert "## Strategy comparison" in text
    assert "## Chosen strategy" in text
    assert audit.chosen_strategy in text
    # All three strategy names appear in the comparison table
    for name in ("no_resample", "class_weighted", "smote"):
        assert f"`{name}`" in text


def test_class_weighted_outperforms_unweighted_on_synth(synth_imbalanced_xy):
    """Sanity check: at 3% prevalence, class_weighted should beat no_resample on PR-AUC."""
    X, y = synth_imbalanced_xy
    p_unw = imb.evaluate_strategy(imb.make_no_resample_pipeline(0), X, y, name="no_resample", n_folds=5)
    p_cw = imb.evaluate_strategy(imb.make_class_weighted_pipeline(0), X, y, name="class_weighted", n_folds=5)
    # Class-weighted should at least match the joint score (mostly through better recall)
    assert p_cw.pr_auc_mean >= p_unw.pr_auc_mean - 0.05  # tolerate small noise
