# Fairness Audit Report — proposal §5.12

_Per-axis demographic parity / equalised odds / predictive parity / calibration-within-group._


Version: 0.1 · Generated: 2026-05-30


## Operating threshold

- Classification threshold: **0.9994**
- Positive label (approve): **1**
- Threshold policy: risk-band 'watch' cut-off = p20 of the model's score distribution (the deployed decision boundary; a hard 0.5 approves ~100% of every group at this prevalence, collapsing all gaps to ~0).


## Per-axis gap summary

| Axis | DP gap | TPR gap | FPR gap | Precision gap | ECE gap |
|---|---|---|---|---|---|
| `Industry` | 0.3636 | 0.3364 | 0.0000 | 0.0000 | 0.0803 |
| `Borrower State` | 0.3515 | 0.3405 | 0.0000 | 0.0000 | 0.0154 |

## Axis: `Industry`

| group | n | sel rate | TPR | FPR | precision | ECE |
|---|---:|---:|---:|---:|---:|---:|
| `other` | 2901 | 0.820 | 0.823 | 0.000 | 1.000 | 0.002 |
| `construction` | 2096 | 0.771 | 0.774 | 0.000 | 1.000 | 0.003 |
| `restaurants` | 1832 | 0.753 | 0.756 | 0.000 | 1.000 | 0.003 |
| `retail` | 1328 | 0.794 | 0.794 | 0.000 | 1.000 | 0.002 |
| `healthcare` | 953 | 0.766 | 0.768 | 0.000 | 1.000 | 0.003 |
| `informationMedia` | 577 | 0.766 | 0.770 | 0.000 | 1.000 | 0.006 |
| `freightTrucking` | 542 | 0.915 | 0.920 | 0.000 | 1.000 | 0.004 |
| `transportation` | 510 | 0.888 | 0.893 | 0.000 | 1.000 | 0.005 |
| `realEstate` | 455 | 0.879 | 0.883 | 0.000 | 1.000 | 0.003 |
| `manufacturing` | 446 | 0.655 | 0.664 | 0.000 | 1.000 | 0.009 |
| `wholesale` | 406 | 0.818 | 0.818 | nan | 1.000 | 0.002 |
| `artsEntertainment` | 377 | 0.817 | 0.817 | nan | 1.000 | 0.002 |
| `finance` | 367 | 0.891 | 0.893 | 0.000 | 1.000 | 0.002 |
| `automotive` | 366 | 0.877 | 0.879 | 0.000 | 1.000 | 0.003 |
| `education` | 250 | 0.740 | 0.743 | 0.000 | 1.000 | 0.005 |

## Axis: `Borrower State`

| group | n | sel rate | TPR | FPR | precision | ECE |
|---|---:|---:|---:|---:|---:|---:|
| `CA` | 1794 | 0.844 | 0.847 | 0.000 | 1.000 | 0.003 |
| `TX` | 1326 | 0.817 | 0.819 | 0.000 | 1.000 | 0.003 |
| `FL` | 1254 | 0.797 | 0.800 | 0.000 | 1.000 | 0.004 |
| `NY` | 830 | 0.798 | 0.800 | 0.000 | 1.000 | 0.003 |
| `GA` | 614 | 0.845 | 0.845 | nan | 1.000 | 0.001 |
| `PA` | 489 | 0.744 | 0.747 | 0.000 | 1.000 | 0.002 |
| `IL` | 464 | 0.789 | 0.794 | 0.000 | 1.000 | 0.007 |
| `NC` | 463 | 0.778 | 0.786 | 0.000 | 1.000 | 0.009 |
| `NJ` | 447 | 0.734 | 0.734 | nan | 1.000 | 0.001 |
| `AZ` | 399 | 0.850 | 0.854 | 0.000 | 1.000 | 0.004 |
| `OH` | 359 | 0.811 | 0.811 | nan | 1.000 | 0.001 |
| `VA` | 358 | 0.791 | 0.791 | nan | 1.000 | 0.002 |
| `MI` | 340 | 0.815 | 0.820 | 0.000 | 1.000 | 0.005 |
| `CO` | 337 | 0.727 | 0.734 | 0.000 | 1.000 | 0.007 |
| `MD` | 334 | 0.814 | 0.814 | nan | 1.000 | 0.001 |

## Selbst et al. (2019) sociotechnical traps
- The audit is reported with explicit value judgements rather than as portable claims.
- Calibration-within-group is the *binding* constraint (PD-reporting weight under IRB).
- Base-rate decompositions are published so reviewers can disagree on visible grounds.
- Fairness claims are conditional on the deployment context (US 2019 funded loans only).