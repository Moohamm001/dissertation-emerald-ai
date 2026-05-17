"""Two-stage feature selection: mutual-info filter + Boruta/SHAP wrapper (proposal §5.6)."""
from __future__ import annotations


def filter_by_mutual_info(threshold: float = 0.1) -> list[str]:
    """Stage 1: drop bottom decile by mutual information against Y."""
    raise NotImplementedError


def boruta_shap_intersection(n_bootstraps: int = 30) -> list[str]:
    """Stage 2: features clearing both Boruta and SHAP-importance thresholds, with bootstrap stability check."""
    raise NotImplementedError
