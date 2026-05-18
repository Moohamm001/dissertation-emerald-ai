"""Linear baselines for the §5.8 benchmark.

Three factories:
  make_lr_l1   — L1-regularised Logistic Regression (sparse, interpretable).
  make_lr_l2   — L2-regularised Logistic Regression (regulatory default).
  make_svm_rbf — RBF kernel SVM with probability output for calibration.

All three accept `class_weight` and `random_state` for consistency with the
imbalance harness (§5.7). Hyperparameters at construction are sensible
defaults; the §5.9 RandomizedSearchCV tunes them per fold.
"""
from __future__ import annotations

from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

from emerald_ai.config import MODEL


def make_lr_l1(
    *,
    C: float = 1.0,
    class_weight: str | None = "balanced",
    random_state: int = MODEL.random_seed,
    **_unused,
) -> LogisticRegression:
    """L1 Logistic Regression. `class_weight='balanced'` is the §5.7 default."""
    return LogisticRegression(
        penalty="l1",
        solver="saga",
        C=C,
        class_weight=class_weight,
        max_iter=3000,
        random_state=random_state,
    )


def make_lr_l2(
    *,
    C: float = 1.0,
    class_weight: str | None = "balanced",
    random_state: int = MODEL.random_seed,
    **_unused,
) -> LogisticRegression:
    """L2 Logistic Regression — the regulatory-default baseline class."""
    return LogisticRegression(
        C=C,
        class_weight=class_weight,
        max_iter=3000,
        random_state=random_state,
    )


def make_svm_rbf(
    *,
    C: float = 1.0,
    gamma: str | float = "scale",
    class_weight: str | None = "balanced",
    random_state: int = MODEL.random_seed,
    **_unused,
) -> SVC:
    """RBF kernel SVM with calibrated probability outputs.

    `probability=True` enables Platt-scaled outputs for §5.10 calibration.
    Slow on >10k rows; the §5.9 harness may down-sample at training time.
    """
    return SVC(
        kernel="rbf",
        C=C,
        gamma=gamma,
        class_weight=class_weight,
        probability=True,
        random_state=random_state,
    )
