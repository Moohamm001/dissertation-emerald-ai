# EMERALD-AI

> **Explainable, calibrated, audit-ready machine learning for green-loan credit scoring.**
> MSc Applied AI dissertation — University of Warwick. License MIT · Python 3.11
> Stage: **proposal v0.4.1 + full end-to-end pipeline working with beginner-friendly lending-officer SPA** (data → leakage audit → EDA → preprocess → selection → imbalance → training → calibration + conformal → fairness audit → FastAPI backend → React SPA console with onboarding tiles, help cards, and one-click example applicant). MLP / FT-Transformer, full Optuna budget, TreeSHAP, DiCE, and a v0.5 fairness re-audit at risk-band thresholds are flagged as deferred.

---

## What this project does (plain English)

When a small business applies for a **green loan** — money borrowed for eco-friendly projects like solar panels, electric-vehicle fleets, or energy-efficient buildings — the lender has to decide: is this borrower likely to pay it back?

Most lenders today use credit-scoring formulas built for ordinary consumer loans. Those formulas weren't designed for green lending. They don't know that a solar installation's cash flow looks nothing like a credit card. They can't tell whether a project labelled "green" actually is. And they can't explain, in a way the borrower or regulator can check, *why* an application was approved or declined.

**EMERALD-AI** is a machine-learning system that:

1. Learns from a real 2019 dataset of **14,135 green-loan transactions** what actually predicts repayment.
2. Compares modern AI methods (XGBoost, gradient boosting, tabular deep learning) head-to-head on the same data.
3. Doesn't just predict — it **explains** every decision so the lending officer and the borrower both know *why*.
4. Reports **how confident** the model is in each individual decision (not just one overall accuracy number).
5. **Audits for unfair bias** across industries, regions, and business sizes.
6. Ships as a **working web app** that a real lender could use — not a research demo locked in a notebook.

The system is designed to comply with the **EU AI Act** and the **UK Financial Conduct Authority's Consumer Duty**, both of which now legally require credit-scoring AI to be transparent, fair, and auditable.

---

## Where the project stands (May 2026)

| Stage | Status | What it means |
|---|---|---|
| **Research proposal** | ✅ **v0.4.1 (2026-05-18)** | Full ~9,636w / 74 refs + 3K condensed ~2,743w / 30 refs. Datasheet-aligned + small-N-honest (v0.4 audit edits + v0.4.1 conformal reframe: marginal coverage as headline, Mondrian conditional as diagnostic, interval width excluded from primary metrics) |
| **Literature review** | ✅ Done (coverage) / 🚧 In progress (depth) | 218 papers in brain, organised by theme; **34 fully read with human-quality notes, 156 bot-discovered abstract-only (not citation-safe), 28 placeholder stubs** |
| **Code scaffold** | ✅ Done | All modules in place, each with docstrings pointing to the proposal section |
| **Automated research bot** | ✅ Done | Keeps discovering new relevant papers from OpenAlex over time |
| **Tests + continuous integration** | ✅ Done | 55 tests passing across literature integrity, discovery bot, data load, and leakage audit |
| **Data loading + leakage audit** | ✅ **Done (2026-05-18)** | 166 columns classified — 90 permitted as features, 76 forbidden; class balance 0.36% delinquent surfaced; datasheet + catalogue committed under `data/governance/` |
| **Exploratory data analysis (EDA)** | ✅ **v0.1 (2026-05-18)** | Univariate distributions + bivariate MI against Y + segment-level conditional default rates with Wilson 95% CIs + quarterly PSI drift. Run: `python -m emerald_ai eda` → `data/governance/eda_report.md`. **Key findings:** `Industry=firearms` 9.09% rate (small-N flagged); `Borrower State=WV/AR/CT/IN/SC` highest at 1.5–2.1%; material PSI drift on `Lender Identifier` (13–14), `Published` (10–11), `Attempted/Assigned` (8–9). |
| **Preprocessing pipeline** | ✅ **v0.1 (2026-05-18)** | ColumnTransformer over the 90 permitted features: Stage 1 drop (>40% missing + EDA-flagged time-leaking); Stage 2 impute + missing-indicators; Stage 3 one-hot (≤10 levels) + target-encode (Industry, Borrower State); Stage 4 StandardScaler. Run: `python -m emerald_ai preprocess` → `data/governance/preprocess_report.md`. **Drops:** 8 high-miss columns (Term/APR/Factor + the five 100%-missing-but-permitted), 2 time-leaking, 35 datetime (deferred to §5.6). |
| **Feature selection (§5.6)** | ✅ **v0.1 (2026-05-18)** | Stage-1 MI filter (drop bottom decile) + Stage-2 bootstrap-stability RF importance (30 rounds, ≥60% selection-frequency threshold). Run: `python -m emerald_ai select` → `data/governance/selection_report.md`. **First pass:** 90 → 71 (MI filter) → 20 (stability). Top selected: Credit Score, Revenue, Payback, Payment Amount, Amount Funded, # Offers Received, Closed Max Term, Lender. SHAP variant deferred to post-§5.8. |
| **Class-imbalance harness (§5.7)** | ✅ **v0.1 (2026-05-18)** | Compares `no_resample` / `class_weighted` / `smote` under 5-fold CV on a LogReg baseline; selects the joint-score winner (PR-AUC × (1 − within-minority-ECE)). Run: `python -m emerald_ai imbalance` → `data/governance/imbalance_report.md`. **Empirical:** SMOTE narrowly wins (joint 0.058 vs class-weighted 0.041 vs no-resample 0.001) but all three produce ECE ≈ 0.32 on the minority — resampling alone does not solve calibration; the §5.10 conformal/calibration layer remains load-bearing. |
| **Model training (§5.8 + §5.9)** | ✅ **v0.1 (2026-05-18)** | Five available families (LR L1/L2, RBF-SVM, RF, XGBoost; LightGBM/CatBoost gated on deps; MLP/FT-Transformer deferred). RandomizedSearchCV in place of full Optuna budget; outer K-fold CV with paired splits for DeLong test. Run: `python -m emerald_ai train` → `data/governance/training_report.md` + persists `models/{current_model,preprocessor,conformal_marginal,feature_names}.joblib`. **First-cut OOF result:** XGBoost wins with mean PR-AUC ≈ 0.10 (~26× random baseline at 0.36% prevalence). |
| **Calibration + conformal (§5.10)** | ✅ **v0.1 (2026-05-18)** | Platt / isotonic / temperature scaling + split-conformal (marginal, finite-sample exact) + Mondrian class-conditional (diagnostic with bootstrap CIs). v0.4.1 framing wired: marginal is headline, conditional is diagnostic, interval width is not a primary metric. Persisted alongside the trained model for the FastAPI backend. |
| **Explainability (§5.11)** | ✅ **v0.1 (2026-05-18)** | Global permutation importance + local coefficient/importance proxy + nearest-feature counterfactual. Run: `python -m emerald_ai explain` → `data/governance/explain_report.md`. **Top-3 features:** Lender, Prod Rank, Closed Max Term — deal-context dominates over borrower-attribute. TreeSHAP / KernelSHAP / DiCE / Quantus deferred (require `shap` / `dice-ml`). |
| **Fairness audit (§5.12)** | ✅ **v0.1 (2026-05-18)** | Per-axis demographic-parity / equalised-odds / predictive-parity / calibration-within-group gaps on Industry × Borrower State. Run: `python -m emerald_ai audit` → `data/governance/fairness_report.md`. **Finding:** at threshold 0.5 the model approves ≈100% of applicants in every group (selection rate 0.997–1.000) so DP/TPR gaps are tiny; meaningful audit requires re-running at lower thresholds — flagged for v0.5 patch. |
| **Web app — FastAPI backend (§5.14)** | ✅ **v0.2 (2026-05-20)** | **11 endpoints live**: `/healthz`, `/model_card` (now exposes the chosen algorithm in plain English + the eight-step training pipeline), `/portfolio`, `/raw_schema` (new — raw input columns + defaults + categorical levels), `/score_raw` + `/explain_raw` (new — accept raw applicant data; the persisted `preprocessor.joblib` runs server-side), `/score` + `/explain` (legacy post-preprocessing endpoints kept for diagnostics), `/batch_score` (CSV upload), `/global_importance`, `/fairness_audit`. CORS enabled for dev. Run: `python -m emerald_ai api` → <http://localhost:8000/docs>. |
| **Web app — React SPA frontend (§5.14)** | ✅ **v0.3 (2026-05-20)** | React 18 + Vite + TypeScript console with **seven views**, soft mint/cream light theme, plain-English help cards on every page, and per-field tooltips. Views: **🏡 Home** (landing page with tiles + 4-step walkthrough), **🧠 About the Model** (new — algorithm card + headline raw features + top-15 processed-feature importances + 8-step training pipeline narrated twice via a plain/technical toggle), **📊 Dashboard** (KPIs + model card), **👤 Score an Applicant** (now accepts **raw values** — FICO score, dollar amounts, industry dropdown — with basic/advanced field toggle; backend runs the preprocessor for the user), **📂 Score a Whole CSV** (3-step uploader with downloadable column template), **🔍 What the Model Looks At** (global importance), **⚖️ Fairness Check** (per-axis gaps + Selbst traps). Run: `cd apps/web && npm install && npm run dev` → <http://localhost:5173>. |
| **Dissertation submission** | ⬜ Week 16 | Final write-up + open-source release. |

