---
key: rudin2019stop
title: "Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead"
themes: [xai-finance]
---

# Rudin (2019) — argues for inherently interpretable models in high-stakes settings

## Key claims
- Post-hoc explanations of opaque models can be unreliable, unstable, or actively misleading.
- For high-stakes decisions (criminal justice, medicine, credit), modellers should use inherently interpretable models (constrained additive models, sparse decision lists, EBMs) instead of explaining black boxes after the fact.
- The 'accuracy vs interpretability trade-off' is often illusory at high-stakes data sizes: interpretable models frequently match black-box accuracy.

## Method (how the claim was established)
Position paper with worked counter-examples from criminal recidivism prediction (COMPAS), medical imaging, and tabular finance.

## Relevance to EMERALD-AI
Critical-perspective citation in section 4.6. EMERALD-AI's pragmatic middle path (constrained tree ensemble + multi-method explanation stack) is explicitly positioned as Rudin's argument acknowledged but not adopted in pure form.

## Quotable lines
- 'Trying to explain black box models, rather than creating models that are interpretable in the first place, is likely to perpetuate bad practice.'
- 'There is no scientific evidence for a general trade-off between accuracy and interpretability.'

## Limitations / counter-evidence
- The 'interpretable models match black-box accuracy' claim has notable exceptions, particularly for very high-dimensional data and certain non-linear-interaction regimes.
- Rudin's preferred model class (EBM, GA²M) has its own engineering and tuning costs.

## How EMERALD-AI uses this paper
Section 4.6 critical-perspective anchor. Counter-position EMERALD-AI must engage with rather than ignore.

## Related entries
- [[dumitrescu2022ml]] — adjacent argument (interpretable can match black-box)
- [[slack2020fooling]] — supporting evidence for Rudin's critique
- → [[themes/4.6-xai-finance]]
