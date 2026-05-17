---
key: arik2021tabnet
title: "TabNet: Attentive interpretable tabular learning"
themes: [tabular-deep-learning, xai-finance]
---

# Arik & Pfister (2021) — TabNet: attention-based tabular DL with built-in feature attribution

## Key claims
- Sequential attention over features with a learnable sparse mask at each decision step.
- The attention masks double as built-in per-instance feature attribution — no post-hoc SHAP needed.
- Competitive with or better than GBDTs on six public tabular datasets in the paper's own benchmark.

## Method (how the claim was established)
Architecture combining sequential attention with sparse feature selection, trained with self-supervised masked feature reconstruction pre-training. Benchmarked on Forest Cover Type, Poker Hand, Sarcos, Higgs, Rossmann, KDD'99.

## Relevance to EMERALD-AI
One of the two DL models in EMERALD-AI's section 5.8 panel. The built-in attention attribution is a design alternative to TreeSHAP — worth empirical comparison even if TreeSHAP remains primary.

## Quotable lines
- 'TabNet uses sequential attention to choose which features to reason from at each decision step, enabling interpretability and better learning.'

## Limitations / counter-evidence
- Later independent benchmarks (e.g. [[shwartz2022deep]], [[grinsztajn2022trees]]) found TabNet underperforms well-tuned GBDTs on most datasets — the original paper's headline claims overstated.
- The 'attention as attribution' claim is contested in the XAI literature (Jain & Wallace 2019).

## How EMERALD-AI uses this paper
Section 5.8 DL comparator. Section 4.3 example of attention-as-attribution claim.

## Related entries
- [[gorishniy2021revisiting]] — FT-Transformer, the stronger sibling
- [[shwartz2022deep]] — independent benchmark showing TabNet underperforms GBDT
- → [[themes/4.3-tabular-deep-learning]]
