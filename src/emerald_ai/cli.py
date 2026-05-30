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
def preprocess(
    data_path: Path | None = typer.Option(None, help="Override raw .xlsx path (default: data/raw/All_Funded_2019_Green Loan.xlsx)"),
    out: Path | None = typer.Option(None, help="Override output report path (default: data/governance/preprocess_report.md)"),
) -> None:
    """Run the §5.5 preprocessing pipeline: drop list + impute + encode + scale.

    Stage 1 (drop) applies the >40% missingness rule and strips EDA-flagged
    time-leaking columns. Stage 2 imputes (median for numerics; explicit
    `__missing__` for categoricals) and appends missing-indicator binaries.
    Stage 3 one-hots low-cardinality categoricals (≤10 levels) and
    target-encodes high-cardinality ones (Industry, Borrower State).
    Stage 4 standardises numerics. Emits ``data/governance/preprocess_report.md``.
    """
    from emerald_ai.features.pipeline import PREPROCESS_REPORT_PATH, run_preprocess
    target = out if out is not None else PREPROCESS_REPORT_PATH
    written, audit = run_preprocess(path=data_path, out_path=target)
    console.print(f"[green]OK[/green]: {written}")
    console.print(
        f"  in={audit.n_input_columns} cols / {audit.n_rows_in} rows  "
        f"-> out={audit.n_output_features} features / {audit.n_rows_out} rows"
    )


@app.command()
def select(
    out: Path | None = typer.Option(None, help="Override output report path (default: data/governance/selection_report.md)"),
    n_bootstraps: int = typer.Option(30, help="Bootstrap rounds for stability filtering"),
    top_k: int = typer.Option(25, help="Top-K features per bootstrap"),
) -> None:
    """Run §5.6 two-stage feature selection: MI filter + bootstrap-stability RF importance.

    Emits ``data/governance/selection_report.md`` listing the features that
    cleared both stages, their MI scores, and per-feature selection frequencies.
    """
    from emerald_ai.data.eda import split_xy
    from emerald_ai.data.load import load_labelled
    from emerald_ai.features.pipeline import fit_transform_with_audit
    from emerald_ai.features.selection import (
        SELECTION_REPORT_PATH, emit_report, run_selection,
    )
    df = load_labelled()
    X, y = split_xy(df)
    X_t, pre, _audit = fit_transform_with_audit(X, y)
    fnames = list(pre.get_feature_names_out())
    import pandas as _pd
    X_df = _pd.DataFrame(X_t, columns=fnames, index=X.index)
    audit = run_selection(X_df, y, n_bootstraps=n_bootstraps, top_k=top_k)
    target = out if out is not None else SELECTION_REPORT_PATH
    written = emit_report(audit, out_path=target)
    console.print(f"[green]OK[/green]: {written}")
    console.print(
        f"  in={audit.n_features_in} -> filter-kept={audit.n_after_filter} "
        f"-> selected={audit.n_selected}"
    )


@app.command()
def imbalance(
    out: Path | None = typer.Option(None, help="Override output report path (default: data/governance/imbalance_report.md)"),
    n_folds: int = typer.Option(5, help="Stratified CV folds"),
) -> None:
    """Run §5.7 class-imbalance strategy comparison.

    Evaluates no_resample / class_weighted / SMOTE under {n_folds}-fold CV
    on a Logistic Regression baseline; selects the joint-score winner
    (PR-AUC × (1 − within-minority-ECE)). Emits
    ``data/governance/imbalance_report.md``.
    """
    from emerald_ai.training.imbalance import IMBALANCE_REPORT_PATH, run_imbalance_selection
    target = out if out is not None else IMBALANCE_REPORT_PATH
    written, audit = run_imbalance_selection(out_path=target, n_folds=n_folds)
    console.print(f"[green]OK[/green]: {written}")
    console.print(f"  chosen strategy: [bold]{audit.chosen_strategy}[/bold]")


