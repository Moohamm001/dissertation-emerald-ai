"""Per-axis fairness audit (proposal §5.12).

Metric definitions follow Hardt, Price & Srebro (2016) and Chouldechova (2017):

  demographic_parity_gap  = max_g P(ŷ=1 | g) − min_g P(ŷ=1 | g)
  equalised_odds_tpr_gap  = max_g TPR_g − min_g TPR_g
  equalised_odds_fpr_gap  = max_g FPR_g − min_g FPR_g
  predictive_parity_gap   = max_g precision_g − min_g precision_g
  calibration_within_gap  = max_g ECE_g − min_g ECE_g

The proposal designates **calibration-within-group** as the binding
constraint (proposal §5.12): under Internal Ratings-Based PD reporting,
miscalibrated probabilities cause real economic harm to a group.

Outputs live in ``data/governance/fairness_report.md``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from emerald_ai.config import PATHS

GOVERNANCE_DIR = PATHS.root / "data" / "governance"
FAIRNESS_REPORT_PATH = GOVERNANCE_DIR / "fairness_report.md"


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def _ece(y_true: np.ndarray, y_score: np.ndarray, n_bins: int = 10) -> float:
    p = np.asarray(y_score, dtype=float)
    y = np.asarray(y_true, dtype=int)
    if len(p) == 0:
        return float("nan")
    bins = np.linspace(0, 1, n_bins + 1)
    bin_ids = np.clip(np.digitize(p, bins) - 1, 0, n_bins - 1)
    ece = 0.0
    n = len(p)
    for b in range(n_bins):
        m = bin_ids == b
        if not m.any():
            continue
        ece += (m.sum() / n) * abs(float(p[m].mean()) - float(y[m].mean()))
    return float(ece)


def _safe_division(a: float, b: float) -> float:
    return a / b if b else float("nan")


# -----------------------------------------------------------------------------
# Core metrics per group
# -----------------------------------------------------------------------------
@dataclass
class GroupResult:
    group: object
    n: int
    positives: int
    predicted_positives: int
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int
    selection_rate: float
    tpr: float
    fpr: float
    precision: float
    ece: float


def _per_group_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_score: np.ndarray,
    groups: np.ndarray,
    *,
    positive_label: int = 1,
) -> list[GroupResult]:
    out: list[GroupResult] = []
    for g in pd.unique(groups):
        mask = groups == g
        yt = y_true[mask].astype(int)
        yp = y_pred[mask].astype(int)
        ys = y_score[mask]

        positives = int((yt == positive_label).sum())
        negatives = int((yt != positive_label).sum())
        pred_pos = int((yp == positive_label).sum())
        tp = int(((yp == positive_label) & (yt == positive_label)).sum())
        fp = int(((yp == positive_label) & (yt != positive_label)).sum())
        tn = int(((yp != positive_label) & (yt != positive_label)).sum())
        fn = int(((yp != positive_label) & (yt == positive_label)).sum())

        out.append(GroupResult(
            group=g,
            n=int(mask.sum()),
            positives=positives,
            predicted_positives=pred_pos,
            true_positives=tp,
            false_positives=fp,
            true_negatives=tn,
            false_negatives=fn,
            selection_rate=_safe_division(pred_pos, int(mask.sum())),
            tpr=_safe_division(tp, positives),
            fpr=_safe_division(fp, negatives),
            precision=_safe_division(tp, pred_pos),
            ece=_ece(yt == positive_label, ys),
        ))
    return out


# -----------------------------------------------------------------------------
# Audit dataclass
# -----------------------------------------------------------------------------
@dataclass
class FairnessAudit:
    axes: dict[str, list[GroupResult]] = field(default_factory=dict)
    gaps: dict[str, dict[str, float]] = field(default_factory=dict)
    threshold: float = 0.50
    positive_label: int = 1


def _compute_gaps(rows: list[GroupResult]) -> dict[str, float]:
    if not rows:
        return {"dp_gap": float("nan"), "tpr_gap": float("nan"), "fpr_gap": float("nan"),
                "precision_gap": float("nan"), "ece_gap": float("nan")}
    rates = [r.selection_rate for r in rows if np.isfinite(r.selection_rate)]
    tprs = [r.tpr for r in rows if np.isfinite(r.tpr)]
    fprs = [r.fpr for r in rows if np.isfinite(r.fpr)]
    precs = [r.precision for r in rows if np.isfinite(r.precision)]
    eces = [r.ece for r in rows if np.isfinite(r.ece)]
    def gap(xs):
        return float(max(xs) - min(xs)) if xs else float("nan")
    return {
        "dp_gap": gap(rates),
        "tpr_gap": gap(tprs),
        "fpr_gap": gap(fprs),
        "precision_gap": gap(precs),
        "ece_gap": gap(eces),
    }


def audit_predictions(
    y_true: np.ndarray | pd.Series,
    y_score: np.ndarray | pd.Series,
    sensitive: dict[str, np.ndarray | pd.Series],
    *,
    threshold: float = 0.50,
    positive_label: int = 1,
) -> FairnessAudit:
    """Run the per-axis audit. ``sensitive`` maps axis-name -> group label array."""
    y_true_arr = np.asarray(y_true, dtype=int)
    y_score_arr = np.asarray(y_score, dtype=float)
    y_pred_arr = (y_score_arr >= threshold).astype(int)

    audit = FairnessAudit(threshold=threshold, positive_label=positive_label)
    for axis, groups in sensitive.items():
        rows = _per_group_metrics(
            y_true_arr, y_pred_arr, y_score_arr, np.asarray(groups),
            positive_label=positive_label,
        )
        audit.axes[axis] = rows
        audit.gaps[axis] = _compute_gaps(rows)
    return audit


# -----------------------------------------------------------------------------
# Report writer
# -----------------------------------------------------------------------------
def emit_report(audit: FairnessAudit, *, out_path: Path = FAIRNESS_REPORT_PATH) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    today = pd.Timestamp.utcnow().date().isoformat()

    sections: list[str] = []
    sections.append(f"# Fairness Audit Report — proposal §5.12\n")
    sections.append("_Per-axis demographic parity / equalised odds / predictive parity / calibration-within-group._\n")
    sections.append(f"\nVersion: 0.1 · Generated: {today}\n")
    sections.append(f"\n## Operating threshold\n\n- Classification threshold: **{audit.threshold:.2f}**\n- Positive label: **{audit.positive_label}**\n")

    sections.append("\n## Per-axis gap summary\n")
    sections.append("| Axis | DP gap | TPR gap | FPR gap | Precision gap | ECE gap |")
    sections.append("|---|---|---|---|---|---|")
    for axis, gaps in audit.gaps.items():
        sections.append(
            f"| `{axis}` | {gaps['dp_gap']:.4f} | {gaps['tpr_gap']:.4f} | "
            f"{gaps['fpr_gap']:.4f} | {gaps['precision_gap']:.4f} | {gaps['ece_gap']:.4f} |"
        )

    for axis, rows in audit.axes.items():
        sections.append(f"\n## Axis: `{axis}`\n")
        # Sort by group size desc, then take top 15 for readability
        rows_sorted = sorted(rows, key=lambda r: r.n, reverse=True)[:15]
        sections.append("| group | n | sel rate | TPR | FPR | precision | ECE |")
        sections.append("|---|---:|---:|---:|---:|---:|---:|")
        for r in rows_sorted:
            sections.append(
                f"| `{str(r.group)[:30]}` | {r.n} | {r.selection_rate:.3f} | "
                f"{r.tpr:.3f} | {r.fpr:.3f} | {r.precision:.3f} | {r.ece:.3f} |"
            )

    sections.append("\n## Selbst et al. (2019) sociotechnical traps")
    sections.append("- The audit is reported with explicit value judgements rather than as portable claims.")
    sections.append("- Calibration-within-group is the *binding* constraint (PD-reporting weight under IRB).")
    sections.append("- Base-rate decompositions are published so reviewers can disagree on visible grounds.")
    sections.append("- Fairness claims are conditional on the deployment context (US 2019 funded loans only).")

    out_path.write_text("\n".join(sections), encoding="utf-8")
    return out_path
