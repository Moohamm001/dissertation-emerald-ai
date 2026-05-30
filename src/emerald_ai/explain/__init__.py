"""Explainability stack (proposal §5.11).

Headline tier uses **SHAP** (exact TreeSHAP for the tree winner, exact linear
Shapley for linear models, KernelSHAP otherwise) for both global and local
explanations, plus **DiCE** for diverse counterfactual recourse. When those
optional deps are absent the module degrades gracefully to permutation
importance, a coefficient/importance proxy, and a greedy 1-D counterfactual —
so the package always runs, and every report states which path was taken.

Explanations are validated empirically (not assumed reliable) via the
faithfulness-correlation metric in :mod:`emerald_ai.explain.fidelity`.

Public entry points:
    global_importance        — permutation-importance ranking (model-agnostic)
    shap_global_importance   — mean(|SHAP|) ranking (preferred when available)
    local_explanation        — per-row contribution surface (SHAP when possible)
    nearest_counterfactual   — minimal single-feature change that flips Y
    diverse_counterfactuals  — DiCE diverse recourse (greedy fallback)
    faithfulness_correlation — empirical explanation-fidelity score
    HAS_SHAP                  — capability flag
"""

from __future__ import annotations

from emerald_ai.explain.counterfactual import (
    diverse_counterfactuals,
    nearest_counterfactual,
)
from emerald_ai.explain.fidelity import faithfulness_correlation
from emerald_ai.explain.shap_engine import (
    HAS_SHAP,
    global_importance,
    local_explanation,
    shap_global_importance,
)

__all__ = [
    "HAS_SHAP",
    "diverse_counterfactuals",
    "faithfulness_correlation",
    "global_importance",
    "local_explanation",
    "nearest_counterfactual",
    "shap_global_importance",
]
