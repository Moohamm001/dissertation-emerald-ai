"""Tests for emerald_ai.data.load.

Verifies dataset shape, label-construction invariants, and the small but
important deterministic mapping in label_creditworthiness.
"""
from __future__ import annotations

import pandas as pd
import pytest

from emerald_ai.data.load import (
    CREDITWORTHY_STATUSES,
    DELINQUENT_STATUSES,
    LABEL_COL,
    STATUS_COL,
    default_data_path,
    label_creditworthiness,
    load_labelled,
    load_raw,
)

REAL_DATA = default_data_path().exists()


@pytest.fixture
def synthetic_frame() -> pd.DataFrame:
    return pd.DataFrame({
        STATUS_COL: ["paidOff", "current", "default", "behind", "weird", None, "  current "],
        "Credit Score": [700, 650, 580, 590, 720, 700, 660],
    })


# ─── unit tests on synthetic data (always run) ─────────────────────────────


def test_label_maps_paidoff_and_current_to_one(synthetic_frame: pd.DataFrame) -> None:
    out = label_creditworthiness(synthetic_frame)
    assert out.loc[0, LABEL_COL] == 1   # paidOff
    assert out.loc[1, LABEL_COL] == 1   # current


def test_label_maps_default_and_behind_to_zero(synthetic_frame: pd.DataFrame) -> None:
    out = label_creditworthiness(synthetic_frame)
    assert out.loc[2, LABEL_COL] == 0   # default
    assert out.loc[3, LABEL_COL] == 0   # behind


def test_label_leaves_unmappable_statuses_as_na(synthetic_frame: pd.DataFrame) -> None:
    out = label_creditworthiness(synthetic_frame)
    assert pd.isna(out.loc[4, LABEL_COL])   # "weird"
    assert pd.isna(out.loc[5, LABEL_COL])   # None


def test_label_strips_whitespace_before_mapping(synthetic_frame: pd.DataFrame) -> None:
    out = label_creditworthiness(synthetic_frame)
    assert out.loc[6, LABEL_COL] == 1   # "  current "


def test_label_does_not_mutate_input(synthetic_frame: pd.DataFrame) -> None:
    before = synthetic_frame.copy()
    label_creditworthiness(synthetic_frame)
    pd.testing.assert_frame_equal(before, synthetic_frame)


def test_status_sets_are_disjoint() -> None:
    """Sanity: a status cannot be both creditworthy and delinquent."""
    assert CREDITWORTHY_STATUSES.isdisjoint(DELINQUENT_STATUSES)


def test_missing_status_column_raises() -> None:
    df = pd.DataFrame({"X": [1, 2, 3]})
    with pytest.raises(KeyError):
        label_creditworthiness(df)


# ─── integration tests on the real dataset (only when present) ─────────────


@pytest.mark.skipif(not REAL_DATA, reason="Real dataset not present locally")
def test_real_dataset_shape() -> None:
    """Proposal §5.3 invariant: 14,135 rows × 166 columns."""
    df = load_raw()
    assert df.shape == (14135, 166), df.shape


@pytest.mark.skipif(not REAL_DATA, reason="Real dataset not present locally")
def test_real_dataset_labelled_coverage() -> None:
    """Proposal §5.2: ≥99% of rows must label cleanly into Y ∈ {0, 1}."""
    df = load_labelled()
    coverage = df[LABEL_COL].notna().mean()
    assert coverage >= 0.99, f"Labelled coverage dropped to {coverage:.3%}"
