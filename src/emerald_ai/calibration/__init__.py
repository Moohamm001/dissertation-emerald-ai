"""Probability calibration + distribution-free uncertainty (proposal §5.10).

Pre-intervention diagnostics: reliability diagrams, Brier score, ECE.
Calibrators:                   Platt, isotonic, temperature scaling.
Uncertainty:                   split-conformal prediction (MAPIE).
"""
from __future__ import annotations
