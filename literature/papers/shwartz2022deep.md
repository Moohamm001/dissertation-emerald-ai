---
key: shwartz2022deep
title: "Tabular data: Deep learning is not all you need"
themes: [gbdt-tabular-sota, tabular-deep-learning]
---

# Shwartz-Ziv & Armon (2022) — independent benchmark showing GBDT > tabular DL

## Key claims
- On 11 public datasets including those used by the original tabular-DL papers, XGBoost beats every deep tabular model tested (TabNet, NODE, DNF-Net, 1D-CNN), often by a wide margin.
- Even on the deep models' own benchmark datasets, XGBoost wins after careful tuning — suggesting the original DL claims were partly tuning-effort artefacts.

## Method (how the claim was established)
Re-ran each deep tabular model on the union of all benchmark datasets used across the original papers, with consistent hyperparameter budget for all methods. Reported AUC, RMSE, and ranking.

## Relevance to EMERALD-AI
Pillar citation for section 4.3's sober positioning on tabular DL. Justifies EMERALD-AI's choice to include DL models as honest comparators rather than headline approaches.

## Quotable lines
- 'Deep models were worse than XGBoost on most of the studied datasets.'
- 'An ensemble of deep models and XGBoost performs best.'

## Limitations / counter-evidence
- The benchmark datasets are small to medium; results may not extend to very large industry datasets.
- The hyperparameter search budget is finite; DL methods may benefit disproportionately from more aggressive tuning.
- Does not test FT-Transformer or SAINT (the strongest recent tabular DL methods).

## How EMERALD-AI uses this paper
Section 4.3 anchor. Justifies the headline of section 5.8 that GBDTs are the primary candidate family.

## Related entries
- [[grinsztajn2022trees]] — corroborating recent benchmark with broader model coverage
- [[gorishniy2021revisiting]] — FT-Transformer (omitted by Shwartz-Ziv)
- → [[themes/4.2-gbdt-tabular-sota]]
- → [[themes/4.3-tabular-deep-learning]]
