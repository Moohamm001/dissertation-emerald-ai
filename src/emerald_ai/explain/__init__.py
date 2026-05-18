"""Explainability stack (proposal §5.11).

First-cut implementation uses sklearn's permutation importance and tree
`feature_importances_` for global explanations and a simple grid-search
counterfactual for local recourse. TreeSHAP / KernelSHAP / DiCE / Quantus
land in a follow-up once their deps (shap, dice-ml, quantus) are added.

Public entry points:
    global_importance       — per-feature mean-attribution rankings
    local_explanation       — per-row contribution surface (linear / tree)
    nearest_counterfactual  — minimal numeric feature change that flips Y
"""
from __future__ import annotations

from emerald_ai.explain.shap_engine import (
    global_importance,
    local_explanation,
)
from emerald_ai.explain.counterfactual import nearest_counterfactual

__all__ = ["global_importance", "local_explanation", "nearest_counterfactual"]
