"""XGBoost — EMERALD-AI's primary candidate (proposal §5.8).

Thin re-export wrapper around `emerald_ai.models.trees.make_xgboost`. The
monotonic-constraint vocabulary lives here because Credit Score / Revenue /
Time In Business are *named* features in the leakage audit and the
constraints are wired by the §5.9 training harness against actual column
names.

Monotonic-constraint policy (proposal §5.8 + Chen & Guestrin 2016):
    Credit Score        →  +1   (higher score must not decrease creditworthiness)
    Revenue             →  +1   (per the leakage-audit column name)
    Time In Business    →  +1
"""
from __future__ import annotations

from emerald_ai.models.trees import make_xgboost as build_model  # back-compat name


# Policy: feature-name -> {-1, 0, +1} monotonicity for booster constraints.
# The training harness translates this into the index-aligned tuple booster
# APIs expect when those features are present in the post-selection X.
MONOTONIC_CONSTRAINTS: dict[str, int] = {
    "Credit Score": 1,
    "Revenue": 1,
    "Time In Business": 1,
}


def monotonic_vector(feature_names: list[str]) -> list[int]:
    """Build a {−1, 0, +1} vector aligned to ``feature_names`` from the policy.

    Features not named in ``MONOTONIC_CONSTRAINTS`` get 0 (unconstrained).
    """
    return [MONOTONIC_CONSTRAINTS.get(f, 0) for f in feature_names]


__all__ = ["build_model", "MONOTONIC_CONSTRAINTS", "monotonic_vector"]
