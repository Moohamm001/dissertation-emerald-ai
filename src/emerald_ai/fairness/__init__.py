"""Fairness audit on green-lending proxy axes (proposal §5.12).

Metrics (computed per axis: Industry, Borrower State, Business Size):
    - demographic-parity gap
    - equalised-odds gap (TPR + FPR differences)
    - predictive-parity gap (precision differences)
    - calibration-within-group via group-stratified reliability diagrams

Mitigations (triggered when thresholds breached):
    - reweighting (Kamiran & Calders 2012)
    - adversarial debiasing (Zhang et al. 2018)
"""
from __future__ import annotations
