---
key: lundberg2017shap
title: "A unified approach to interpreting model predictions"
themes: [xai-finance]
---

# Lundberg & Lee (2017) — SHAP unifies feature attribution under a game-theoretic axiom set

## Key claims
- Six existing attribution methods (LIME, DeepLIFT, Layer-wise relevance propagation, classic Shapley, QII, Shapley sampling) are special cases of a single 'additive feature attribution' framework.
- Within that framework, only Shapley values uniquely satisfy three desirable axioms: local accuracy, missingness, and consistency.
- KernelSHAP estimates Shapley values via a weighted linear regression on perturbation samples — model-agnostic and computationally tractable.

## Method (how the claim was established)
Theoretical unification (axiom-satisfaction proofs) + empirical comparison with LIME and DeepLIFT on MNIST and a medical risk-prediction case study.

## Relevance to EMERALD-AI
Foundational citation for EMERALD-AI's entire XAI stack. The axiomatic uniqueness argument is what lets reviewers know SHAP is not just one explainer among many — it is the unique one satisfying its axiom set.

## Quotable lines
- 'We propose SHAP values as a unified measure of feature importance.'
- 'SHAP values are the unique solution to the class of additive feature attribution methods that satisfies the three desirable properties of local accuracy, missingness, and consistency.'

## Limitations / counter-evidence
- The 'unique under the axioms' claim depends on accepting the axioms — see [[aas2021explaining]], [[janzing2020feature]] for causal-inference critiques.
- KernelSHAP scales poorly with feature count and is biased under feature dependence — TreeSHAP [[lundberg2020trees]] is the relevant production tool.

## How EMERALD-AI uses this paper
Section 4.6 axiomatic-grounding citation. Section 5.11 KernelSHAP cross-check citation.

## Related entries
- [[lundberg2020trees]] — TreeSHAP follow-up
- [[ribeiro2016lime]] — LIME, the perturbation predecessor unified here
- [[aas2021explaining]] — critique under feature dependence
- → [[themes/4.6-xai-finance]]
