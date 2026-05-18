# Class-Imbalance Strategy Report — proposal §5.7

_Compares balancing strategies on a Logistic Regression baseline under stratified
5-fold CV. Resampling is applied strictly inside training folds._

Version: 0.1 · Generated: 2026-05-18

## Setup

| | Value |
|---|---:|
| Total rows | 14,022 |
| Minority observations (Y=0, delinquent) | 50 |
| Empirical prevalence | 0.357% |
| CV folds | 5 |
| Master seed | 42 |

## Strategy comparison

| Strategy | Minority PR-AUC | Within-minority ECE | Joint score |
|---|---|---|---:|
| `no_resample` | 0.0527 ± 0.0243 | 0.9730 ± 0.0082 | 0.0014 |
| `class_weighted` | 0.0601 ± 0.0278 | 0.3132 ± 0.1474 | 0.0413 |
| `smote` | 0.0855 ± 0.0465 | 0.3209 ± 0.1616 | 0.0581 |

_Joint score = PR-AUC × (1 − within-minority-ECE); higher is better._

## Chosen strategy

**`smote`** maximised the joint score on this baseline.

The chosen strategy is fed forward into the §5.8 modelling stage. Each model
family may re-evaluate independently (a booster's `scale_pos_weight` is
strictly equivalent to `class_weight='balanced'` on a linear model only at
the gradient level; the §5.8 commit will revisit).

## Notes

- **SMOTE caveat (v0.4.1 §4.4):** SMOTE interpolates between extremely sparse
  seeds at 0.36% prevalence and risks off-manifold synthetic points. If it
  underperforms `class_weighted` on the joint score, that is empirical
  evidence supporting the v0.4.1 framing rather than a methodological failure.
- **Focal loss** is documented but not implemented in this stage — it requires
  the neural training stack landing in §5.8.
- **In-fold-only constraint** [Santos et al., 2018]: the imblearn Pipeline
  enforces this structurally; validation folds are never resampled.
