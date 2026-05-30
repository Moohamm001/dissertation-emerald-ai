"""Tests for the §5.8 tabular deep-learning models (torch-gated)."""

from __future__ import annotations

import importlib.util

import numpy as np
import pytest

HAS_TORCH = importlib.util.find_spec("torch") is not None
pytestmark = pytest.mark.skipif(not HAS_TORCH, reason="torch not installed")


@pytest.fixture
def toy_xy():
    rng = np.random.default_rng(0)
    n = 400
    X = rng.normal(size=(n, 8)).astype(np.float32)
    y = (2.0 * X[:, 0] - 1.5 * X[:, 1] + rng.normal(scale=0.5, size=n) > 0).astype(int)
    return X, y


def test_mlp_fits_and_learns_signal(toy_xy):
    from sklearn.metrics import roc_auc_score

    from emerald_ai.models import make_model

    X, y = toy_xy
    model = make_model("mlp", max_epochs=25, hidden=(32, 16))
    model.fit(X, y)
    proba = model.predict_proba(X)
    assert proba.shape == (len(y), 2)
    assert np.allclose(proba.sum(axis=1), 1.0, atol=1e-5)
    assert roc_auc_score(y, proba[:, 1]) > 0.75  # learned the planted signal


def test_ft_transformer_fits_and_predicts(toy_xy):
    from sklearn.metrics import roc_auc_score

    from emerald_ai.models import make_model

    X, y = toy_xy
    model = make_model("ft_transformer", max_epochs=25, d_token=16, n_blocks=2, n_heads=2)
    model.fit(X, y)
    proba = model.predict_proba(X)
    assert proba.shape == (len(y), 2)
    assert roc_auc_score(y, proba[:, 1]) > 0.70


def test_deep_models_are_clonable(toy_xy):
    """sklearn clone must work so the models slot into the CV harness."""
    from sklearn.base import clone

    from emerald_ai.models import make_model

    model = make_model("mlp", max_epochs=5)
    cloned = clone(model)  # raises if get_params/set_params are non-conformant
    assert cloned.max_epochs == 5


def test_deep_models_registered_when_torch_present():
    from emerald_ai.models import available_models

    avail = available_models()
    assert "mlp" in avail and "ft_transformer" in avail
