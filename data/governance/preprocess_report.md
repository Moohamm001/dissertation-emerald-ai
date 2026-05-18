# Preprocessing Report — proposal §5.5

_Companion to `datasheet.md`, `feature_catalogue.yaml`, and `eda_report.md`.
Operates on the post-EDA permitted-feature frame; rows with missing labels
have already been dropped upstream._

Version: 0.1 · Generated: 2026-05-18

## Stage 1 — Drop list

| Reason | Threshold | Count | Columns |
|---|---|---:|---|
| Missingness > 40% | hard drop | 8 | `1st Online Engmnt`, `APR`, `App Out`, `Factor`, `Lender Identifier`, `Monthly Credit Card Charges`, `Published`, `Term` |
| Time-leaking (EDA PSI ≫ 0.25 by construction) | hard drop | 2 | `Start Month`, `Start Annual Day` |
| Datetime (deferred to §5.6 feature engineering) | typed drop | 35 | `Start`, `Start TS`, `End`, `End TS`, `Assigned`, `Assigned TS`, `Current Assigned`, `Current Assigned TS`, `Attempted`, `Attempted TS`, `Contacted`, `Contacted TS`, … (+23 more) |

## Stage 2 — Missing-data treatment

- Numeric features: median imputation + missing-indicator binary appended per feature.
- Categorical features: explicit `__missing__` level added before encoding.

## Stage 3 — Encoding

- **Low-cardinality categoricals (≤10 unique levels):** OneHotEncoder with `handle_unknown='ignore'`.
  Columns (5): `Mineral Group`, `Location`, `Marketing Mineral Group`, `Payment Frequency`, `Deal Type`
- **High-cardinality categoricals:** TargetEncoder (binary target, internal cross-fit, random_state=42).
  Columns (7): `Loan Purpose`, `Industry`, `Lender`, `Prod Type`, `Product`, `Borrower City`, `Borrower State`
  Master seed: 42 (from `emerald_ai.config.MODEL.random_seed`).

## Stage 4 — Scaling

- All surviving numerics → StandardScaler. Tree-based learners are scale-invariant; the same fitted preprocessor is reused across all six model families (proposal §5.8) to keep comparisons identical.

## Shape summary

| | Value |
|---|---:|
| Input columns (after EDA permitted-set) | 90 |
| Output features (post-encoding + indicators) | 90 |
| Numeric retained | 33 |
| Low-cardinality categoricals | 5 |
| High-cardinality categoricals | 7 |
| Rows in | 14022 |
| Rows out | 14022 |

## Top-20 input-column missingness (for traceability)

| Column | Missing % |
|---|---:|
| `App Out` | 100.00% |
| `1st Online Engmnt` | 100.00% |
| `Monthly Credit Card Charges` | 100.00% |
| `Published` | 98.77% |
| `Lender Identifier` | 97.60% |
| `Term` | 86.29% |
| `APR` | 59.26% |
| `Factor` | 41.57% |
| `Payment Amount` | 37.40% |
| `Processor Assigned TS` | 21.91% |
| `DocPrep` | 21.79% |
| `DocPrep TS` | 21.79% |
| `Shared w/ Funding Desk` | 21.79% |
| `Contacted` | 17.58% |
| `Contacted TS` | 17.58% |
| `Payment Frequency` | 16.18% |
| `Online App Complete TS` | 14.41% |
| `Attempted` | 11.83% |
| `Attempted TS` | 11.83% |
| `Current Assigned` | 7.88% |
