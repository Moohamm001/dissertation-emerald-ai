"""Fairness audit on green-lending proxy axes (proposal §5.12).

Metrics (computed per axis: Industry, Borrower State, Business Size):
    - demographic-parity gap
    - equalised-odds gap (TPR + FPR differences)
    - predictive-parity gap (precision differences)
    - calibration-within-group (group-stratified ECE)

Implementation is dep-light (no AIF360) — the proposal calls AIF360 out as
the eventual home for in-/post-processing mitigations, but the audit
*metric layer* can be computed directly from y_true / y_pred / sensitive.

The Selbst et al. (2019) sociotechnical traps frame the audit's
interpretation; see `data/governance/fairness_report.md` for the policy
the dissertation commits to.
"""
from __future__ import annotations

from emerald_ai.fairness.audit import (
    FairnessAudit,
    GroupResult,
    audit_predictions,
    emit_report,
)

__all__ = ["FairnessAudit", "GroupResult", "audit_predictions", "emit_report"]