**Plain-English summary:** the *reading and design* phase is finished. The *building and experimenting* phase starts now.

---

**For non-technical readers** — the sections above cover what you need. The rest of this README is for engineers and supervisors who want command-level detail.

**New here (technical)?** → [**QUICKSTART.md**](QUICKSTART.md) (5-minute hands-on tour)
**Need a specific command?** → [**HOWTORUN.md**](HOWTORUN.md) (full operations reference)
**Just want to read the research?** → [`docs/proposal/proposal_fourth_draft_3k.docx`](docs/proposal/) (v0.4.1, **~2,740 words total** — 2,077-word body + curated 30-ref bibliography). For the full ~9,600-word supervisor-facing version with all 74 refs, see [`docs/proposal/proposal_fourth_draft.docx`](docs/proposal/).

---

## Project status (live numbers)

```
  papers in brain   : 218      (76 human-curated + 142 bot-only; 14 promoted in v0.3)
    of which read   :  34/218  (analysed = full notes; remaining 156 indexed = abstract-only, 28 stub)
  citation edges    :  80
  research questions:  15      (auto-generated from gaps.md)
  authors indexed   : 2001
  methods detected  :  22      (XGBoost, LightGBM, CatBoost, SHAP, DiCE, conformal, ...)
  datasets detected :   9      (COMPAS, FICO, Adult, German Credit, Lending Club, ...)
  themes drafted    :   8/8    (lit-review sections 4.1-4.8)
  tests passing     : 108/108  (above + models + calibration + conformal + explain + fairness + eval)
  top-level dirs    :   7      (.github, apps, src, research, docs, data, tests)
  commits on main   :   9
```

Numbers refresh with `python -m emerald_ai research status`.

---

## What this project is, in 30 seconds (technical)

Green-loan origination has grown at >40% CAGR since 2018, but credit-risk infrastructure still uses scorecards designed for conventional consumer credit. EMERALD-AI is an end-to-end ML framework that benchmarks modern tabular learners on a real 2019 green-loan dataset (14,135 transactions × 166 features), integrates **calibration**, **distribution-free uncertainty**, **multi-method explainability**, and a **fairness audit** aligned with the **EU AI Act (Annex III)** and **FCA Consumer Duty** — delivered as a full-stack decision-support platform for lending officers.

It occupies an explicit literature gap: no published work simultaneously delivers, on real green-loan data, all six of (i) modern tabular benchmarking under identical preprocessing, (ii) post-hoc calibration + conformal uncertainty, (iii) multi-method XAI with empirical fidelity validation, (iv) sociotechnically-disciplined fairness audit on green-lending-appropriate proxies, (v) an explicit reject-inference treatment of accepted-only selection bias, and (vi) a deployable lending-officer interface.

---

## What works today

> Every command runs the same on Windows, macOS, and Linux — no Make required. Use `python -m emerald_ai <command>` (or `python emerald.py <command>` from a fresh clone with no install).

