# `data/` — Datasets and Pipeline Outputs

This directory holds **all data** consumed and produced by the EMERALD-AI pipeline. **Nothing in `data/raw/`, `data/interim/`, or `data/processed/` is committed to git** — see the project [`.gitignore`](../.gitignore). Only `.gitkeep` markers and this README are tracked.

## Layout

```
data/
├── raw/         ← Original, immutable source data (the .xlsx).  GITIGNORED.
├── interim/     ← Intermediate transformations (after leakage audit, before encoding). GITIGNORED.
└── processed/   ← Modelling-ready feature frames + persisted preprocessors. GITIGNORED.
```

## Primary dataset

| Property | Value |
|---|---|
| Name | 2019 All Funded Green Loan Dataset |
| Shape | 14,135 rows × 166 columns |
| Labelled rows | 14,022 (99.2%) — those with non-null `Deal Status` |
| Period | Calendar year 2019 |
| Granularity | One row per funded loan transaction |
| Sensitivity | **Proprietary** — supplied for academic use only, redistribution prohibited |

### How to obtain

Place the raw file at:

```
data/raw/All_Funded_2019_Green Loan.xlsx
```

The dataset is **not redistributed** in this repository. If you are an authorised collaborator, request it via the channel on the dissertation cover sheet. If you have no prior authorisation, contact the corresponding researcher first.

### Label construction (proposal §5.2)

```
Y = 1  if Deal Status ∈ {paidOff, current}
Y = 0  if Deal Status ∈ {default, behind}
NaN    otherwise  (113 rows; excluded from labelled set)
```

The `current` mapping introduces censoring bias — see the sensitivity analysis described in proposal §5.2 and in [`../research/literature/gaps.md`](../research/literature/gaps.md) entry M1.

## Feature categories (proposal §5.3)

Each of the 166 columns falls into one of six categories:

| Category | Permitted as feature? |
|---|---|
| Pre-funding applicant attributes | Yes |
| Pre-funding loan-offer attributes | Yes |
| Loan structural metadata | Yes |
| Deal-progression timestamps | Yes (with care — see leakage audit) |
| Post-funding observed outcomes | **No** — defines Y, must not enter X |
| Administrative / free-text | **No** |

The leakage audit (see `src/emerald_ai/data/leakage_audit.py`) produces a feature catalogue committed to the project's documentation; it is the canonical data-governance artefact.

## Data ethics

- The dataset is de-identified by the providing institution prior to release.
- No personally identifying information enters analysis.
- All artefacts derived from the data are stored in encrypted university storage and destroyed at dissertation submission, per Warwick research ethics protocol and UK GDPR.

## Datasheet

A full datasheet ([Gebru et al., 2021](../research/literature/papers/gebru2021datasheets.md)) will be generated as part of the dissertation submission. Stub: `docs/datasheet.md` (to come).
