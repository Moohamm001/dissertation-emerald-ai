---
key: bellamy2018aif360
title: "AI Fairness 360: An extensible toolkit for detecting, understanding, and mitigating unwanted algorithmic bias"
themes: [fairness-compliance]
---

# Bellamy et al. (2018) — AIF360 toolkit

## Key claims
- AIF360 provides a unified Python API for 70+ fairness metrics and 10+ bias-mitigation algorithms (pre-, in-, post-processing).
- Designed for production deployment with documentation, examples, and integration with major ML frameworks.

## Method (how the claim was established)
Toolkit paper. Implements the published fairness and mitigation literature in a unified API.

## Relevance to EMERALD-AI
Implementation citation for EMERALD-AI's section 5.12 fairness audit. AIF360 is the toolkit; [[hardt2016eqodds]] and [[chouldechova2017fair]] are the underlying theoretical basis.

## Quotable lines
- 'A comprehensive open-source library… containing a comprehensive set of fairness metrics for datasets and models, explanations for these metrics, and algorithms to mitigate bias.'

## Limitations / counter-evidence
- The toolkit does not choose which fairness criterion to optimise for the user — choosing remains a domain decision.
- Many mitigation algorithms degrade accuracy substantially; cost-benefit must be assessed empirically.

## How EMERALD-AI uses this paper
Section 4.7 + section 5.12 implementation citation.

## Related entries
- [[hardt2016eqodds]] — equalised odds theory
- [[chouldechova2017fair]] — impossibility result
- [[kamiran2012preprocessing]] — reweighting mitigation (implemented in AIF360)
- → [[themes/4.7-fairness-compliance]]
