# Quickstart — 5 Minutes from Clone to First Run

This walkthrough gets a newcomer producing real output without needing the proprietary dataset. By the end you'll have rebuilt the proposal, run the autonomous research engine, and inspected one paper's structured record.

> **Already past quickstart?** See [`HOWTORUN.md`](HOWTORUN.md) for the full reference.

---

## Minute 0 — clone

```bash
git clone <repo-url> emerald-ai
cd emerald-ai
```

## Minute 1 — install

Pick one. Both produce the same outcome.

```bash
# Option A — pip (universal)
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell
# source .venv/bin/activate       # macOS / Linux / WSL
pip install -e ".[dev,docs]"

# Option B — uv (faster, lockfile-resolved)
uv sync --extra dev --extra docs
```

Expected: one line per package installed, then a prompt. No errors.

---

## Minute 2 — verify the install

```bash
python -m emerald_ai version
```

**Expected output:**
```
EMERALD-AI v0.1.0
```

If that runs, the package is installed correctly.

**Three equivalent ways to invoke any command:**

| Command form | When to use |
|---|---|
| `python -m emerald_ai <cmd>` | **Recommended.** Works after `pip install -e .`. Cross-platform. |
| `python emerald.py <cmd>` | Works without installing the package — just the deps. Cross-platform. |
| `emerald <cmd>` | Shortest, but only works if your Python `Scripts/` dir is on PATH. |

The rest of this guide uses `python -m emerald_ai …`.

```bash
pytest
```

**Expected output (the last line):**
```
14 passed in 0.5s
```

That's 4 smoke tests + 10 literature-brain integrity tests. If they pass, everything is wired correctly.

---

## Minute 3 — meet the literature brain

The project carries a structured knowledge base of 62 references with citation graph, theme analysis, and gap log. Let's look at it.

```bash
python -m emerald_ai research status
```

**Expected output:**
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

Now inspect one paper's full machine-readable record:

```bash
python -m emerald_ai research show chen2016xgboost
```

**Expected output (truncated):**
```json
{
  "key": "chen2016xgboost",
  "title": "XGBoost: A scalable tree boosting system",
  "authors": ["Chen, T.", "Guestrin, C."],
  "year": 2016,
  "venue": "KDD '16, 785-794",
  "contributions": [
    "A scalable gradient-boosting framework combining (a) second-order Newton boosting, ...",
    "Wins or matches state-of-the-art on the majority of Kaggle tabular competitions ..."
  ],
  "weaknesses": [
    "Original paper does not cover monotonic constraints, GPU training, ...",
    "Tree ensembles extrapolate poorly; OOD generalisation is a known weakness ..."
  ],
  "referenced_papers": ["ke2017lightgbm", "lundberg2020trees", "prokhorenkova2018catboost"],
  "themes": ["gbdt-tabular-sota"],
  "confidence": "high",
  "verified": true,
  "status": "analysed"
}
```

The same record exists in human-readable form at `research/literature/papers/chen2016xgboost.md`. Both views are committed; the markdown is the source of truth, the JSON regenerates.

---

## Minute 4 — render the citation graph

```bash
python -m emerald_ai research graph
```

**Expected output:**
```
Wrote research/literature/state/citations.dot  (80 edges)
  Render with: dot -Tsvg research/literature/state/citations.dot -o research/literature/state/citations.svg
```

If you have Graphviz installed, render it:
```bash
dot -Tsvg research/literature/state/citations.dot -o citations.svg
```

Open `citations.svg` in any browser — you'll see how the 62 papers cite each other inside the brain.

---

## Minute 5 — see the proposal

The dissertation proposal is generated from a `python-docx` script so it stays diffable. Rebuild it:

```bash
python -m emerald_ai proposal
```

**Expected output:**
```
cd docs/proposal && python build_proposal.py
OK: proposal_second_draft.docx
```

Open `docs/proposal/proposal_second_draft.docx` in Word or LibreOffice. ~6,750 words, 61 references, eight literature subsections, sixteen methodology subsections.

> **If you get `PermissionError`** — Word already has the file open. Close it and retry.

---

## You've now seen all the working subsystems

| What you ran | What it proved |
|---|---|
| `python -m emerald_ai version` + `pytest` | Package installs and tests pass |
| `python -m emerald_ai research status` | The literature brain is real, populated, and queryable |
| `python -m emerald_ai research show <key>` | Per-paper structured records exist in the 10-field schema |
| `python -m emerald_ai research graph` | The citation graph is built from intra-brain references |
| `python -m emerald_ai proposal` | The dissertation proposal regenerates from source |

---

## Where to go next

| If you want to… | Read |
|---|---|
| Run any other command, see every option | [`HOWTORUN.md`](HOWTORUN.md) |
| Understand the research design + literature gap | [`docs/proposal/proposal_second_draft.docx`](docs/proposal/) |
| Add a paper, extend the literature brain | [`research/literature/BRAIN.md`](research/literature/BRAIN.md) |
| Understand the research-automation spec | [`research/automation.txt`](research/automation.txt) + [`research/literature/state/README.md`](research/literature/state/README.md) |
| Start implementing the ML pipeline | [`HOWTORUN.md` §9](HOWTORUN.md#9-ml-pipeline--train--evaluate--explain--audit) + the docstrings in `src/emerald_ai/` |
| Look up a domain term | [`research/literature/glossary.md`](research/literature/glossary.md) |
| Obtain the dataset | [`data/README.md`](data/README.md) |

---

## Common first-time gotchas

| Symptom | Fix |
|---|---|
| `emerald: command not found` | Use `python -m emerald_ai ...` or `python emerald.py ...` — both work without `emerald` on PATH |
| `ModuleNotFoundError: typer` | `pip install -e ".[dev,docs]"` — dev extras weren't installed |
| `python -m emerald_ai proposal` → `PermissionError` | Close the .docx in Word first |
| `dot: command not found` | Install Graphviz from https://graphviz.org/download/ — only needed for graph rendering |
| Citation graph SVG is huge | Run `dot -Tsvg -Gsplines=line ...` for a flatter layout, or filter the .dot file first |

For anything else, see [`HOWTORUN.md` §12 — Troubleshooting](HOWTORUN.md#12-troubleshooting).
