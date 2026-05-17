"""Target-leakage audit (proposal §5.3).

Classifies each feature into pre-funding / loan-offer / structural / timestamp /
post-funding / administrative categories, computes mutual information with Y
restricted to the strictly-pre-funding observability window, and drops any
feature whose informativeness collapses under the temporal filter.
"""
from __future__ import annotations

from enum import Enum


class FeatureCategory(str, Enum):
    """Six-way classification of dataset columns (proposal §5.3)."""

    PRE_FUNDING_APPLICANT = "pre_funding_applicant"
    PRE_FUNDING_LOAN_OFFER = "pre_funding_loan_offer"
    STRUCTURAL_METADATA = "structural_metadata"
    DEAL_TIMESTAMP = "deal_timestamp"
    POST_FUNDING_OUTCOME = "post_funding_outcome"  # NOT permitted as feature
    ADMINISTRATIVE = "administrative"              # NOT permitted as feature


def run_leakage_audit() -> None:
    """Produce the feature catalogue committed to the repo as the leakage-audit artefact."""
    raise NotImplementedError
