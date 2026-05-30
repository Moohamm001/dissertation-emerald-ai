"""Evaluation metrics + statistical comparison (proposal §5.13).

Primary metric tier (v0.4.1 §5.13):
    pr_auc_minority           — Precision-Recall AUC against the minority class.
    within_minority_ece       — ECE on the minority subset (calibration on the
                                 class that matters for adverse-action decisions).
    recall_at_top_decile      — regulator-relevant recall in the top-10% riskiest.

Secondary (cross-study comparability only):
    roc_auc, ks_statistic, f1, brier, ece, mcc, conformal_marginal_coverage.

Statistical comparison:
    delong_test               — paired AUC test (DeLong et al., 1988).
    paired_bootstrap          — 10,000-resample CI for any metric pair.

Raw accuracy is *deliberately excluded* — constant predictor scores 99.64%
on this prevalence and the metric is uninformative.
"""
from __future__ import annotations

from emerald_ai.eval.metrics import (
    brier_score,
    delong_test,
    ece,
    f1_at,
    ks_statistic,
    matthews_corrcoef,
    paired_bootstrap,
    pr_auc_minority,
    recall_at_top_decile,
    roc_auc,
    within_minority_ece,
)
from emerald_ai.eval.risk_bands import (
    RISK_BAND_PERCENTILES,
    band_for,
    risk_band_thresholds,
)

__all__ = [
    "RISK_BAND_PERCENTILES",
    "band_for",
    "brier_score",
    "delong_test",
    "ece",
    "f1_at",
    "ks_statistic",
    "matthews_corrcoef",
    "paired_bootstrap",
    "pr_auc_minority",
    "recall_at_top_decile",
    "risk_band_thresholds",
    "roc_auc",
    "within_minority_ece",
]
