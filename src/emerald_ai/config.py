"""Project-wide configuration and path constants.

All filesystem paths used by the pipeline live here so that callers (CLI,
notebooks, API) reference a single source of truth and can be repointed for
testing or alternative deployments via environment variables.
"""
from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, Field

# Repo root resolution — works in editable install + container deployments
REPO_ROOT: Path = Path(os.environ.get("EMERALD_REPO_ROOT", Path(__file__).resolve().parents[2]))


class Paths(BaseModel):
    """Canonical filesystem layout."""

    root: Path = REPO_ROOT
    data_raw: Path = REPO_ROOT / "data" / "raw"
    data_interim: Path = REPO_ROOT / "data" / "interim"
    data_processed: Path = REPO_ROOT / "data" / "processed"
    models: Path = REPO_ROOT / "models"
    mlruns: Path = REPO_ROOT / "mlruns"
    notebooks: Path = REPO_ROOT / "notebooks"
    literature: Path = REPO_ROOT / "literature"
    docs: Path = REPO_ROOT / "docs"


class ModelConfig(BaseModel):
    """Hyperparameter-search budgets and CV protocol (see proposal §5.9)."""

    outer_folds: int = Field(10, description="Outer CV folds for generalisation estimation")
    inner_folds: int = Field(5, description="Inner CV folds for hyperparameter tuning")
    n_trials_per_model: int = Field(100, description="Optuna TPE trials per outer fold per model")
    random_seed: int = Field(42, description="Master seed for reproducibility")
    calibration_split_fraction: float = Field(0.1, description="Held-out fraction for post-hoc calibration")


class FairnessConfig(BaseModel):
    """Fairness audit configuration (see proposal §5.12)."""

    proxy_axes: list[str] = Field(default_factory=lambda: ["Industry", "Borrower State", "Business Size"])
    disparate_impact_threshold: float = 0.8
    equalised_odds_gap_threshold: float = 0.1


PATHS = Paths()
MODEL = ModelConfig()
FAIRNESS = FairnessConfig()
