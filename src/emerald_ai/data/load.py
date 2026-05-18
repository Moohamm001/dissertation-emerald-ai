"""Load and label the 2019 All Funded Green Loan dataset.

Implements the binary target construction defined in proposal §5.2:
    Y = 1 if Deal Status in {paidOff, current}    (creditworthy)
    Y = 0 if Deal Status in {default, behind}     (delinquent)
    NaN otherwise                                  (excluded from labelled set)
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from emerald_ai.config import PATHS

DEFAULT_FILENAME = "All_Funded_2019_Green Loan.xlsx"

CREDITWORTHY_STATUSES = frozenset({"paidOff", "current"})
DELINQUENT_STATUSES = frozenset({"default", "behind"})

LABEL_COL = "Y"
STATUS_COL = "Deal Status"


def default_data_path() -> Path:
    return PATHS.data_raw / DEFAULT_FILENAME


def load_raw(path: Path | None = None) -> pd.DataFrame:
    """Load the raw .xlsx dataset.

    Returns the unmodified frame: 14,135 rows × 166 columns.
    """
    path = Path(path) if path is not None else default_data_path()
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {path}. See data/README.md for acquisition instructions."
        )
    return pd.read_excel(path)


def label_creditworthiness(df: pd.DataFrame, status_col: str = STATUS_COL) -> pd.DataFrame:
    """Append the binary creditworthiness target Y.

    Rows with status outside the two allowed sets receive NaN and should be
    dropped from the supervised-learning pool. See proposal §5.2 for the
    censoring-bias sensitivity protocol that conditions on this label.
    """
    if status_col not in df.columns:
        raise KeyError(f"Status column {status_col!r} not in dataset")

    out = df.copy()
    status = out[status_col].astype("string").str.strip()
    out[LABEL_COL] = (
        status.where(status.isin(CREDITWORTHY_STATUSES | DELINQUENT_STATUSES))
        .map(lambda s: 1 if s in CREDITWORTHY_STATUSES else (0 if s in DELINQUENT_STATUSES else None))
        .astype("Int8")
    )
    return out


def load_labelled(path: Path | None = None) -> pd.DataFrame:
    """Load + label in one step; convenience for callers that want supervised data."""
    return label_creditworthiness(load_raw(path))
