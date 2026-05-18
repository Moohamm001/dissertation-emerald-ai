"""EMERALD-AI command-line interface - the single entrypoint for every project task.

Three equivalent ways to invoke:

    python emerald.py <command>       # zero-install launcher (project root)
    python -m emerald_ai <command>    # after `pip install -e .`
    emerald <command>                 # after install, if Scripts dir is on PATH

Examples:
    python -m emerald_ai --help
    python -m emerald_ai version
    python -m emerald_ai research status
    python -m emerald_ai proposal
    python -m emerald_ai test
    python -m emerald_ai check        # lint + typecheck + test
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import typer
from rich.console import Console

from emerald_ai import __version__
from emerald_ai.config import PATHS

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
def eda(
    data_path: Path | None = typer.Option(None, help="Override raw .xlsx path (default: data/raw/All_Funded_2019_Green Loan.xlsx)"),
    out: Path | None = typer.Option(None, help="Override output report path (default: data/governance/eda_report.md)"),
) -> None:
    """Run exploratory data analysis on the 90 permitted features (proposal §5.4).

    Emits ``data/governance/eda_report.md`` with univariate distributions,
    bivariate association against Y, segment-level conditional default rates,
    and quarterly PSI drift diagnostics.
    """
    from emerald_ai.data.eda import EDA_REPORT_PATH, run_eda
    target = out if out is not None else EDA_REPORT_PATH
    written = run_eda(path=data_path, out_path=target)
    console.print(f"[green]OK[/green]: {written}")


@app.command()
def preprocess() -> None:
    """Run leakage audit, encoding, scaling, imbalance treatment (proposal sec.5.3, sec.5.5, sec.5.7)."""
    raise NotImplementedError("Preprocessing pipeline not yet implemented.")


@app.command()
def train(
    model: str = typer.Option("all", "--model", "-m", help="Model family: lr | svm | rf | xgboost | lightgbm | catboost | mlp | ft_transformer | all"),
) -> None:
    """Train one or all model families under nested CV + Bayesian HPO (proposal sec.5.8, sec.5.9)."""
    raise NotImplementedError(f"Training for {model!r} not yet implemented.")


@app.command()
def evaluate() -> None:
    """Compute metrics, calibration, conformal intervals (proposal sec.5.10, sec.5.13)."""
    raise NotImplementedError("Evaluation not yet implemented.")


@app.command()
def explain(
    applicant_id: int | None = typer.Option(None, "--applicant-id", "-a"),
) -> None:
    """Generate global + local SHAP + counterfactual + fidelity reports (proposal sec.5.11)."""
    raise NotImplementedError("Explainability pipeline not yet implemented.")


@app.command()
def audit(
    axis: str = typer.Option("all", "--axis", help="Proxy axis: industry | state | business_size | all"),
) -> None:
    """Run fairness + robustness + drift audit (proposal sec.5.12)."""
    raise NotImplementedError("Audit pipeline not yet implemented.")


# -------------------------------------------------------------
# Research-automation subcommands (see research_automation.txt
# and src/emerald_ai/research/)
# -------------------------------------------------------------
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
    """Run a full sweep: ingest -> graph -> roll-up -> questions -> save."""
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
        console.print("[yellow]Brain state not yet built - run [bold]emerald research run[/bold] first.[/yellow]")
        return
    manifest = json.loads((state_dir / "manifest.json").read_text(encoding="utf-8"))
    console.print(f"[bold]Brain state - last run {manifest['last_run']}[/bold]")
    console.print(f"  papers     : {manifest['papers_count']}")
    for fname in ("citations", "questions", "authors", "methods", "datasets", "keywords"):
        path = state_dir / f"{fname}.json"
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            n = len(data) if isinstance(data, (list, dict)) else 0
            console.print(f"  {fname:<10} : {n}")


@research_app.command("graph")
def research_graph(
    out: str = typer.Option("research/literature/state/citations.dot", "--out", "-o"),
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


# -------------------------------------------------------------
# Autonomous-discovery subcommands - the "bot" that grows the brain
# -------------------------------------------------------------


@research_app.command("discover")
def research_discover(
    seed: list[str] | None = typer.Option(
        None,
        "--seed",
        "-s",
        help="OpenAlex Work ID to seed from. Repeatable. If omitted, uses seeds-from-index.",
    ),
    query: list[str] | None = typer.Option(
        None,
        "--query",
        "-q",
        help="Free-text search query to derive seeds from. Repeatable.",
    ),
    depth: int = typer.Option(2, "--depth", "-d", min=0, max=5, help="Max BFS depth"),
    max_papers: int = typer.Option(10, "--max", "-m", min=1, max=200, help="Cap accepted papers"),
    threshold: float = typer.Option(0.45, "--threshold", "-t", min=0.0, max=1.0),
    mailto: str | None = typer.Option(None, "--mailto", help="Polite-pool contact email"),
) -> None:
    """Grow the brain by traversing the citation graph from seeds.

    No API key required - uses OpenAlex's polite pool. Politeness defaults:
    1 req/s, on-disk cache, exponential backoff on 429. See discovery.py docstring.

    Examples:
        python -m emerald_ai research discover --query "green credit scoring explainable"
        python -m emerald_ai research discover --seed W2964121823 --depth 3 --max 30
        python -m emerald_ai research discover  # seeds = papers already in brain (depth 1)
    """
    from emerald_ai.research import (
        DiscoveryConfig,
        OpenAlexSource,
        discover,
        seeds_from_index,
        seeds_from_search,
    )

    source = OpenAlexSource(mailto=mailto)

    if seed:
        seeds = list(seed)
    elif query:
        console.print(f"[dim]Resolving {len(query)} search queries -> seed IDs...[/dim]")
        seeds = seeds_from_search(source, list(query), per_query=5)
    else:
        seeds = seeds_from_index(only_with_openalex_id=True)
        if not seeds:
            console.print(
                "[yellow]No openalex_id in current brain. Pass --seed <W...> or --query <text>.[/yellow]"
            )
            raise typer.Exit(code=1)

    console.print(f"[bold]Discovering[/bold] from {len(seeds)} seed(s), depth<={depth}, max={max_papers}")
    cfg = DiscoveryConfig(max_depth=depth, max_papers=max_papers, threshold=threshold)
    report = discover(source, seeds, config=cfg)

    console.print("\n[bold green]Discovery complete[/bold green]")
    console.print(f"  candidates examined : {report.candidates_seen}")
    console.print(f"  accepted            : {len(report.accepted)}")
    console.print(f"  rejected            : {len(report.rejected)}")
    console.print(f"  errors              : {len(report.errors)}")
    console.print(f"  depth reached       : {report.depth_reached}")
    console.print(f"  saturated           : {report.saturated}")
    if report.accepted:
        console.print("\n[bold]New papers:[/bold]")
        for key, s in report.accepted:
            console.print(f"  [green]+[/green] {s:.2f}  [cyan]{key}[/cyan]")
    console.print(
        "\nNext: [cyan]python -m emerald_ai research run[/cyan] to ingest the new sidecars into state."
    )


@research_app.command("bot")
def research_bot(
    rounds: int = typer.Option(3, "--rounds", "-r", min=1, max=20),
    depth: int = typer.Option(2, "--depth", "-d", min=0, max=5),
    max_per_round: int = typer.Option(10, "--max", "-m", min=1, max=200),
    threshold: float = typer.Option(0.45, "--threshold", "-t", min=0.0, max=1.0),
    mailto: str | None = typer.Option(None, "--mailto"),
) -> None:
    """Run multiple discovery rounds; the brain seeds each next round.

    Stops early when a round adds nothing (global saturation).
    """
    from emerald_ai.research import (
        DiscoveryConfig,
        OpenAlexSource,
        ResearchEngine,
        discover,
        seeds_from_index,
    )

    source = OpenAlexSource(mailto=mailto)
    cfg = DiscoveryConfig(max_depth=depth, max_papers=max_per_round, threshold=threshold)

    for round_no in range(1, rounds + 1):
        console.print(f"\n[bold cyan]-- Round {round_no}/{rounds} --[/bold cyan]")
        seeds = seeds_from_index(only_with_openalex_id=True)
        if not seeds:
            console.print(
                "[yellow]No seeds with openalex_id available. Run --query once to bootstrap.[/yellow]"
            )
            raise typer.Exit(code=1)
        report = discover(source, seeds, config=cfg)
        console.print(
            f"  accepted={len(report.accepted)}  rejected={len(report.rejected)}  errors={len(report.errors)}"
        )
        if not report.accepted:
            console.print("[yellow]Global saturation - no new papers this round, stopping.[/yellow]")
            break
        # ingest newly accepted papers into the engine's state
        ResearchEngine().run()

    console.print("\n[bold green]Bot finished[/bold green]")


# -------------------------------------------------------------
# Authoring & build commands (previously make targets)
# -------------------------------------------------------------


def _run(cmd: list[str], *, cwd: Path | None = None, check: bool = True) -> int:
    """Run a subprocess, streaming output, returning its exit code."""
    console.print(f"[dim]$ {' '.join(cmd)}[/dim]" + (f"   [dim](in {cwd})[/dim]" if cwd else ""))
    completed = subprocess.run(cmd, cwd=cwd, check=False)
    if check and completed.returncode != 0:
        raise typer.Exit(code=completed.returncode)
    return completed.returncode


@app.command()
def proposal() -> None:
    """Rebuild the dissertation proposal docx (docs/proposal/proposal_second_draft.docx).

    Close the .docx in Word/LibreOffice first or you'll hit a PermissionError.
    """
    script = PATHS.docs / "proposal" / "build_proposal.py"
    if not script.exists():
        console.print(f"[red]Script not found:[/red] {script}")
        raise typer.Exit(code=1)
    _run([sys.executable, str(script.name)], cwd=script.parent)


@app.command()
def literature() -> None:
    """Regenerate literature/papers/*.md from build_papers.py."""
    script = PATHS.literature / "build_papers.py"
    if not script.exists():
        console.print(f"[red]Script not found:[/red] {script}")
        raise typer.Exit(code=1)
    _run([sys.executable, str(script.name)], cwd=script.parent)


# -------------------------------------------------------------
# Code-quality commands (wrappers around ruff / black / mypy / pytest)
# -------------------------------------------------------------


def _src_paths() -> list[str]:
    return ["src", "tests", "apps/api"]


@app.command()
def lint() -> None:
    """Run ruff + black --check on src, tests, api."""
    _run([sys.executable, "-m", "ruff", "check", *_src_paths()])
    _run([sys.executable, "-m", "black", "--check", *_src_paths()])


@app.command(name="format")
def format_code() -> None:
    """Auto-format source with ruff --fix + black."""
    _run([sys.executable, "-m", "ruff", "check", "--fix", *_src_paths()])
    _run([sys.executable, "-m", "black", *_src_paths()])


@app.command()
def typecheck() -> None:
    """Run mypy in strict mode on src/."""
    _run([sys.executable, "-m", "mypy", "src"])


@app.command()
def test(
    fast: bool = typer.Option(False, "--fast", help="Skip slow + integration tests"),
    cov: bool = typer.Option(False, "--cov", help="Open HTML coverage report"),
) -> None:
    """Run the pytest suite."""
    cmd = [sys.executable, "-m", "pytest"]
    if fast:
        cmd += ["-m", "not slow and not integration"]
    if cov:
        cmd += ["--cov-report=html"]
    _run(cmd)
    if cov:
        console.print("\n[cyan]Coverage report:[/cyan] htmlcov/index.html")


@app.command()
def check() -> None:
    """Run lint + typecheck + test in sequence (the canonical pre-commit gate)."""
    lint()
    typecheck()
    test()
    console.print("\n[bold green]All checks passed.[/bold green]")


# -------------------------------------------------------------
# Application commands
# -------------------------------------------------------------


@app.command()
def api(
    host: str = typer.Option("0.0.0.0", "--host"),
    port: int = typer.Option(8000, "--port", "-p"),
    reload: bool = typer.Option(True, "--reload/--no-reload"),
) -> None:
    """Start the FastAPI backend dev server (apps/api/main.py)."""
    cmd = [
        sys.executable, "-m", "uvicorn", "apps.api.main:app",
        "--host", host, "--port", str(port),
        "--app-dir", str(PATHS.root),
    ]
    if reload:
        cmd.append("--reload")
    _run(cmd)


# -------------------------------------------------------------
# Housekeeping
# -------------------------------------------------------------


@app.command()
def clean(
    all_artifacts: bool = typer.Option(False, "--all", help="Also remove .venv/ and node_modules/"),
) -> None:
    """Remove caches, build artefacts, and coverage reports (keeps data/ and models/)."""
    root = PATHS.root
    targets = [
        ".pytest_cache", ".mypy_cache", ".ruff_cache", ".coverage", "coverage.xml",
        "htmlcov", "build", "dist",
    ]
    if all_artifacts:
        targets += [".venv", "apps/web/node_modules", "apps/web/dist"]

    removed = 0
    for t in targets:
        path = root / t
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
            else:
                path.unlink(missing_ok=True)
            console.print(f"  [yellow]removed[/yellow] {t}")
            removed += 1

    # also wipe __pycache__ and *.egg-info
    for cache in root.rglob("__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)
        removed += 1
    for egg in root.glob("*.egg-info"):
        shutil.rmtree(egg, ignore_errors=True)
        removed += 1

    console.print(f"\n[green]Clean complete[/green] - removed {removed} item(s).")


if __name__ == "__main__":
    app()
