"""Load and label the 2019 All Funded Green Loan dataset.

Implements the binary target construction defined in proposal §5.2:
    Y = 1 if Deal Status ∈ {paidOff, current}
    Y = 0 if Deal Status ∈ {default, behind}
    NaN  otherwise (excluded from labelled set)
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from emerald_ai.config import PATHS

CREDITWORTHY_STATUSES = frozenset({"paidOff", "current"})
DELINQUENT_STATUSES = frozenset({"default", "behind"})


def load_raw(path: Path | None = None) -> pd.DataFrame:
    """Load the raw .xlsx dataset.

    Args:
        path: Optional override. Defaults to ``data/raw/All_Funded_2019_Green Loan.xlsx``.

    Returns:
        The unmodified raw frame, 14,135 rows × 166 columns.
    """
    raise NotImplementedError("Implement when dataset is wired in (proposal §5.3).")


def label_creditworthiness(df: pd.DataFrame, status_col: str = "Deal Status") -> pd.DataFrame:
    """Append the binary creditworthiness target Y.

    Args:
        df: Raw frame with a Deal Status column.
        status_col: Name of the deal-status column.

    Returns:
        Frame with an additional ``Y`` column; rows with unmappable status remain NaN.
    """
    raise NotImplementedError
