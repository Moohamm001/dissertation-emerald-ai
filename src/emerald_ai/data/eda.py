"""Exploratory Data Analysis on the 90 permitted features (proposal §5.4).

Four layers mirroring the proposal:
  1. Univariate    — distributional summaries (numeric + categorical entropy).
  2. Bivariate     — Pearson / Spearman / mutual information against Y.
  3. Segment       — conditional default rates by Industry / Borrower State / Tier
                     with Wilson-score 95% confidence intervals.
  4. Drift         — Population Stability Index per feature across quarters.

The leakage audit (`emerald_ai.data.leakage_audit`) gates which columns are
permitted; this module operates on the resulting permitted subset.

Output: `data/governance/eda_report.md` — companion to `datasheet.md`.

Run:
    python -m emerald_ai eda
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from emerald_ai.config import PATHS
from emerald_ai.data.leakage_audit import (
    COLUMN_CLASSIFICATION,
    PERMITTED_CATEGORIES,
    FeatureCategory,
)
from emerald_ai.data.load import LABEL_COL, load_labelled

GOVERNANCE_DIR = PATHS.root / "data" / "governance"
EDA_REPORT_PATH = GOVERNANCE_DIR / "eda_report.md"


# -----------------------------------------------------------------------------
# Column slicing
# -----------------------------------------------------------------------------
def permitted_columns(df: pd.DataFrame) -> list[str]:
    """Names of permitted-as-feature columns present in ``df``.

    Falls back to ``COLUMN_CLASSIFICATION`` rather than re-running the audit so
    EDA is fast and self-contained. Unclassified columns are excluded (treated
    as administrative per the audit's fail-closed default).
    """
    return [
        c
        for c in df.columns
        if c != LABEL_COL
        and COLUMN_CLASSIFICATION.get(c) in PERMITTED_CATEGORIES
    ]


def split_xy(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Return (X over permitted columns, Y) dropping unlabelled rows.

    Labels are kept as Int8 from ``load.label_creditworthiness``.
    """
    if LABEL_COL not in df.columns:
        raise KeyError(f"{LABEL_COL!r} missing — call load_labelled first")
    cols = permitted_columns(df)
    labelled = df[df[LABEL_COL].notna()].copy()
    return labelled[cols], labelled[LABEL_COL].astype("Int8")


# -----------------------------------------------------------------------------
# Layer 1 — univariate
# -----------------------------------------------------------------------------
@dataclass
class UnivariateRow:
    name: str
    dtype: str
    n: int
    missingness_pct: float
    n_unique: int
    # numeric-only
    mean: float | None
    std: float | None
    skew: float | None
    kurtosis: float | None
    p01: float | None
    p25: float | None
    p50: float | None
    p75: float | None
    p99: float | None
    # categorical-only
    top_value: object | None
    top_freq_pct: float | None
    shannon_entropy: float | None

    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in self.__dataclass_fields__}


def _shannon_entropy(series: pd.Series) -> float:
    """Bits of Shannon entropy on the value distribution (NaN-excluded)."""
    counts = series.value_counts(dropna=True)
    total = counts.sum()
    if total == 0:
        return 0.0
    p = counts / total
    return float(-(p * np.log2(p)).sum())