@app.command()
def train(
    families: str = typer.Option("all", "--families", "-f", help="Comma-separated family names or 'all'"),
    n_outer_folds: int = typer.Option(5, help="Outer CV folds"),
    n_inner_folds: int = typer.Option(3, help="Inner CV folds for the hyperparameter search"),
    n_search_candidates: int = typer.Option(12, help="RandomizedSearch trial budget per family-fold"),
    tuner: str = typer.Option("random", help="Hyperparameter search: 'random' (fast) or 'optuna' (TPE)"),
    n_trials: int = typer.Option(50, help="Optuna trials per family-fold (only when --tuner optuna)"),
    persist: bool = typer.Option(True, help="Persist best model + preprocessor + conformal to models/"),
) -> None:
    """Train all available families with nested CV (§5.8 + §5.9).

    Persists ``models/{current_model,preprocessor,conformal_marginal,feature_names}``
    so the FastAPI backend can serve them. Emits ``data/governance/training_report.md``.

    Use ``--tuner optuna`` for the proposal's full TPE hyperparameter search
    (slower); the default ``--tuner random`` runs RandomizedSearchCV.
    """
    from emerald_ai.data.eda import split_xy
    from emerald_ai.data.load import load_labelled
    from emerald_ai.features.pipeline import fit_transform_with_audit
    from emerald_ai.models import available_models
    from emerald_ai.training.cv import emit_report, nested_cv

    fam_list = None if families == "all" else [f.strip() for f in families.split(",")]
    if fam_list is None:
        fam_list = available_models()

    df = load_labelled()
    X, y = split_xy(df)
    X_t, pre, _audit = fit_transform_with_audit(X, y)
    feature_names = list(pre.get_feature_names_out())

    audit, oof = nested_cv(
        X_t, y,
        families=fam_list,
        n_outer_folds=n_outer_folds,
        n_inner_folds=n_inner_folds,
        n_search_candidates=n_search_candidates,
        tuner=tuner,
        n_trials=n_trials,
    )
    report = emit_report(audit)
    console.print(f"[green]OK[/green]: {report}")
    console.print(f"  families: {audit.families}")

    if persist:
        _persist_artefacts(X_t, y, oof, audit, pre, feature_names)
        console.print(f"  persisted artefacts to {PATHS.root / 'models'}")


def _persist_artefacts(X_t, y, oof, audit, preprocessor, feature_names):
    """Pick the best family by mean PR-AUC, refit on all rows, save with preprocessor + conformal."""
    import json
    import joblib
    import numpy as np
    from emerald_ai.calibration import SplitConformal
    from emerald_ai.models import FACTORIES

    by_family: dict[str, list[float]] = {}
    for r in audit.fold_results:
        by_family.setdefault(r.family, []).append(r.pr_auc)
    if not by_family:
        return
    best_family = max(by_family, key=lambda k: float(np.mean(by_family[k])))
    console.print(f"  best family: [bold]{best_family}[/bold] (mean PR-AUC = {np.mean(by_family[best_family]):.4f})")

    model = FACTORIES[best_family]()
    model.fit(X_t, y)

    classes = getattr(model, "classes_", np.array([0, 1]))
    pos_idx = int(np.where(classes == 1)[0][0]) if 1 in classes else 1
    scores_full = model.predict_proba(X_t)[:, pos_idx]
    conf = SplitConformal(alpha=0.10).fit(scores_full, y)

    out_dir = PATHS.root / "models"
    out_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, out_dir / "current_model.joblib")
    joblib.dump(preprocessor, out_dir / "preprocessor.joblib")
    joblib.dump(conf, out_dir / "conformal_marginal.joblib")
    (out_dir / "feature_names.json").write_text(json.dumps(feature_names), encoding="utf-8")
    (out_dir / "best_family.txt").write_text(best_family, encoding="utf-8")


