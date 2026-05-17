"""Three-layer explainability stack (proposal §5.11).

Global:        TreeSHAP mean-|φ|, SHAP interaction values, PDP/ALE, monotonicity
               verification.
Local:         per-applicant TreeSHAP waterfall; KernelSHAP cross-check sample;
               LIME secondary explanation.
Counterfactual: DiCE — minimal feature changes flipping the decision; constrained
                to actionable features; plausibility-checked against training dist.

Explanation fidelity is empirically validated via Quantus.
"""
from __future__ import annotations
