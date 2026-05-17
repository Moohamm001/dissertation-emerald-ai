---
key: lin2017focal
title: "Focal loss for dense object detection"
themes: [imbalance-calibration]
---

# Lin, Goyal, Girshick, He & Dollár (2017) — focal loss for extreme imbalance

## Key claims
- A modulating factor (1 - p_t)^γ applied to standard cross-entropy down-weights easy examples and focuses training on hard, misclassified cases.
- Enables one-stage object detectors to match the accuracy of two-stage detectors (RetinaNet result).

## Method (how the claim was established)
Derivation of the focal loss + extensive empirical evaluation on COCO object detection (1:1000 foreground:background imbalance).

## Relevance to EMERALD-AI
Origin paper for focal loss as a loss-level imbalance treatment. Used for the neural baseline in section 5.7 — particularly relevant given default prevalence in credit data, though less extreme than object detection.

## Quotable lines
- 'A novel loss we term the focal loss that addresses class imbalance by reshaping the standard cross entropy loss such that it down-weights the loss assigned to well-classified examples.'

## Limitations / counter-evidence
- The γ hyperparameter must be tuned; γ=2 is the common default but data-dependent.
- Does not address the calibration question — focal-loss models can be poorly calibrated and need post-hoc fix.
- Originally for dense detection; transfer to tabular classification is the by-now-standard extrapolation but not what the paper actually studied.

## How EMERALD-AI uses this paper
Section 5.7 loss-level imbalance treatment for the MLP and FT-Transformer baselines.

## Related entries
- [[chawla2002smote]] — resampling-based alternative
- → [[themes/4.4-imbalance-calibration]]