| Subsystem | State | Try it |
|---|---|---|
| Literature brain (218 refs, 80-edge citation graph, 15 research questions) | **WORKS** | `python -m emerald_ai research status` |
| Autonomous research engine (idempotent, 10-field schema, audit-trail) | **WORKS** | `python -m emerald_ai research run` |
| **Autonomous discovery bot** (OpenAlex crawler, null-tolerant, crash-resistant, no API key) | **WORKS** | `python -m emerald_ai research discover --query "explainable green credit scoring"` |
| Proposal authoring pipeline (python-docx → v0.4.1 full ~9,600w / 74 refs + v0.4.1 3K condensed ~2,740w / 30 refs) | **WORKS** | `python -m emerald_ai proposal` + `python docs/proposal/build_proposal_condensed.py` |
| Tests + CI (ruff + black + mypy + pytest on 3.11/3.12) — 55 passing | **WORKS** | `python -m emerald_ai check` |
| Cross-platform CLI (Windows / macOS / Linux, no Make required) | **WORKS** | `python -m emerald_ai --help` |
| FastAPI backend | **PARTIAL** | `python -m emerald_ai api` (only `/healthz` for now; rest scaffolded) |
| Data layer (load + leakage audit + datasheet + feature catalogue) | **WORKS** | `python -m emerald_ai.data.leakage_audit` — emits `data/governance/{feature_catalogue.yaml, feature_audit_summary.md, datasheet.md}` |
| EDA pipeline (univariate + bivariate + segment-level + drift) | **WORKS** | `python -m emerald_ai eda` — emits `data/governance/eda_report.md` |
| Preprocessing pipeline (ColumnTransformer: drop + impute + encode + scale) | **WORKS** | `python -m emerald_ai preprocess` — emits `data/governance/preprocess_report.md` |
| Feature selection (§5.6 MI filter + bootstrap-stability RF importance) | **WORKS** | `python -m emerald_ai select` — emits `data/governance/selection_report.md` |
| Class-imbalance harness (§5.7 no-resample / class-weighted / SMOTE comparison) | **WORKS** | `python -m emerald_ai imbalance` — emits `data/governance/imbalance_report.md` |
| Training harness (§5.8 + §5.9 nested CV + RandomizedSearchCV) | **WORKS** | `python -m emerald_ai train` — emits `data/governance/training_report.md` + persists `models/*.joblib` |
| Calibration + conformal (§5.10 Platt/isotonic/temperature + split + Mondrian) | **WORKS** | called from `train`; conformal persisted to `models/conformal_marginal.joblib` |
| Explainability (§5.11 permutation importance + local proxy + counterfactual) | **WORKS** | `python -m emerald_ai explain` — emits `data/governance/explain_report.md` |
| Fairness audit (§5.12 DP / EO / PP / calibration-within-group) | **WORKS** | `python -m emerald_ai audit` — emits `data/governance/fairness_report.md` |
| Evaluation metrics (§5.13 PR-AUC + within-min ECE + recall@top-decile + DeLong + bootstrap) | **WORKS** | `python -m emerald_ai evaluate` (in-sample smoke) |
| FastAPI backend (§5.14 — 8 endpoints incl. /batch_score, /portfolio, /global_importance, /fairness_audit) | **WORKS** | `python -m emerald_ai api` — Swagger at `/docs` |
| React + Vite SPA (Dashboard / Single / Batch / SHAP / Fairness) | **WORKS** | `cd apps/web && npm install && npm run dev` — UI at `:5173` |
| React SPA frontend | **STUB** | scaffold deferred until the API serves real predictions |

---

## Architecture at a glance

```
┌──────────────────────────┐    ┌─────────────────────────────────────────────────────────┐
│  data/raw/*.xlsx         │    │  research/literature/   (KNOWLEDGE BRAIN  — WORKS)     │
│  proprietary, gitignored │───▶│  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  14,135 × 166 features   │    │  │ themes/ │  │ papers/  │  │ gaps.md  │  │ state/   │ │
└──────────────────────────┘    │  │ 8 files │  │ 190 .md  │  │ 15 gaps  │  │ JSON     │ │
              │                 │  └─────────┘  │ + .json  │  └──────────┘  │ graph,   │ │
              │                 │  index.yaml   └──────────┘                │ rollups, │ │
              │                 │  + auto_index.yaml (bot)                  │ RQs      │ │
              │                 │  (76 manual + 142 bot-only = 218 unique)  └──────────┘ │
              │                 │                ▲              ▲                          │
              ▼                 │                │              │ BFS crawl, threshold     │
┌──────────────────────────────┐│                │   ┌──────────┴──────────────────────┐  │
│  src/emerald_ai/  (PACKAGE)  ││                │   │  OpenAlex (free, no API key)    │  │
│                              ││                │   │  1 req/s · on-disk cache        │  │
│  data/      load+leakage  ✓  ││                │   │  null-tolerant · crash-resistant│  │
│  features/  pipeline    STUB ││                │   └─────────────────────────────────┘  │
│  models/    LR SVM RF XGB    ││            ┌───┴──────────────────────────────────────┐ │
│             LGBM CatBoost    │ STUB        │ Engine: parse -> graph -> roll-up         │ │
│             MLP FT-Transformer│ STUB       │ Discovery bot: BFS, relevance scoring,    │ │
│  training/  nested CV+Optuna │ STUB        │ saturation-aware, idempotent              │ │
│  calibration Platt+conformal │ STUB        └──────────────────────────────────────────┘ │
│  explain/   TreeSHAP+DiCE    │ STUB                                                      │
│  fairness/  AIF360 audit     │ STUB     ┌──────────────────────────────────────┐         │
│  eval/      PR-AUC, KS, ECE  │ STUB     │  apps/api/main.py (FastAPI) PARTIAL  │         │
│  research/  bot + engine     │ WORKS───▶│  /healthz YES   /score /explain ... │         │
│  cli.py     emerald CLI      │ WORKS    └────────────────────┬─────────────────┘         │
└──────────────┬───────────────┘                               │                            │
               │                                               ▼                            │
               ▼                                  ┌────────────────────────────┐            │
   ┌───────────────────────┐                      │  apps/web/ (React + Vite)  │            │
   │  docs/proposal/       │                      │  Dashboard, Single Predict,│ STUB       │
   │  build_proposal.py    │ WORKS                │  Batch Score, SHAP Explorer│            │
   │  -> fourth_draft.docx │                      └────────────────────────────┘            │
   └───────────────────────┘                                                                │
                                                                                            │
    [ tests/ 108 passing : pipeline above + models + calibration + conformal + explain + fairness + eval ]
```

---

## Traceability — empirical finding → proposal § → code module → governance artefact

> _The literature brain (`research/literature/`) indexes **external** sources. This table is the
> code brain: it indexes **internal** decisions, mapping each empirical finding from the data through
> the proposal section that motivates it, the module that implements it, and the governance artefact
> that records the result. Updated as each stage lands._

