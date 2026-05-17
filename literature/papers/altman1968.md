---
key: altman1968
title: "Financial ratios, discriminant analysis and the prediction of corporate bankruptcy"
themes: [evolution-credit-scoring]
---

# Altman (1968) — Z-score / discriminant analysis for bankruptcy prediction

## Key claims
- A linear combination of five financial ratios (working capital / assets, retained earnings / assets, EBIT / assets, market value equity / book value debt, sales / assets) discriminates bankrupt vs solvent firms with 95% accuracy one year before failure on the original sample.
- The Z-score (Z = 1.2 X1 + 1.4 X2 + 3.3 X3 + 0.6 X4 + 1.0 X5) becomes the founding artefact of statistical credit / bankruptcy scoring.

## Method (how the claim was established)
Multiple discriminant analysis (MDA) on a matched sample of 33 bankrupt manufacturing firms (1946-1965) vs 33 non-bankrupt controls.

## Relevance to EMERALD-AI
Context / lineage citation. Establishes the lineage that runs from MDA → logistic regression → modern ML. Useful to ground the historical narrative in section 4.1; not a methodological dependency for EMERALD-AI.

## Quotable lines
- 'The Z-score is a useful summary statistic for distinguishing potentially bankrupt firms…'
- The original 95% / 72% one- and two-year-ahead accuracy figures.

## Limitations / counter-evidence
- Sample is small (66 firms), US-only, manufacturing-only, 1946-1965.
- Linear model with no provision for non-linearity; later Zeta and Z'' variants attempt repair.
- Predates the modern ML treatment of class imbalance and out-of-sample validation.

## How EMERALD-AI uses this paper
Cited in section 4.1 as the lineage origin of statistical credit modelling. No direct methodological use.

## Related entries
- [[beaver1966]] — earlier univariate ratio analysis Altman extends
- [[hand1997statistical]] — review tracing the lineage forward
- → [[themes/4.1-evolution-credit-scoring]]
