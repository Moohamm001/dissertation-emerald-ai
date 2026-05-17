---
key: angelopoulos2023conformal
title: "Conformal prediction: A gentle introduction"
themes: [imbalance-calibration]
---

# Angelopoulos & Bates (2023) — modern tutorial on split-conformal prediction

## Key claims
- Split-conformal prediction wraps any black-box model to produce prediction sets with guaranteed marginal coverage at user-specified confidence levels, distribution-free, finite-sample.
- The only requirement is exchangeability of the calibration and test data.
- Adaptive variants (Mondrian, conformalised quantile regression) extend the guarantee to conditional coverage in specific regimes.

## Method (how the claim was established)
Tutorial paper synthesising the conformal prediction literature into a practitioner-accessible reference.

## Relevance to EMERALD-AI
Primary citation for EMERALD-AI's section 5.10 conformal prediction implementation. The modern reference if a reviewer asks 'why is this distribution-free?'

## Quotable lines
- 'Conformal prediction is a user-friendly paradigm for creating statistically rigorous uncertainty sets for the predictions of any black-box model.'

## Limitations / counter-evidence
- Marginal coverage guarantee does not imply conditional coverage — a high-risk applicant may still get an overconfident interval. Mondrian conformal addresses this partially.
- Requires a held-out calibration set, reducing data available for training/validation.
- The exchangeability assumption fails under distribution shift — a real concern for credit data.

## How EMERALD-AI uses this paper
Section 4.4 anchor. Section 5.10 implementation citation.

## Related entries
- [[vovk2005alrw]] — foundational textbook
- [[platt1999probabilistic]], [[zadrozny2002isotonic]] — point-calibration counterparts
- → [[themes/4.4-imbalance-calibration]]
