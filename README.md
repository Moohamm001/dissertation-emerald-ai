# EMERALD-AI

> **Explainable, calibrated, audit-ready machine learning for green-loan credit scoring.**
> MSc Applied AI dissertation — University of Warwick · Python 3.11+ · MIT licence

EMERALD-AI is two things in one repository:

1. **A research framework** — an end-to-end ML pipeline that predicts green-loan repayment, explains every decision, says how confident it is, and audits itself for bias — trained on a real 2019 dataset of **14,135 green-loan transactions**.
2. **A working web app** — a FastAPI backend + React console a lending officer could actually use, not a notebook locked in a drawer.

---

## What problem does it solve? (plain English)

When a business applies for a **green loan** — money for solar panels, EV fleets, energy-efficient buildings — the lender must decide whether it will be repaid. Most lenders score these with formulas built for ordinary consumer credit, which (a) don't understand green cash-flows, (b) can't explain *why* an applicant was approved or declined, and (c) are increasingly **illegal** under the EU AI Act and the UK FCA Consumer Duty, both of which now require credit-scoring AI to be transparent, fair, and auditable.

EMERALD-AI is built to meet that bar:

| It… | How |
|---|---|
| **Predicts** repayment | Benchmarks modern tabular learners (Logistic Regression → XGBoost → LightGBM/CatBoost → deep tabular nets) under identical preprocessing |
| **Explains** every decision | SHAP feature attributions + counterfactual "what would change the outcome" recourse |
| **Knows its own confidence** | Post-hoc calibration + conformal prediction (distribution-free coverage guarantees) |
| **Audits itself for bias** | Demographic-parity / equalised-odds / calibration gaps across industry, region, business size |
| **Ships as a product** | REST API + React console: score one applicant, score a CSV, inspect the model, review fairness |

The explicit research gap it fills: *no published framework simultaneously delivers all of modern tabular benchmarking, calibration + conformal uncertainty, multi-method explainability, a disciplined fairness audit, and a deployable interface — on real green-loan data.*

---

## Project status

> **One table, the single source of truth.** ✅ runs end-to-end today · 🟡 partial/first-cut · ⬜ planned.

| Area | Status | Entry point |
|---|---|---|
| Research proposal (v0.4.1, ~9,600 w / 74 refs + 2,740 w condensed) | ✅ | `docs/proposal/` |
| Literature brain (243 papers, 34 fully analysed, citation graph, auto-discovery bot) | ✅ | `python -m emerald_ai research status` |
| Data load + leakage audit (166 cols → 90 permitted / 76 forbidden; 0.36% default rate) | ✅ | `python -m emerald_ai.data.leakage_audit` |
| EDA (univariate + bivariate MI + segment risk + quarterly drift) | ✅ | `python -m emerald_ai eda` |
| Preprocessing (drop → impute → encode → scale) | ✅ | `python -m emerald_ai preprocess` |
| Feature selection (MI filter + bootstrap-stability RF) | ✅ | `python -m emerald_ai select` |
| Class-imbalance harness (none / class-weighted / SMOTE) | ✅ | `python -m emerald_ai imbalance` |
| Model training (nested CV; LR · SVM · RF · XGBoost · LightGBM · CatBoost · MLP · FT-Transformer) | ✅ | `python -m emerald_ai train` |
| Hyperparameter optimisation (RandomizedSearch + Optuna TPE w/ pruning) | ✅ | `python -m emerald_ai train --tuner optuna` |
| Deep tabular models (MLP, FT-Transformer — sklearn-compatible torch) | ✅ | `--families mlp,ft_transformer` |
| Calibration + conformal (Platt/isotonic/temperature + split + Mondrian) | ✅ | persisted in `train` |
| Explainability (exact TreeSHAP + DiCE counterfactuals + faithfulness check) | ✅ | `python -m emerald_ai explain` |
| Fairness audit (DP / EO / PP / calibration-within-group, at risk-band thresholds) | ✅ | `python -m emerald_ai audit` |
| Backend API (11 endpoints) | ✅ | `python -m emerald_ai api` → `/docs` |
| React console (8 views) | ✅ | `cd apps/web && npm install && npm run dev` |
| Test suite | ✅ 125 tests | `python -m emerald_ai test` |
| Dissertation submission | ⬜ Week 16 | — |

**Best model today:** CatBoost (mean OOF PR-AUC ≈ 0.118, ~33× the 0.36%-prevalence random baseline), narrowly ahead of XGBoost (0.105) and Random Forest (0.103). The MLP and FT-Transformer trail the GBDTs on ranking but are far better-calibrated on the minority class — see `data/governance/training_report.md`.

---

## Quick start (3 commands)

```bash
pip install -e ".[ml,api,dev]"        # install (see docs/USAGE.md for the full extras matrix)
python -m emerald_ai research status  # prove the install: prints the literature-brain state
python -m emerald_ai --help           # see every command
```

> **Windows-friendly by design.** Every task is a cross-platform `python -m emerald_ai <command>`. There is no `make` requirement.

To run the full ML pipeline you need the proprietary dataset at `data/raw/All_Funded_2019_Green Loan.xlsx` (see [`data/README.md`](data/README.md)). Then:

