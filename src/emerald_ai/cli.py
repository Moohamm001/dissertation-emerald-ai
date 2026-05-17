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


# ─────────────────────────────────────────────────────────────
# Research-automation subcommands (see research_automation.txt
# and src/emerald_ai/research/)
# ─────────────────────────────────────────────────────────────
research_app = typer.Typer(
    name="research",
    help="Autonomous literature-brain automation (implements research_automation.txt).",
    no_args_is_help=True,
)
app.add_typer(research_app, name="research")


@research_app.command("run")
def research_run(
    force: bool = typer.Option(False, "--force", "-f", help="Re-process even already-analysed papers"),
) -> None:
    """Run a full sweep: ingest → graph → roll-up → questions → save."""
    from emerald_ai.research import ResearchEngine

    result = ResearchEngine().run(force=force)
    console.print("[bold green]Research sweep complete[/bold green]")
    for k, v in result.items():
        console.print(f"  [cyan]{k:>12}[/cyan] = {v}")


@research_app.command("status")
def research_status() -> None:
    """Print the current state of the brain (manifest + counts)."""
    import json

    from emerald_ai.config import PATHS

    state_dir = PATHS.literature / "state"
    if not (state_dir / "manifest.json").exists():
        console.print("[yellow]Brain state not yet built — run [bold]emerald research run[/bold] first.[/yellow]")
        return
    manifest = json.loads((state_dir / "manifest.json").read_text(encoding="utf-8"))
    console.print(f"[bold]Brain state — last run {manifest['last_run']}[/bold]")
    console.print(f"  papers     : {manifest['papers_count']}")
    for fname in ("citations", "questions", "authors", "methods", "datasets", "keywords"):
        path = state_dir / f"{fname}.json"
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            n = len(data) if isinstance(data, (list, dict)) else 0
            console.print(f"  {fname:<10} : {n}")


@research_app.command("graph")
def research_graph(
    out: str = typer.Option("literature/state/citations.dot", "--out", "-o"),
) -> None:
    """Emit the citation graph as a Graphviz DOT file."""
    import json
    from pathlib import Path

    from emerald_ai.config import PATHS

    edges = json.loads((PATHS.literature / "state" / "citations.json").read_text(encoding="utf-8"))
    lines = ["digraph citations {", '  rankdir=LR;', '  node [shape=box, fontsize=10];']
    for e in edges:
        lines.append(f'  "{e["source"]}" -> "{e["target"]}";')
    lines.append("}")
    Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    console.print(f"[green]Wrote[/green] {out}  ({len(edges)} edges)")
    console.print(f"  Render with: [cyan]dot -Tsvg {out} -o {out.replace('.dot', '.svg')}[/cyan]")


@research_app.command("show")
def research_show(key: str = typer.Argument(..., help="Paper key (filename slug)")) -> None:
    """Pretty-print a paper's structured record."""
    import json

    from emerald_ai.research.state import State

    record = State.load_paper(key)
    if record is None:
        console.print(f"[red]No record for key [bold]{key}[/bold].[/red]  Have you run [cyan]emerald research run[/cyan]?")
        raise typer.Exit(code=1)
    console.print_json(json.dumps(record.model_dump(mode="json"), indent=2))


if __name__ == "__main__":
    app()
