# Training Report — proposal §5.8 + §5.9

_Companion to `selection_report.md` and `imbalance_report.md`. Nested CV
training across six classifier families (LR L1/L2, RBF-SVM, RF, XGBoost,
LightGBM, CatBoost; MLP / FT-Transformer deferred). Primary metric is
PR-AUC against the minority class; within-minority ECE and recall@top-decile
are co-headline per v0.4.1 §5.13._

Version: 0.1 · Generated: 2026-05-18

## Setup

| | Value |
|---|---:|
| Total rows | 14,022 |
| Minority (Y=0, delinquent) | 50 |
| Features in | 90 |
| Outer folds | 5 |
| Inner folds (RandomizedSearchCV) | 3 |
| Search candidates per family-fold | 12 |
| Families | lr_l1, lr_l2, svm_rbf, rf, xgboost |
| Master seed | 42 |

## Per-family performance (outer-fold mean ± std)

| Family | PR-AUC | ROC-AUC | within-min ECE | recall@top-decile |
|---|---|---|---|---|
| `lr_l1` | 0.0318 ± 0.0111 | 0.9016 ± 0.0473 | 0.3092 ± 0.1020 | 0.7000 ± 0.1414 |
| `lr_l2` | 0.1003 ± 0.0524 | 0.9232 ± 0.0553 | 0.2937 ± 0.1515 | 0.8000 ± 0.1732 |
| `rf` | 0.1370 ± 0.0692 | 0.9451 ± 0.0780 | 0.6021 ± 0.2422 | 0.9000 ± 0.1225 |
| `svm_rbf` | 0.0499 ± 0.0245 | 0.9004 ± 0.0931 | 0.9765 ± 0.0096 | 0.7800 ± 0.2280 |
| `xgboost` | 0.1847 ± 0.1175 | 0.9656 ± 0.0343 | 0.9462 ± 0.0295 | 0.9200 ± 0.1304 |

## Notes

- **RandomizedSearchCV used in place of Optuna TPE for first cut**: the
  proposal's full HPO budget (100 trials per family per outer fold) requires
  many hours of compute; this report uses ~12 candidates per family-fold to
  produce a faithful nested-CV structure on a runnable budget. Optuna TPE
  + HyperBand swap-in lives in `emerald_ai.training.tune` and will populate
  the v0.5 patch.
- **Deferred families**: MLP and FT-Transformer require torch + a separate
  training loop; flagged in `emerald_ai.models.__init__` as deferred.
- Each model family's best estimator per outer fold is available via the
  returned `audit.fold_results[i].best_params` for traceability.
