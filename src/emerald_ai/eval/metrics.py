"""Evaluation metric primitives + statistical comparison tests (proposal §5.13).

All functions operate on flat arrays so they compose with the OOF predictions
produced by `emerald_ai.training.cv.nested_cv`. Each is unit-testable in
isolation.
"""
from __future__ import annotations

from typing import Callable

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    f1_score,
    matthews_corrcoef as _mcc,
    roc_auc_score,
)


# -----------------------------------------------------------------------------
# Primary tier
# -----------------------------------------------------------------------------
def pr_auc_minority(y_true: np.ndarray, y_score: np.ndarray, *, minority_label: int = 0) -> float:
    """PR-AUC against the minority class."""
    y = np.asarray(y_true, dtype=int)
    s = np.asarray(y_score, dtype=float)
    if minority_label == 0:
        return float(average_precision_score(y == 0, 1 - s))
    return float(average_precision_score(y == 1, s))


def within_minority_ece(
    y_true: np.ndarray, y_score: np.ndarray, *, minority_label: int = 0, n_bins: int = 10
) -> float:
    """ECE restricted to rows where y == minority_label."""
    y = np.asarray(y_true, dtype=int)
    s = np.asarray(y_score, dtype=float)
    mask = y == minority_label
    if not mask.any():
        return float("nan")
    p = s[mask]
    bins = np.linspace(0, 1, n_bins + 1)
    bin_ids = np.clip(np.digitize(p, bins) - 1, 0, n_bins - 1)
    out = 0.0
    for b in range(n_bins):
        m = bin_ids == b
        if not m.any():
            continue
        out += (m.sum() / len(p)) * abs(float(p[m].mean()) - 0.0)
    return float(out)