@app.command()
def audit(
    out: Path | None = typer.Option(None, help="Override fairness_report.md output path"),
) -> None:
    """Run the §5.12 fairness audit on the persisted model against Industry / Borrower State.

    Emits ``data/governance/fairness_report.md``.
    """
    import json
    import joblib
    import numpy as np
    from emerald_ai.data.eda import split_xy
    from emerald_ai.data.load import load_labelled
    from emerald_ai.fairness import audit_predictions, emit_report
    from emerald_ai.fairness.audit import FAIRNESS_REPORT_PATH

    models_dir = PATHS.root / "models"
    if not (models_dir / "current_model.joblib").exists():
        console.print("[red]No trained model artefacts found.[/red] Run `python -m emerald_ai train` first.")
        raise typer.Exit(1)

    model = joblib.load(models_dir / "current_model.joblib")
    preprocessor = joblib.load(models_dir / "preprocessor.joblib")
    df = load_labelled()
    X_raw, y = split_xy(df)
    X_t = preprocessor.transform(X_raw)
    classes = getattr(model, "classes_", np.array([0, 1]))
    pos_idx = int(np.where(classes == 1)[0][0]) if 1 in classes else 1
    scores = model.predict_proba(X_t)[:, pos_idx]

    sensitive = {
        "Industry": X_raw["Industry"].fillna("__missing__").to_numpy(),
        "Borrower State": X_raw["Borrower State"].fillna("__missing__").to_numpy(),
    }
    # §5.12 fix: auditing at a hard 0.5 threshold is uninformative here — at
    # 0.36% prevalence the model approves ~100% of every group, so all gaps
    # collapse to ~0. Audit at the *deployed* decision boundary instead: the
    # risk-band watch cut-off (p20 of the score distribution), the same cut the
    # API serves. This makes selection rates non-degenerate and the gaps real.
    from emerald_ai.eval.risk_bands import risk_band_thresholds
    thresholds = risk_band_thresholds(scores)
    operating_threshold = thresholds["watch_cut"]
    audit_obj = audit_predictions(np.asarray(y), scores, sensitive, threshold=operating_threshold)
    audit_obj.threshold_policy = (
        f"risk-band 'watch' cut-off = p{thresholds['watch_percentile']:.0f} of the model's "
        f"score distribution (the deployed decision boundary; a hard 0.5 approves ~100% of "
        f"every group at this prevalence, collapsing all gaps to ~0)."
    )
    target = out if out is not None else FAIRNESS_REPORT_PATH
    written = emit_report(audit_obj, out_path=target)
    console.print(f"[green]OK[/green]: {written}")
    console.print(
        f"  audited at watch-band threshold = {operating_threshold:.4f} "
        f"(p{thresholds['watch_percentile']:.0f}); high-risk cut = {thresholds['high_risk_cut']:.4f}"
    )
    for axis, gaps in audit_obj.gaps.items():
        console.print(
            f"  {axis}: DP={gaps['dp_gap']:.3f} TPR={gaps['tpr_gap']:.3f} "
            f"FPR={gaps['fpr_gap']:.3f} prec={gaps['precision_gap']:.3f} ECE={gaps['ece_gap']:.3f}"
        )


@app.command()
def evaluate() -> None:
    """Compute primary + secondary metrics on the persisted model (§5.10 + §5.13).

    Reads ``models/current_model.joblib`` + ``preprocessor.joblib`` and prints
    the headline trio (PR-AUC, within-minority ECE, recall@top-decile) plus
    secondary tier (ROC-AUC, KS, F1, Brier, MCC) on the labelled supervisory
    pool. No held-out split here — this is a smoke check, not the §5.9
    nested-CV report (that lives in `data/governance/training_report.md`).
    """
    import joblib
    import numpy as np
    from emerald_ai.data.eda import split_xy
    from emerald_ai.data.load import load_labelled
    from emerald_ai.eval import (
        brier_score, ece, f1_at, ks_statistic, matthews_corrcoef,
        pr_auc_minority, recall_at_top_decile, roc_auc, within_minority_ece,
    )

    models_dir = PATHS.root / "models"
    if not (models_dir / "current_model.joblib").exists():
        console.print("[red]No model.[/red] Run `python -m emerald_ai train` first.")
        raise typer.Exit(1)

    model = joblib.load(models_dir / "current_model.joblib")
    pre = joblib.load(models_dir / "preprocessor.joblib")
    df = load_labelled()
    X, y = split_xy(df)
    X_t = pre.transform(X)
    classes = getattr(model, "classes_", np.array([0, 1]))
    pos_idx = int(np.where(classes == 1)[0][0]) if 1 in classes else 1
    scores = model.predict_proba(X_t)[:, pos_idx]

    primary = {
        "PR-AUC (minority)": pr_auc_minority(np.asarray(y), scores),
        "within-minority ECE": within_minority_ece(np.asarray(y), scores),
        "recall@top-decile": recall_at_top_decile(np.asarray(y), scores),
    }
    secondary = {
        "ROC-AUC": roc_auc(np.asarray(y), scores),
        "KS": ks_statistic(np.asarray(y), scores),
        "F1@0.5": f1_at(np.asarray(y), scores),
        "Brier": brier_score(np.asarray(y), scores),
        "ECE (marginal)": ece(np.asarray(y), scores),
        "MCC@0.5": matthews_corrcoef(np.asarray(y), scores),
    }
    console.print(
        "[yellow]In-sample metrics (model evaluated on its training pool). "
        "For honest OOF estimates see data/governance/training_report.md.[/yellow]"
    )
    console.print("[bold]Primary tier:[/bold]")
    for k, v in primary.items():
        console.print(f"  {k:<24s} {v:.4f}")
    console.print("[bold]Secondary tier:[/bold]")
    for k, v in secondary.items():
        console.print(f"  {k:<24s} {v:.4f}")


