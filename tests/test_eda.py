"""Tests for the EDA module (proposal §5.4).

These tests use synthetic frames so they run without the proprietary dataset.
End-to-end smoke against the real dataset is performed manually via
`python -m emerald_ai eda`.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from emerald_ai.data import eda
from emerald_ai.data.load import LABEL_COL


@pytest.fixture
def synthetic_frame() -> pd.DataFrame:
    """A small frame whose columns map to known leakage-audit categories.

    Industry / Borrower State are pre-funding applicant; Credit Score is
    too. Term Complete Percentage is post-funding (forbidden). Y is the
    binary label.
    """
    rng = np.random.default_rng(42)
    n = 500
    df = pd.DataFrame({
        "Credit Score": rng.normal(700, 50, n).round(),
        "Revenue": rng.normal(50000, 15000, n),
        "Industry": rng.choice(["retail", "construction", "manufacturing", "other"], n),
        "Borrower State": rng.choice(["TX", "CA", "NY", "FL"], n),
        # Forbidden — should be excluded by permitted_columns():
        "Term Complete Percentage": rng.uniform(0, 1, n),
        "Deal Status": rng.choice(["paidOff", "current", "default", "behind"], n, p=[0.27, 0.72, 0.009, 0.001]),
        # Label — pandas Int8 extension dtype (numpy has no "Int8")
        LABEL_COL: pd.array(rng.choice([0, 1], n, p=[0.05, 0.95]), dtype="Int8"),
    })
    # Inject a few NaNs into Y to test row filtering
    df.loc[rng.choice(n, 5, replace=False), LABEL_COL] = pd.NA
    return df


def test_permitted_columns_excludes_forbidden(synthetic_frame: pd.DataFrame):
    cols = eda.permitted_columns(synthetic_frame)
    assert "Credit Score" in cols
    assert "Industry" in cols
    assert "Borrower State" in cols
    assert "Term Complete Percentage" not in cols
    assert "Deal Status" not in cols
    assert LABEL_COL not in cols


def test_split_xy_drops_unlabelled(synthetic_frame: pd.DataFrame):
    X, y = eda.split_xy(synthetic_frame)
    assert len(X) == len(y)
    assert y.isna().sum() == 0
    # Five rows had NA labels; they must be dropped
    assert len(X) == len(synthetic_frame) - 5


def test_univariate_summary_distinguishes_numeric_and_categorical(synthetic_frame: pd.DataFrame):
    X, _ = eda.split_xy(synthetic_frame)
    summary = eda.univariate_summary(X)
    num_rows = summary[summary["mean"].notna()]
    cat_rows = summary[summary["mean"].isna()]
    assert "Credit Score" in num_rows["name"].values
    assert "Industry" in cat_rows["name"].values
    # Numeric rows have entropy=None; categorical rows have entropy>0
    assert num_rows["shannon_entropy"].isna().all()
    assert (cat_rows["shannon_entropy"].dropna() > 0).all()


def test_bivariate_returns_all_columns(synthetic_frame: pd.DataFrame):
    X, y = eda.split_xy(synthetic_frame)
    biv = eda.bivariate_against_y(X, y)
    assert set(biv["name"]) == set(X.columns)
    # Numeric features get a Pearson; categoricals do not
    pearson_credit = biv.loc[biv["name"] == "Credit Score", "pearson_vs_y"].iloc[0]
    pearson_industry = biv.loc[biv["name"] == "Industry", "pearson_vs_y"].iloc[0]
    assert not np.isnan(pearson_credit)
    assert np.isnan(pearson_industry)
    # MI is defined for everything
    assert (biv["mi_nats_vs_y"] >= 0).all()


def test_conditional_default_rates_sorts_descending(synthetic_frame: pd.DataFrame):
    X, y = eda.split_xy(synthetic_frame)
    rates = eda.conditional_default_rates(X, y, by="Industry")
    assert list(rates["delinquent_rate"]) == sorted(rates["delinquent_rate"], reverse=True)
    # All segments returned; rates are valid probabilities
    assert (rates["delinquent_rate"] >= 0).all()
    assert (rates["delinquent_rate"] <= 1).all()
    # Wilson CIs contain the point estimate
    assert (rates["ci95_lo"] <= rates["delinquent_rate"]).all()
    assert (rates["ci95_hi"] >= rates["delinquent_rate"]).all()


def test_wilson_ci_handles_zero_successes():
    lo, hi = eda._wilson_ci(0, 100)
    assert lo == 0.0
    assert 0.0 < hi < 0.05  # Wilson upper bound on 0/100 is ~3.7%


def test_wilson_ci_handles_empty_sample():
    lo, hi = eda._wilson_ci(0, 0)
    assert np.isnan(lo) and np.isnan(hi)


def test_psi_identical_distributions_is_zero():
    rng = np.random.default_rng(0)
    s = pd.Series(rng.normal(0, 1, 1000))
    assert eda.psi(s, s) < 1e-6


def test_psi_shifted_distribution_is_positive():
    rng = np.random.default_rng(0)
    ref = pd.Series(rng.normal(0, 1, 1000))
    cur = pd.Series(rng.normal(2, 1, 1000))  # mean-shifted
    assert eda.psi(ref, cur) > 0.25  # conventionally "material shift"


def test_psi_categorical_handles_new_category():
    ref = pd.Series(["A", "B", "A", "B"] * 100)
    cur = pd.Series(["A", "C", "A", "C"] * 100)  # B disappears, C appears
    result = eda.psi(ref, cur)
    assert result > 0
    assert np.isfinite(result)


def test_run_eda_emits_report(tmp_path, synthetic_frame: pd.DataFrame, monkeypatch):
    """End-to-end orchestrator with the load step mocked to the synthetic frame."""
    monkeypatch.setattr(eda, "load_labelled", lambda path=None: synthetic_frame)
    out = tmp_path / "eda_report.md"
    written = eda.run_eda(out_path=out)
    assert written == out
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    # Section headers present
    assert "## 1. Univariate distributions" in content
    assert "## 2. Bivariate association with Y" in content
    assert "## 3. Conditional delinquent rates by segment" in content
    # The two segment axes show up
    assert "By `Industry`" in content
    assert "By `Borrower State`" in content
