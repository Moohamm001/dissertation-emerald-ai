---
key: lessmann2015benchmark
title: "Benchmarking state-of-the-art classification algorithms for credit scoring: An update of research"
themes: [evolution-credit-scoring, benchmarking, gbdt-tabular-sota]
---

# Lessmann et al. (2015) — 41-classifier credit-scoring benchmark

## Key claims
- Heterogeneous ensemble methods (random forest, gradient boosting, stacking) dominate single learners.
- The marginal accuracy gains from architectural sophistication shrink as dataset size grows.
- The choice of evaluation metric matters: AUC, PCC, Brier score, and partial-AUC can rank methods differently — multi-metric reporting is mandatory.

## Method (how the claim was established)
Compared 41 classifiers across 8 real credit datasets using 6 metrics. Applied the Friedman test + Nemenyi post-hoc to control multiple-comparison error.

## Relevance to EMERALD-AI
Pillar citation for sections 4.1 and 4.2. Establishes 'ensembles dominate' as a credit-scoring consensus, motivating EMERALD-AI's primary focus on GBDTs. Methodological exemplar for nested CV and multi-metric reporting.

## Quotable lines
- 'Several heterogeneous ensemble classifiers, namely AvgS, HCES-Bag, MGN-1-stacking, and stacking, perform significantly better than the industry standard, logistic regression.'
- The Friedman-Nemenyi ranking diagrams from Figures 3-4 are widely cited.

## Limitations / counter-evidence
- Datasets are still relatively small (largest ~150k records).
- Does not cover XGBoost (2016) or modern tabular DL.
- No fairness, calibration, or explainability dimension.

## How EMERALD-AI uses this paper
Sections 4.1 and 4.2 anchor citation. Section 5.13 methodological precedent for multi-metric reporting with paired statistical testing.

## Related entries
- [[baesens2003benchmark]] — the original benchmark being updated
- [[dumitrescu2022ml]] — newer reframing
- [[chen2016xgboost]] — XGBoost, post-dates this study
- → [[themes/4.1-evolution-credit-scoring]]
- → [[themes/4.2-gbdt-tabular-sota]]