@app.command()
def explain(
    out: Path | None = typer.Option(None, help="Override output path (default: data/governance/explain_report.md)"),
    n_repeats: int = typer.Option(5, help="Permutation-importance repeats"),
) -> None:
    """Run the global explainability layer on the persisted model (§5.11).

    Computes permutation importance against PR-AUC and writes a markdown
    report ranked by mean importance. Local + counterfactual layers are
    served via the /explain FastAPI endpoint.
    """
    import joblib
    import json
    import numpy as np
    import pandas as pd
    from emerald_ai.data.eda import split_xy
    from emerald_ai.data.load import load_labelled
    from emerald_ai.explain import (
        HAS_SHAP,
        faithfulness_correlation,
        global_importance,
        shap_global_importance,
    )

    models_dir = PATHS.root / "models"
    if not (models_dir / "current_model.joblib").exists():
        console.print("[red]No model.[/red] Run `python -m emerald_ai train` first.")
        raise typer.Exit(1)

    model = joblib.load(models_dir / "current_model.joblib")
    pre = joblib.load(models_dir / "preprocessor.joblib")
    feature_names = json.loads((models_dir / "feature_names.json").read_text())
    df = load_labelled()
    X, y = split_xy(df)
    X_t = pre.transform(X)

    target = out if out is not None else (PATHS.root / "data" / "governance" / "explain_report.md")
    target.parent.mkdir(parents=True, exist_ok=True)
    today = pd.Timestamp.utcnow().date().isoformat()

    sections: list[str] = [f"# Explainability Report — proposal §5.11\n\nVersion: 0.2 · Generated: {today}\n"]

    if HAS_SHAP:
        console.print("[dim]Computing SHAP global attributions...[/dim]")
        shap_df = shap_global_importance(model, X_t, feature_names=feature_names, max_samples=500)
        shap_rows = "\n".join(
            f"| `{r['feature']}` | {r['mean_abs_shap']:.4f} | {r['mean_signed_shap']:+.4f} |"
            for _, r in shap_df.head(25).iterrows()
        )
        # Empirical fidelity on a sample: do the SHAP attributions track prediction drops?
        from emerald_ai.explain.shap_engine import _shap_values_matrix
        n_fid = min(200, len(X_t))
        Xs = X_t[:n_fid]
        fid = faithfulness_correlation(model, Xs, _shap_values_matrix(model, Xs), n_subsets=30)
        sections.append(
            "## Global feature attribution — mean(|SHAP|)\n\n"
            "Exact TreeSHAP on the persisted model; signed column shows net direction.\n\n"
            f"| Feature | mean(\\|SHAP\\|) | mean signed SHAP |\n|---|---|---|\n{shap_rows}\n"
        )
        sections.append(
            f"## Explanation fidelity\n\n"
            f"Faithfulness correlation (Bhatt et al., 2020) on {n_fid} instances: "
            f"**{fid:.3f}** (∈[-1,1]; higher means SHAP attribution mass tracks the "
            f"model's actual prediction drops under feature ablation).\n"
        )
        top3 = list(shap_df["feature"].head(3))
    else:
        console.print("[yellow]shap not installed — using permutation importance fallback.[/yellow]")
        imp = global_importance(model, X_t, y, feature_names=feature_names, n_repeats=n_repeats)
        rows = "\n".join(
            f"| `{r['feature']}` | {r['importance_mean']:.4f} ± {r['importance_std']:.4f} |"
            for _, r in imp.head(25).iterrows()
        )
        sections.append(
            "## Top-25 features by permutation importance (PR-AUC scoring)\n\n"
            f"| Feature | Importance |\n|---|---|\n{rows}\n\n"
            "_Fallback view: install the `xai` extra (`pip install -e \".[xai]\"`) for exact SHAP attributions._\n"
        )
        top3 = list(imp["feature"].head(3))

    target.write_text("\n".join(sections) + "\n", encoding="utf-8")
    console.print(f"[green]OK[/green]: {target}")
    console.print(f"  top-3: {top3}")


# `audit` is defined above (alongside `train`) — old stub removed in §5.12 commit.


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