def univariate_summary(X: pd.DataFrame) -> pd.DataFrame:
    """Per-column univariate summary. Numeric and categorical columns each
    populate their own field block; the other block is left as ``None``.
    """
    rows: list[UnivariateRow] = []
    for col in X.columns:
        s = X[col]
        n = int(s.shape[0])
        miss = float(s.isna().mean() * 100)
        nunique = int(s.nunique(dropna=True))
        if pd.api.types.is_numeric_dtype(s):
            ss = s.dropna().astype(float)
            if ss.empty:
                rows.append(UnivariateRow(col, str(s.dtype), n, miss, nunique,
                                          None, None, None, None,
                                          None, None, None, None, None,
                                          None, None, None))
                continue
            q = ss.quantile([0.01, 0.25, 0.50, 0.75, 0.99])
            rows.append(UnivariateRow(
                name=col,
                dtype=str(s.dtype),
                n=n,
                missingness_pct=miss,
                n_unique=nunique,
                mean=float(ss.mean()),
                std=float(ss.std(ddof=1)) if ss.size > 1 else 0.0,
                skew=float(ss.skew()) if ss.size > 2 else None,
                kurtosis=float(ss.kurt()) if ss.size > 3 else None,
                p01=float(q.iloc[0]),
                p25=float(q.iloc[1]),
                p50=float(q.iloc[2]),
                p75=float(q.iloc[3]),
                p99=float(q.iloc[4]),
                top_value=None,
                top_freq_pct=None,
                shannon_entropy=None,
            ))
        else:
            ss = s.dropna()
            if ss.empty:
                rows.append(UnivariateRow(col, str(s.dtype), n, miss, nunique,
                                          None, None, None, None,
                                          None, None, None, None, None,
                                          None, None, None))
                continue
            counts = ss.value_counts()
            top = counts.index[0]
            top_pct = float(counts.iloc[0] / counts.sum() * 100)
            rows.append(UnivariateRow(
                name=col, dtype=str(s.dtype), n=n,
                missingness_pct=miss, n_unique=nunique,
                mean=None, std=None, skew=None, kurtosis=None,
                p01=None, p25=None, p50=None, p75=None, p99=None,
                top_value=top, top_freq_pct=top_pct,
                shannon_entropy=_shannon_entropy(ss),
            ))
    return pd.DataFrame([r.to_dict() for r in rows])


# -----------------------------------------------------------------------------
# Layer 2 — bivariate against Y
# -----------------------------------------------------------------------------
def _mutual_information_binary(x: pd.Series, y: pd.Series, bins: int = 20) -> float:
    """Mutual information I(X;Y) in nats for a feature vs binary Y.

    Numeric x is binned at equal-frequency quantiles (with NaN as its own bin);
    categorical x uses raw levels (with NaN as its own bin).
    """
    if pd.api.types.is_numeric_dtype(x):
        xf = pd.qcut(x, q=bins, duplicates="drop", labels=False)
    else:
        xf = x.astype("category").cat.codes
    xf = pd.Series(xf, index=x.index).fillna(-1).astype(int)
    yi = y.astype(int)
    df = pd.DataFrame({"x": xf, "y": yi}).dropna()
    if df.empty:
        return 0.0
    joint = pd.crosstab(df["x"], df["y"]).to_numpy().astype(float)
    total = joint.sum()
    if total == 0:
        return 0.0
    pxy = joint / total
    px = pxy.sum(axis=1, keepdims=True)
    py = pxy.sum(axis=0, keepdims=True)
    denom = px @ py
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(pxy > 0, np.log(pxy / np.where(denom > 0, denom, 1)), 0.0)
    return float((pxy * ratio).sum())


