# `notebooks/` — Exploratory and Audit Notebooks

Reproducible Jupyter notebooks used for exploratory data analysis, model development sketches, and audit visualisations. The canonical pipeline lives in `src/emerald_ai/`; notebooks are for exploration and reporting, not production code.

## Conventions

- One notebook per analytical question, numbered `NN_<slug>.ipynb`.
- Notebooks `nbstripout`-cleaned on commit (no embedded outputs) to keep the diff manageable.
- Any logic worth keeping migrates to `src/emerald_ai/` and is invoked from the notebook via `import emerald_ai…`.
- Cell tags: `slow` (long-running), `gpu` (requires GPU), `data` (requires raw data).

## Planned notebooks

| Number | Notebook | Purpose |
|---|---|---|
| 01 | `01_eda.ipynb` | Univariate, bivariate, multivariate EDA — proposal §5.4 |
| 02 | `02_leakage_audit.ipynb` | Target-leakage screening, feature-category catalogue — proposal §5.3 |
| 03 | `03_preprocessing.ipynb` | Pipeline construction + transformation sanity checks — proposal §5.5 |
| 04 | `04_imbalance_experiments.ipynb` | SMOTE-NC vs class-weight vs focal-loss — proposal §5.7 |
| 05 | `05_model_benchmark.ipynb` | Headline cross-model comparison — proposal §5.8–5.9 |
| 06 | `06_calibration_conformal.ipynb` | Reliability diagrams + conformal intervals — proposal §5.10 |
| 07 | `07_explainability.ipynb` | TreeSHAP, counterfactuals, fidelity — proposal §5.11 |
| 08 | `08_fairness_audit.ipynb` | AIF360 audit on proxy axes — proposal §5.12 |
