"""scikit-learn ColumnTransformer pipeline (proposal §5.5).

Stages:
    1. Missing-data treatment   (median impute + missingness indicators)
    2. Outlier handling         (1st/99th percentile winsorisation)
    3. Encoding                 (one-hot for low-card; leave-one-out target for high-card)
    4. Scaling                  (StandardScaler for distance-based learners; identity for trees)
    5. Feature interactions     (loan-to-revenue, payback-to-monthly-sales, factor-rate-adj APR)

The pipeline is built once and reused identically at train and inference time
to prevent train/test leakage and to keep behaviour comparable across model
families.
"""
from __future__ import annotations


def build_preprocessor() -> object:
    """Return the fitted-once ColumnTransformer used across all model families."""
    raise NotImplementedError