def bivariate_against_y(X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
    """Pearson / Spearman / MI of every column against Y. Non-numeric columns
    receive ``NaN`` for the correlation columns and a valid MI score.
    """
    rows: list[dict] = []
    yf = y.astype(float)
    for col in X.columns:
        s = X[col]
        if pd.api.types.is_numeric_dtype(s):
            sf = s.astype(float)
            mask = sf.notna() & yf.notna()
            if mask.sum() < 3:
                pearson = spearman = float("nan")
            else:
                pearson = float(sf[mask].corr(yf[mask], method="pearson"))
                spearman = float(sf[mask].corr(yf[mask], method="spearman"))
        else:
            pearson = spearman = float("nan")
        mi = _mutual_information_binary(s, y.dropna().astype(int).reindex(s.index).fillna(method=None) if False else y.fillna(0).astype(int))
        rows.append({
            "name": col,
            "dtype": str(s.dtype),
            "pearson_vs_y": pearson,
            "spearman_vs_y": spearman,
            "mi_nats_vs_y": float(mi),
        })
    return pd.DataFrame(rows)


# -----------------------------------------------------------------------------
# Layer 3 — segment-level conditional default rates
# -----------------------------------------------------------------------------
def _wilson_ci(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson-score 95% CI on a binomial proportion. Tight at small N — the
    right choice for the 0.36% prevalence regime (proposal §4.4)."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denom
    return (max(0.0, centre - margin), min(1.0, centre + margin))


def conditional_default_rates(
    X: pd.DataFrame, y: pd.Series, by: str, min_n: int = 30
) -> pd.DataFrame:
    """Per-segment delinquent rate (Y=0) with Wilson 95% CI.

    Segments with fewer than ``min_n`` observations are reported but flagged
    via ``small_n``. Y=0 is the delinquent class in proposal §5.2.
    """
    if by not in X.columns:
        raise KeyError(f"Segment column {by!r} not in X")
    df = pd.DataFrame({"seg": X[by], "y": y.astype(int)}).dropna(subset=["seg"])
    out: list[dict] = []
    for seg, grp in df.groupby("seg", dropna=True):
        n = int(grp.shape[0])
        delinquent = int((grp["y"] == 0).sum())
        rate = delinquent / n if n else float("nan")
        lo, hi = _wilson_ci(delinquent, n)
        out.append({
            "segment": seg,
            "n": n,
            "delinquent": delinquent,
            "delinquent_rate": rate,
            "ci95_lo": lo,
            "ci95_hi": hi,
            "small_n": n < min_n,
        })
    return pd.DataFrame(out).sort_values("delinquent_rate", ascending=False).reset_index(drop=True)


# -----------------------------------------------------------------------------
# Layer 4 — drift (Population Stability Index)
# -----------------------------------------------------------------------------
def psi(
    reference: pd.Series, current: pd.Series, bins: int = 10, smooth: float = 1e-4
) -> float:
    """Population Stability Index between two distributions of the same feature.

    For numeric series, bins are determined by reference quantiles (with edge
    snapping to ±inf so out-of-range ``current`` values still bin). For
    non-numeric series, bins are the union of observed categories.

    Conventional reading (proposal §5.4 calls this out as the drift signal):
        PSI < 0.10  → stable
        PSI < 0.25  → moderate shift
        PSI ≥ 0.25  → material shift (re-train / re-calibrate)
    """
    ref = reference.dropna()
    cur = current.dropna()
    if ref.empty or cur.empty:
        return float("nan")

    if pd.api.types.is_numeric_dtype(reference):
        edges = ref.quantile(np.linspace(0, 1, bins + 1)).unique()
        if edges.size < 2:
            return 0.0
        edges = np.concatenate(([-np.inf], edges[1:-1], [np.inf]))
        ref_counts, _ = np.histogram(ref.astype(float), bins=edges)
        cur_counts, _ = np.histogram(cur.astype(float), bins=edges)
    else:
        cats = pd.Index(ref.unique()).union(cur.unique())
        ref_counts = np.array([(ref == c).sum() for c in cats], dtype=float)
        cur_counts = np.array([(cur == c).sum() for c in cats], dtype=float)

    ref_p = ref_counts / max(ref_counts.sum(), 1)
    cur_p = cur_counts / max(cur_counts.sum(), 1)
    ref_p = ref_p + smooth
    cur_p = cur_p + smooth
    return float(((cur_p - ref_p) * np.log(cur_p / ref_p)).sum())


def psi_temporal(
    X: pd.DataFrame, time_col: str = "Start", reference_period: int = 1
) -> pd.DataFrame:
    """PSI per feature, computed for each quarter against the reference quarter.

    Splits rows by quarter of ``time_col`` (parsed as datetime). Returns a long-
    format DataFrame indexed by (feature, period) so plots / tables can pivot.
    """
    if time_col not in X.columns:
        raise KeyError(f"Time column {time_col!r} not in X")
    t = pd.to_datetime(X[time_col], errors="coerce")
    quarter = t.dt.quarter
    rows: list[dict] = []
    feature_cols = [c for c in X.columns if c != time_col]
    ref_mask = quarter == reference_period
    if not ref_mask.any():
        raise ValueError(f"Reference quarter Q{reference_period} has no rows")
    for col in feature_cols:
        ref = X.loc[ref_mask, col]
        for q in sorted([int(v) for v in quarter.dropna().unique()]):
            if q == reference_period:
                continue
            cur = X.loc[quarter == q, col]
            rows.append({
                "feature": col,
                "period": f"Q{q}",
                "psi_vs_Q{0}".format(reference_period): psi(ref, cur),
                "n_ref": int(ref_mask.sum()),
                "n_cur": int((quarter == q).sum()),
            })
    return pd.DataFrame(rows)


# -----------------------------------------------------------------------------
# Report writer
# -----------------------------------------------------------------------------
def _fmt(x, decimals: int = 3) -> str:
    if x is None:
        return "—"
    if isinstance(x, float):
        if math.isnan(x):
            return "—"
        return f"{x:.{decimals}f}"
    return str(x)


def _emit_table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        return "_(no rows)_\n"
    sep = "|".join(["---"] * len(headers))
    lines = ["| " + " | ".join(headers) + " |", f"|{sep}|"]
    lines.extend("| " + " | ".join(r) + " |" for r in rows)
    return "\n".join(lines) + "\n"


def write_report(
    *,
    univ: pd.DataFrame,
    biv: pd.DataFrame,
    segments: dict[str, pd.DataFrame],
    drift: pd.DataFrame | None,
    out_path: Path = EDA_REPORT_PATH,
) -> Path:
    """Emit data/governance/eda_report.md."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    today = pd.Timestamp.utcnow().date().isoformat()

    body: list[str] = []
    body.append(f"# EDA Report — 2019 All Funded Green Loan dataset\n")
    body.append(
        "_Companion to `datasheet.md` and `feature_catalogue.yaml`. Operates on the "
        "90 permitted features after the proposal §5.3 leakage audit; rows with "
        "missing labels (113 of 14,135) are excluded._\n"
    )
    body.append(f"Version: 0.1 · Generated: {today}\n")

    # --- 1. Univariate ----------------------------------------------------
    body.append("\n## 1. Univariate distributions\n")
    body.append(
        "Numeric columns report mean / std / skewness / kurtosis and the 1/25/50/75/99 "
        "percentile spine. Categorical columns report the top level, its frequency, and "
        "Shannon entropy of the value distribution (a high-entropy categorical is more "
        "informative than a degenerate one)._\n"
    )
    num = univ[univ["mean"].notna()].copy()
    cat = univ[univ["mean"].isna()].copy()
    body.append(f"_{len(num)} numeric features, {len(cat)} categorical features._\n")

    body.append("\n### 1.1 Numeric features (top 20 by absolute skewness)\n")
    if not num.empty:
        num["abs_skew"] = num["skew"].abs()
        top_num = num.sort_values("abs_skew", ascending=False).head(20)
        rows = [[
            r["name"], _fmt(r["missingness_pct"], 1), _fmt(r["mean"]),
            _fmt(r["std"]), _fmt(r["skew"]), _fmt(r["kurtosis"]),
            _fmt(r["p01"]), _fmt(r["p50"]), _fmt(r["p99"]),
        ] for _, r in top_num.iterrows()]
        body.append(_emit_table(
            ["feature", "miss%", "mean", "std", "skew", "kurt", "p01", "p50", "p99"], rows))

    body.append("\n### 1.2 Categorical features (top 20 by entropy)\n")
    if not cat.empty:
        top_cat = cat.sort_values("shannon_entropy", ascending=False).head(20)
        rows = [[
            r["name"], _fmt(r["missingness_pct"], 1), _fmt(r["n_unique"]),
            str(r["top_value"])[:40], _fmt(r["top_freq_pct"], 1), _fmt(r["shannon_entropy"]),
        ] for _, r in top_cat.iterrows()]
        body.append(_emit_table(
            ["feature", "miss%", "n_unique", "top_value", "top_freq%", "entropy_bits"], rows))

    # --- 2. Bivariate -----------------------------------------------------
    body.append("\n## 2. Bivariate association with Y\n")
    body.append(
        "_Mutual information is reported in nats; Pearson / Spearman are defined for "
        "numeric features only. Sorted by MI to surface the highest-signal features "
        "regardless of monotonicity._\n"
    )
    biv_sorted = biv.sort_values("mi_nats_vs_y", ascending=False).head(25)
    rows = [[
        r["name"], r["dtype"], _fmt(r["pearson_vs_y"]),
        _fmt(r["spearman_vs_y"]), _fmt(r["mi_nats_vs_y"], 4),
    ] for _, r in biv_sorted.iterrows()]
    body.append(_emit_table(
        ["feature", "dtype", "Pearson(Y)", "Spearman(Y)", "MI(Y) [nats]"], rows))

    # --- 3. Segment-level rates -------------------------------------------
    body.append("\n## 3. Conditional delinquent rates by segment\n")
    body.append(
        "_Y=0 = delinquent (default ∪ behind). Wilson 95% CIs widen sharply on segments "
        "with few observations — these are flagged. The underlying base rate is 0.36% "
        "(50 of 14,022)._\n"
    )
    for seg_name, seg_df in segments.items():
        body.append(f"\n### 3.{list(segments).index(seg_name)+1} By `{seg_name}`\n")
        top = seg_df.head(15)
        rows = [[
            str(r["segment"])[:30], str(r["n"]), str(r["delinquent"]),
            _fmt(r["delinquent_rate"] * 100, 2),
            f"[{_fmt(r['ci95_lo']*100, 2)}, {_fmt(r['ci95_hi']*100, 2)}]",
            "small-N" if r["small_n"] else "",
        ] for _, r in top.iterrows()]
        body.append(_emit_table(
            ["segment", "n", "delinquent", "rate %", "95% CI %", "flag"], rows))

    # --- 4. Drift ---------------------------------------------------------
    body.append("\n## 4. Distribution-shift diagnostics (quarterly PSI)\n")
    if drift is None or drift.empty:
        body.append("_(PSI not computed — see `psi_temporal()` for the entrypoint.)_\n")
    else:
        body.append(
            "_PSI per feature, computed against Q1 2019 as the reference. Conventional "
            "thresholds: <0.10 stable; 0.10–0.25 moderate shift; ≥0.25 material._\n"
        )
        psi_col = next((c for c in drift.columns if c.startswith("psi_vs_Q")), None)
        if psi_col:
            top = drift.sort_values(psi_col, ascending=False).head(20)
            rows = [[
                r["feature"], r["period"], _fmt(r[psi_col], 3),
                str(r["n_ref"]), str(r["n_cur"]),
            ] for _, r in top.iterrows()]
            body.append(_emit_table(
                ["feature", "period", psi_col, "n_ref", "n_cur"], rows))

    out_path.write_text("\n".join(body), encoding="utf-8")
    return out_path


# -----------------------------------------------------------------------------
# Orchestrator
# -----------------------------------------------------------------------------
def run_eda(
    path: Path | None = None,
    *,
    segment_columns: tuple[str, ...] = ("Industry", "Borrower State"),
    drift_time_col: str = "Start",
    out_path: Path = EDA_REPORT_PATH,
) -> Path:
    """End-to-end EDA. Loads the labelled dataset, runs every layer that has
    the required inputs, and emits the markdown report.

    Returns the path of the emitted report.
    """
    df = load_labelled(path)
    X, y = split_xy(df)

    univ = univariate_summary(X)
    biv = bivariate_against_y(X, y)
    segments: dict[str, pd.DataFrame] = {}
    for seg in segment_columns:
        if seg in X.columns:
            segments[seg] = conditional_default_rates(X, y, by=seg)
    drift: pd.DataFrame | None = None
    if drift_time_col in X.columns:
        try:
            drift = psi_temporal(X, time_col=drift_time_col)
        except Exception as exc:  # pragma: no cover — drift is best-effort
            print(f"[eda] WARNING: drift skipped — {exc}")

    return write_report(univ=univ, biv=biv, segments=segments, drift=drift, out_path=out_path)


def main() -> None:  # pragma: no cover
    out = run_eda()
    print(f"OK: {out}")


if __name__ == "__main__":  # pragma: no cover
    main()