def recall_at_top_decile(
    y_true: np.ndarray, y_score: np.ndarray, *, minority_label: int = 0
) -> float:
    """Recall on minority class among the top-10% riskiest predictions."""
    y = np.asarray(y_true, dtype=int)
    s = np.asarray(y_score, dtype=float)
    n = len(s)
    if n == 0:
        return float("nan")
    k = max(1, n // 10)
    riskiest = np.argsort(s)[:k] if minority_label == 0 else np.argsort(s)[::-1][:k]
    mask = y == minority_label
    if not mask.any():
        return float("nan")
    return float(mask[riskiest].sum() / mask.sum())


# -----------------------------------------------------------------------------
# Secondary tier
# -----------------------------------------------------------------------------
def roc_auc(y_true: np.ndarray, y_score: np.ndarray) -> float:
    return float(roc_auc_score(np.asarray(y_true).astype(int), np.asarray(y_score)))


def ks_statistic(y_true: np.ndarray, y_score: np.ndarray) -> float:
    """Industry-standard KS in credit risk = max |TPR - FPR|."""
    y = np.asarray(y_true, dtype=int)
    s = np.asarray(y_score, dtype=float)
    order = np.argsort(-s)
    y_ord = y[order]
    pos = (y_ord == 1).astype(int)
    neg = (y_ord == 0).astype(int)
    n_pos = pos.sum()
    n_neg = neg.sum()
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    tpr = np.cumsum(pos) / n_pos
    fpr = np.cumsum(neg) / n_neg
    return float(np.max(np.abs(tpr - fpr)))


def f1_at(y_true: np.ndarray, y_score: np.ndarray, *, threshold: float = 0.5) -> float:
    y_pred = (np.asarray(y_score) >= threshold).astype(int)
    return float(f1_score(np.asarray(y_true).astype(int), y_pred, zero_division=0))


def brier_score(y_true: np.ndarray, y_score: np.ndarray) -> float:
    return float(brier_score_loss(np.asarray(y_true).astype(int), np.asarray(y_score)))


def ece(y_true: np.ndarray, y_score: np.ndarray, *, n_bins: int = 10, positive_class: int = 1) -> float:
    y = (np.asarray(y_true) == positive_class).astype(int)
    p = np.asarray(y_score, dtype=float)
    if len(p) == 0:
        return float("nan")
    bins = np.linspace(0, 1, n_bins + 1)
    bin_ids = np.clip(np.digitize(p, bins) - 1, 0, n_bins - 1)
    out = 0.0
    n = len(p)
    for b in range(n_bins):
        m = bin_ids == b
        if not m.any():
            continue
        out += (m.sum() / n) * abs(float(p[m].mean()) - float(y[m].mean()))
    return float(out)


def matthews_corrcoef(y_true: np.ndarray, y_score: np.ndarray, *, threshold: float = 0.5) -> float:
    y_pred = (np.asarray(y_score) >= threshold).astype(int)
    return float(_mcc(np.asarray(y_true).astype(int), y_pred))


# -----------------------------------------------------------------------------
# Statistical comparison
# -----------------------------------------------------------------------------
def delong_test(y_true: np.ndarray, score_a: np.ndarray, score_b: np.ndarray) -> dict:
    """Paired AUC test [DeLong et al., 1988]. Returns z-statistic, p-value, ΔAUC.

    Implementation follows Sun & Xu (2014) — V10/V01 estimators with paired
    structure preserved.
    """
    y = np.asarray(y_true, dtype=int)
    sa = np.asarray(score_a, dtype=float)
    sb = np.asarray(score_b, dtype=float)

    pos = y == 1
    neg = ~pos
    n_pos = pos.sum()
    n_neg = neg.sum()
    if n_pos == 0 or n_neg == 0:
        return {"z": float("nan"), "p_value": float("nan"), "delta_auc": float("nan")}

    def _structural_components(s: np.ndarray):
        xp = s[pos]
        xn = s[neg]
        # Element-wise placement of each positive over negatives → V10
        # via row-wise rank-style comparison
        # V10[i] = (1/m) * sum_j [I(xp[i] > xn[j]) + 0.5*I(xp[i] == xn[j])]
        cmp = (xp[:, None] > xn[None, :]).astype(float) + 0.5 * (xp[:, None] == xn[None, :])
        v10 = cmp.mean(axis=1)
        v01 = cmp.mean(axis=0)
        auc = cmp.mean()
        return v10, v01, auc

    v10_a, v01_a, auc_a = _structural_components(sa)
    v10_b, v01_b, auc_b = _structural_components(sb)

    s10 = np.cov(v10_a, v10_b, ddof=1)
    s01 = np.cov(v01_a, v01_b, ddof=1)
    var_delta = (s10[0, 0] + s10[1, 1] - 2 * s10[0, 1]) / n_pos
    var_delta += (s01[0, 0] + s01[1, 1] - 2 * s01[0, 1]) / n_neg
    delta = auc_a - auc_b
    if var_delta <= 0:
        return {"z": float("nan"), "p_value": float("nan"), "delta_auc": float(delta)}
    z = delta / np.sqrt(var_delta)
    # Two-sided p-value via normal approximation
    from scipy.stats import norm
    p = 2 * (1 - norm.cdf(abs(z)))
    return {"z": float(z), "p_value": float(p), "delta_auc": float(delta)}


def paired_bootstrap(
    y_true: np.ndarray,
    score_a: np.ndarray,
    score_b: np.ndarray,
    metric_fn: Callable,
    *,
    n_resamples: int = 10_000,
    random_state: int = 0,
    **metric_kwargs,
) -> dict:
    """Paired bootstrap 95% CI on (metric(score_a) − metric(score_b))."""
    y = np.asarray(y_true)
    sa = np.asarray(score_a)
    sb = np.asarray(score_b)
    rng = np.random.default_rng(random_state)
    diffs = np.empty(n_resamples)
    for i in range(n_resamples):
        idx = rng.integers(0, len(y), len(y))
        ma = metric_fn(y[idx], sa[idx], **metric_kwargs)
        mb = metric_fn(y[idx], sb[idx], **metric_kwargs)
        diffs[i] = ma - mb
    return {
        "delta_mean": float(diffs.mean()),
        "ci95_lo": float(np.quantile(diffs, 0.025)),
        "ci95_hi": float(np.quantile(diffs, 0.975)),
        "p_one_sided": float((diffs <= 0).mean()),
    }
