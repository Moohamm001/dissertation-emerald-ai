# EMERALD-AI

> **Explainable, calibrated, audit-ready machine learning for green-loan credit scoring.**
> MSc Applied AI dissertation — University of Warwick. License MIT · Python 3.11
> Stage: **proposal + scaffold + literature brain + autonomous research bot.** ML pipeline begins after proposal approval.

**New here?** → [**QUICKSTART.md**](QUICKSTART.md) (5-minute hands-on tour)
**Need a specific command?** → [**HOWTORUN.md**](HOWTORUN.md) (full operations reference)
**Just want to read the research?** → [`docs/proposal/proposal_second_draft.docx`](docs/proposal/)

---

## Project status (live)

```
  papers in brain   : 108      (62 human-curated + 46 bot-discovered via OpenAlex)
  citation edges    :  80
  research questions:  15      (auto-generated from gaps.md)
  authors indexed   : 1087
  methods detected  :  22      (XGBoost, LightGBM, CatBoost, SHAP, DiCE, conformal, ...)
  datasets detected :   9      (COMPAS, FICO, Adult, German Credit, Lending Club, ...)
  themes drafted    :   8/8    (lit-review sections 4.1-4.8)
  tests passing     :  21/21   (smoke + brain integrity + discovery bot)
  top-level dirs    :   7      (.github, apps, src, research, docs, data, tests)
  commits on main   :   6
```

Numbers refresh with `python -m emerald_ai research status`.

---

## What this project is, in 30 seconds

Green-loan origination has grown at >40% CAGR since 2018, but credit-risk infrastructure still uses scorecards designed for conventional consumer credit. EMERALD-AI is an end-to-end ML framework that benchmarks modern tabular learners on a real 2019 green-loan dataset (14,135 transactions × 166 features), integrates **calibration**, **distribution-free uncertainty**, **multi-method explainability**, and a **fairness audit** aligned with the **EU AI Act (Annex III)** and **FCA Consumer Duty** — delivered as a full-stack decision-support platform for lending officers.

It occupies an explicit literature gap: no published work simultaneously delivers, on real green-loan data, all five of (i) modern tabular benchmarking under identical preprocessing, (ii) post-hoc calibration + conformal uncertainty, (iii) multi-method XAI with empirical fidelity validation, (iv) fairness audit on green-lending-appropriate proxies, and (v) a deployable lending-officer interface.

---

## What works today

> Every command runs the same on Windows, macOS, and Linux — no Make required. Use `python -m emerald_ai <command>` (or `python emerald.py <command>` from a fresh clone with no install).

| Subsystem | State | Try it |
|---|---|---|
| Literature brain (82 refs, 80-edge citation graph, 15 research questions) | **WORKS** | `python -m emerald_ai research status` |
| Autonomous research engine (idempotent, 10-field schema, audit-trail) | **WORKS** | `python -m emerald_ai research run` |
| **Autonomous discovery bot** (OpenAlex crawler, null-tolerant, crash-resistant, no API key) | **WORKS** | `python -m emerald_ai research discover --query "explainable green credit scoring"` |
| Proposal authoring pipeline (python-docx → reproducible .docx, 6,750 words, 61 refs) | **WORKS** | `python -m emerald_ai proposal` |
| Tests + CI (ruff + black + mypy + pytest on 3.11/3.12) — 21 passing | **WORKS** | `python -m emerald_ai check` |
| Cross-platform CLI (Windows / macOS / Linux, no Make required) | **WORKS** | `python -m emerald_ai --help` |
| FastAPI backend | **PARTIAL** | `python -m emerald_ai api` (only `/healthz` for now; rest scaffolded) |
| ML pipeline (preprocess / train / evaluate / explain / audit) | **STUB** | CLI raises `NotImplementedError` with a pointer to the relevant proposal section |
| React SPA frontend | **STUB** | scaffold deferred until the API serves real predictions |

---

## Architecture at a glance

```
┌──────────────────────────┐    ┌─────────────────────────────────────────────────────────┐
│  data/raw/*.xlsx         │    │  research/literature/   (KNOWLEDGE BRAIN  — WORKS)     │
│  proprietary, gitignored │───▶│  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  14,135 × 166 features   │    │  │ themes/ │  │ papers/  │  │ gaps.md  │  │ state/   │ │
└──────────────────────────┘    │  │ 8 files │  │ 49 .md   │  │ 15 gaps  │  │ JSON     │ │
              │                 │  └─────────┘  │ + .json  │  └──────────┘  │ graph,   │ │
              │                 │  index.yaml   └──────────┘                │ rollups, │ │
              │                 │  + auto_index.yaml (bot)                  │ RQs      │ │
              │                 │  (62 manual + 20 bot = 82 refs)           └──────────┘ │
              │                 │                ▲              ▲                          │
              ▼                 │                │              │ BFS crawl, threshold     │
┌──────────────────────────────┐│                │   ┌──────────┴──────────────────────┐  │
│  src/emerald_ai/  (PACKAGE)  ││                │   │  OpenAlex (free, no API key)    │  │
│                              ││                │   │  1 req/s · on-disk cache        │  │
│  data/      preprocess  STUB ││                │   │  null-tolerant · crash-resistant│  │
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
   │  -> second_draft.docx │                      └────────────────────────────┘            │
   └───────────────────────┘                                                                │
                                                                                            │
                          [ tests/ 21 passing : smoke + brain integrity + discovery bot ]
```

---

## Where to look for X

| If you want to find… | Look in |
|---|---|
| The dissertation research design | `docs/proposal/proposal_second_draft.docx` |
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

Full methodology in [`docs/proposal/proposal_second_draft.docx`](docs/proposal/), §5.

---

## Literature brain

The repo contains a structured knowledge base under [`research/literature/`](research/literature/) — not a static bibliography, but a queryable, versioned representation of the lit review intended to evolve through the project:

- `research/literature/BRAIN.md` — usage rules
- `research/literature/index.yaml` — 62 human-curated references (themes, relevance, verification status, search-query hints for placeholder citations)
- `research/literature/auto_index.yaml` — 46 references added by the discovery bot; separated so the bot never touches the human-curated index
- `research/literature/themes/4.1`–`4.8.md` — eight argumentative-spine files mirroring the proposal's literature-review subsections
- `research/literature/papers/<key>.md` — 75 paper notes (34 human-written + 41 bot-stubbed; claims, method, EMERALD-AI relevance, limitations, links)
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
Brain state - last run 2026-05-18T08:13:29+00:00
  papers     : 108     (62 human-curated + 46 bot-discovered)
  citations  : 80
  questions  : 15
  authors    : 1087
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