```bash
python -m emerald_ai eda          # explore
python -m emerald_ai preprocess   # build features
python -m emerald_ai train        # train + calibrate + persist models/
python -m emerald_ai api          # serve at http://localhost:8000/docs
```

**Full command reference, troubleshooting, and workflows → [`docs/USAGE.md`](docs/USAGE.md).**

---

## Architecture

```
 data/raw/*.xlsx (proprietary, gitignored)
        │  14,135 × 166
        ▼
 ┌──────────────────────────────────────────────────────────┐
 │ src/emerald_ai/   (the pipeline)                           │
 │   data/      load + leakage audit                          │
 │   features/  preprocess + selection                        │
 │   training/  imbalance harness + nested CV + HPO           │
 │   models/    LR · SVM · RF · XGBoost · LGBM · CatBoost · DL │
 │   calibration/ Platt/isotonic/temp + conformal             │
 │   explain/   SHAP + counterfactuals                        │
 │   fairness/  DP/EO/PP/calibration-within-group audit       │
 │   eval/      PR-AUC · ECE · recall@decile · DeLong          │
 │   research/  literature-brain engine + OpenAlex bot        │
 │   cli.py     the single entrypoint                         │
 └───────────────┬───────────────────────────┬───────────────┘
                 │ persists models/*.joblib   │ writes data/governance/*.md
                 ▼                            ▼
        apps/api/  (FastAPI, 11 endpoints) ──▶ apps/web/ (React console, 8 views)

 research/literature/  ── the knowledge brain: 243 papers, citation graph,
                          themes, gaps, glossary; grown by an OpenAlex bot.
```

---

## Repository layout

```
README.md                  ← you are here
docs/
  USAGE.md                 ← full operations guide (install · commands · troubleshooting)
  proposal/                ← dissertation proposal (drafts + python-docx build script)
src/emerald_ai/            ← the Python package (pipeline + CLI + research engine)
apps/
  api/                     ← FastAPI backend
  web/                     ← React + Vite console
research/literature/       ← the knowledge brain (read BRAIN.md first)
data/                      ← dataset (gitignored) + data/governance/ analysis reports
tests/                     ← pytest suite (108 tests)
```

---

## Research design at a glance

- **Task:** binary creditworthiness — Y=1 (paid-off ∪ current) vs Y=0 (default ∪ behind); 0.36% default prevalence.
- **Models:** linear baselines (L1/L2 LR, RBF-SVM) → tree ensembles (RF, XGBoost, LightGBM, CatBoost) → deep tabular (MLP, FT-Transformer), all under identical preprocessing.
- **Validation:** nested stratified CV; PR-AUC, within-minority ECE, recall@top-decile as the primary metrics (raw accuracy is excluded — a constant predictor scores 99.6%).
- **Uncertainty:** post-hoc calibration + split-conformal prediction (marginal coverage as the headline, Mondrian class-conditional as a diagnostic).
- **Explainability:** SHAP (global + local) + counterfactual recourse, fidelity-checked.
- **Fairness:** DP / EO / PP / calibration-within-group across Industry, Borrower State, business-size proxies.
- **Regulatory framing:** EU AI Act (Reg. 2024/1689, Annex III) · FCA Consumer Duty (PS22/9) · EBA loan-origination guidelines.

Full methodology: [`docs/proposal/proposal_fourth_draft.docx`](docs/proposal/) (§5).

---

## The literature brain

`research/literature/` is not a static bibliography — it's a queryable, versioned knowledge base that grows itself:

- **243 papers** indexed (34 with full human-quality notes; the rest abstract-only, clearly flagged — never citation-safe until reviewed).
- An **autonomous discovery bot** crawls the OpenAlex citation graph (no API key, polite 1 req/s, idempotent) and writes new candidates into `auto_index.yaml`, kept strictly separate from the human-curated `index.yaml`.
- A **research engine** parses paper notes into a structured schema, builds the citation graph, and generates research questions from the gap log.

```bash
python -m emerald_ai research status                       # current counts
python -m emerald_ai research discover --query "explainable credit scoring"   # grow it
python -m emerald_ai research run                          # ingest new papers
```

Read [`research/literature/BRAIN.md`](research/literature/BRAIN.md) before writing about any paper. The three hard rules — never invent citations, always mark uncertainty, always track provenance — are enforced by the schema and the tests.

---

## Reproducibility & governance

Every analysis stage writes a dated markdown report to `data/governance/` (datasheet, EDA, preprocessing, selection, imbalance, training, calibration, explainability, fairness). These are the audit trail: each empirical finding traces to a proposal section, a code module, and a governance artefact. See [`docs/USAGE.md`](docs/USAGE.md#traceability) for the finding → § → module → artefact table.

---

## Licence & citation

- **Code:** MIT — see [`LICENSE`](LICENSE).
- **Dataset:** proprietary; redistribution prohibited — see [`data/README.md`](data/README.md).
- **Citation:** metadata in [`CITATION.cff`](CITATION.cff).

This is an academic dissertation; external contributions are not invited during the marking period.
