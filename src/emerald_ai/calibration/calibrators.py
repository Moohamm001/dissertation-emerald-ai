"""Post-hoc calibrators (proposal §5.10).

Three families compared on a held-out calibration fold:
    Platt scaling          — logistic regression on score logits.
    Isotonic regression    — non-parametric monotonic mapping.
    Temperature scaling    — single-parameter for neural learners (here a
                             gradient-free 1-D search since we are operating
                             on already-fit sklearn-style outputs).

`calibrate(method, ...)` returns a `CalibrationResult` with the fitted
calibrator plus pre/post ECE so the dissertation can directly cite both.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression


@dataclass
class CalibrationResult:
    method: str
    fitted: Callable[[np.ndarray], np.ndarray]
    ece_pre: float
    ece_post: float
    within_minority_ece_pre: float
    within_minority_ece_post: float


def expected_calibration_error(
    y_true: np.ndarray,
    y_score: np.ndarray,
    *,
    n_bins: int = 10,
    positive_class: int = 1,
) -> float:
    """Standard equal-width ECE on a binary classification probability."""
    y = (np.asarray(y_true) == positive_class).astype(int)
    p = np.asarray(y_score, dtype=float)
    if len(p) == 0:
        return float("nan")
    bins = np.linspace(0, 1, n_bins + 1)
    bin_ids = np.clip(np.digitize(p, bins) - 1, 0, n_bins - 1)
    ece = 0.0
    n = len(p)
    for b in range(n_bins):
        mask = bin_ids == b
        if not mask.any():
            continue
        w = mask.sum() / n
        avg_p = float(p[mask].mean())
        avg_y = float(y[mask].mean())
        ece += w * abs(avg_p - avg_y)
    return float(ece)


def _within_minority_ece(y_true, y_score, minority_label=0, n_bins=10) -> float:
    """Mirror of training.imbalance.within_minority_ece — kept private here to
    avoid importing from a sibling that already imports calibration in tests."""
    y_arr = np.asarray(y_true)
    mask = y_arr == minority_label
    if not mask.any():
        return float("nan")
    p = np.asarray(y_score)[mask]
    bins = np.linspace(0, 1, n_bins + 1)
    bin_ids = np.clip(np.digitize(p, bins) - 1, 0, n_bins - 1)
    ece = 0.0
    for b in range(n_bins):
        in_bin = bin_ids == b
        if not in_bin.any():
            continue
        ece += (in_bin.sum() / len(p)) * abs(float(p[in_bin].mean()) - 0.0)
    return float(ece)


# -----------------------------------------------------------------------------
# Method implementations
# -----------------------------------------------------------------------------
def _platt(scores: np.ndarray, y: np.ndarray) -> Callable[[np.ndarray], np.ndarray]:
    """Platt scaling: fit a logistic on the score → label mapping."""
    s = scores.reshape(-1, 1)
    lr = LogisticRegression(max_iter=2000)
    lr.fit(s, y)
    return lambda x: lr.predict_proba(np.asarray(x).reshape(-1, 1))[:, 1]


def _isotonic(scores: np.ndarray, y: np.ndarray) -> Callable[[np.ndarray], np.ndarray]:
    """Isotonic regression — non-parametric, monotonic, robust."""
    iso = IsotonicRegression(out_of_bounds="clip")
    iso.fit(scores, y)
    return lambda x: iso.predict(np.asarray(x))


def _temperature(scores: np.ndarray, y: np.ndarray) -> Callable[[np.ndarray], np.ndarray]:
    """Single-parameter temperature search on (clipped) logits.

    Minimises NLL over T ∈ (0.1, 10) via golden-section search. Vectorised,
    no autograd required.
    """
    eps = 1e-7
    p_clipped = np.clip(scores, eps, 1 - eps)
    logits = np.log(p_clipped / (1 - p_clipped))

    def nll(T: float) -> float:
        scaled = logits / T
        p = 1.0 / (1.0 + np.exp(-scaled))
        return float(-(y * np.log(p + eps) + (1 - y) * np.log(1 - p + eps)).mean())

    # Golden-section search
    lo, hi = 0.1, 10.0
    phi = (np.sqrt(5) - 1) / 2
    for _ in range(60):
        d = hi - lo
        x1 = hi - phi * d
        x2 = lo + phi * d
        if nll(x1) < nll(x2):
            hi = x2
        else:
            lo = x1
    T_star = (lo + hi) / 2

    def calibrate_fn(x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=float)
        x_clipped = np.clip(x, eps, 1 - eps)
        logits_new = np.log(x_clipped / (1 - x_clipped))
        return 1.0 / (1.0 + np.exp(-logits_new / T_star))

    return calibrate_fn


METHODS: dict[str, Callable] = {
    "platt": _platt,
    "isotonic": _isotonic,
    "temperature": _temperature,
}


def calibrate(
    method: str,
    scores_cal: np.ndarray,
    y_cal: np.ndarray,
    *,
    scores_test: np.ndarray | None = None,
    y_test: np.ndarray | None = None,
    minority_label: int = 0,
) -> CalibrationResult:
    """Fit ``method`` on calibration scores+labels; report pre/post ECE on test
    (if supplied; otherwise on the calibration fold itself for sanity)."""
    if method not in METHODS:
        raise KeyError(f"Unknown method {method!r}. Available: {list(METHODS)}")
    y_cal = np.asarray(y_cal, dtype=int)
    fitted = METHODS[method](np.asarray(scores_cal, dtype=float), y_cal)

    eval_scores = scores_test if scores_test is not None else scores_cal
    eval_y = y_test if y_test is not None else y_cal
    eval_y = np.asarray(eval_y, dtype=int)
    eval_scores = np.asarray(eval_scores, dtype=float)

    ece_pre = expected_calibration_error(eval_y, eval_scores)
    ece_post = expected_calibration_error(eval_y, fitted(eval_scores))
    min_ece_pre = _within_minority_ece(eval_y, eval_scores, minority_label=minority_label)
    min_ece_post = _within_minority_ece(eval_y, fitted(eval_scores), minority_label=minority_label)

    return CalibrationResult(
        method=method,
        fitted=fitted,
        ece_pre=ece_pre,
        ece_post=ece_post,
        within_minority_ece_pre=min_ece_pre,
        within_minority_ece_post=min_ece_post,
    )
