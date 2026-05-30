# EMERALD-AI — Usage Guide

Everything you can run, how to install it, and how to fix it when it breaks. This is the single operations reference; the [README](../README.md) is the overview.

> **One way to invoke commands.** Every task is `python -m emerald_ai <command>`. It works identically on Windows, macOS, and Linux with no extra tooling. Two equivalent shortcuts exist if you prefer them: `python emerald.py <command>` (no install needed, from the repo root) and `emerald <command>` (after install, if your Python `Scripts/` dir is on `PATH`).

## Contents

1. [Install](#1-install)
2. [Verify](#2-verify)
3. [The ML pipeline](#3-the-ml-pipeline)
4. [The web app](#4-the-web-app)
5. [The literature brain & research bot](#5-the-literature-brain--research-bot)
6. [Authoring the proposal](#6-authoring-the-proposal)
7. [Tests & code quality](#7-tests--code-quality)
8. [Traceability](#traceability)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Install

**Prerequisites:** Python ≥ 3.11, git. Node ≥ 20 only for the web app. (The project is developed on Python 3.13 too; the heaviest deep-learning deps are the only ones sensitive to the version — see [Troubleshooting](#9-troubleshooting).)

```bash
git clone <repo-url> emerald-ai && cd emerald-ai
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell  (macOS/Linux: source .venv/bin/activate)
pip install -e ".[ml,api,dev]"    # the common working set
```

Dependencies are grouped into optional extras so you only install what you need:

| Extra | Adds | Install when you want to… |
|---|---|---|
| `ml` | scikit-learn, imbalanced-learn, XGBoost, LightGBM, CatBoost, Optuna, MAPIE | run the ML pipeline |
| `xai` | SHAP, LIME, DiCE, AIF360, Quantus | get real SHAP attributions + DiCE counterfactuals |
| `dl` | PyTorch, rtdl | train the MLP / FT-Transformer deep tabular models |
| `api` | FastAPI, uvicorn, python-multipart | serve the backend |
| `mlops` | MLflow, DVC, Evidently, Prometheus | experiment tracking + drift monitoring |
| `docs` | python-docx, pypdf, Jupyter, matplotlib, seaborn | rebuild the proposal / run notebooks |
| `dev` | pytest, ruff, black, mypy, pre-commit | develop + run the test suite |
| `all` | everything above | one-shot full environment |

Combine freely: `pip install -e ".[ml,xai,api,dev]"`. For everything: `pip install -e ".[all]"`.

`uv` users: `uv sync --extra ml --extra api --extra dev`.

---

## 2. Verify

```bash
python -m emerald_ai version          # → EMERALD-AI v0.1.0
python -m emerald_ai research status  # prints the literature-brain state (no dataset needed)
python -m emerald_ai test             # → 125 passing
```

If those work, the install is sound. `research status` is the best smoke test because it needs no dataset and exercises the package end-to-end.

---

## 3. The ML pipeline

The pipeline is a chain of stages, each a CLI command that writes a dated report to `data/governance/`. Run them in order the first time; afterwards any stage can be re-run on its own.

**First, add the dataset.** It is proprietary and gitignored. Place it at `data/raw/All_Funded_2019_Green Loan.xlsx` (see [`../data/README.md`](../data/README.md)).

```bash
python -m emerald_ai eda          # §5.4  exploratory analysis      → data/governance/eda_report.md
python -m emerald_ai preprocess   # §5.5  drop/impute/encode/scale  → preprocess_report.md
python -m emerald_ai select       # §5.6  MI + stability selection  → selection_report.md
python -m emerald_ai imbalance    # §5.7  none/weighted/SMOTE        → imbalance_report.md
python -m emerald_ai train        # §5.8  nested CV + calibration    → training_report.md + models/*.joblib
python -m emerald_ai evaluate     # §5.13 metrics on the trained model (in-sample smoke check)
python -m emerald_ai explain      # §5.11 SHAP / importance          → explain_report.md
python -m emerald_ai audit        # §5.12 fairness gaps              → fairness_report.md
```

Useful options:

```bash
python -m emerald_ai train --families xgboost,lightgbm,rf   # restrict to specific families
python -m emerald_ai train --no-persist                     # don't overwrite models/
python -m emerald_ai select --n-bootstraps 50               # more stability rounds
python -m emerald_ai imbalance --n-folds 10
```

`train` persists `models/{current_model, preprocessor, conformal_marginal}.joblib`, `feature_names.json`, and `best_family.txt` — these are what the API serves. Re-running `train` overwrites them.

**What the metrics mean.** Primary tier: **PR-AUC** (minority-class ranking), **within-minority ECE** (calibration on defaulters), **recall@top-decile** (how many real defaults you catch in your riskiest 10%). Raw accuracy is deliberately excluded — at 0.36% prevalence, predicting "everyone repays" scores 99.6%.

---

## 4. The web app

Two processes: the FastAPI backend (serves the trained model) and the React console (the UI).

```bash
# terminal 1 — backend (needs models/ populated by `train`, and the [api] extra)
python -m emerald_ai api                        # → http://localhost:8000/docs  (Swagger UI)
python -m emerald_ai api --port 8080 --no-reload

# terminal 2 — frontend (needs Node ≥ 20)
cd apps/web && npm install && npm run dev        # → http://localhost:5173
```

**11 API endpoints:** `/healthz`, `/model_card`, `/portfolio`, `/raw_schema`, `/score_raw`, `/explain_raw`, `/score`, `/explain`, `/batch_score`, `/global_importance`, `/fairness_audit`. Browse and try them all at `/docs`.

**8 console views:** Home, About the Model, Data & Analyses, Dashboard, Score an Applicant, Score a Whole CSV, What the Model Looks At, Fairness Check. The "Score an Applicant" view takes **raw values** (FICO score, dollar amounts, an industry dropdown) — the persisted preprocessor runs server-side, so you never touch a standardised z-score.

If the API returns `503`, you haven't run `train` yet — there are no model artefacts to load.

---

## 5. The literature brain & research bot

```bash
python -m emerald_ai research status                 # counts + last-run timestamp
python -m emerald_ai research show chen2016xgboost   # one paper's structured record
python -m emerald_ai research run                    # re-ingest notes → graph → rollups (idempotent)
python -m emerald_ai research graph                  # emit citation graph as Graphviz DOT
```

**Grow the brain autonomously** (crawls OpenAlex; no API key; polite 1 req/s; idempotent):

```bash
# bootstrap from a search
python -m emerald_ai research discover --query "explainable green credit scoring" --max 10
# recurse from papers already in the brain
python -m emerald_ai research discover --depth 2 --max 20
# multi-round until saturation
python -m emerald_ai research bot --rounds 5
# then ingest what it found
python -m emerald_ai research run
```

Bot-discovered papers land in `auto_index.yaml` with `auto_discovered: true` and are **never citation-safe** until a human reviews the note and (optionally) promotes the entry into the curated `index.yaml`. Set `EMERALD_OPENALEX_MAILTO=you@example.com` or pass `--mailto` to join OpenAlex's polite pool.

Read [`../research/literature/BRAIN.md`](../research/literature/BRAIN.md) before editing any paper note. Markdown is the source of truth; the JSON sidecars and `state/*.json` regenerate — never hand-edit them.

---

## 6. Authoring the proposal

```bash
python -m emerald_ai proposal      # rebuilds docs/proposal/proposal_*.docx from build_proposal.py
```

The proposal is generated from a `python-docx` script so it stays diffable. Edit `docs/proposal/build_proposal.py`, then rerun. **Close the `.docx` in Word first** or you'll hit a `PermissionError` (Word holds an exclusive lock).

---

## 7. Tests & code quality

```bash
python -m emerald_ai check        # lint + typecheck + test (the pre-commit gate)
python -m emerald_ai test         # pytest (125 tests)
python -m emerald_ai test --fast  # skip slow + integration
python -m emerald_ai lint         # ruff + black --check
python -m emerald_ai format       # auto-fix with ruff + black
python -m emerald_ai typecheck    # mypy strict on src/
```

CI runs the same suite on push + PR (`.github/workflows/ci.yml`) on Python 3.11 and 3.12.

---

## Traceability

The audit chain from empirical finding → proposal section → code module → governance artefact. Each ML stage writes its report under `data/governance/`.

| Empirical finding | § | Code module | Artefact |
|---|---|---|---|
| 90 permitted / 76 forbidden features after target-leakage audit | §5.3 | `data/leakage_audit.py` | `feature_catalogue.yaml`, `feature_audit_summary.md` |
| 0.36% default prevalence (50 / 14,022 labelled) | §5.2 | `data/load.py` | `datasheet.md` |
| Term 86% / APR 60% / Factor 42% missing → dropped (>40% rule) | §5.5 | `features/pipeline.py` | `preprocess_report.md` |
| Quarterly drift (PSI) on Lender / Published / Attempted-Assigned | §5.4 | `data/eda.py` | `eda_report.md` |
| Industry risk gradient (firearms 9% small-N → retail 0.08%) | §5.4 | `data/eda.py` | `eda_report.md` |
| 90 → 71 (MI) → 20 (stability) features selected | §5.6 | `features/selection.py` | `selection_report.md` |
| SMOTE narrowly best, but all strategies leave ECE ≈ 0.32 on the minority | §5.7 | `training/imbalance.py` | `imbalance_report.md` |
| CatBoost wins nested CV (mean PR-AUC ≈ 0.118); GBDTs lead, deep nets better-calibrated | §5.8 | `training/cv.py`, `models/` | `training_report.md` |
| Conformal: marginal coverage = headline, Mondrian = diagnostic | §5.10 | `calibration/conformal.py` | `models/conformal_marginal.joblib` |
| Top features: Lender, Prod Rank, Closed Max Term (deal-context dominates) | §5.11 | `explain/` | `explain_report.md` |
| Fairness audit re-run at risk-band thresholds (0.5 was uninformative) | §5.12 | `fairness/audit.py` | `fairness_report.md` |

---

## 9. Troubleshooting

| Symptom | Fix |
|---|---|
| `emerald: command not found` | Use `python -m emerald_ai …` — works without `emerald` on `PATH`. |
| `ModuleNotFoundError: emerald_ai` | `pip install -e ".[ml,api,dev]"` — the editable install is missing. |
| `ModuleNotFoundError: xgboost` / `optuna` / `shap` | Install the matching extra (e.g. `pip install -e ".[ml,xai]"`). |
| API returns `503` on `/score` | No model artefacts — run `python -m emerald_ai train` first. |
| `python -m emerald_ai proposal` → `PermissionError` | Close the `.docx` in Word, then retry. |
| `pip install torch` / `rtdl` fails on Python 3.13 | The deep-learning extra is the only version-sensitive one; use Python 3.11/3.12 for `[dl]`, or skip it — the tree models are the primary deliverable. |
| `research run` reports more papers than `research status` | You ran the discovery bot; the new papers aren't ingested yet — run `research run` once to reconcile. |
| `dot: command not found` rendering the citation graph | Install Graphviz (https://graphviz.org/download/) — only needed for SVG rendering. |
| CI fails on `mypy strict` | Run `python -m emerald_ai typecheck` locally and add the missing annotations. |

When in doubt, `python -m emerald_ai check` surfaces lint, type, and test failures in one pass.
