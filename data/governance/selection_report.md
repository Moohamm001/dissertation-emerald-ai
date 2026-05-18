# Feature Selection Report — proposal §5.6

_Companion to `datasheet.md`, `eda_report.md`, `preprocess_report.md`. Two-stage
selection: MI filter (Stage 1) + bootstrap-stability RF importance (Stage 2)._

Version: 0.1 · Generated: 2026-05-18

## Stage 1 — Mutual-information filter

| | Value |
|---|---:|
| Drop quantile (bottom) | 0.10 |
| Features in | 90 |
| Features retained after filter | 71 |
| Features dropped | 19 |

**Filter-dropped features:** `Borrower Zip`, `Deal Type___missing__`, `Deal Type_complementary`, `Deal Type_draw`, `Deal Type_graduation`, `Deal Type_stacked`, `Industry`, `Location___missing__`, `Marketing Credit Score`, `Mineral Group_2. Platinum`, `Mineral Group_5. Bronze`, `Mineral Group_7. N/A`, … (+7 more)

## Stage 2 — Bootstrap-stability wrapper

| | Value |
|---|---:|
| Top-K per bootstrap | 20 |
| Bootstrap rounds | 10 |
| Selection-frequency threshold | 60% |
| Final selected features | **20** |
| Master seed | 42 |

Bootstraps are stratified within each class so the minority (0.36% prevalence)
is always represented; the in-fold-only constraint from Santos et al. (2018)
is moot here because no resampling-then-relabelling happens in this stage.

**Selected features:** `# Offers Received`, `Amount Funded`, `Average Monthly Sales`, `Borrower State`, `Closed Max Term`, `Commission`, `Credit Score`, `Is Lender Renewal`, `Lender`, `Max Offer Received $`, `Payback`, `Payment Amount`, `Payment Frequency_weekly`, `Points`, `Prod Id`, `Prod Rank`, `Prod Type`, `Product`, `Revenue`, `missingindicator_Payment Amount`

## Top-30 features by selection frequency

| Feature | MI(Y) [nats] | Selection freq |
|---|---:|---:|
| `Max Offer Received $` | 0.0009 | 100.0% |
| `Closed Max Term` | 0.0033 | 100.0% |
| `Amount Funded` | 0.0011 | 100.0% |
| `Revenue` | 0.0024 | 100.0% |
| `Average Monthly Sales` | 0.0010 | 100.0% |
| `Payback` | 0.0010 | 100.0% |
| `Commission` | 0.0025 | 100.0% |
| `Payment Amount` | 0.0023 | 100.0% |
| `Points` | 0.0031 | 100.0% |
| `Prod Id` | 0.0082 | 100.0% |
| `Prod Rank` | 0.0012 | 100.0% |
| `Lender` | 0.0084 | 100.0% |
| `Prod Type` | 0.0020 | 100.0% |
| `Product` | 0.0078 | 100.0% |
| `Credit Score` | 0.0004 | 80.0% |
| `Is Lender Renewal` | 0.0025 | 80.0% |
| `Payment Frequency_weekly` | 0.0021 | 80.0% |
| `# Offers Received` | 0.0007 | 70.0% |
| `missingindicator_Payment Amount` | 0.0033 | 70.0% |
| `Borrower State` | 0.0007 | 70.0% |
| `Amount Sought` | 0.0001 | 40.0% |
| `Is Product Renewal` | 0.0024 | 40.0% |
| `Marketing Time in Business` | 0.0002 | 20.0% |
| `Is Borrower Renewal` | 0.0015 | 10.0% |
| `Current Tier` | 0.0018 | 10.0% |
| `Start Business Day` | 0.0010 | 10.0% |
| `Days Since Last Opportunity` | 0.0005 | 10.0% |
| `# Borrower Renewals` | 0.0006 | 10.0% |
| `Online App Completed` | 0.0010 | 0.0% |
| `Mktg Tier` | 0.0015 | 0.0% |

## Notes

- This is the §5.6 first cut. A SHAP-importance variant on a tuned XGBoost is
  the documented next step once the modelling stage lands; the present
  RandomForest-based ranking provides the bootstrap-stability invariant the
  proposal calls out without adding the boruta-py / shap dependencies prematurely.
- The selection is independent of any imbalance strategy choice — that
  decision lives in §5.7 (`imbalance.py`) and is applied **inside** each
  cross-validation fold during modelling, never before selection.
