"""Tests for emerald_ai.data.leakage_audit.

Locks in the invariants that gate every downstream preprocessing / modelling
step: post-funding outcome columns must never be admitted as features, and
the audit must emit the catalogue + summary artefacts where the rest of the
pipeline expects them.
"""
from __future__ import annotations

import pandas as pd
import pytest
import yaml

from emerald_ai.data.leakage_audit import (
    COLUMN_CLASSIFICATION,
    FeatureCategory,
    PERMITTED_CATEGORIES,
    classify_columns,
    run_leakage_audit,
)
from emerald_ai.data.load import LABEL_COL, default_data_path, load_labelled

REAL_DATA = default_data_path().exists()


# ─── deterministic invariants (always run) ─────────────────────────────────


@pytest.mark.parametrize("col", [
    "Deal Status", "Term Complete Percentage", "Percent Paid",
    "Closed", "Closed TS", "Month Closed", "Original Close Date",
    "Is Offer Accepted", "Is Closed",
])
def test_post_funding_columns_are_forbidden(col: str) -> None:
    cat = COLUMN_CLASSIFICATION.get(col)
    assert cat is not None, f"{col!r} missing from classification"
    assert cat not in PERMITTED_CATEGORIES, (
        f"{col!r} is classified {cat.value} but post-funding columns must never be permitted features."
    )


@pytest.mark.parametrize("col", [
    "Credit Score", "Revenue", "Average Monthly Sales", "Time In Business",
    "Industry", "Borrower State", "Amount Funded", "Amount Sought",
    "APR", "Factor", "Lender", "Current Tier",
])
def test_core_pre_funding_features_are_permitted(col: str) -> None:
    cat = COLUMN_CLASSIFICATION.get(col)
    assert cat is not None, f"{col!r} missing from classification"
    assert cat in PERMITTED_CATEGORIES, (
        f"Core pre-funding feature {col!r} is classified {cat.value} and would be dropped."
    )


def test_no_column_classified_twice() -> None:
    """Sanity: the classification dict cannot have a key appearing under two categories."""
    # dict literal forbids dup keys at parse time, but guard against future edits.
    keys = list(COLUMN_CLASSIFICATION.keys())
    assert len(keys) == len(set(keys))


def test_permitted_categories_are_exactly_the_four_pre_funding_ones() -> None:
    assert PERMITTED_CATEGORIES == {
        FeatureCategory.PRE_FUNDING_APPLICANT,
        FeatureCategory.PRE_FUNDING_LOAN_OFFER,
        FeatureCategory.STRUCTURAL_METADATA,
        FeatureCategory.DEAL_TIMESTAMP,
    }


# ─── integration tests on the real dataset ─────────────────────────────────


@pytest.mark.skipif(not REAL_DATA, reason="Real dataset not present locally")
def test_audit_classifies_every_column() -> None:
    """No column should default to ADMINISTRATIVE silently — every column has an explicit class."""
    df = load_labelled()
    audits = classify_columns(df)
    # All audited names (LABEL_COL is skipped inside classify_columns)
    classified_names = {a.name for a in audits}
    raw_names = set(df.columns) - {LABEL_COL}
    assert classified_names == raw_names

    unclassified = [a for a in audits if a.name not in COLUMN_CLASSIFICATION]
    assert not unclassified, (
        f"{len(unclassified)} columns missing from COLUMN_CLASSIFICATION: "
        f"{[a.name for a in unclassified[:10]]}"
    )


@pytest.mark.skipif(not REAL_DATA, reason="Real dataset not present locally")
def test_audit_emits_artefacts(tmp_path) -> None:
    df = load_labelled()
    result = run_leakage_audit(df, out_dir=tmp_path)
    catalogue = yaml.safe_load((tmp_path / "feature_catalogue.yaml").read_text(encoding="utf-8"))
    assert catalogue["dataset"]["n_rows"] == 14135
    assert catalogue["dataset"]["n_columns"] == 166
    assert result["n_permitted"] + result["n_forbidden"] == 166
    # Class balance recorded
    assert "0" in catalogue["dataset"]["class_balance"]
    assert "1" in catalogue["dataset"]["class_balance"]
