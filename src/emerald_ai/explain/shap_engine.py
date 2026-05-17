"""TreeSHAP (primary) + KernelSHAP (cross-check) (proposal §5.11).

References (literature/papers/):
    lundberg2017shap.md   — original SHAP, axiomatic uniqueness
    lundberg2020trees.md  — TreeSHAP, exact polynomial-time attribution
    aas2021explaining.md  — KernelSHAP bias under feature dependence (cross-check rationale)
"""
from __future__ import annotations
