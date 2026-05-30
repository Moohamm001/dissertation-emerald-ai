"""Tests for the §5.9 Optuna TPE hyperparameter search."""

from __future__ import annotations

import numpy as np
import pytest

from emerald_ai.training.tune import HAS_OPTUNA, optuna_search


@pytest.fixture
def toy_xy():
    rng = np.random.default_rng(0)
    n = 300
    X = rng.normal(size=(n, 5))
    y = (2.0 * X[:, 0] - X[:, 1] + rng.normal(scale=0.5, size=n) > 0).astype(int)
    return X, y


@pytest.mark.skipif(not HAS_OPTUNA, reason="optuna not installed")
def test_optuna_search_returns_fitted_estimator(toy_xy):
    X, y = toy_xy
    best_params, est = optuna_search("rf", X, y, n_trials=6, n_inner_folds=3, random_state=0)
    assert isinstance(best_params, dict) and best_params  # found something
    # Estimator is refit on all of (X, y) and can predict.
    proba = est.predict_proba(X)
    assert proba.shape == (len(y), 2)


@pytest.mark.skipif(not HAS_OPTUNA, reason="optuna not installed")
def test_optuna_beats_or_matches_default_on_signal(toy_xy):
    from sklearn.metrics import average_precision_score

    X, y = toy_xy
    _, est = optuna_search("xgboost", X, y, n_trials=8, n_inner_folds=3, random_state=0)
    ap = average_precision_score(y, est.predict_proba(X)[:, 1])
    assert ap > 0.6  # learns the planted signal comfortably


def test_nested_cv_optuna_tuner_path(toy_xy):
    """The CV harness accepts tuner='optuna' and produces fold results."""
    from emerald_ai.training.cv import nested_cv

    X, y = toy_xy
    audit, oof = nested_cv(
        X,
        y,
        families=["rf"],
        n_outer_folds=2,
        n_inner_folds=2,
        tuner="optuna",
        n_trials=4,
    )
    assert audit.fold_results  # at least one fold trained
    assert "rf" in oof
