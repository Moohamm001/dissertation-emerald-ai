# Training Report — proposal §5.8 + §5.9

_Companion to `selection_report.md` and `imbalance_report.md`. Nested CV
training across the full model zoo: linear baselines (LR L1/L2, RBF-SVM),
tree ensembles (RF, XGBoost, LightGBM, CatBoost), and tabular deep learning
(MLP, FT-Transformer). Primary metric is PR-AUC against the minority class;
within-minority ECE and recall@top-decile are co-headline per v0.4.1 §5.13._

Version: 0.2 · Generated: 2026-05-30

## Setup

| | Value |
|---|---:|
| Total rows | 14,022 |
| Minority (Y=0, delinquent) | 50 |
| Features in | 90 |
| Outer folds | 3 |
| Inner folds (RandomizedSearchCV) | 2 |
| Search candidates per family-fold | 6 |
| Families | lr_l2, rf, xgboost, lightgbm, catboost, mlp, ft_transformer |
| Master seed | 42 |

## Per-family performance (outer-fold mean ± std)

| Family | PR-AUC | ROC-AUC | within-min ECE | recall@top-decile |
|---|---|---|---|---|
| `catboost` | 0.1179 ± 0.0735 | 0.9396 ± 0.0474 | 0.9451 ± 0.0182 | 0.8566 ± 0.1465 |
| `ft_transformer` | 0.0636 ± 0.0600 | 0.8724 ± 0.0842 | 0.3981 ± 0.1582 | 0.6569 ± 0.1620 |
| `lightgbm` | 0.0955 ± 0.0578 | 0.9161 ± 0.0883 | 0.9121 ± 0.1291 | 0.7978 ± 0.1300 |
| `lr_l2` | 0.0356 ± 0.0053 | 0.8719 ± 0.0659 | 0.3771 ± 0.1750 | 0.6373 ± 0.1189 |
| `mlp` | 0.0614 ± 0.0306 | 0.8849 ± 0.0874 | 0.3934 ± 0.2158 | 0.7574 ± 0.1288 |
| `rf` | 0.1034 ± 0.0693 | 0.9447 ± 0.0342 | 0.6134 ± 0.1118 | 0.8983 ± 0.0743 |
| `xgboost` | 0.1045 ± 0.0543 | 0.9509 ± 0.0289 | 0.9587 ± 0.0197 | 0.8566 ± 0.1465 |

## Notes

- **Hyperparameter search**: this run uses the reduced-budget RandomizedSearchCV
  by default (3 outer × 2 inner folds × 6 candidates for runtime). The proposal's
  full Optuna TPE study (with median pruning) is implemented in
  `emerald_ai.training.tune` and runs via `python -m emerald_ai train --tuner optuna`.
- **Tabular deep learning is live**: MLP and FT-Transformer (native torch,
  `emerald_ai.models.deep`) are trained alongside the GBDTs. On this small-N,
  highly-imbalanced problem the GBDTs lead on PR-AUC (CatBoost 0.118 > XGBoost
  0.105 > RF 0.103 > LightGBM 0.096 > FT-T 0.064 > MLP 0.061 > LR 0.036), but the
  deep models are markedly better-calibrated on the minority (within-minority ECE
  ≈ 0.39–0.40 vs the GBDTs' 0.91–0.96) — consistent with the tabular-DL literature.
- Each model family's best estimator per outer fold is available via the
  returned `audit.fold_results[i].best_params` for traceability.
