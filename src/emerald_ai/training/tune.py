"""Optuna TPE hyperparameter optimisation (proposal §5.9).

The nested-CV harness in :mod:`emerald_ai.training.cv` ships a reduced-budget
``RandomizedSearchCV`` by default so the pipeline runs in minutes. This module
provides the proposal's full-fidelity alternative: a **Tree-structured Parzen
Estimator (TPE)** study with **median pruning**, searching continuous
distributions rather than a coarse grid, scored by stratified-CV PR-AUC against
the minority class.

It degrades gracefully — if ``optuna`` is not installed, ``HAS_OPTUNA`` is
``False`` and ``optuna_search`` raises a clear ImportError, so the caller falls
back to RandomizedSearchCV.

Entry point:
    optuna_search(family, X, y, *, n_trials, n_inner_folds, random_state)
        -> (best_params, best_estimator)   # estimator refit on all of (X, y)
"""

from __future__ import annotations

import numpy as np
from sklearn.model_selection import StratifiedKFold, cross_val_score

from emerald_ai.config import MODEL
from emerald_ai.models import FACTORIES

try:  # optional, gated dependency — see pyproject [ml] extra
    import optuna

    HAS_OPTUNA = True
    optuna.logging.set_verbosity(optuna.logging.WARNING)
except ImportError:  # pragma: no cover
    optuna = None
    HAS_OPTUNA = False


def suggest_params(trial, family: str) -> dict:
    """Sample one hyperparameter configuration for ``family`` from ``trial``.

    Search spaces mirror SEARCH_SPACES in cv.py but over continuous/log
    distributions, which is where TPE earns its keep over grid/random search.
    """
    if family in ("lr_l1", "lr_l2"):
        return {"C": trial.suggest_float("C", 1e-3, 1e2, log=True)}
    if family == "svm_rbf":
        return {
            "C": trial.suggest_float("C", 1e-2, 1e2, log=True),
            "gamma": trial.suggest_categorical("gamma", ["scale", "auto"]),
        }
    if family == "rf":
        return {
            "n_estimators": trial.suggest_int("n_estimators", 200, 900, step=100),
            "max_depth": trial.suggest_categorical("max_depth", [None, 6, 10, 16, 24]),
            "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 30, log=True),
        }
    if family == "xgboost":
        return {
            "n_estimators": trial.suggest_int("n_estimators", 200, 900, step=100),
            "max_depth": trial.suggest_int("max_depth", 3, 10),
            "learning_rate": trial.suggest_float("learning_rate", 1e-2, 3e-1, log=True),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        }
    if family == "lightgbm":
        return {
            "n_estimators": trial.suggest_int("n_estimators", 200, 900, step=100),
            "num_leaves": trial.suggest_int("num_leaves", 15, 127, log=True),
            "learning_rate": trial.suggest_float("learning_rate", 1e-2, 3e-1, log=True),
        }
    if family == "catboost":
        return {
            "iterations": trial.suggest_int("iterations", 200, 800, step=100),
            "depth": trial.suggest_int("depth", 4, 10),
            "learning_rate": trial.suggest_float("learning_rate", 1e-2, 3e-1, log=True),
        }
    return {}


def optuna_search(
    family: str,
    X: np.ndarray,
    y: np.ndarray,
    *,
    n_trials: int = 50,
    n_inner_folds: int = 3,
    timeout: float | None = None,
    random_state: int = MODEL.random_seed,
):
    """Run a TPE study for one family; return (best_params, refit best_estimator).

    Scoring is inner stratified-CV mean ``average_precision`` (PR-AUC) — the
    dissertation's primary metric. A median pruner kills unpromising trials
    early. The returned estimator is refit on all of ``(X, y)``.
    """
    if not HAS_OPTUNA:  # pragma: no cover
        raise ImportError('optuna is not installed. Install the [ml] extra: pip install -e ".[ml]"')

    X = np.asarray(X)
    y = np.asarray(y).astype(int)
    factory = FACTORIES[family]
    inner = StratifiedKFold(n_splits=n_inner_folds, shuffle=True, random_state=random_state)

    def objective(trial) -> float:
        params = suggest_params(trial, family)
        model = factory(random_state=random_state, **params)
        try:
            scores = cross_val_score(model, X, y, scoring="average_precision", cv=inner, n_jobs=-1)
        except Exception:  # pragma: no cover - reject infeasible configs
            return float("-inf")
        return float(np.mean(scores))

    sampler = optuna.samplers.TPESampler(seed=random_state)
    pruner = optuna.pruners.MedianPruner(n_warmup_steps=5)
    study = optuna.create_study(direction="maximize", sampler=sampler, pruner=pruner)
    study.optimize(objective, n_trials=n_trials, timeout=timeout, show_progress_bar=False)

    best_params = dict(study.best_params)
    best_estimator = factory(random_state=random_state, **best_params)
    best_estimator.fit(X, y)
    return best_params, best_estimator
