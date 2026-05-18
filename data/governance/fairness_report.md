# Fairness Audit Report — proposal §5.12

_Per-axis demographic parity / equalised odds / predictive parity / calibration-within-group._


Version: 0.1 · Generated: 2026-05-18


## Operating threshold

- Classification threshold: **0.50**
- Positive label: **1**


## Per-axis gap summary

| Axis | DP gap | TPR gap | FPR gap | Precision gap | ECE gap |
|---|---|---|---|---|---|
| `Industry` | 0.0135 | 0.0000 | 1.0000 | 0.0909 | 0.0760 |
| `Borrower State` | 0.0109 | 0.0000 | 1.0000 | 0.0208 | 0.0111 |

## Axis: `Industry`

| group | n | sel rate | TPR | FPR | precision | ECE |
|---|---:|---:|---:|---:|---:|---:|
| `other` | 2901 | 0.998 | 1.000 | 0.375 | 0.999 | 0.001 |
| `construction` | 2096 | 0.997 | 1.000 | 0.333 | 0.999 | 0.001 |
| `restaurants` | 1832 | 0.997 | 1.000 | 0.250 | 0.999 | 0.002 |
| `retail` | 1328 | 0.999 | 1.000 | 0.000 | 1.000 | 0.001 |
| `healthcare` | 953 | 0.998 | 1.000 | 0.000 | 1.000 | 0.001 |
| `informationMedia` | 577 | 0.998 | 1.000 | 0.667 | 0.997 | 0.003 |
| `freightTrucking` | 542 | 0.998 | 1.000 | 0.667 | 0.996 | 0.003 |
| `transportation` | 510 | 0.998 | 1.000 | 0.667 | 0.996 | 0.004 |
| `realEstate` | 455 | 0.998 | 1.000 | 0.500 | 0.998 | 0.002 |
| `manufacturing` | 446 | 0.987 | 1.000 | 0.000 | 1.000 | 0.004 |
| `wholesale` | 406 | 1.000 | 1.000 | nan | 1.000 | 0.001 |
| `artsEntertainment` | 377 | 1.000 | 1.000 | nan | 1.000 | 0.000 |
| `finance` | 367 | 0.997 | 1.000 | 0.000 | 1.000 | 0.002 |
| `automotive` | 366 | 0.997 | 1.000 | 0.000 | 1.000 | 0.001 |
| `education` | 250 | 0.996 | 1.000 | 0.000 | 1.000 | 0.002 |

## Axis: `Borrower State`

| group | n | sel rate | TPR | FPR | precision | ECE |
|---|---:|---:|---:|---:|---:|---:|
| `CA` | 1794 | 0.997 | 1.000 | 0.000 | 1.000 | 0.001 |
| `TX` | 1326 | 0.998 | 1.000 | 0.000 | 1.000 | 0.001 |
| `FL` | 1254 | 0.997 | 1.000 | 0.000 | 1.000 | 0.001 |
| `NY` | 830 | 0.999 | 1.000 | 0.500 | 0.999 | 0.002 |
| `GA` | 614 | 1.000 | 1.000 | nan | 1.000 | 0.000 |
| `PA` | 489 | 1.000 | 1.000 | 1.000 | 0.996 | 0.003 |
| `IL` | 464 | 0.994 | 1.000 | 0.000 | 1.000 | 0.003 |
| `NC` | 463 | 0.996 | 1.000 | 0.600 | 0.993 | 0.007 |
| `NJ` | 447 | 1.000 | 1.000 | nan | 1.000 | 0.000 |
| `AZ` | 399 | 0.995 | 1.000 | 0.000 | 1.000 | 0.002 |
| `OH` | 359 | 1.000 | 1.000 | nan | 1.000 | 0.000 |
| `VA` | 358 | 1.000 | 1.000 | nan | 1.000 | 0.000 |
| `MI` | 340 | 0.997 | 1.000 | 0.500 | 0.997 | 0.002 |
| `CO` | 337 | 0.994 | 1.000 | 0.333 | 0.997 | 0.004 |
| `MD` | 334 | 1.000 | 1.000 | nan | 1.000 | 0.000 |

## Selbst et al. (2019) sociotechnical traps
- The audit is reported with explicit value judgements rather than as portable claims.
- Calibration-within-group is the *binding* constraint (PD-reporting weight under IRB).
- Base-rate decompositions are published so reviewers can disagree on visible grounds.
- Fairness claims are conditional on the deployment context (US 2019 funded loans only).