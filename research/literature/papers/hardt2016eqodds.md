---
key: hardt2016eqodds
title: "Equality of opportunity in supervised learning"
themes: [fairness-compliance]
---

# Hardt, Price & Srebro (2016) — equalised odds and equal opportunity

## Key claims
- 'Equalised odds' requires the true-positive rate AND false-positive rate to be equal across protected groups; 'equal opportunity' requires only TPR equality.
- Both criteria can be enforced post-hoc by learning a group-conditional threshold from a calibrated score.
- These criteria are weaker than demographic parity and avoid demographic-parity's failure mode of underwriting on protected-group membership rather than risk.

## Method (how the claim was established)
Theoretical derivation of post-hoc threshold-adjustment procedure + empirical demonstration on the FICO credit-scoring dataset.

## Relevance to EMERALD-AI
Foundational citation for section 4.7's parity-definition framework. Equalised-odds gap is one of the four metrics EMERALD-AI's section 5.12 fairness audit reports.

## Quotable lines
- 'We propose a criterion for discrimination against a specified sensitive attribute in supervised learning: that the prediction be independent of the protected attribute, conditional on the true label.'
- The FICO case study showing the trade-off between equal opportunity and aggregate accuracy.

## Limitations / counter-evidence
- The post-hoc threshold approach assumes the underlying score is well-calibrated within each group — often false in practice.
- Equalised odds is incompatible with calibration when base rates differ [[chouldechova2017fair]].
- 'Protected group' must be observable at inference time, which is often not the case in credit.

## How EMERALD-AI uses this paper
Section 4.7 anchor. Section 5.12 equalised-odds gap metric.

## Related entries
- [[chouldechova2017fair]] — impossibility result
- [[kleinberg2017inherent]] — same result from a different angle
- [[bellamy2018aif360]] — toolkit implementation
- → [[themes/4.7-fairness-compliance]]
