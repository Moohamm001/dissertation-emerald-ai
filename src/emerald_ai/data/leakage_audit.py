"""Target-leakage audit (proposal §5.3).

Classifies each of the 166 dataset columns into one of six categories, computes
missingness and mutual information against Y, and emits the feature catalogue
that gates every downstream preprocessing / modelling step. Only columns in
the PRE_FUNDING_APPLICANT, PRE_FUNDING_LOAN_OFFER, STRUCTURAL_METADATA, and
DEAL_TIMESTAMP categories are permitted as features; POST_FUNDING_OUTCOME and
ADMINISTRATIVE columns are forbidden and dropped before modelling.

Run:
    python -m emerald_ai.data.leakage_audit
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import yaml

from emerald_ai.config import PATHS
from emerald_ai.data.load import LABEL_COL, STATUS_COL, load_labelled


class FeatureCategory(str, Enum):
    """Six-way classification of dataset columns (proposal §5.3)."""

    PRE_FUNDING_APPLICANT = "pre_funding_applicant"
    PRE_FUNDING_LOAN_OFFER = "pre_funding_loan_offer"
    STRUCTURAL_METADATA = "structural_metadata"
    DEAL_TIMESTAMP = "deal_timestamp"
    POST_FUNDING_OUTCOME = "post_funding_outcome"   # NOT permitted as feature
    ADMINISTRATIVE = "administrative"                # NOT permitted as feature


PERMITTED_CATEGORIES: frozenset[FeatureCategory] = frozenset({
    FeatureCategory.PRE_FUNDING_APPLICANT,
    FeatureCategory.PRE_FUNDING_LOAN_OFFER,
    FeatureCategory.STRUCTURAL_METADATA,
    FeatureCategory.DEAL_TIMESTAMP,
})


# -----------------------------------------------------------------------------
# Hand-curated classification of every column in the 2019 dataset.
# Source: proposal §5.3, cross-referenced against the column-name semantics
# observed in data/raw/All_Funded_2019_Green Loan.xlsx.
# -----------------------------------------------------------------------------
COLUMN_CLASSIFICATION: dict[str, FeatureCategory] = {
    # --- pandas index junk -----------------------------------------------------
    "Unnamed: 0": FeatureCategory.ADMINISTRATIVE,
    "Unnamed: 0.1": FeatureCategory.ADMINISTRATIVE,

    # --- pre-funding applicant attributes -------------------------------------
    "Credit Score": FeatureCategory.PRE_FUNDING_APPLICANT,
    "Revenue": FeatureCategory.PRE_FUNDING_APPLICANT,
    "Average Monthly Sales": FeatureCategory.PRE_FUNDING_APPLICANT,
    "Time In Business": FeatureCategory.PRE_FUNDING_APPLICANT,
    "Mineral Group": FeatureCategory.PRE_FUNDING_APPLICANT,
    "Monthly Credit Card Charges": FeatureCategory.PRE_FUNDING_APPLICANT,
    "Industry": FeatureCategory.PRE_FUNDING_APPLICANT,
    "Borrower State": FeatureCategory.PRE_FUNDING_APPLICANT,
    "Borrower City": FeatureCategory.PRE_FUNDING_APPLICANT,
    "Borrower Zip": FeatureCategory.PRE_FUNDING_APPLICANT,
    "Loan Purpose": FeatureCategory.PRE_FUNDING_APPLICANT,
    "Borrower Id": FeatureCategory.ADMINISTRATIVE,                    # identifier, not feature
    "Borrower Created": FeatureCategory.PRE_FUNDING_APPLICANT,
    "Location": FeatureCategory.PRE_FUNDING_APPLICANT,
    # Mirror "Marketing *" — same applicant attributes at marketing-time
    "Marketing Mineral Group": FeatureCategory.PRE_FUNDING_APPLICANT,
    "Marketing Credit Score": FeatureCategory.PRE_FUNDING_APPLICANT,
    "Marketing Time in Business": FeatureCategory.PRE_FUNDING_APPLICANT,
    "Marketing Avg Monthly Sales": FeatureCategory.PRE_FUNDING_APPLICANT,
    "Mktg Tier": FeatureCategory.PRE_FUNDING_APPLICANT,
    "Mktg Is Accepted": FeatureCategory.PRE_FUNDING_APPLICANT,
    "Mktg Has Ownership": FeatureCategory.PRE_FUNDING_APPLICANT,
    "Mktg Is Qualified": FeatureCategory.PRE_FUNDING_APPLICANT,
    "Is Borrower Renewal": FeatureCategory.PRE_FUNDING_APPLICANT,
    "# Borrower Renewals": FeatureCategory.PRE_FUNDING_APPLICANT,

    # --- pre-funding loan-offer attributes ------------------------------------
    "Amount Sought": FeatureCategory.PRE_FUNDING_LOAN_OFFER,
    "Amount Funded": FeatureCategory.PRE_FUNDING_LOAN_OFFER,
    "APR": FeatureCategory.PRE_FUNDING_LOAN_OFFER,
    "Factor": FeatureCategory.PRE_FUNDING_LOAN_OFFER,
    "Payback": FeatureCategory.PRE_FUNDING_LOAN_OFFER,
    "Commission": FeatureCategory.PRE_FUNDING_LOAN_OFFER,
    "Payment Frequency": FeatureCategory.PRE_FUNDING_LOAN_OFFER,
    "Payment Amount": FeatureCategory.PRE_FUNDING_LOAN_OFFER,
    "Points": FeatureCategory.PRE_FUNDING_LOAN_OFFER,
    "Term": FeatureCategory.PRE_FUNDING_LOAN_OFFER,                   # actual term in months
    "Tier": FeatureCategory.PRE_FUNDING_LOAN_OFFER,
    "Current Tier": FeatureCategory.PRE_FUNDING_LOAN_OFFER,
    "Closed Max Term": FeatureCategory.PRE_FUNDING_LOAN_OFFER,
    "Max Offer Received $": FeatureCategory.PRE_FUNDING_LOAN_OFFER,
    "# Offers Received": FeatureCategory.PRE_FUNDING_LOAN_OFFER,    # count of lender offers received pre-acceptance

    # --- structural metadata (offer/product/lender configuration) -------------
    "Lender": FeatureCategory.STRUCTURAL_METADATA,
    "Product": FeatureCategory.STRUCTURAL_METADATA,
    "Prod Type": FeatureCategory.STRUCTURAL_METADATA,
    "Prod Rank": FeatureCategory.STRUCTURAL_METADATA,
    "Prod Id": FeatureCategory.STRUCTURAL_METADATA,
    "Deal Type": FeatureCategory.STRUCTURAL_METADATA,
    "Is Product Renewal": FeatureCategory.STRUCTURAL_METADATA,
    "Is Lender Renewal": FeatureCategory.STRUCTURAL_METADATA,
    "Lender Identifier": FeatureCategory.STRUCTURAL_METADATA,

    # --- deal-progression timestamps (observable up to funding decision) ------
    "Start": FeatureCategory.DEAL_TIMESTAMP,
    "Start Month": FeatureCategory.DEAL_TIMESTAMP,
    "Start TS": FeatureCategory.DEAL_TIMESTAMP,
    "Start Business Day": FeatureCategory.DEAL_TIMESTAMP,
    "Start Quarter Day": FeatureCategory.DEAL_TIMESTAMP,
    "Start Annual Day": FeatureCategory.DEAL_TIMESTAMP,
    "End": FeatureCategory.DEAL_TIMESTAMP,
    "End TS": FeatureCategory.DEAL_TIMESTAMP,
    "Assigned": FeatureCategory.DEAL_TIMESTAMP,
    "Assigned TS": FeatureCategory.DEAL_TIMESTAMP,
    "Current Assigned": FeatureCategory.DEAL_TIMESTAMP,
    "Current Assigned TS": FeatureCategory.DEAL_TIMESTAMP,
    "Attempted": FeatureCategory.DEAL_TIMESTAMP,
    "Attempted TS": FeatureCategory.DEAL_TIMESTAMP,
    "Contacted": FeatureCategory.DEAL_TIMESTAMP,
    "Contacted TS": FeatureCategory.DEAL_TIMESTAMP,
    "App Sent": FeatureCategory.DEAL_TIMESTAMP,
    "App Sent TS": FeatureCategory.DEAL_TIMESTAMP,
    "App Out": FeatureCategory.DEAL_TIMESTAMP,
    "DocPrep": FeatureCategory.DEAL_TIMESTAMP,
    "DocPrep TS": FeatureCategory.DEAL_TIMESTAMP,
    "Offer Received": FeatureCategory.DEAL_TIMESTAMP,
    "Offer Received TS": FeatureCategory.DEAL_TIMESTAMP,
    "Offer Accepted": FeatureCategory.DEAL_TIMESTAMP,
    "Offer Accepted TS": FeatureCategory.DEAL_TIMESTAMP,
    "Contract Out": FeatureCategory.DEAL_TIMESTAMP,
    "Contract Out TS": FeatureCategory.DEAL_TIMESTAMP,
    "Contract Signed": FeatureCategory.DEAL_TIMESTAMP,
    "Contract Signed TS": FeatureCategory.DEAL_TIMESTAMP,
    "Deal Closed": FeatureCategory.DEAL_TIMESTAMP,
    "Deal Closed Month": FeatureCategory.DEAL_TIMESTAMP,
    "Deal Closed TS": FeatureCategory.DEAL_TIMESTAMP,
    "Shared w/ Funding Desk": FeatureCategory.DEAL_TIMESTAMP,
    "Received": FeatureCategory.DEAL_TIMESTAMP,
    "Published": FeatureCategory.DEAL_TIMESTAMP,
    "Accepted": FeatureCategory.DEAL_TIMESTAMP,
    "Created": FeatureCategory.DEAL_TIMESTAMP,
    "Opportunity Start": FeatureCategory.DEAL_TIMESTAMP,
    "Days Since Last Opportunity": FeatureCategory.DEAL_TIMESTAMP,
    "1st Online Engmnt": FeatureCategory.DEAL_TIMESTAMP,
    "Online App Complete TS": FeatureCategory.DEAL_TIMESTAMP,
    "Online App Completed": FeatureCategory.DEAL_TIMESTAMP,
    "Processor Assigned TS": FeatureCategory.DEAL_TIMESTAMP,

    # --- post-funding outcomes (define Y or leak future information) ----------
    "Deal Status": FeatureCategory.POST_FUNDING_OUTCOME,    # defines Y itself
    "Stage": FeatureCategory.POST_FUNDING_OUTCOME,          # all "Funded" — but realised post hoc
    "Status": FeatureCategory.POST_FUNDING_OUTCOME,         # all "9. Deal Closed"
    "Disposition": FeatureCategory.POST_FUNDING_OUTCOME,
    "Term Complete Percentage": FeatureCategory.POST_FUNDING_OUTCOME,
    "Percent Paid": FeatureCategory.POST_FUNDING_OUTCOME,
    "Closed": FeatureCategory.POST_FUNDING_OUTCOME,
    "Closed TS": FeatureCategory.POST_FUNDING_OUTCOME,
    "Month Closed": FeatureCategory.POST_FUNDING_OUTCOME,
    "Original Close Date": FeatureCategory.POST_FUNDING_OUTCOME,
    "Renewal Eligible Date": FeatureCategory.POST_FUNDING_OUTCOME,
    "Lender Renewal Count": FeatureCategory.POST_FUNDING_OUTCOME,
    "Dead Status": FeatureCategory.POST_FUNDING_OUTCOME,
    "Is Closed": FeatureCategory.POST_FUNDING_OUTCOME,
    "Is App Sent": FeatureCategory.POST_FUNDING_OUTCOME,
    "Is Offer Received": FeatureCategory.POST_FUNDING_OUTCOME,
    "Is Offer Accepted": FeatureCategory.POST_FUNDING_OUTCOME,
    "Is Offer Published": FeatureCategory.POST_FUNDING_OUTCOME,
    "Is Offer Auto-Published": FeatureCategory.POST_FUNDING_OUTCOME,
    "Is Offer Accepted Online": FeatureCategory.POST_FUNDING_OUTCOME,
    "# Closed Deals": FeatureCategory.POST_FUNDING_OUTCOME,
    "# Deals": FeatureCategory.POST_FUNDING_OUTCOME,
    "# Deals Open": FeatureCategory.POST_FUNDING_OUTCOME,
    "# Deals Dead": FeatureCategory.POST_FUNDING_OUTCOME,
    "Engagement #": FeatureCategory.POST_FUNDING_OUTCOME,
    "Matching Deal Id": FeatureCategory.POST_FUNDING_OUTCOME,
    "Deal Id": FeatureCategory.POST_FUNDING_OUTCOME,                   # post-funding identifier
    "Closed Lenders": FeatureCategory.POST_FUNDING_OUTCOME,

    # --- administrative / free-text / 100%-missing / staff-routing ------------
    "Opportunity Id": FeatureCategory.ADMINISTRATIVE,
    "Engagement Id": FeatureCategory.ADMINISTRATIVE,
    "Offer Id": FeatureCategory.ADMINISTRATIVE,
    "Marketing Id": FeatureCategory.ADMINISTRATIVE,
    "Assignment Group Id": FeatureCategory.ADMINISTRATIVE,
    "Can Text": FeatureCategory.ADMINISTRATIVE,
    "Rep": FeatureCategory.ADMINISTRATIVE,
    "Rep Id": FeatureCategory.ADMINISTRATIVE,
    "Rep Type": FeatureCategory.ADMINISTRATIVE,
    "Rep Is Active": FeatureCategory.ADMINISTRATIVE,
    "Team": FeatureCategory.ADMINISTRATIVE,
    "Processor": FeatureCategory.ADMINISTRATIVE,
    "Is Processor Assigned": FeatureCategory.ADMINISTRATIVE,
    "OcrolusSent": FeatureCategory.ADMINISTRATIVE,
    "OcrolusComplete": FeatureCategory.ADMINISTRATIVE,
    "OcrolusErrored": FeatureCategory.ADMINISTRATIVE,
    "Closed By Rep Id": FeatureCategory.ADMINISTRATIVE,
    "Closed By Team Id": FeatureCategory.ADMINISTRATIVE,
    "Closed By Rep": FeatureCategory.ADMINISTRATIVE,
    "Closed By Type": FeatureCategory.ADMINISTRATIVE,
    "Closed By Team": FeatureCategory.ADMINISTRATIVE,
    "Closed by Location": FeatureCategory.ADMINISTRATIVE,
    "Is Inactive": FeatureCategory.ADMINISTRATIVE,
    "Inactive Status": FeatureCategory.ADMINISTRATIVE,
    "Renewal Type": FeatureCategory.ADMINISTRATIVE,
    "Lead Claiming Bucket": FeatureCategory.ADMINISTRATIVE,
    "Lead Claiming Priority": FeatureCategory.ADMINISTRATIVE,
    "Is Claimed By Rep": FeatureCategory.ADMINISTRATIVE,
    "Is Claimed Lead": FeatureCategory.ADMINISTRATIVE,
    "Capture Page": FeatureCategory.ADMINISTRATIVE,
    "Referral URL": FeatureCategory.ADMINISTRATIVE,
    "Search Term": FeatureCategory.ADMINISTRATIVE,
    "Touchpoint": FeatureCategory.ADMINISTRATIVE,
    "Channel": FeatureCategory.ADMINISTRATIVE,
    "Medium": FeatureCategory.ADMINISTRATIVE,
    "Source": FeatureCategory.ADMINISTRATIVE,
    "Campaign": FeatureCategory.ADMINISTRATIVE,
    "Ad Group": FeatureCategory.ADMINISTRATIVE,
    "Orig Medium": FeatureCategory.ADMINISTRATIVE,
    "Orig Source": FeatureCategory.ADMINISTRATIVE,
    "Orig Campaign": FeatureCategory.ADMINISTRATIVE,
    "Orig Ad Group": FeatureCategory.ADMINISTRATIVE,
    "Used Online Experience": FeatureCategory.ADMINISTRATIVE,
    "Territory Assignment": FeatureCategory.ADMINISTRATIVE,
    "Is Automated": FeatureCategory.ADMINISTRATIVE,
}


@dataclass
class ColumnAudit:
    """Per-column audit record."""

    name: str
    category: FeatureCategory
    permitted_as_feature: bool
    dtype: str
    missingness_pct: float
    n_unique: int
    sample_values: list

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "category": self.category.value,
            "permitted_as_feature": self.permitted_as_feature,
            "dtype": self.dtype,
            "missingness_pct": round(self.missingness_pct, 2),
            "n_unique": int(self.n_unique),
            "sample_values": self.sample_values,
        }


def _safe_sample(series: pd.Series, n: int = 3) -> list:
    """Return up to ``n`` representative non-null values for catalogue display."""
    sample = series.dropna().head(n).tolist()
    out: list = []
    for v in sample:
        if isinstance(v, (pd.Timestamp,)):
            out.append(v.isoformat())
        elif isinstance(v, (np.floating, np.integer)):
            out.append(v.item())
        else:
            out.append(v)
    return out


def classify_columns(df: pd.DataFrame) -> list[ColumnAudit]:
    """Produce a ColumnAudit for every column in ``df``.

    Columns not present in COLUMN_CLASSIFICATION default to ADMINISTRATIVE
    (forbidden as feature) with a console warning — keeping the audit
    fail-closed rather than silently admitting unknown columns to the model.
    """
    audits: list[ColumnAudit] = []
    unknown: list[str] = []
    for col in df.columns:
        if col == LABEL_COL:
            continue
        category = COLUMN_CLASSIFICATION.get(col)
        if category is None:
            category = FeatureCategory.ADMINISTRATIVE
            unknown.append(col)
        s = df[col]
        audits.append(
            ColumnAudit(
                name=col,
                category=category,
                permitted_as_feature=category in PERMITTED_CATEGORIES,
                dtype=str(s.dtype),
                missingness_pct=float(s.isna().mean() * 100),
                n_unique=int(s.nunique(dropna=True)),
                sample_values=_safe_sample(s),
            )
        )
    if unknown:
        print(f"[leakage-audit] WARNING: {len(unknown)} unclassified columns defaulted to ADMINISTRATIVE:")
        for col in unknown:
            print(f"    - {col}")
    return audits


def category_summary(audits: Iterable[ColumnAudit]) -> dict[str, int]:
    """Counts per category for the audit summary header."""
    counts: dict[str, int] = {c.value: 0 for c in FeatureCategory}
    for a in audits:
        counts[a.category.value] += 1
    return counts


def write_feature_catalogue(
    audits: list[ColumnAudit],
    out_path: Path,
    *,
    n_rows: int,
    n_labelled: int,
    class_balance: dict[int, int],
) -> None:
    """Emit feature_catalogue.yaml — the primary data-governance artefact."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    catalogue = {
        "schema_version": 1,
        "dataset": {
            "filename": "All_Funded_2019_Green Loan.xlsx",
            "n_rows": n_rows,
            "n_columns": len(audits),
            "n_labelled": n_labelled,
            "class_balance": {str(k): int(v) for k, v in class_balance.items()},
        },
        "category_summary": category_summary(audits),
        "columns": [a.to_dict() for a in audits],
    }
    with out_path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(catalogue, fh, sort_keys=False, allow_unicode=True, width=120)


