"""Model architectures (proposal §5.8).

Six classifier families organised into three groups for controlled comparison:

  Linear baselines (regulatory-default class):
      lr_l1, lr_l2, svm_rbf  →  see emerald_ai.models.linear

  Tree ensembles (expected state of the art):
      rf, xgboost, lightgbm, catboost  →  see emerald_ai.models.trees

  Tabular deep learning (requires the [dl] extra / torch):
      mlp, ft_transformer  →  see emerald_ai.models.deep. The factories raise
      ImportError when torch is absent, so available_models() skips them.

Use `make_model(name, ...)` for the canonical entry point; it dispatches to
the right factory and returns an sklearn-compatible estimator (unfitted).

Monotonic constraints (proposal §5.8): the booster factories accept
`monotonic_constraints` keyed by feature index; the training harness wires
them up when Credit Score / Revenue / Time in Business survive selection.
"""
from __future__ import annotations

from typing import Callable

from emerald_ai.models.deep import make_ft_transformer, make_mlp
from emerald_ai.models.linear import make_lr_l1, make_lr_l2, make_svm_rbf
from emerald_ai.models.trees import (
    make_catboost,
    make_lightgbm,
    make_rf,
    make_xgboost,
)


FACTORIES: dict[str, Callable] = {
    "lr_l1": make_lr_l1,
    "lr_l2": make_lr_l2,
    "svm_rbf": make_svm_rbf,
    "rf": make_rf,
    "xgboost": make_xgboost,
    "lightgbm": make_lightgbm,
    "catboost": make_catboost,
    "mlp": make_mlp,
    "ft_transformer": make_ft_transformer,
}


def available_models() -> list[str]:
    """Names of model factories that can be instantiated in the current env.

    A factory is 'available' iff its import-time dependencies are present.
    LightGBM / CatBoost raise an ImportError at construction time when absent.
    """
    available: list[str] = []
    for name, factory in FACTORIES.items():
        try:
            factory()
        except (ImportError, ModuleNotFoundError):
            continue
        available.append(name)
    return available


def make_model(name: str, **kwargs):
    """Dispatch to the right factory by name. Raises KeyError if unknown."""
    if name not in FACTORIES:
        raise KeyError(f"Unknown model {name!r}. Available: {list(FACTORIES)}")
    return FACTORIES[name](**kwargs)


__all__ = ["FACTORIES", "available_models", "make_model"]


# Backward-compat shim for any caller still using the old dict-of-paths.
MODEL_REGISTRY: dict[str, str] = {
    "lr_l1": "emerald_ai.models.linear",
    "lr_l2": "emerald_ai.models.linear",
    "svm_rbf": "emerald_ai.models.linear",
    "rf": "emerald_ai.models.trees",
    "xgboost": "emerald_ai.models.trees",
    "lightgbm": "emerald_ai.models.trees",
    "catboost": "emerald_ai.models.trees",
    "mlp": "emerald_ai.models.deep",
    "ft_transformer": "emerald_ai.models.deep",
}
