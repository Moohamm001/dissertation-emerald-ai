"""Tree ensembles for the §5.8 benchmark.

Four factories, all returning sklearn-compatible estimators:
  make_rf       — sklearn RandomForestClassifier (variance-reduction baseline).
  make_xgboost  — XGBoost (primary candidate; monotonic constraints supported).
  make_lightgbm — LightGBM (alternative GBDT; ImportError if dep missing).
  make_catboost — CatBoost (categorical-native; ImportError if dep missing).

`monotonic_constraints` is a list of {-1, 0, +1} of length n_features
(non-decreasing on +1 ⇒ higher Credit Score / Revenue / Time in Business
yields non-decreasing P(Y=1|X)). The training harness in §5.9 wires this
when those features are present in X.
"""
from __future__ import annotations

from typing import Sequence

from sklearn.ensemble import RandomForestClassifier

from emerald_ai.config import MODEL


def make_rf(
    *,
    n_estimators: int = 400,
    max_depth: int | None = None,
    min_samples_leaf: int = 5,
    class_weight: str | None = "balanced_subsample",
    random_state: int = MODEL.random_seed,
    **_unused,
) -> RandomForestClassifier:
    """Random Forest with class-balanced subsample for the §5.4 prevalence."""
    return RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_leaf=min_samples_leaf,
        class_weight=class_weight,
        n_jobs=-1,
        random_state=random_state,
    )


def make_xgboost(
    *,
    n_estimators: int = 400,
    max_depth: int = 6,
    learning_rate: float = 0.05,
    subsample: float = 0.8,
    colsample_bytree: float = 0.8,
    scale_pos_weight: float | None = None,
    monotonic_constraints: Sequence[int] | None = None,
    random_state: int = MODEL.random_seed,
    **_unused,
):
    """XGBoost — primary candidate of proposal §5.8.

    `scale_pos_weight` is the GBM equivalent of `class_weight='balanced'`.
    Caller can pass it explicitly; if `None`, defaults to the prevalence-
    derived value (sum_neg / sum_pos) applied automatically at fit time.

    `monotonic_constraints` should be a tuple of {-1, 0, +1} of length
    n_features; the training harness builds it from the selected feature
    list against the proposal's directional priors.
    """
    import xgboost as xgb

    params: dict = {
        "n_estimators": n_estimators,
        "max_depth": max_depth,
        "learning_rate": learning_rate,
        "subsample": subsample,
        "colsample_bytree": colsample_bytree,
        "objective": "binary:logistic",
        "eval_metric": "aucpr",
        "tree_method": "hist",
        "random_state": random_state,
        "n_jobs": -1,
    }
    if scale_pos_weight is not None:
        params["scale_pos_weight"] = scale_pos_weight
    if monotonic_constraints is not None:
        params["monotone_constraints"] = "(" + ",".join(str(c) for c in monotonic_constraints) + ")"
    return xgb.XGBClassifier(**params)


def make_lightgbm(
    *,
    n_estimators: int = 400,
    max_depth: int = -1,
    num_leaves: int = 31,
    learning_rate: float = 0.05,
    class_weight: str | None = "balanced",
    monotonic_constraints: Sequence[int] | None = None,
    random_state: int = MODEL.random_seed,
    **_unused,
):
    """LightGBM — alternative GBDT. Requires `lightgbm` package."""
    try:
        import lightgbm as lgb
    except ImportError as exc:
        raise ImportError(
            "lightgbm is not installed. Add it to the project deps or "
            "use `pip install lightgbm`."
        ) from exc
    params: dict = {
        "n_estimators": n_estimators,
        "max_depth": max_depth,
        "num_leaves": num_leaves,
        "learning_rate": learning_rate,
        "class_weight": class_weight,
        "objective": "binary",
        "random_state": random_state,
        "n_jobs": -1,
        "verbose": -1,
    }
    if monotonic_constraints is not None:
        params["monotone_constraints"] = list(monotonic_constraints)
    return lgb.LGBMClassifier(**params)


def make_catboost(
    *,
    iterations: int = 400,
    depth: int = 6,
    learning_rate: float = 0.05,
    class_weights: Sequence[float] | None = None,
    monotonic_constraints: Sequence[int] | None = None,
    random_state: int = MODEL.random_seed,
    **_unused,
):
    """CatBoost — categorical-native gradient booster. Requires `catboost`."""
    try:
        from catboost import CatBoostClassifier
    except ImportError as exc:
        raise ImportError(
            "catboost is not installed. Add it to the project deps or "
            "use `pip install catboost`."
        ) from exc
    params: dict = {
        "iterations": iterations,
        "depth": depth,
        "learning_rate": learning_rate,
        "random_seed": random_state,
        "verbose": 0,
        "loss_function": "Logloss",
        "eval_metric": "PRAUC:type=Classic",
    }
    if class_weights is not None:
        params["class_weights"] = list(class_weights)
    if monotonic_constraints is not None:
        params["monotone_constraints"] = list(monotonic_constraints)
    return CatBoostClassifier(**params)