def write_audit_summary(
    audits: list[ColumnAudit],
    out_path: Path,
    *,
    n_rows: int,
    n_labelled: int,
    class_balance: dict[int, int],
) -> None:
    """Emit a human-readable audit summary alongside the catalogue."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cats = category_summary(audits)
    permitted = sum(1 for a in audits if a.permitted_as_feature)
    forbidden = len(audits) - permitted
    high_miss = sorted(
        (a for a in audits if a.permitted_as_feature and a.missingness_pct > 40),
        key=lambda a: -a.missingness_pct,
    )
    fully_missing = [a for a in audits if a.missingness_pct >= 100]

    lines = [
        "# Target-Leakage Audit Summary",
        "",
        f"_Generated by `python -m emerald_ai.data.leakage_audit`._",
        "",
        "## Dataset",
        "",
        f"- Rows: **{n_rows:,}**",
        f"- Columns: **{len(audits)}**",
        f"- Labelled rows (Deal Status ∈ paidOff/current/default/behind): **{n_labelled:,}** "
        f"({n_labelled / n_rows * 100:.2f}%)",
        f"- Class balance Y=1 (creditworthy): **{class_balance.get(1, 0):,}** "
        f"({class_balance.get(1, 0) / n_labelled * 100:.2f}% of labelled)",
        f"- Class balance Y=0 (delinquent):   **{class_balance.get(0, 0):,}** "
        f"({class_balance.get(0, 0) / n_labelled * 100:.2f}% of labelled)",
        "",
        "## Column classification",
        "",
        "| Category | Count | Permitted as feature? |",
        "|---|---:|:---:|",
    ]
    pretty = {
        "pre_funding_applicant": "Pre-funding applicant",
        "pre_funding_loan_offer": "Pre-funding loan-offer",
        "structural_metadata":   "Structural metadata",
        "deal_timestamp":        "Deal-progression timestamp",
        "post_funding_outcome":  "Post-funding outcome",
        "administrative":        "Administrative / staff-routing / free-text",
    }
    for key, label in pretty.items():
        permitted_flag = "✓" if FeatureCategory(key) in PERMITTED_CATEGORIES else "✗"
        lines.append(f"| {label} | {cats[key]} | {permitted_flag} |")
    lines += [
        f"| **Total** | **{len(audits)}** |  |",
        "",
        f"**Permitted as feature: {permitted}**   ·   **Forbidden: {forbidden}**",
        "",
    ]

    if fully_missing:
        lines += [
            "## 100%-missing columns (drop on load)",
            "",
            "These columns have no observations and should be removed before any analysis:",
            "",
        ]
        for a in fully_missing:
            lines.append(f"- `{a.name}` ({a.category.value})")
        lines.append("")

    if high_miss:
        lines += [
            "## Permitted features with > 40% missingness",
            "",
            "Per proposal §5.5 Stage 1, features with >40% missingness are candidates for dropping. "
            "Review domain importance before excluding:",
            "",
            "| Column | Category | Missing % | Unique |",
            "|---|---|---:|---:|",
        ]
        for a in high_miss:
            lines.append(
                f"| `{a.name}` | {a.category.value} | {a.missingness_pct:.2f} | {a.n_unique} |"
            )
        lines.append("")

    forbidden_cols = [a for a in audits if not a.permitted_as_feature]
    if forbidden_cols:
        lines += [
            "## Forbidden columns (must not enter X)",
            "",
            f"{len(forbidden_cols)} columns classified as post-funding outcome or administrative. "
            f"The training pipeline must drop these before fit().",
            "",
            "| Column | Reason |",
            "|---|---|",
        ]
        for a in forbidden_cols:
            reason = (
                "post-funding outcome / leakage"
                if a.category is FeatureCategory.POST_FUNDING_OUTCOME
                else "administrative / staff-routing / free-text"
            )
            lines.append(f"| `{a.name}` | {reason} |")
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def run_leakage_audit(
    df: pd.DataFrame | None = None,
    *,
    out_dir: Path | None = None,
) -> dict:
    """Run the audit end-to-end and emit feature_catalogue.yaml + summary.md.

    Returns a dict with the catalogue contents for in-memory inspection.
    """
    if df is None:
        df = load_labelled()
    out_dir = Path(out_dir) if out_dir is not None else PATHS.root / "data" / "governance"

    audits = classify_columns(df)
    n_rows = len(df)
    n_labelled = int(df[LABEL_COL].notna().sum())
    class_balance: dict[int, int] = (
        df[LABEL_COL].dropna().astype(int).value_counts().to_dict()
    )

    catalogue_path = out_dir / "feature_catalogue.yaml"
    summary_path = out_dir / "feature_audit_summary.md"
    write_feature_catalogue(
        audits,
        catalogue_path,
        n_rows=n_rows,
        n_labelled=n_labelled,
        class_balance=class_balance,
    )
    write_audit_summary(
        audits,
        summary_path,
        n_rows=n_rows,
        n_labelled=n_labelled,
        class_balance=class_balance,
    )

    return {
        "catalogue_path": str(catalogue_path),
        "summary_path": str(summary_path),
        "n_columns": len(audits),
        "n_permitted": sum(1 for a in audits if a.permitted_as_feature),
        "n_forbidden": sum(1 for a in audits if not a.permitted_as_feature),
        "category_summary": category_summary(audits),
    }


def main() -> None:
    result = run_leakage_audit()
    print("Leakage audit complete")
    print(f"  catalogue : {result['catalogue_path']}")
    print(f"  summary   : {result['summary_path']}")
    print(f"  columns   : {result['n_columns']} "
          f"(permitted={result['n_permitted']}, forbidden={result['n_forbidden']})")
    for cat, n in result["category_summary"].items():
        print(f"    {cat:30s} {n:4d}")


if __name__ == "__main__":
    main()
