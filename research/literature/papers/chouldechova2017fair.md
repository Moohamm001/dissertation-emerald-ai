---
key: chouldechova2017fair
title: "Fair prediction with disparate impact: A study of bias in recidivism prediction instruments"
themes: [fairness-compliance]
---

# Chouldechova (2017) — impossibility theorem: calibration and equal error rates incompatible

## Key claims
- For any binary classifier, if base rates differ across protected groups, the following three properties cannot simultaneously hold: (i) calibration within groups, (ii) equal false-positive rates, (iii) equal false-negative rates.
- This is a mathematical impossibility, not a tuning failure — applies to any classifier.
- The choice of which fairness criterion to optimise is therefore a value judgement, not a technical one.

## Method (how the claim was established)
Analytic proof + case study using ProPublica's COMPAS recidivism data.

## Relevance to EMERALD-AI
Pillar citation for section 4.7's core argument that the four parity definitions are incompatible and modellers must choose. Cited alongside [[kleinberg2017inherent]] for the same result.

## Quotable lines
- 'When the recidivism prevalence differs across groups, an instrument that satisfies predictive parity… cannot simultaneously satisfy equal false-positive rates and equal false-negative rates.'
- 'No risk-assessment instrument can satisfy all of the fairness criteria simultaneously.'

## Limitations / counter-evidence
- The impossibility holds in the worst case; in specific regimes (similar base rates, calibration interventions) the practical trade-off can be small.
- The result does not dictate which criterion to choose — that is left to the deploying institution.

## How EMERALD-AI uses this paper
Section 4.7 anchor. Section 5.12 underpins the explicit acknowledgement that multiple criteria are reported rather than one optimised.

## Related entries
- [[hardt2016eqodds]] — defines equalised odds
- [[kleinberg2017inherent]] — same impossibility from a different angle
- → [[themes/4.7-fairness-compliance]]
