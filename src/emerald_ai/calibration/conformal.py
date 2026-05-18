"""Split-conformal prediction (proposal §5.10).

Per v0.4.1's small-N-minority reframe:

  • SplitConformal (marginal) — HEADLINE. Finite-sample exact coverage for any
    exchangeable distribution. With ~2,800 rows in the calibration split the
    guarantee P(Y ∈ C(X)) = ⌈(N_cal+1)(1-α)⌉ / (N_cal+1) ≈ 1-α.

  • MondrianConformal (class-conditional) — DIAGNOSTIC. The same conformal
    guarantee but per-class. At 50 minority observations split across cal/test,
    the empirical coverage estimate carries a wide CI; ``bootstrap_class_
    conditional_coverage()`` quantifies that uncertainty so reviewers can see
    the precision of the diagnostic itself.

Interval *width* is intentionally not exposed as a primary metric — at
~10 minority observations in the calibration set the width is a
measurement-precision artefact rather than a model-quality signal.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class ConformalSet:
    """Per-row prediction set."""

    include_0: np.ndarray  # bool[n]: 0 in C(x)?
    include_1: np.ndarray  # bool[n]: 1 in C(x)?

    @property
    def coverage_components(self) -> dict[str, np.ndarray]:
        return {
            "include_0": self.include_0,
            "include_1": self.include_1,
            "set_size": self.include_0.astype(int) + self.include_1.astype(int),
        }


def _nonconformity(scores: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """Standard binary nonconformity: 1 - P(true class)."""
    s = np.asarray(scores, dtype=float)
    y = np.asarray(labels, dtype=int)
    # P(true class) = s if y=1 else 1-s
    p_true = np.where(y == 1, s, 1 - s)
    return 1.0 - p_true


class SplitConformal:
    """Marginal-coverage split-conformal prediction at a target ``alpha``."""

    def __init__(self, *, alpha: float = 0.10):
        if not 0.0 < alpha < 1.0:
            raise ValueError("alpha must be in (0, 1)")
        self.alpha = alpha
        self.q_hat_: float | None = None

    def fit(self, scores_cal: np.ndarray, y_cal: np.ndarray) -> "SplitConformal":
        nc = _nonconformity(scores_cal, y_cal)
        n = len(nc)
        if n == 0:
            raise ValueError("Calibration set is empty")
        # Finite-sample exact quantile
        level = np.clip(np.ceil((n + 1) * (1 - self.alpha)) / n, 0.0, 1.0)
        self.q_hat_ = float(np.quantile(nc, level, method="higher"))
        return self

    def predict(self, scores: np.ndarray) -> ConformalSet:
        if self.q_hat_ is None:
            raise RuntimeError("Call fit() before predict()")
        s = np.asarray(scores, dtype=float)
        # 0 ∈ C(x) iff nonconformity(score, 0) ≤ q_hat
        # = (1 - (1-s)) = s ≤ q_hat
        include_0 = s <= self.q_hat_
        include_1 = (1 - s) <= self.q_hat_
        return ConformalSet(include_0=include_0, include_1=include_1)

    def marginal_coverage(self, scores: np.ndarray, y: np.ndarray) -> float:
        sets = self.predict(scores)
        y_arr = np.asarray(y, dtype=int)
        hit = np.where(y_arr == 1, sets.include_1, sets.include_0)
        return float(hit.mean())


class MondrianConformal:
    """Class-conditional split-conformal — separate threshold per class."""

    def __init__(self, *, alpha: float = 0.10):
        if not 0.0 < alpha < 1.0:
            raise ValueError("alpha must be in (0, 1)")
        self.alpha = alpha
        self.q_hat_per_class_: dict[int, float] = {}

    def fit(self, scores_cal: np.ndarray, y_cal: np.ndarray) -> "MondrianConformal":
        y = np.asarray(y_cal, dtype=int)
        nc = _nonconformity(scores_cal, y_cal)
        self.q_hat_per_class_ = {}
        for c in (0, 1):
            mask = y == c
            n = int(mask.sum())
            if n == 0:
                self.q_hat_per_class_[c] = float("nan")
                continue
            level = np.clip(np.ceil((n + 1) * (1 - self.alpha)) / n, 0.0, 1.0)
            self.q_hat_per_class_[c] = float(np.quantile(nc[mask], level, method="higher"))
        return self

    def predict(self, scores: np.ndarray) -> ConformalSet:
        if not self.q_hat_per_class_:
            raise RuntimeError("Call fit() before predict()")
        s = np.asarray(scores, dtype=float)
        q0 = self.q_hat_per_class_.get(0, float("nan"))
        q1 = self.q_hat_per_class_.get(1, float("nan"))
        # Tolerate NaN thresholds (degenerate when a class is missing from cal)
        include_0 = s <= q0 if np.isfinite(q0) else np.zeros_like(s, dtype=bool)
        include_1 = (1 - s) <= q1 if np.isfinite(q1) else np.zeros_like(s, dtype=bool)
        return ConformalSet(include_0=include_0, include_1=include_1)

    def class_conditional_coverage(
        self, scores: np.ndarray, y: np.ndarray
    ) -> dict[int, float]:
        sets = self.predict(scores)
        y_arr = np.asarray(y, dtype=int)
        out: dict[int, float] = {}
        for c in (0, 1):
            mask = y_arr == c
            if not mask.any():
                out[c] = float("nan")
                continue
            hit = sets.include_1[mask] if c == 1 else sets.include_0[mask]
            out[c] = float(hit.mean())
        return out


def bootstrap_class_conditional_coverage(
    scores: np.ndarray,
    y: np.ndarray,
    *,
    alpha: float = 0.10,
    n_bootstraps: int = 500,
    random_state: int = 0,
) -> dict[int, tuple[float, float, float]]:
    """Per-class Mondrian coverage with 95% bootstrap CIs.

    Resamples both calibration and evaluation indices to capture the joint
    uncertainty in (q_hat, empirical coverage). The 50/50 split inside each
    resample mimics the dissertation's calibration/test partition.
    """
    rng = np.random.default_rng(random_state)
    y = np.asarray(y, dtype=int)
    scores = np.asarray(scores, dtype=float)
    results: dict[int, list[float]] = {0: [], 1: []}

    for _ in range(n_bootstraps):
        idx = rng.choice(len(y), size=len(y), replace=True)
        s_b, y_b = scores[idx], y[idx]
        half = len(y_b) // 2
        cal_s, cal_y = s_b[:half], y_b[:half]
        test_s, test_y = s_b[half:], y_b[half:]
        try:
            mc = MondrianConformal(alpha=alpha).fit(cal_s, cal_y)
            cov = mc.class_conditional_coverage(test_s, test_y)
        except (ValueError, RuntimeError):
            continue
        for c in (0, 1):
            if np.isfinite(cov.get(c, float("nan"))):
                results[c].append(cov[c])

    out: dict[int, tuple[float, float, float]] = {}
    for c in (0, 1):
        vals = np.asarray(results[c])
        if vals.size == 0:
            out[c] = (float("nan"), float("nan"), float("nan"))
            continue
        out[c] = (
            float(vals.mean()),
            float(np.quantile(vals, 0.025)),
            float(np.quantile(vals, 0.975)),
        )
    return out
