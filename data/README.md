# `data/` — Datasets, Pipeline Outputs, and Analyses

This directory holds **all data** consumed and produced by the EMERALD-AI pipeline, plus the
governance artefacts emitted by every analysis stage. **Nothing in `data/raw/`, `data/interim/`,
or `data/processed/` is committed to git** — see the project [`.gitignore`](../.gitignore). Only
`data/governance/`, `.gitkeep` markers, and this README are tracked.

## Layout

```
data/
├── raw/         ← Original, immutable source data (the .xlsx).  GITIGNORED.
├── interim/     ← Intermediate transformations (after leakage audit, before encoding). GITIGNORED.
├── processed/   ← Modelling-ready feature frames + persisted preprocessors. GITIGNORED.
└── governance/  ← Datasheet + audit summaries + per-stage analysis reports. TRACKED.
```

---

## 1 · Primary dataset

The training corpus is the entire 2019 funded book of a US marketplace lender that originates
green-purpose financing for small and medium businesses (solar, EV fleets, energy-efficient
buildings, sustainable agriculture). The dataset was supplied under an academic-use-only research
agreement and is **not** redistributed in this repository.

| Property | Value |
|---|---|
| Name | 2019 All Funded Green Loan Dataset |
| Source file | `data/raw/All_Funded_2019_Green Loan.xlsx` |
| Shape | **14,135 rows × 166 columns** |
| Labelled rows | **14,022 (99.20 %)** — those with non-null `Deal Status` |
| Period | 1 Jan 2019 – 31 Dec 2019 (calendar-year cross-section) |
| Granularity | One row per funded loan transaction |
| Sensitivity | **Proprietary** — academic use only, redistribution prohibited |
| Class balance | **0.36 % delinquent** (50 default+behind / 14,022 labelled) — heavy minority class |

### How to obtain

The dataset is not redistributed. Place the raw file at:

```
data/raw/All_Funded_2019_Green Loan.xlsx
```

If you are an authorised collaborator, request it via the channel on the dissertation cover sheet.

### Label construction (proposal §5.2)

```
Y = 1  if Deal Status ∈ {paidOff, current}      → "creditworthy"
Y = 0  if Deal Status ∈ {default, behind}       → "delinquent"
NaN    otherwise  (113 rows; excluded from the labelled set)
```

Mapping `current` to the positive class introduces right-censoring bias (some currently-paying
loans may yet default). The sensitivity analysis described in proposal §5.2 and tracked in
[`../research/literature/gaps.md`](../research/literature/gaps.md) entry **M1** quantifies the
exposure.

---

## 2 · Feature categories and the leakage audit (proposal §5.3)

Every one of the 166 columns is classified into exactly one of six categories. The classification
is the canonical data-governance decision: training on a forbidden column would yield a
near-perfect classifier that has already seen the outcome.

| Category | Count | Permitted as feature? |
|---|---:|:---:|
| Pre-funding applicant attributes | 23 | ✓ |
| Pre-funding loan-offer attributes | 15 | ✓ |
| Structural metadata | 9 | ✓ |
| Deal-progression timestamps | 43 | ✓ (with care — see §5.5) |
| Post-funding observed outcomes | 28 | **✗** defines Y |
| Administrative / staff-routing / free-text | 48 | **✗** |
| **Total** | **166** | **90 permitted · 76 forbidden** |

The audit script (`src/emerald_ai/data/leakage_audit.py`) emits the canonical
`feature_catalogue.yaml`, the human-readable `feature_audit_summary.md`, and the Gebru et al.
(2021) datasheet — all under `data/governance/`.

---

## 3 · What we have analysed

Every analysis stage below is implemented as a CLI subcommand of `emerald_ai`, runs on the same
labelled 14,022-row frame, and emits a markdown governance report under `data/governance/`. The
React web app surfaces the same content in plain English at the **🗄️ Data & Analyses** view.

### 3.1 Exploratory data analysis (proposal §5.4)

Four sub-layers over the 90 permitted features:

1. **Univariate distributions** — mean / std / skewness / kurtosis + 1/25/50/75/99 percentile spine
   for the 36 numeric columns; top level, frequency, and Shannon entropy for the 54 categoricals.
2. **Bivariate association with Y** — Pearson, Spearman, and mutual information (in nats).
3. **Segment-conditional default rates** — Wilson 95 % CIs, small-N flagging.
4. **Quarterly distribution drift** — Population Stability Index against Q1 2019 reference.

