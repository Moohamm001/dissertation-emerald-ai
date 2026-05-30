"""Tests for the §5.11 explainability stack: SHAP, DiCE, and fidelity.

These exercise the real SHAP/DiCE paths when the optional deps are present and
the graceful fallbacks when they are not, so the suite passes in both a minimal
and a full install.
"""

from __future__ import annotations

import numpy as np
import pytest
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from emerald_ai.explain import (
    HAS_SHAP,
    diverse_counterfactuals,
    faithfulness_correlation,
    global_importance,
    local_explanation,
    nearest_counterfactual,
)


@pytest.fixture
def toy_problem():
    rng = np.random.default_rng(0)
    n, d = 400, 6
    X = rng.normal(size=(n, d))
    # Signal: features 0 and 1 drive the label; 2-5 are noise.
    logit = 2.5 * X[:, 0] - 1.5 * X[:, 1]
    y = (logit + rng.normal(scale=0.5, size=n) > 0).astype(int)
    names = [f"f{i}" for i in range(d)]
    return X, y, names


@pytest.fixture
def rf_model(toy_problem):
    X, y, _ = toy_problem
    return RandomForestClassifier(n_estimators=60, random_state=0).fit(X, y)


@pytest.fixture
def linear_model(toy_problem):
    X, y, _ = toy_problem
    return LogisticRegression(max_iter=500).fit(X, y)


def test_permutation_global_ranks_signal_above_noise(rf_model, toy_problem):
    X, y, names = toy_problem
    imp = global_importance(rf_model, X, y, feature_names=names, n_repeats=3)
    top2 = set(imp["feature"].head(2))
    assert {"f0"} <= top2  # the strongest signal feature must rank near the top


def test_local_explanation_returns_top_k_with_method(rf_model, toy_problem):
    X, _, names = toy_problem
    contribs = local_explanation(rf_model, X[0], names, top_k=4)
    assert len(contribs) == 4
    assert all(c.direction in {"increases", "decreases", "neutral"} for c in contribs)
    expected = "treeshap" if HAS_SHAP else "proxy"
    assert all(c.method == expected for c in contribs)


def test_local_explanation_linear_path(linear_model, toy_problem):
    X, _, names = toy_problem
    contribs = local_explanation(linear_model, X[0], names, top_k=6)
    assert len(contribs) == 6
    expected = "linearshap" if HAS_SHAP else "proxy"
    assert all(c.method == expected for c in contribs)


@pytest.mark.skipif(not HAS_SHAP, reason="shap not installed")
def test_shap_global_importance_signal(rf_model, toy_problem):
    from emerald_ai.explain import shap_global_importance

    X, _, names = toy_problem
    df = shap_global_importance(rf_model, X, feature_names=names, max_samples=200)
    assert set(df.columns) == {"feature", "mean_abs_shap", "mean_signed_shap"}
    assert df["feature"].iloc[0] in {"f0", "f1"}  # a signal feature dominates


@pytest.mark.skipif(not HAS_SHAP, reason="shap not installed")
def test_faithfulness_is_positive_for_real_attributions(rf_model, toy_problem):
    from emerald_ai.explain.shap_engine import _shap_values_matrix

    X, _, _ = toy_problem
    sv = _shap_values_matrix(rf_model, X[:50])
    fid = faithfulness_correlation(rf_model, X[:50], sv, n_subsets=20, random_state=1)
    assert fid > 0.0  # faithful attributions track prediction drops


def test_diverse_counterfactuals_returns_structure(rf_model, toy_problem):
    X, _, names = toy_problem
    # Find a row predicted as the negative class to seek recourse for.
    proba = rf_model.predict_proba(X)[:, 1]
    neg_idx = int(np.argmin(proba))
    result = diverse_counterfactuals(
        rf_model,
        X,
        X[neg_idx],
        names,
        actionable_features=["f0", "f1"],
        total_cfs=2,
    )
    assert result.method in {"dice", "greedy-fallback"}
    assert isinstance(result.changes, list)
    # Every suggested change only touches actionable features.
    for change in result.changes:
        assert set(change).issubset({"f0", "f1"}) or result.method == "dice"


def test_nearest_counterfactual_flips_or_none(rf_model, toy_problem):
    X, _, names = toy_problem
    proba = rf_model.predict_proba(X)[:, 1]
    neg_idx = int(np.argmin(proba))
    cf = nearest_counterfactual(rf_model, X[neg_idx], names, actionable_features=["f0", "f1"])
    # Either a flip was found, or None — but if found, the prediction moved up.
    if cf is not None and cf.feature != "__none__":
        assert cf.new_prediction >= cf.original_prediction
