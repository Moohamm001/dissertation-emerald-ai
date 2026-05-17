# EMERALD-AI

**An Explainable, Calibrated, and Audit-Ready Machine Learning Framework for Green Loan Credit Scoring, Operationalised as a Full-Stack Decision-Support Platform.**

MSc Applied Artificial Intelligence Dissertation — University of Warwick.

---

## What this project is

Green-loan origination has grown at a compound annual rate exceeding 40% since 2018, yet credit-risk infrastructure for sustainable lending remains anchored in scorecards designed for conventional consumer credit. **EMERALD-AI** is an end-to-end framework — research pipeline plus production web application — that benchmarks modern tabular learners on a real-world 2019 green-loan dataset (14,135 funded transactions, 166 features), integrates calibration, distribution-free uncertainty, multi-method explainability, and a fairness/robustness audit aligned to the **EU AI Act (Annex III)** and **FCA Consumer Duty**.

The framework occupies an explicit, defended literature gap: no published work simultaneously delivers, on real green-loan data, (i) modern tabular benchmarking under identical preprocessing, (ii) post-hoc calibration and conformal uncertainty, (iii) a multi-method explainability stack with empirical fidelity validation, (iv) a fairness audit on green-lending-appropriate proxies, and (v) a deployable lending-officer-facing interface.

> **Status:** scaffold + proposal + literature brain. Implementation begins after proposal approval. See [`docs/proposal/`](docs/proposal/) for the current proposal and [`literature/`](literature/) for the knowledge base.

---

## Project layout

```
.
├── README.md                  ← you are here
├── LICENSE                    ← MIT (code only; data licence is separate, see data/README.md)
├── CITATION.cff               ← academic citation metadata
├── pyproject.toml             ← uv-managed Python dependencies (pinned)
├── Makefile                   ← canonical entrypoints (make help)
│
├── src/emerald_ai/            ← Python package: data, features, models, training,
│                                 calibration, explain, fairness, eval, cli
├── api/                       ← FastAPI backend (REST endpoints; production scoring)
├── web/                       ← React 18 + Vite frontend (Dashboard, Single Predict,
│                                 Batch Score, SHAP Explorer)
│
├── docs/
│   ├── proposal/              ← Dissertation proposal (first draft, second draft, build script)
│   └── architecture/          ← (to come) C4 diagrams, MLOps stack diagrams
├── literature/                ← Knowledge brain: index.yaml + themes/ + papers/ + gaps + glossary
│                                 Read literature/BRAIN.md first for usage rules
│
├── data/
│   ├── raw/                   ← Original .xlsx (GITIGNORED — proprietary)
│   ├── interim/               ← Intermediate transformations (GITIGNORED)
│   └── processed/             ← Modelling-ready features (GITIGNORED)
│
├── notebooks/                 ← Jupyter notebooks: EDA, model dev, audit
├── scripts/                   ← Reproducibility scripts (make reproduce wraps these)
├── tests/                     ← pytest suite
└── .github/workflows/         ← CI: lint, type-check, test
```

---

## Quick start

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

```bash
make help            # list all available targets
make lint            # ruff + black --check + mypy
make test            # pytest
make proposal        # rebuild docs/proposal/proposal_second_draft.docx
make literature      # regenerate literature/papers/*.md from build_papers.py
make reproduce       # (will) run the full ML pipeline end-to-end
```

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

The repo contains a structured knowledge base under [`literature/`](literature/) — not a static bibliography, but a queryable, versioned representation of the lit review intended to evolve through the project:

- `literature/BRAIN.md` — usage rules
- `literature/index.yaml` — 62 indexed references with themes, relevance, verification status
- `literature/themes/4.1`–`4.8.md` — eight argumentative-spine files mirroring the proposal's literature-review subsections
- `literature/papers/<key>.md` — 34 critical-paper notes (claims, method, EMERALD-AI relevance, limitations, links)
- `literature/gaps.md` — 10 literature gaps + 5 methodology gaps, with suggested next actions
- `literature/glossary.md` — domain terms

Read `BRAIN.md` before writing about any paper.

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
- `make reproduce` will re-run the full pipeline from raw data to scored test set in ≤ 8 hours wall-clock on the target hardware (Google Colab Pro+ A100 + Warwick HPC CPU).
- Each model card and datasheet ([Gebru et al., 2021](literature/index.yaml)) regenerated automatically on each merge to `main`.

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
