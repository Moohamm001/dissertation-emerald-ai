# How to Run EMERALD-AI

Operational guide for every piece of the project that can be invoked today. Sections are independent — jump to the one you need.

> The dissertation is at **proposal + scaffold** stage. Subsystems are marked **WORKS** (runs end-to-end now) or **STUB** (raises `NotImplementedError` until the ML pipeline is implemented).

## How to invoke commands (read this once)

Three equivalent forms — pick the one that fits your environment. Every example below uses `python -m emerald_ai <command>`, but you can substitute either of the others.

| Form | Works without install? | Works on Windows? | Recommended for |
|---|---|---|---|
| `python -m emerald_ai <command>` | No (needs `pip install -e .`) | Yes | **Most users.** Cross-platform. |
| `python emerald.py <command>` | Yes — only needs runtime deps | Yes | Quick experiments from a fresh clone. |
| `emerald <command>` | No — and needs `Scripts/` on PATH | Sometimes | Shortest form once everything is wired. |
| `make <target>` | Needs Make installed | No (without WSL) | Unix users who like Make. Thin wrapper. |

If you're on Windows and `make` isn't a familiar tool, ignore the Makefile entirely. Everything below works with `python -m emerald_ai …`.

---

## Contents

1. [Prerequisites](#1-prerequisites)
2. [Install](#2-install)
3. [Verify the install](#3-verify-the-install)
4. [Research automation — the literature brain](#4-research-automation--the-literature-brain) **WORKS**
5. [Proposal authoring — rebuild the .docx](#5-proposal-authoring--rebuild-the-docx) **WORKS**
6. [Tests and code quality](#6-tests-and-code-quality) **WORKS**
7. [Backend API — FastAPI](#7-backend-api--fastapi) **PARTIAL** (only `/healthz`)
8. [Frontend — React SPA](#8-frontend--react-spa) **STUB** (README only)
9. [ML pipeline — train / evaluate / explain / audit](#9-ml-pipeline--train--evaluate--explain--audit) **STUB**
10. [End-to-end reproduction](#10-end-to-end-reproduction) **STUB** (wires the above)
11. [Common workflows](#11-common-workflows)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Prerequisites

| Tool | Required for | Minimum | Notes |
|---|---|---|---|
| Python | Everything Python | 3.11 | Project pinned via `.python-version`; 3.12/3.13 also fine |
| pip *or* uv | Install deps | latest | `uv` is preferred (faster, lockfile-resolved); pip works |
| make | Canonical entrypoints | any | Optional — every target can also be invoked directly |
| git | Version control | 2.30+ | Project is git-initialised on branch `main` |
| Node + pnpm | Frontend (later) | 20 + 9 | Not required until the React SPA scaffold lands |
| Graphviz `dot` | Render citation graph SVG | 2.40+ | Only needed for `emerald research graph` SVG rendering |
| Word / LibreOffice | View proposal `.docx` | any | Optional viewer |

Working directory throughout this guide: `X:\Dissertation Warwick` (Windows) or whatever you cloned to.

---

## 2. Install

### Option A — uv (recommended)

```bash
uv sync --extra dev --extra docs
```

This creates `.venv/` with deps resolved from `pyproject.toml`. To install the full ML/DL/XAI/MLOps stack:

```bash
uv sync --extra all
```

### Option B — pip

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# Bash / WSL / macOS
source .venv/bin/activate

pip install -e ".[dev,docs]"
```

### Optional extras

| Extra | What it adds |
|---|---|
| `ml` | scikit-learn, imbalanced-learn, XGBoost, LightGBM, CatBoost, Optuna, MAPIE |
| `dl` | PyTorch, rtdl (FT-Transformer) |
| `xai` | SHAP, LIME, DiCE, AIF360, Quantus |
| `mlops` | MLflow, DVC, Evidently, Prometheus client |
| `api` | FastAPI, uvicorn |
| `docs` | python-docx, pypdf, Jupyter, matplotlib, seaborn |
| `dev` | pytest, ruff, black, mypy, pre-commit |
| `all` | everything above |

Install any combo: `pip install -e ".[ml,xai,dev]"`.

### Optional — git hooks

```bash
pre-commit install
```

Installs ruff + black + nbstripout + gitleaks on every commit.

---

## 3. Verify the install

```bash
python -m emerald_ai version           # → EMERALD-AI v0.1.0
python -m emerald_ai --help            # lists every subcommand
python -m emerald_ai research --help   # lists run / status / show / graph
python -m emerald_ai test              # → 14 passed
python -m emerald_ai check             # lint + typecheck + test in one shot
```

If `emerald` is not found after install, your Python `Scripts/` directory is not on PATH. Workaround:

```bash
python -m emerald_ai.cli version
```

---

## 4. Research automation — the literature brain

**WORKS.** Implements the eight-step workflow in [`research/automation.txt`](research/automation.txt).

### One-shot sweep

```bash
python -m emerald_ai research run
# Unix shortcut: make research
```

Idempotent — re-running over an unchanged brain is a no-op except for the manifest timestamp.

### See current state

```bash
python -m emerald_ai research status
# Unix shortcut: make research-status
```

Expected output:

```
Brain state — last run 2026-05-17T19:44:12+00:00
  papers     : 62
  citations  : 80
  questions  : 15
  authors    : 179
  methods    : 22
  datasets   : 9
  keywords   : 12
```

### Inspect a single paper's structured record

```bash
python -m emerald_ai research show chen2016xgboost
```

Prints the full JSON sidecar (10-field schema + provenance).

### Force re-process every paper

```bash
python -m emerald_ai research run --force
# Unix shortcut: make research-force
```

Use after you change the parser, the schema, or paper notes en-masse.

### Render the citation graph

```bash
python -m emerald_ai research graph
# writes research/literature/state/citations.dot

# Render to SVG (needs Graphviz):
dot -Tsvg research/literature/state/citations.dot -o research/literature/state/citations.svg
```

### Extend the brain — manual path

1. Add a new entry to `research/literature/index.yaml` (key, title, authors, year, themes, relevance, verified, search_query).
2. If `relevance` ≥ high, also add a `research/literature/papers/<key>.md` note. Easiest: add a dict to `research/literature/build_papers.py` and run `python -m emerald_ai literature`.
3. Run `python -m emerald_ai research run` — the new paper is picked up and added to the graph / rollups automatically.
4. Run `python -m emerald_ai test` — integrity tests catch dangling refs and missing sidecars.

Hand-edit the markdown + YAML. **Never hand-edit `research/literature/state/*.json`** — they regenerate.

### Extend the brain — autonomous path (the discovery bot)

```bash
# Bootstrap from a free-text search (no openalex_id needed in your brain yet)
python -m emerald_ai research discover --query "explainable green credit scoring" --max 5

# Recurse from your existing brain (uses any entry with an openalex_id as a seed)
python -m emerald_ai research discover --depth 2 --max 20

# From a specific seed (OpenAlex Work ID)
python -m emerald_ai research discover --seed W2964121823 --depth 3 --max 30

# Multi-round; stops at global saturation
python -m emerald_ai research bot --rounds 5 --depth 2 --max 10
```

The bot:
- Uses **OpenAlex** — free, no API key. Set `EMERALD_OPENALEX_MAILTO=you@example.com` or pass `--mailto` to join the polite pool (higher rate limits).
- Throttles to **1 req/s** with on-disk cache under `research/literature/state/cache/openalex/` (gitignored).
- Writes new papers to **`research/literature/auto_index.yaml`** (separate from the human-curated index) and **`research/literature/papers/<key>.md`** with `auto_discovered: true` in the frontmatter.
- Tracks every external ID examined in **`research/literature/state/discovery_seen.json`** so re-runs skip them — idempotent.
- Scores candidates with a **pure-Python relevance function** (keyword + citation overlap + recency + log-citation count). No LLM, no API key.
- **Stops at saturation** — after N consecutive low-score candidates (default 8), the loop exits early.

After the bot accepts new papers, run `python -m emerald_ai research run` to ingest the new sidecars into `research/literature/state/`.

**Reviewing bot output.** Auto-discovered papers have stub paper bodies with `_(human review pending)_` placeholders. Promote them by editing the `.md` and setting `verified: true` in `auto_index.yaml`, or move them to `index.yaml` for permanent inclusion.

---

## 5. Proposal authoring — rebuild the `.docx`

**WORKS.** The proposal is generated from a `python-docx` script so it stays diffable.

### Rebuild

```bash
python -m emerald_ai proposal
# Unix shortcut: make proposal
# Direct alternative: cd docs/proposal && python build_proposal.py
```

Output: `docs/proposal/proposal_second_draft.docx` (overwrites in place).

> **Close the docx in Word first** or you get `PermissionError: proposal_second_draft.docx`. Word holds an exclusive lock while the file is open.

### Edit workflow

| Change scope | Edit |
|---|---|
| Major restructuring | `docs/proposal/build_proposal.py`, then `python -m emerald_ai proposal` |
| Theme-level prose (§4 lit-review) | `research/literature/themes/4.X-*.md` (source of truth) → mirror into `build_proposal.py` |
| New citation | `research/literature/index.yaml` (+ optional `papers/<key>.md`), then cite in the proposal text |
| New gap surfaced | `research/literature/gaps.md` — research engine picks it up on next `python -m emerald_ai research run` |

---

## 6. Tests and code quality

**WORKS.**

### Run everything

```bash
python -m emerald_ai check                  # lint + typecheck + test
# Unix shortcut: make check
```

### Individually

```bash
python -m emerald_ai lint                   # ruff + black --check
python -m emerald_ai format                 # auto-fix with ruff + black
python -m emerald_ai typecheck              # mypy strict
python -m emerald_ai test                   # pytest with coverage
python -m emerald_ai test --fast            # skip slow + integration tests
python -m emerald_ai test --cov             # also open HTML coverage report
```

### Current test count

```
tests/test_smoke.py             4 tests   (package + subpackages + paths + CLI)
tests/test_literature_brain.py  9 tests   (brain integrity + state integrity + idempotency)
                                ─────
                               13 tests   (you'll see 14 because one test is parameterised)
```

CI runs the same suite on push + PR via `.github/workflows/ci.yml` on Python 3.11 and 3.12.

---

## 7. Backend API — FastAPI

**PARTIAL.** Only `/healthz` is implemented; the scoring/explain/audit endpoints are planned.

### Run the dev server

```bash
python -m emerald_ai api
# With custom host/port:
python -m emerald_ai api --host 127.0.0.1 --port 8080
# Unix shortcut: make api
```

Then:
- http://localhost:8000/healthz — `{"status": "ok", "version": "0.1.0"}`
- http://localhost:8000/docs — interactive Swagger UI

### Planned endpoints (proposal §5.14)

| Method | Path | Status |
|---|---|---|
| GET  | `/healthz` | ✓ implemented |
| POST | `/score` | planned |
| POST | `/batch_score` | planned |
| POST | `/explain` | planned |
| GET  | `/portfolio` | planned |
| GET  | `/fairness_audit` | planned |
| GET  | `/model_card` | planned |

---

## 8. Frontend — React SPA

**STUB.** `apps/web/` contains only `README.md`; the scaffold lands once the API serves real predictions.

When scaffolded:

```bash
cd apps/web
pnpm install
pnpm dev          # opens http://localhost:5173
```

Reads the API base URL from `VITE_API_BASE_URL` (default: `http://localhost:8000`).

---

## 9. ML pipeline — train / evaluate / explain / audit

**STUB.** Every command raises `NotImplementedError` and points at the proposal section that defines its contract.

### Prerequisite — install the dataset

The 2019 All Funded Green Loan `.xlsx` is gitignored (proprietary). Place at:

```
data/raw/All_Funded_2019_Green Loan.xlsx
```

See [`data/README.md`](data/README.md) for how to obtain it.

### CLI commands (all currently stubs)

```bash
python -m emerald_ai eda                                # proposal §5.4
python -m emerald_ai preprocess                         # §5.3, §5.5, §5.7
python -m emerald_ai train --model xgboost              # §5.8, §5.9
python -m emerald_ai train --model all                  # all six families
python -m emerald_ai evaluate                           # §5.10, §5.13
python -m emerald_ai explain --applicant-id 42          # §5.11
python -m emerald_ai audit --axis industry              # §5.12
python -m emerald_ai audit --axis all                   # all proxy axes
```

### Implementation order (mirrors proposal §5)

1. `src/emerald_ai/data/load.py` + `leakage_audit.py` → §5.2–5.3
2. `src/emerald_ai/features/pipeline.py` + `selection.py` → §5.5–5.6
3. `src/emerald_ai/models/xgboost_model.py` (primary candidate first) → §5.8
4. `src/emerald_ai/training/cv.py` + `tune.py` → §5.9
5. `src/emerald_ai/calibration/`, `explain/`, `fairness/`, `eval/` → §5.10–5.13
6. Wire each into `src/emerald_ai/cli.py` (replace `NotImplementedError` with real calls)
7. Add tests under `tests/` mirroring the module layout
8. Notebooks in `research/notebooks/` follow the same order (`01_eda.ipynb` → `08_fairness_audit.ipynb`)

---

## 10. End-to-end reproduction

**STUB.** Wires §9 commands into one entrypoint.

```bash
python -m emerald_ai reproduce                # cross-platform
# Or, with Make / Bash:
make reproduce
bash research/scripts/reproduce.sh

Target: ≤ 8 hours wall-clock on Google Colab Pro+ A100 (DL models) + Warwick HPC CPU (GBDT models). See proposal §5.16.

---

## 11. Common workflows

### "I just cloned the repo"

```bash
pip install -e ".[dev,docs]"
pytest                          # confirms scaffold integrity
make research-status            # see the brain
```

### "I added a paper"

```bash
# 1. Edit research/literature/index.yaml (+ optionally papers/<key>.md or build_papers.py)
make literature                 # regenerates papers/*.md if you edited build_papers.py
make research                   # picks up new paper, updates graph + rollups
pytest tests/test_literature_brain.py  # confirms integrity
git add research/literature/ && git commit -m "docs(lit): add <key>"
```

### "I updated a theme paragraph"

```bash
# 1. Edit research/literature/themes/4.X-*.md  (the source of truth)
# 2. Mirror the change into docs/proposal/build_proposal.py
make proposal                   # rebuild the docx (close Word first!)
git add research/literature/ docs/proposal/ && git commit -m "docs(proposal): tighten §4.X"
```

### "I started implementing the ML pipeline"

```bash
# 1. Drop the .xlsx into data/raw/
# 2. Implement a module, e.g. src/emerald_ai/data/load.py
# 3. Add a test under tests/test_data_load.py
# 4. Wire into emerald_ai/cli.py (replace NotImplementedError)
make check                      # lint + typecheck + test
git add -p && git commit -m "feat(data): wire load_raw + label_creditworthiness"
```

### "I want a visual of how papers cite each other"

```bash
make research-graph
dot -Tsvg research/literature/state/citations.dot -o citations.svg
# open citations.svg in any browser
```

---

## 12. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `emerald: command not found` | Python Scripts dir not on PATH | Use `python -m emerald_ai ...` or `python emerald.py ...` — both work without the `emerald` script |
| `python -m emerald_ai proposal` → `PermissionError: proposal_second_draft.docx` | Word has the file open | Close the file in Word, retry |
| `pytest` → `ModuleNotFoundError: emerald_ai` | Editable install missing | `pip install -e ".[dev,docs]"` |
| `pytest` → `ModuleNotFoundError: typer` | dev/docs extras not installed | `pip install -e ".[dev,docs]"` |
| `python -m emerald_ai research run` → 0 analysed papers | Paper markdowns indented (old bug) | `python -m emerald_ai literature` to regenerate, then `python -m emerald_ai research run --force` |
| `dot: command not found` when rendering graph | Graphviz not installed | Install Graphviz from https://graphviz.org/download/ |
| `git status` shows `~$*.docx` files | MS Office lock files | Already gitignored — they'll never be staged |
| `git status` shows the `.xlsx` | The dataset is being tracked accidentally | Confirm `.gitignore` has `*.xlsx` and `data/raw/**`; if already staged: `git rm --cached "data/raw/..."` |
| CI failing on `mypy strict` | New code missing type annotations | `python -m emerald_ai typecheck` locally, add annotations, push again |
| `python -m emerald_ai research run` fails after pulling new code | Schema changed | `python -m emerald_ai research run --force` to re-process under the new schema |
| Notebook diffs huge | nbstripout not installed | `pre-commit install` once, then commits auto-strip outputs |

If something else breaks, run `python -m emerald_ai check` first — it surfaces lint/type/test failures in one go.
