"""EMERALD-AI command-line interface.

Each subcommand wraps one stage of the pipeline described in the proposal,
making the same operations available from the terminal, the Makefile, and CI.

Usage:
    emerald --help
    emerald eda
    emerald preprocess
    emerald train --model xgboost
    emerald evaluate
    emerald explain --applicant-id 42
    emerald audit --axis industry
"""
from __future__ import annotations

import typer
from rich.console import Console

from emerald_ai import __version__

console = Console()
app = typer.Typer(
    name="emerald",
    help="EMERALD-AI: explainable green-loan credit scoring.",
    add_completion=False,
    no_args_is_help=True,
)


@app.command()
def version() -> None:
    """Print the installed EMERALD-AI version."""
    console.print(f"EMERALD-AI v{__version__}")


@app.command()
def eda() -> None:
    """Run exploratory data analysis (proposal §5.4)."""
    raise NotImplementedError("EDA pipeline not yet implemented — see proposal §5.4.")


@app.command()
def preprocess() -> None:
    """Run leakage audit, encoding, scaling, imbalance treatment (proposal §5.3, §5.5, §5.7)."""
    raise NotImplementedError("Preprocessing pipeline not yet implemented.")


@app.command()
def train(
    model: str = typer.Option("all", "--model", "-m", help="Model family: lr | svm | rf | xgboost | lightgbm | catboost | mlp | ft_transformer | all"),
) -> None:
    """Train one or all model families under nested CV + Bayesian HPO (proposal §5.8, §5.9)."""
    raise NotImplementedError(f"Training for {model!r} not yet implemented.")


@app.command()
def evaluate() -> None:
    """Compute metrics, calibration, conformal intervals (proposal §5.10, §5.13)."""
    raise NotImplementedError("Evaluation not yet implemented.")


@app.command()
def explain(
    applicant_id: int | None = typer.Option(None, "--applicant-id", "-a"),
) -> None:
    """Generate global + local SHAP + counterfactual + fidelity reports (proposal §5.11)."""
    raise NotImplementedError("Explainability pipeline not yet implemented.")


@app.command()
def audit(
    axis: str = typer.Option("all", "--axis", help="Proxy axis: industry | state | business_size | all"),
) -> None:
    """Run fairness + robustness + drift audit (proposal §5.12)."""
    raise NotImplementedError("Audit pipeline not yet implemented.")


if __name__ == "__main__":
    app()
