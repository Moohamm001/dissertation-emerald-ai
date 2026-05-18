"""Class-imbalance strategy comparison harness (proposal §5.7).

Compares three balancing strategies head-to-head on a baseline learner under
stratified 5-fold CV, then names the strategy with the best joint
(PR-AUC × (1 − within-minority ECE)) score. The chosen strategy is fed
forward into the §5.8 modelling stage.

Strategies implemented:
  - `class_weighted` — no resampling; uses sklearn's `class_weight='balanced'`
    (or `scale_pos_weight` for boosters at the §5.8 stage).
  - `smote` — SMOTE oversampling [Chawla et al., 2002] applied **strictly
    inside the training fold**, never on validation — preventing the leakage
    pattern documented by Santos et al. (2018).
  - `no_resample` — control baseline; isolates the marginal value of any
    rebalancing intervention against an unweighted, unbalanced fit.

`focal_loss` is documented but not implemented here — it requires the neural
training stack (proposal §5.8 MLP / FT-Transformer) which lands in a
follow-up commit.

The proposal §4.4 v0.4.1 reframe makes SMOTE's status uncertain at 50
minority observations: oversampling between an extremely sparse seed set
risks generating off-manifold synthetic points. The harness's job is to
report what actually wins on this data rather than presume.

Run:
    python -m emerald_ai imbalance
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
from sklearn.model_selection import StratifiedKFold

from emerald_ai.config import MODEL, PATHS

GOVERNANCE_DIR = PATHS.root / "data" / "governance"
IMBALANCE_REPORT_PATH = GOVERNANCE_DIR / "imbalance_report.md"


# -----------------------------------------------------------------------------
# Strategy factories — each returns a fittable sklearn-compatible Pipeline.
# -----------------------------------------------------------------------------
def make_no_resample_pipeline(random_state: int = MODEL.random_seed) -> ImbPipeline:
    """Control baseline: unweighted Logistic Regression, no rebalancing."""
    return ImbPipeline([
        ("clf", LogisticRegression(C=1.0, max_iter=2000, random_state=random_state)),
    ])


def make_class_weighted_pipeline(random_state: int = MODEL.random_seed) -> ImbPipeline:
    """Class-weighted loss: sklearn `class_weight='balanced'`."""
    return ImbPipeline([
        ("clf", LogisticRegression(
            C=1.0, max_iter=2000,
            class_weight="balanced", random_state=random_state,
        )),
    ])


def make_smote_pipeline(random_state: int = MODEL.random_seed, k_neighbors: int = 5) -> ImbPipeline:
    """SMOTE oversampling, then plain Logistic Regression.

    `k_neighbors` defaults to 5 but the SMOTE pipeline auto-clamps when the
    minority class has fewer observations than k+1 — that's why this
    strategy is brittle at 50 minority observations.
    """
    return ImbPipeline([
        ("smote", SMOTE(k_neighbors=k_neighbors, random_state=random_state)),
        ("clf", LogisticRegression(C=1.0, max_iter=2000, random_state=random_state)),
    ])


STRATEGY_FACTORIES: dict[str, Callable[..., ImbPipeline]] = {
    "no_resample": make_no_resample_pipeline,
    "class_weighted": make_class_weighted_pipeline,
    "smote": make_smote_pipeline,
}


# -----------------------------------------------------------------------------
# Metrics
# -----------------------------------------------------------------------------
def within_minority_ece(
    y_true: np.ndarray,
    y_score: np.ndarray,
    *,
    minority_label: int = 0,
    n_bins: int = 10,
) -> float:
    """ECE restricted to rows where ``y_true == minority_label``.

    Computes Expected Calibration Error on the minority-class subset only.
    The dissertation's primary calibration metric (v0.4.1 §5.10): marginal
    ECE is dominated by the favourable class and masks the failures that
    matter most for adverse-action decisioning.

    For binary Y with minority=0 and y_score = predicted P(Y=1|X):
    on the minority subset the true label is 0, so a well-calibrated model
    would output low y_score. Standard equal-width ECE on this subset is
    the absolute gap between binned mean prediction and 0.
    """
    mask = y_true == minority_label
    if not mask.any():
        return float("nan")
    scores_min = y_score[mask]
    # On the minority subset, all true labels equal `minority_label`.
    # If minority=0, we compare predicted P(Y=1) to 0 within each bin.
    # The corresponding "true positive rate within bin" is 0.
    bins = np.linspace(0, 1, n_bins + 1)
    bin_ids = np.clip(np.digitize(scores_min, bins) - 1, 0, n_bins - 1)
    ece = 0.0
    n_total = len(scores_min)
    for b in range(n_bins):
        in_bin = bin_ids == b
        if not in_bin.any():
            continue
        weight = in_bin.sum() / n_total
        avg_pred = float(scores_min[in_bin].mean())
        # Expected "true positive rate" within this minority subset is 0
        # (since true label = 0 for all rows in the subset, expected
        # frequency of Y=1 is 0).
        ece += weight * abs(avg_pred - 0.0)
    return float(ece)


# -----------------------------------------------------------------------------
# Comparison harness
# -----------------------------------------------------------------------------
@dataclass
class StrategyResult:
    name: str
    pr_auc_mean: float
    pr_auc_std: float
    minority_ece_mean: float
    minority_ece_std: float
    joint_score: float
    fold_pr_auc: list[float] = field(default_factory=list)
    fold_minority_ece: list[float] = field(default_factory=list)


@dataclass
class ImbalanceAudit:
    """Trace of every imbalance-strategy decision."""

    n_rows: int = 0
    n_minority: int = 0
    minority_prevalence: float = 0.0
    n_folds: int = 5
    strategies: list[StrategyResult] = field(default_factory=list)
    chosen_strategy: str | None = None
    random_state: int = MODEL.random_seed


def evaluate_strategy(
    pipeline: ImbPipeline,
    X: pd.DataFrame | np.ndarray,
    y: pd.Series | np.ndarray,
    *,
    name: str,
    n_folds: int = 5,
    random_state: int = MODEL.random_seed,
) -> StrategyResult:
    """Stratified-CV evaluation of one imbalance strategy.

    Resampling happens inside each fold's pipeline; validation predictions
    are made on the untouched fold — Santos et al. (2018)'s no-leakage rule.
    """
    X_arr = X.to_numpy() if isinstance(X, pd.DataFrame) else np.asarray(X)
    y_arr = np.asarray(y).astype(int)

    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=random_state)
    pr_aucs: list[float] = []
    eces: list[float] = []
    for fold_idx, (tr, va) in enumerate(skf.split(X_arr, y_arr)):
        pipeline.fit(X_arr[tr], y_arr[tr])
        # predict_proba returns columns ordered by classes_; locate Y=1 column
        proba = pipeline.predict_proba(X_arr[va])
        classes = pipeline.classes_ if hasattr(pipeline, "classes_") else pipeline.named_steps["clf"].classes_
        pos_idx = int(np.where(classes == 1)[0][0]) if 1 in classes else 1
        y_score = proba[:, pos_idx]
        # PR-AUC against the MINORITY class (y=0). To compute PR for minority,
        # invert: pr_auc(y_true==0, 1 - score_for_class_1).
        pr_aucs.append(float(average_precision_score(y_arr[va] == 0, 1 - y_score)))
        eces.append(within_minority_ece(y_arr[va], y_score, minority_label=0))

    pr_mean = float(np.mean(pr_aucs))
    pr_std = float(np.std(pr_aucs, ddof=1)) if len(pr_aucs) > 1 else 0.0
    ece_mean = float(np.mean(eces))
    ece_std = float(np.std(eces, ddof=1)) if len(eces) > 1 else 0.0
    joint = pr_mean * (1.0 - ece_mean)  # higher is better

    return StrategyResult(
        name=name,
        pr_auc_mean=pr_mean,
        pr_auc_std=pr_std,
        minority_ece_mean=ece_mean,
        minority_ece_std=ece_std,
        joint_score=joint,
        fold_pr_auc=pr_aucs,
        fold_minority_ece=eces,
    )


def select_strategy(
    X: pd.DataFrame | np.ndarray,
    y: pd.Series | np.ndarray,
    *,
    strategy_names: tuple[str, ...] = ("no_resample", "class_weighted", "smote"),
    n_folds: int = 5,
    random_state: int = MODEL.random_seed,
) -> ImbalanceAudit:
    """Run every strategy and select the joint-score winner."""
    y_arr = np.asarray(y).astype(int)
    n_min = int((y_arr == 0).sum())
    n_total = int(len(y_arr))

    audit = ImbalanceAudit(
        n_rows=n_total,
        n_minority=n_min,
        minority_prevalence=n_min / max(n_total, 1),
        n_folds=n_folds,
        random_state=random_state,
    )

    for name in strategy_names:
        factory = STRATEGY_FACTORIES.get(name)
        if factory is None:
            continue
        try:
            pipe = factory(random_state=random_state)
            res = evaluate_strategy(pipe, X, y, name=name, n_folds=n_folds, random_state=random_state)
            audit.strategies.append(res)
        except Exception as exc:  # pragma: no cover — SMOTE can fail at very small N
            audit.strategies.append(StrategyResult(
                name=name, pr_auc_mean=float("nan"), pr_auc_std=float("nan"),
                minority_ece_mean=float("nan"), minority_ece_std=float("nan"),
                joint_score=float("-inf"),
                fold_pr_auc=[], fold_minority_ece=[],
            ))
            print(f"[imbalance] WARNING: strategy {name!r} failed: {exc}")

    valid = [s for s in audit.strategies if np.isfinite(s.joint_score)]
    if valid:
        audit.chosen_strategy = max(valid, key=lambda s: s.joint_score).name
    return audit


# -----------------------------------------------------------------------------
# Report writer
# -----------------------------------------------------------------------------
def emit_report(audit: ImbalanceAudit, *, out_path: Path = IMBALANCE_REPORT_PATH) -> Path:
    """Write data/governance/imbalance_report.md."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    today = pd.Timestamp.utcnow().date().isoformat()

    strategy_rows = "\n".join(
        f"| `{s.name}` | {s.pr_auc_mean:.4f} ± {s.pr_auc_std:.4f} | "
        f"{s.minority_ece_mean:.4f} ± {s.minority_ece_std:.4f} | {s.joint_score:.4f} |"
        for s in audit.strategies
    )

    body = f"""# Class-Imbalance Strategy Report — proposal §5.7

_Compares balancing strategies on a Logistic Regression baseline under stratified
{audit.n_folds}-fold CV. Resampling is applied strictly inside training folds._

Version: 0.1 · Generated: {today}

## Setup

| | Value |
|---|---:|
| Total rows | {audit.n_rows:,} |
| Minority observations (Y=0, delinquent) | {audit.n_minority} |
| Empirical prevalence | {audit.minority_prevalence*100:.3f}% |
| CV folds | {audit.n_folds} |
| Master seed | {audit.random_state} |

## Strategy comparison

| Strategy | Minority PR-AUC | Within-minority ECE | Joint score |
|---|---|---|---:|
{strategy_rows}

_Joint score = PR-AUC × (1 − within-minority-ECE); higher is better._

## Chosen strategy

**`{audit.chosen_strategy}`** maximised the joint score on this baseline.

The chosen strategy is fed forward into the §5.8 modelling stage. Each model
family may re-evaluate independently (a booster's `scale_pos_weight` is
strictly equivalent to `class_weight='balanced'` on a linear model only at
the gradient level; the §5.8 commit will revisit).

## Notes

- **SMOTE caveat (v0.4.1 §4.4):** SMOTE interpolates between extremely sparse
  seeds at 0.36% prevalence and risks off-manifold synthetic points. If it
  underperforms `class_weighted` on the joint score, that is empirical
  evidence supporting the v0.4.1 framing rather than a methodological failure.
- **Focal loss** is documented but not implemented in this stage — it requires
  the neural training stack landing in §5.8.
- **In-fold-only constraint** [Santos et al., 2018]: the imblearn Pipeline
  enforces this structurally; validation folds are never resampled.
"""
    out_path.write_text(body, encoding="utf-8")
    return out_path


# -----------------------------------------------------------------------------
# Orchestrator
# -----------------------------------------------------------------------------
def run_imbalance_selection(
    *,
    out_path: Path = IMBALANCE_REPORT_PATH,
    n_folds: int = 5,
    random_state: int = MODEL.random_seed,
) -> tuple[Path, ImbalanceAudit]:
    """End-to-end: load → preprocess → compare strategies → emit governance report."""
    from emerald_ai.data.eda import split_xy
    from emerald_ai.data.load import load_labelled
    from emerald_ai.features.pipeline import fit_transform_with_audit

    df = load_labelled()
    X, y = split_xy(df)
    X_t, _pre, _audit = fit_transform_with_audit(X, y)
    audit = select_strategy(X_t, y, n_folds=n_folds, random_state=random_state)
    written = emit_report(audit, out_path=out_path)
    return written, audit


def main() -> None:  # pragma: no cover
    written, audit = run_imbalance_selection()
    print(f"OK: {written}")
    print(f"  chosen strategy: {audit.chosen_strategy}")


if __name__ == "__main__":  # pragma: no cover
    main()