**Findings.**
- **Industry risk gradient.** `firearms` 9.09 % delinquent (n=11, small-N flagged); the rest
  span 0.08 %–1.35 % — a ~17× range. `retail` is the safest sizeable industry; `manufacturing`
  the riskiest.
- **State cluster.** WV / AR / CT / IN / SC at 1.43 %–2.08 % delinquent — ~4–6× the base rate.
- **Material temporal drift.** Quarterly PSI vs Q1 of 13–14 on `Lender Identifier`, 10–12 on
  `Published`, 8–9 on `Attempted`/`Assigned`. `Start Month` and `Start Annual Day` show
  PSI ≈ 16 by construction (pure-time columns) and are dropped at preprocessing.
- **Heavy skew.** Most numerics have skewness > 3 (Amount Sought ≈ 109; Payment Amount ≈ 69),
  motivating tree-based learners + StandardScaler.

→ Re-run: `python -m emerald_ai eda` · Artefact: `data/governance/eda_report.md`.

### 3.2 Preprocessing pipeline (proposal §5.5)

A single `ColumnTransformer` shared across every downstream model so all family-comparison results
are on identical feature representations:

1. **Drop list** — 8 columns over the 40 % missingness threshold (`Term`, `APR`, `Factor`, plus the
   five 100 %-missing-but-permitted fields), and 2 EDA-flagged time-leaking columns
   (`Start Month`, `Start Annual Day`).
2. **Missing-data treatment** — numerics: median imputation + per-feature missing-indicator;
   categoricals: explicit `__missing__` level before encoding.
3. **Encoding** — low-cardinality (≤10 levels) → OneHotEncoder; high-cardinality (`Industry`,
   `Borrower State`, `Lender`, `Loan Purpose`, `Prod Type`, `Product`, `Borrower City`) →
   TargetEncoder with internal cross-fitting.
4. **Scaling** — StandardScaler on all surviving numerics.

**Shape change.** 90 permitted input columns → **90 processed features** on 14,022 labelled
rows. 35 raw datetime columns deferred to §5.6 feature engineering.

→ Re-run: `python -m emerald_ai preprocess` · Artefact: `data/governance/preprocess_report.md`.

### 3.3 Feature selection (proposal §5.6)

Two-stage selection:

- **Stage 1** — Mutual-information filter, drop bottom decile: **90 → 71**.
- **Stage 2** — Bootstrap-stability wrapper over Random-Forest MDI, 10 stratified rounds,
  selection-frequency threshold 60 %: **71 → 20**.

**Survivors at ≥60 % frequency.** Credit Score, Revenue, Payback, Payment Amount, Amount Funded,
# Offers Received, Closed Max Term, Lender, Prod Rank, Average Monthly Sales, Borrower State,
Commission, Is Lender Renewal, Max Offer Received $, Points, Payment Frequency (weekly), Prod Id,
Prod Type, Product, missing-indicator on Payment Amount.

→ Re-run: `python -m emerald_ai select` · Artefact: `data/governance/selection_report.md`.

### 3.4 Class-imbalance harness (proposal §5.7)

Three strategies compared under stratified 5-fold CV on a Logistic-Regression baseline; joint
score = PR-AUC × (1 − within-minority ECE):

| Strategy | Minority PR-AUC | Within-minority ECE | Joint score |
|---|---|---|---:|
| `no_resample` | 0.053 ± 0.024 | 0.973 ± 0.008 | 0.001 |
| `class_weighted` | 0.060 ± 0.028 | 0.313 ± 0.147 | 0.041 |
| **`smote` ✓** | **0.086 ± 0.047** | 0.321 ± 0.162 | **0.058** |

**Reading.** SMOTE narrowly wins, but all three strategies leave the minority Expected Calibration
Error ≈ 0.32 — resampling alone does **not** solve calibration at 0.36 % prevalence. That is the
empirical motivation for the §5.10 conformal + post-hoc calibration layer.

→ Re-run: `python -m emerald_ai imbalance` · Artefact: `data/governance/imbalance_report.md`.

### 3.5 Model training and comparison (proposal §5.8 + §5.9)

Five classifier families competed under nested CV (5 outer × 3 inner folds, 12 RandomizedSearch
candidates per family-fold). Primary metric PR-AUC against the minority class; ROC-AUC,
within-minority ECE, and recall@top-decile are co-headline per §5.13.