| Empirical finding (source) | Proposal § | Code module | Governance artefact |
|---|---|---|---|
| 90 permitted / 76 forbidden after target-leakage audit (166 columns × 6 categories) | §5.3 | `src/emerald_ai/data/leakage_audit.py` | `data/governance/feature_catalogue.yaml` + `feature_audit_summary.md` |
| 0.36% delinquent prevalence (49 default + 1 behind / 14,022 labelled = 99.20% coverage) | §4.4 + §5.2 | `src/emerald_ai/data/load.py` (`label_creditworthiness`) | `data/governance/datasheet.md` §2 |
| `Monthly Credit Card Charges` 100% missing in 2019; Term 86.4% / APR 59.6% / Factor 42.0% (>40% drop threshold) | §5.5 Stage 1 | `src/emerald_ai/features/pipeline.py` (`build_preprocessor`) | `data/governance/preprocess_report.md` |
| Material quarterly PSI on `Lender Identifier` (13–14) / `Published` (10–11) / `Attempted/Assigned` (8–9); pure-time PSI ~16 by construction (`Start Month`, `Start Annual Day`) | §5.4 + §5.5 | `src/emerald_ai/data/eda.py` (`psi_temporal`) + `pipeline.TIME_LEAKING_COLUMNS` | `data/governance/eda_report.md` §4 |
| Industry-level risk gradient (firearms 9.09% small-N → retail 0.08%, ~17× range); state-level cluster WV/AR/CT/IN/SC at 1.5–2.1% | §5.4 + §5.12 | `src/emerald_ai/data/eda.py` (`conditional_default_rates`) | `data/governance/eda_report.md` §3 |
| 90 preprocessed features → 71 (MI filter) → 20 (bootstrap-stability) — Credit Score, Revenue, Payback, Payment Amount, Amount Funded, # Offers Received, Closed Max Term, Lender survive | §5.6 | `src/emerald_ai/features/selection.py` | `data/governance/selection_report.md` |
| SMOTE narrowly wins joint score (0.058) over class-weighted (0.041) vs no-resample (0.001) on a LogReg baseline; all three ECE ≈ 0.32 on minority — resampling alone doesn't solve calibration | §5.7 + §5.10 | `src/emerald_ai/training/imbalance.py` (`select_strategy`) | `data/governance/imbalance_report.md` |
| Conformal claim split under N=50 minority: marginal coverage = headline (`SplitConformal`); Mondrian conditional = diagnostic with bootstrap CIs; interval width excluded from primary metrics | §4.4 + §5.10 + §5.13 | `src/emerald_ai/calibration/conformal.py` | persisted at `models/conformal_marginal.joblib`; served via `/score` |
| XGBoost wins nested-CV with mean PR-AUC ≈ 0.10 (~26× random baseline) on a 3-family / 3-fold / 4-candidate first cut; LR/RF/XGB compared on identical splits | §5.8 + §5.9 | `src/emerald_ai/training/cv.py` + `src/emerald_ai/models/{linear,trees}.py` | `data/governance/training_report.md` |
| Permutation importance: top-3 features are Lender, Prod Rank, Closed Max Term — deal-context dominates borrower-attribute signals | §5.11 | `src/emerald_ai/explain/shap_engine.py` + `counterfactual.py` | `data/governance/explain_report.md` |
| At threshold 0.5 the trained model approves ~100% of applicants in every Industry / Borrower State group → DP/TPR gaps are tiny; the audit needs to be re-run at the §5.7 risk-band thresholds for v0.5 | §5.12 | `src/emerald_ai/fairness/audit.py` | `data/governance/fairness_report.md` |
| Lending-officer console serves Dashboard + Single Predict + Batch Score + SHAP Explorer + Fairness Panel against the FastAPI backend; CORS + Vite dev proxy wired | §5.14 | `apps/web/src/views/*.tsx` + `apps/web/src/api.ts` | `apps/web/README.md` |
| Reject-inference bounded by data (no rejected applicants): model framed as conditional on prior accept-policy | §4.4 + §5.2 + §8 | (TBD — sensitivity analysis in `src/emerald_ai/eval/`) | `data/governance/datasheet.md` §5 |

This table is the answer to "should we have more brain about code?" — yes, but lightweight. The literature brain
(papers) lives in `research/literature/`; the code brain (this table + the governance artefacts under
`data/governance/` + the §-pointing docstrings) lives at the project's top level so a supervisor can audit
the empirical → methodological → code chain end to end without spelunking subdirectories.

---

## Where to look for X

