"""Evaluation metrics + statistical comparison (proposal §5.13).

Primary:   PR-AUC.
Secondary: ROC-AUC, KS, F1@operating-point, recall@top-decile, Brier, ECE, MCC.
Tests:     DeLong (AUC), paired bootstrap (PR-AUC, ECE).
"""
from __future__ import annotations
