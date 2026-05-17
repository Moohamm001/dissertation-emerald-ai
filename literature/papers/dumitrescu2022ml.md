---
key: dumitrescu2022ml
title: "Machine learning for credit scoring: Improving logistic regression with non-linear decision-tree effects"
themes: [evolution-credit-scoring, xai-finance]
---

# Dumitrescu, Hue, Hurlin & Tokpavi (2022) — penalised LR + tree interactions ≈ XGBoost

## Key claims
- An adaptive lasso logistic regression augmented with decision-tree-derived non-linear interaction terms ('penalised logistic tree regression', PLTR) matches XGBoost AUC on multiple credit datasets.
- The accuracy-interpretability frontier is not fixed: with careful feature construction, interpretable models can recover most of the predictive gain claimed by opaque ones.

## Method (how the claim was established)
Used short shallow CART trees to extract interaction features, then fit an adaptive-lasso LR on the augmented feature set. Compared to XGBoost, RF, and plain LR on six credit datasets.

## Relevance to EMERALD-AI
Critical citation for section 4.1's central argument that the accuracy/interpretability trade-off is a design choice. Strengthens the case for EMERALD-AI's middle-path posture (constrained tree ensemble + explanation stack) rather than pure-DL.

## Quotable lines
- 'PLTR achieves a performance close to that of more complex algorithms while remaining intrinsically interpretable.'
- 'The interpretability-performance trade-off can be substantially mitigated.'

## Limitations / counter-evidence
- The 'close to XGBoost' claim still leaves a gap that may matter at scale.
- The interaction-extraction step itself uses opaque trees, so the 'interpretable' label applies to the final LR coefficient surface, not the entire pipeline.
- Results are on conventional, not green, credit data.

## How EMERALD-AI uses this paper
Section 4.1 framing citation. Could also justify including a PLTR-style model in the comparison panel of section 5.8 — currently not, but worth flagging as a possible extension.

## Related entries
- [[lessmann2015benchmark]] — the benchmark this paper revisits
- [[rudin2019stop]] — adjacent argument for interpretable models in high-stakes settings
- → [[themes/4.1-evolution-credit-scoring]]
- → [[themes/4.6-xai-finance]]