| If you want to find… | Look in |
|---|---|
| The dissertation research design | `docs/proposal/proposal_fourth_draft.docx` (v0.4.1, full) or `proposal_fourth_draft_3k.docx` (v0.4.1, 3K condensed) |
| Why a particular method was chosen | `research/literature/themes/4.X-*.md` (argumentative spine) |
| Notes on a specific cited paper | `research/literature/papers/<key>.md` or `<key>.json` |
| Open questions / unverified claims | `research/literature/gaps.md` |
| A domain term definition | `research/literature/glossary.md` |
| Where to put new code for stage X | docstring at top of `src/emerald_ai/<stage>/__init__.py` |
| The full command catalogue | `python -m emerald_ai --help` (or `HOWTORUN.md` for descriptions) |
| The autonomous research workflow spec | `research/automation.txt` |
| The dataset (it's gitignored) | `data/README.md` for acquisition instructions |

---

## Project layout

```
.
├── README.md                  ← you are here (pitch + architecture + where-to-look)
├── QUICKSTART.md              ← 5-minute hands-on tutorial for newcomers
├── HOWTORUN.md                ← full topic-split operations reference
├── LICENSE  CITATION.cff      ← MIT + academic citation metadata
├── pyproject.toml  Makefile   ← uv-managed deps + Unix convenience wrapper
├── emerald.py                 ← zero-install CLI launcher (python emerald.py …)
│
├── apps/                      ← RUNTIME APPLICATIONS (backend + frontend together)
│   ├── api/                   ← FastAPI backend (REST endpoints; production scoring)
│   └── web/                   ← React 18 + Vite SPA (Dashboard, Single Predict,
│                                  Batch Score, SHAP Explorer)
│
├── src/emerald_ai/            ← PYTHON PACKAGE: data, features, models, training,
│                                  calibration, explain, fairness, eval, research, cli
│
├── research/                  ← RESEARCH WORKSPACE
│   ├── automation.txt         ← Spec for the autonomous research workflow
│   ├── literature/            ← Knowledge brain (index.yaml + themes + papers + gaps + glossary)
│   │   ├── BRAIN.md           ← read first for usage rules
│   │   ├── state/             ← Auto-generated: citation graph, rollups, generated questions
│   │   ├── papers/<key>.{md,json}  ← Per-paper notes + JSON sidecars (10-field schema)
│   │   ├── themes/            ← Argumentative spine (one file per proposal §4.X subsection)
│   │   ├── gaps.md, glossary.md
│   │   ├── auto_index.yaml    ← Bot-discovered papers (separate from index.yaml)
│   │   └── build_papers.py    ← Regenerates papers/*.md from a dict
│   ├── notebooks/             ← Jupyter notebooks: EDA, model dev, audit
│   └── scripts/               ← Reproducibility scripts (make reproduce wraps these)
│
├── docs/
│   ├── proposal/              ← Dissertation proposal (first/second drafts + build script)
│   └── architecture/          ← (to come) C4 diagrams, MLOps stack diagrams
│
├── data/                      ← DATA (gitignored — proprietary green-loan dataset)
│   ├── raw/  interim/  processed/
│
├── tests/                     ← pytest suite (smoke + brain integrity + discovery)
└── .github/                   ← CI workflow + PR/issue templates
```

**Top-level directories: 7** — `.github`, `apps`, `data`, `docs`, `research`, `src`, `tests`. Each one has a single, clear purpose.

---

## Quick start

> For a guided 5-minute walkthrough with expected outputs, see [**QUICKSTART.md**](QUICKSTART.md).

### Prerequisites

- Python ≥ 3.11
- [uv](https://github.com/astral-sh/uv) for dependency management (preferred) or pip
- Node ≥ 20 + pnpm (for the frontend, when implemented)
- Make (for the canonical entrypoints)

### Install

```bash
# clone
git clone <YOUR_FORK_URL> emerald-ai
cd emerald-ai

# install python deps (uv recommended)
uv sync               # creates .venv with pinned deps from pyproject.toml + uv.lock
# OR
pip install -e ".[dev]"
```

### Add the dataset

The 2019 All Funded Green Loan dataset is **proprietary** and not redistributed in this repository. See [`data/README.md`](data/README.md) for how to obtain it. Once obtained, place at:

```
data/raw/All_Funded_2019_Green Loan.xlsx
```

### Common tasks

The Python CLI is the canonical entrypoint. The Makefile is a thin convenience wrapper for Unix users — Windows users should use the Python form directly.

| Task | Cross-platform (recommended) | Unix shortcut |
|---|---|---|
| List all commands | `python -m emerald_ai --help` | `make help` |
| Run all checks (lint + typecheck + test) | `python -m emerald_ai check` | `make check` |
| Tests only | `python -m emerald_ai test` | `make test` |
| Rebuild the proposal docx | `python -m emerald_ai proposal` | `make proposal` |
| Regenerate paper notes | `python -m emerald_ai literature` | `make literature` |
| Run the research engine | `python -m emerald_ai research run` | `make research` |
| Brain status | `python -m emerald_ai research status` | `make research-status` |
| Citation graph (DOT) | `python -m emerald_ai research graph` | `make research-graph` |
| Start the FastAPI dev server | `python -m emerald_ai api` | `make api` |
| Reproduce ML pipeline (when implemented) | `python -m emerald_ai reproduce` | `make reproduce` |

**For a full operations guide — every command, every subsystem, troubleshooting — see [`HOWTORUN.md`](HOWTORUN.md).**

---

## Research design at a glance

- **Problem:** Binary creditworthiness classification, Y=1 (paidOff ∪ current) vs Y=0 (default ∪ behind).
- **Dataset:** 14,135 funded transactions × 166 features, 99.2% labelled coverage.
- **Models compared (6 families, identical preprocessing):**
  - Linear baselines: L1/L2 Logistic Regression, RBF-SVM
  - Tree ensembles: Random Forest, XGBoost (primary), LightGBM, CatBoost
  - Tabular deep learning: MLP, FT-Transformer
- **Training:** 5×10 nested stratified CV + Bayesian HPO (Optuna TPE + HyperBand)
- **Calibration:** Platt / isotonic / temperature, on a dedicated calibration split
- **Uncertainty:** Split-conformal prediction with 90% / 95% marginal coverage
- **Explainability (three-layer):** TreeSHAP (global + local), KernelSHAP cross-check, LIME, DiCE counterfactuals — validated via Quantus fidelity metrics
- **Fairness:** AIF360 audit on Industry, Borrower State, business-size proxies — demographic parity, equalised odds, predictive parity, calibration-within-group
- **Deployment:** FastAPI + React SPA + MLflow + Prometheus + Evidently (drift monitoring)

Full methodology in [`docs/proposal/proposal_fourth_draft.docx`](docs/proposal/) (v0.4.1), §5.

---

## Literature brain

The repo contains a structured knowledge base under [`research/literature/`](research/literature/) — not a static bibliography, but a queryable, versioned representation of the lit review intended to evolve through the project:

- `research/literature/BRAIN.md` — usage rules
- `research/literature/index.yaml` — 76 human-curated references (themes, relevance, verification status, search-query hints for placeholder citations)
- `research/literature/auto_index.yaml` — 156 references added by the discovery bot; on key collision the manual entry wins (engine.py:39), so promotion is just "append the key into index.yaml with curated metadata"
- `research/literature/themes/4.1`–`4.8.md` — eight argumentative-spine files mirroring the proposal's literature-review subsections
- `research/literature/papers/<key>.md` — 190 paper notes (34 human-written + 156 bot-stubbed; 14 of those stubs now back human-curated index entries via v0.3 promotion)
- `research/literature/papers/<key>.json` — machine-readable sidecar in the 10-field schema, populated by the research engine
- `research/literature/gaps.md` — 10 literature gaps + 5 methodology gaps, with suggested next actions
- `research/literature/glossary.md` — domain terms
- `research/literature/state/` — auto-generated state (citation graph, rollups, generated questions, discovery history); see [`research/literature/state/README.md`](research/literature/state/README.md)

Read `BRAIN.md` before writing about any paper.

---

## Research automation

The brain is driven by an idempotent **research engine** (`src/emerald_ai/research/`) that implements the workflow specified in [`research/automation.txt`](research/automation.txt). Re-running over an unchanged brain is a no-op except for the manifest timestamp; adding a new paper key to `research/literature/index.yaml` schedules it for analysis on the next run.

### What the engine does

| # | Step (from `research/automation.txt`) | How |
|---|---|---|
| 1 | Read existing research memory first | `State.load()` reads all of `research/literature/state/` |
| 2 | Check processed-papers DB before re-analysing | `state/processed.json` — keys at status `analysed`/`indexed` skipped unless `--force` |
| 3 | For every new paper, extract the 10-field schema | Parses `papers/<key>.md` sections into a `PaperRecord` (title, authors, year, abstract, methodology, contributions, weaknesses, future_works, referenced_papers, important_keywords) |
| 4 | Save structured summary as markdown + JSON | Markdown is the source of truth (hand-edited); JSON sidecar `papers/<key>.json` is regenerated |
| 5 | Add citation relationships into a graph | `state/citations.json` populated from `[[wiki-links]]` in paper bodies — intra-brain only, no invented external refs |
| 6 | Roll up authors, institutions, methods, datasets, keywords | `state/{authors,institutions,methods,datasets,keywords}.json` |
| 7 | Generate research questions from gaps | One `ResearchQuestion` per `G#`/`M#` heading in `gaps.md`, with traceback ID |
| 8 | Mark uncertain claims clearly; never invent citations | `confidence` field on every record (`high`/`medium`/`low`/`unknown`); `verified` flag mirrored from `index.yaml`; `search_query` retained for placeholder citations |

### Current snapshot

```
$ python -m emerald_ai research status
Brain state - last run 2026-05-18T13:08:02+00:00
  papers     : 218     (76 human-curated in index.yaml + 142 bot-only in auto_index.yaml)
  citations  : 80
  questions  : 15
  authors    : 2001
  methods    : 22      (XGBoost, LightGBM, CatBoost, SHAP, LIME, DiCE, SMOTE, conformal, ...)
  datasets   :  9      (COMPAS, FICO, Adult, German Credit, Lending Club, KDD, Higgs, ...)
  keywords   : 68
```

### Commands

```bash
python -m emerald_ai research run               # full sweep; idempotent
python -m emerald_ai research run --force       # re-process even already-analysed papers
python -m emerald_ai research status            # current counts + last-run timestamp
python -m emerald_ai research show <key>        # pretty-print one paper's structured record
python -m emerald_ai research graph             # emit citation graph as Graphviz DOT
                                                # render: dot -Tsvg research/literature/state/citations.dot -o ...svg

# Autonomous discovery — grow the brain by crawling OpenAlex (no API key needed)
python -m emerald_ai research discover --query "explainable green credit scoring"
python -m emerald_ai research discover --seed W2964121823 --depth 3 --max 30
python -m emerald_ai research discover                 # seeds = papers already in brain (depth 1)
python -m emerald_ai research bot --rounds 5           # multi-round; stops at saturation
```

### Autonomous discovery bot

Implements rules 4–5 of [`research/automation.txt`](research/automation.txt) — "Build connections between papers" and "Traverse references recursively". The bot crawls the OpenAlex citation graph from seeds (either explicitly provided, derived from a search query, or pulled from the existing brain), scores each candidate with a pure-Python relevance function (keyword overlap with themes + citation overlap with the brain + recency + log-citation count), and accepts those above threshold.

- **No API key required.** Uses OpenAlex's polite pool with `mailto=` identifier (set `EMERALD_OPENALEX_MAILTO` or pass `--mailto`).
- **Polite by default.** 1 req/s, on-disk cache under `research/literature/state/cache/openalex/` (gitignored), exponential backoff on 429.
- **Saturation-aware.** Stops after N consecutive low-score candidates so a runaway crawl can't burn through your quota.
- **Provenance-separated.** Bot-discovered papers go into `research/literature/auto_index.yaml` and their markdown carries `auto_discovered: true` in the frontmatter — the human-curated `research/literature/index.yaml` is never touched.
- **Idempotent.** `research/literature/state/discovery_seen.json` records every external ID ever examined (accepted, rejected, or errored) so reruns skip them.

Typical workflow:

```bash
# 1. Seed from search (one-time bootstrap, no openalex_id required)
python -m emerald_ai research discover --query "explainable credit scoring green loans" --max 5

# 2. Now that the brain has OpenAlex IDs, recurse depth=2 from them
python -m emerald_ai research discover --depth 2 --max 20

# 3. Re-run the engine to ingest the new paper sidecars into state
python -m emerald_ai research run
```

### Operating rules (enforced by the engine + the tests in `tests/test_literature_brain.py`)

- **Never re-process** already-analysed papers without `--force` — rule 3 of the spec.
- **Never invent citations** — wiki-link edges only resolve between keys present in `index.yaml`. Orphan edges fail CI.
- **Always mark uncertainty** — every field carries a confidence; placeholder citations carry a `verified: false` flag and a `search_query` hint.
- **Markdown is the source of truth.** JSON sidecars regenerate; hand-edits to JSON are lost on next run.

---

## Regulatory positioning

EMERALD-AI is designed against (not certified against) the following regulatory frameworks:

| Framework | Relevance | Treated in |
|---|---|---|
| EU AI Act (Reg. 2024/1689) — Annex III, Articles 9–15, 61 | Credit scoring is high-risk; mandatory risk mgmt, data governance, transparency, human oversight, accuracy/robustness logging, post-market monitoring | Sections 4.7, 5.10–5.14, 5.16 |
| FCA Consumer Duty (PS22/9) | Outcome-based; explainability + consumer-support obligations | Sections 4.7, 5.11, 5.14 |
| EBA Guidelines on Loan Origination & Monitoring (EBA/GL/2020/06) | Sector-specific model robustness + explainability for loan-originating institutions | Section 4.7 |
| UK GDPR / Equality Act 2010 | Data privacy + indirect-discrimination protection | Section 5.16 |
| EU Taxonomy (Reg. 2020/852), Climate Bonds Std v4, Green Loan Principles 2023 | Definitional context for "green" labelling | Section 4.5 |

---

## Reproducibility

- Python deps pinned in `uv.lock` (deterministic resolver).
- Data + models versioned with DVC (introduced once implementation begins).
- Experiment runs tracked in MLflow with hyperparameter, code-version, and RNG-seed lineage.
- `python -m emerald_ai reproduce` will re-run the full pipeline from raw data to scored test set in ≤ 8 hours wall-clock on the target hardware (Google Colab Pro+ A100 + Warwick HPC CPU).
- Each model card and datasheet ([Gebru et al., 2021](research/literature/index.yaml)) regenerated automatically on each merge to `main`.

---

## Recent activity

```
(uncommitted, 2026-05-20)  §5.14 risk-band re-calibration — percentile cut-offs
            ↳ Symptom: under hard-coded thresholds (0.5 / 0.8) the model
              approved ~99.7% of all applicants and flagged ~0% of actual
              defaulters as high_risk — the badges carried no information
              because raw probabilities cluster very close to 1 at 0.36%
              prevalence.
            ↳ apps/api/main.py: introduced _risk_band_thresholds() which
              caches percentile-based cut-offs (p5 → high_risk, p20 → watch,
              top 80% → approve) computed from the trained model's score
              distribution on the full labelled supervisory pool. /score,
              /score_raw, /batch_score now use these instead of 0.5/0.8;
              ScoreResponse gained a score_percentile field; /model_card
              exposes the cut-off values + percentile policy.
            ↳ Empirical: under the new bands, full pool splits 80/15/5
              approve/watch/high_risk; **100% of actual defaulters (50/50)
              now land in high_risk**, false-positive high_risk on repayers
              4.66%. The hard 0.5/0.8 cut-offs flagged ~0% of defaults.
            ↳ apps/web/src/views/SinglePredict.tsx: badge now shows the
              applicant's percentile rank against the historical pool, with
              a heads-up help-card explaining why raw probabilities cluster
              high. apps/web/src/views/AboutModel.tsx: new "Risk-band
              cut-offs" table on the algorithm card showing the actual
              numbers in use.
            ↳ READMEs refreshed.

(uncommitted, 2026-05-20)  §5.14 raw-input UX overhaul + new About-the-Model view
            ↳ apps/api/main.py: three new endpoints — /raw_schema (returns the
              raw input columns the persisted preprocessor was fit on, with
              dataset defaults, p05/p25/p75/p95 ranges for numerics, and the
              top-40 categories for each categorical), /score_raw and
              /explain_raw (accept {"raw": {col: value}} payloads, build a
              one-row DataFrame, run preprocessor.transform(), then score /
              explain). /model_card extended with algorithm_label +
              algorithm_plain (e.g. "XGBoost — gradient-boosted decision
              trees" + a plain-English description), headline_raw_features
              (the basics the simple form starts with), and an 8-step
              training_pipeline narrated in both plain and technical register.
            ↳ apps/web/src/views/SinglePredict.tsx: rewritten end-to-end.
              Users now type real values (FICO 720, Revenue $350k, industry
              dropdown for "Retail Trade", etc.) — the standardised-z-score
              form is gone. Basic mode shows the 9 headline raw fields;
              "Show advanced fields" expands to every preprocessor input.
              Numeric inputs show the dataset's p25–p75 typical range under
              the field; categoricals render as <select> with the dataset's
              top-40 levels.
            ↳ apps/web/src/views/AboutModel.tsx (new): algorithm card with
              the family name + plain-English description, the headline-raw
              feature table with units and typical ranges, the top-15
              processed-feature importances from /global_importance, the
              eight-step training pipeline narrated twice (Plain English /
              Technical toggle), and a governance & regulatory-alignment
              card.
            ↳ apps/web/src/App.tsx + Welcome.tsx: new view wired into the
              sidebar (🧠 About the Model) and surfaced as the first tile +
              first walkthrough step on Home.
            ↳ READMEs (top-level + apps/web/) refreshed to mirror the new
              endpoints, the new view, and the raw-input pivot.

(uncommitted, 2026-05-18)  §5.14 lending-officer console — React SPA + 4 new API endpoints
            ↳ apps/api/main.py: extended from 4 endpoints to 8. New:
              /portfolio (KPI aggregates), /global_importance (top-K
              permutation importance), /fairness_audit (structured JSON),
              /batch_score (real CSV upload → scored CSV download, replaces
              the prior 501 stub). CORS middleware enabled for localhost dev.
              ModelCard schema gained feature_names + best_family fields.
            ↳ apps/web/: React 18 + Vite + TypeScript SPA scaffolded from
              scratch (no Tailwind / state-mgmt lib — just useState + CSS).
              5 views in src/views/: Dashboard, SinglePredict, BatchScore,
              ShapExplorer, FairnessPanel. Typed fetch wrapper in api.ts
              with Vite proxy /api -> localhost:8000. Dark-theme CSS.
              `npm run build` produces 37 modules / 160KB / 51KB gzipped.
            ↳ apps/web/README.md: full local-dev + deployment instructions.
            ↳ Tests: TypeScript compile clean; production build succeeds.
              Python suite unchanged at 108 passing.
            ↳ README: stage table marks `Web app — FastAPI backend` and
              `Web app — React SPA frontend` both ✅ Done; traceability
              gains a §5.14 row; this entry.

(uncommitted, 2026-05-18)  §5.8 → §5.14 — full pipeline from models to FastAPI
            ↳ src/emerald_ai/models/{linear,trees}.py: six classifier factories
              (lr_l1, lr_l2, svm_rbf, rf, xgboost; lightgbm + catboost gated
              on optional deps with informative ImportError; mlp + ft_transformer
              deferred to v0.5 — require torch). FACTORIES registry +
              `make_model()` dispatcher + `available_models()` helper.
            ↳ src/emerald_ai/training/cv.py: nested-CV training harness.
              Outer StratifiedKFold + inner RandomizedSearchCV (proposal's
              full Optuna budget deferred). emit_report() ->
              data/governance/training_report.md. Per-fold best_params + OOF
              predictions returned for downstream calibration / stacking.
            ↳ src/emerald_ai/calibration/{calibrators,conformal}.py: Platt /
              isotonic / temperature scaling + SplitConformal (marginal
              finite-sample exact) + MondrianConformal (class-conditional
              diagnostic) + bootstrap_class_conditional_coverage(). The
              v0.4.1 framing (marginal headline / Mondrian diagnostic /
              interval width NOT primary) is wired structurally.
            ↳ src/emerald_ai/explain/{shap_engine,counterfactual}.py:
              global permutation importance + local coefficient/importance
              proxy + nearest-feature greedy counterfactual. TreeSHAP /
              KernelSHAP / DiCE / Quantus deferred (require shap, dice-ml).
            ↳ src/emerald_ai/fairness/audit.py: per-axis DP / EO / PP /
              ECE gaps, manual implementation (no AIF360 dep). Selbst et al.
              (2019) traps documented in the emitted report.
            ↳ src/emerald_ai/eval/metrics.py: pr_auc_minority,
              within_minority_ece, recall_at_top_decile (primary tier);
              roc_auc, ks_statistic, f1_at, brier_score, ece,
              matthews_corrcoef (secondary); delong_test +
              paired_bootstrap for statistical comparison. Raw accuracy
              deliberately excluded (constant predictor = 99.64%).
            ↳ apps/api/main.py: /healthz + /model_card + /score + /explain
              wired against the persisted artefacts; /batch_score and
              /fairness_audit stubbed pending CSV pipeline. Lazy artefact
              loading returns 503 with remediation hint when models/* missing.
            ↳ CLI: `python -m emerald_ai {train,evaluate,explain,audit}`
              now run end-to-end and emit governance reports. The pre-existing
              evaluate/explain/audit stubs were replaced.
            ↳ Real-data findings (3 families, 3 outer folds, 4 search
              candidates per fold — reduced from §5.9's full grid for runtime):
                • XGBoost wins (mean PR-AUC ≈ 0.10 OOF, ~26× random baseline
                  at 0.36% prevalence).
                • Top-3 by permutation importance: Lender / Prod Rank /
                  Closed Max Term — deal-context dominates borrower-attribute.
                • At threshold 0.5 the model approves ~100% of applicants in
                  every group → fairness audit needs lower thresholds to be
                  informative; flagged for v0.5 patch.
            ↳ tests/test_models_calibration_eval.py: 18 new synthetic-data
              tests covering model factories, calibration ECE reduction,
              SplitConformal marginal coverage, Mondrian per-class
              coverage, global/local explainability, fairness gaps,
              DeLong test, paired bootstrap CIs. Suite 90 -> 108 passing.

bec29fb  feat(features+training): §5.6 selection + §5.7 imbalance harness + traceability
            ↳ src/emerald_ai/features/selection.py: two-stage selection.
              Stage 1 MI filter (drop bottom decile). Stage 2 bootstrap-
              stability with RandomForest mean-decrease-impurity across
              30 stratified resamples (Boruta-light; SHAP variant deferred
              to post-§5.8). Real-data: 90 -> 71 -> 20 (Credit Score,
              Revenue, Payback, Payment Amount, Amount Funded, ...).
            ↳ src/emerald_ai/training/imbalance.py: three-strategy
              comparison harness (no_resample / class_weighted / smote)
              on LogReg baseline under stratified 5-fold CV.
              within-minority-ECE metric implemented per v0.4.1 §5.10.
              Real-data: SMOTE wins joint score (0.058) but all three
              ECE ≈ 0.32 — dissertation-grade evidence that resampling
              alone does not solve calibration; the §5.10 conformal +
              calibration layer remains load-bearing.
            ↳ tests/test_features_selection.py + test_imbalance.py:
              14 new tests (signal-vs-noise discrimination, Wilson CIs,
              SMOTE on small-N, joint-score selection). Suite 76 -> 90.
            ↳ CLI: `python -m emerald_ai select` + `imbalance` wired.
            ↳ README traceability table extended with two new rows.

2b337e9  feat(features): preprocessing pipeline (§5.5) + code-traceability index
            ↳ src/emerald_ai/features/pipeline.py: full ColumnTransformer
              implementation. Stage 1 drop-list (>40% miss + EDA-flagged
              time-leaking); Stage 2 median impute + missing-indicators;
              Stage 3 one-hot (≤10 levels) + TargetEncoder (Industry,
              Borrower State); Stage 4 StandardScaler. fit_transform_with_audit
              + emit_report → data/governance/preprocess_report.md.
            ↳ Real-data run: 90 input cols (post-EDA permitted) -> 90 output
              features on 14,022 labelled rows. Drops 8 high-miss columns
              (Term/APR/Factor + the five 100%-missing-but-permitted —
              App Out, 1st Online Engmnt, MCCC, Lender Identifier, Published),
              2 time-leaking (Start Month, Start Annual Day), 35 datetime
              (deferred to §5.6).
            ↳ tests/test_features_pipeline.py: 10 tests covering drop-list
              triggers, low/high-card split, fit-transform invariants
              (standardised numerics, missing-indicator dimensionality),
              unseen-level safety on both encoders. Suite 66 -> 76 passing.
            ↳ src/emerald_ai/cli.py: `python -m emerald_ai preprocess`
              replaces the prior NotImplementedError stub.
            ↳ README.md: new "Traceability" section indexing every empirical
              finding -> proposal § -> code module -> governance artefact
              (the "code brain" answer to the literature brain).

74a1345  feat(eda): four-layer EDA module on 90 permitted features (§5.4)
            ↳ univariate / bivariate-MI / segment-level Wilson CIs / quarterly
              PSI. Surfaced: firearms 9.09% (small-N), WV/AR/CT/IN/SC at
              1.5-2.1%, material PSI on Lender Identifier (13-14) / Published
              (10-11) / Attempted-Assigned (8-9); pure-time PSI ~16 by
              construction. 11 new tests; suite 55 -> 66 passing.

5efcec4  chore(brain): bot crawl +110 entries; refresh state + README log
            ↳ auto_index.yaml 46 -> 156 entries; ~92 new bot-stub paper
              sidecars (auto_discovered/verified:false); state/* regenerated.

4e9b25f  feat(data): Gebru datasheet + leakage-audit tests + load helpers
            ↳ data/governance/datasheet.md (7 sections, Gebru et al. schema);
              tests/test_data_load.py + test_leakage_audit.py; suite
              21 -> 55 passing.

ae8aa1f  docs(proposal): v0.4 datasheet patch + v0.4.1 small-N reframe + 3K
            ↳ §4.4 0.36% prevalence recalibration; §5.2 label counts +
              paidOff-only headline; §5.3 90/76 split + MCCC transparency
              note; §5.5 drop-list casualties; v0.4.1 conformal claim split
              (marginal headline / Mondrian diagnostic / width excluded);
              3K-condensed companion with 30-ref bibliography.

8ff6fab  revamp README + research-to-brain integration + v0.3 proposal
            ↳ bot discovery grew brain 82 -> 218 papers (76 curated + 142 bot);
              14 promoted into index.yaml with curated metadata;
              proposal_third_draft.docx rebuilt (~8,500 words, 74 refs)
              — adds climate-credit channel (§4.5), opacity framing (§4.6),
              sociotechnical fairness critique (§4.7), reject-inference
              treatment (§4.4/§5.2), MLOps deployment evidence (§5.14);
              first ML deliverable: data/load.py + leakage_audit.py wired up,
              feature_catalogue.yaml emitted to data/governance/
              (90 permitted features / 76 forbidden; class balance 0.36% delinquent).

a9313eb  readme update
            ↳ live-counts refresh and commit-log housekeeping after the
              query-driven bot run.

54ddb06  docs(readme): update live counts + commit log + bot status

e6606f7  add bot for query paper
            ↳ user-driven bot run: 15 new papers discovered (62 -> 82) and
              committed to research/literature/auto_index.yaml

e101681  fix(tests): isolate State.PAPERS_JSON_DIR + clean up leaked fixtures
            ↳ post-mortem on the previous commit; test isolation now patches
              all module-level path constants so fixtures can't leak

4597838  fix(research-bot): tolerate null fields in OpenAlex responses + survive crashes
            ↳ fixed `AttributeError: 'NoneType' object has no attribute 'get'`
              hit on arXiv preprints; added 2 regression tests; made bot
              crash-resistant by writing .md/.json/.yaml + discovery_seen.json together

5306f34  refactor: restructure top-level dirs from 10 -> 7 via apps/ and research/ groupings
            ↳ frontend + backend grouped under apps/; literature, notebooks,
              scripts, automation.txt grouped under research/

ef6d7ee  feat(research): autonomous research-automation engine per research_automation.txt
            ↳ ResearchEngine + OpenAlex source + relevance scoring + BFS
              discovery + idempotent state persistence

90edcdb  Initial scaffold: EMERALD-AI dissertation project (v0.1.0)
            ↳ initial layout, MIT license, gitignore for proprietary data,
              CI workflow, Python package skeleton, FastAPI stub
```

Each commit is a self-contained, testable step. Run `git log --stat` for file-by-file detail.

---

## Contributing & questions

This is an academic dissertation; external contributions are not invited during the marking period. After submission, the repo will accept issues and PRs under the standard MIT terms.

For questions about the research, contact the author via the channel on the dissertation cover sheet.

---

## License

- **Code:** MIT — see [`LICENSE`](LICENSE).
- **Dataset:** Proprietary; redistribution prohibited. See [`data/README.md`](data/README.md).
- **Documentation & figures:** CC BY 4.0 (where compatible with cited sources).

---

## Citation

If you reference this work, please use the metadata in [`CITATION.cff`](CITATION.cff). A BibTeX entry will be added on dissertation submission.