| Family | PR-AUC | ROC-AUC | Recall@top-decile |
|---|---|---|---|
| `lr_l1` | 0.032 ± 0.011 | 0.902 ± 0.047 | 0.70 ± 0.14 |
| `lr_l2` | 0.100 ± 0.052 | 0.923 ± 0.055 | 0.80 ± 0.17 |
| `svm_rbf` | 0.050 ± 0.025 | 0.900 ± 0.093 | 0.78 ± 0.23 |
| `rf` | 0.137 ± 0.069 | 0.945 ± 0.078 | 0.90 ± 0.12 |
| **`xgboost` ✓** | **0.185 ± 0.118** | **0.966 ± 0.034** | **0.92 ± 0.13** |

**Reading.** XGBoost tops the league on every headline metric. PR-AUC ≈ 0.19 is ~52× the
random-baseline at 0.36 % prevalence; recall@top-decile = 0.92 means that reviewing only the top
10 % most-risky catches 92 % of actual defaulters. LightGBM / CatBoost gated on optional deps;
MLP / FT-Transformer deferred to v0.5 (torch dependency).

→ Re-run: `python -m emerald_ai train` · Artefact: `data/governance/training_report.md`.

### 3.6 Calibration and conformal uncertainty (proposal §5.10)

Platt, isotonic, and temperature scaling compete on a dedicated calibration split; the chosen
calibrator is wrapped by a **split-conformal predictor** for distribution-free finite-sample
marginal coverage. The v0.4.1 framing is structural: marginal coverage is the headline guarantee;
**Mondrian (class-conditional) coverage** is reported as a diagnostic with bootstrap CIs;
interval width is excluded from the primary metrics (small-N makes width unstable).

Persisted artefacts: `models/conformal_marginal.joblib`. Served by the FastAPI `/score` endpoint.

### 3.7 Explainability (proposal §5.11)

Three layers: global permutation importance, local coefficient/importance proxy, and a
nearest-feature greedy counterfactual.

**Top-3 globally important features.** Lender, Prod Rank, Closed Max Term — deal-context
dominates borrower-attribute signals. TreeSHAP / KernelSHAP / DiCE / Quantus are deferred (require
`shap` + `dice-ml`).

→ Re-run: `python -m emerald_ai explain` · Artefact: `data/governance/explain_report.md`.

### 3.8 Fairness audit (proposal §5.12)

Per protected proxy (Industry, Borrower State, business-size proxies): demographic-parity gap,
equalised-odds (TPR/FPR) gap, predictive-parity (precision) gap, calibration-within-group (ECE)
gap.

**Honest finding (v0.1).** At the hard-coded 0.5 threshold the model approves ~99.7 % of
applicants in every group, so DP/TPR gaps look tiny (0.01–0.08) — but for the wrong reason: the
classifier isn't separating anyone yet. The v0.4 patch introduced percentile-based risk bands
(bottom 5 % → high-risk, 5th–20th → watch) under which 100 % of actual defaulters land in
high-risk; the v0.5 patch re-runs the audit at those operating points and is the meaningful audit.

→ Re-run: `python -m emerald_ai audit` · Artefact: `data/governance/fairness_report.md`.

---

## 4 · Governance artefacts (tracked under `data/governance/`)

| File | Produced by | Purpose |
|---|---|---|
| `datasheet.md` | `python -m emerald_ai.data.leakage_audit` | Gebru et al. (2021) seven-section datasheet |
| `feature_catalogue.yaml` | same | Machine-readable column classifications |
| `feature_audit_summary.md` | same | Human-readable target-leakage audit summary |
| `eda_report.md` | `python -m emerald_ai eda` | §5.4 four-layer EDA |
| `preprocess_report.md` | `python -m emerald_ai preprocess` | §5.5 pipeline trace |
| `selection_report.md` | `python -m emerald_ai select` | §5.6 two-stage selection |
| `imbalance_report.md` | `python -m emerald_ai imbalance` | §5.7 strategy bake-off |
| `training_report.md` | `python -m emerald_ai train` | §5.8 + §5.9 nested-CV results |
| `explain_report.md` | `python -m emerald_ai explain` | §5.11 importances + counterfactuals |
| `fairness_report.md` | `python -m emerald_ai audit` | §5.12 per-axis gap audit |

The traceability table in the top-level [`../README.md`](../README.md) ties each empirical
finding above back to its proposal § and to its source module under `src/emerald_ai/`.

---

## 5 · Data ethics

- The dataset is de-identified by the providing institution prior to release.
- No personally identifying information enters analysis.
- All artefacts derived from the data are stored in encrypted university storage and destroyed at
  dissertation submission, per Warwick research ethics protocol and UK GDPR.
- Reject-inference bound: the dataset contains only **accepted** applicants. The trained model is
  therefore framed as conditional on the lender's prior accept-policy (see proposal §4.4, §5.2, §8).
