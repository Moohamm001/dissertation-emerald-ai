# Gaps Log — Open Holes and Unaddressed Questions

This log tracks what is currently missing, unverified, or hand-waved in the literature review and methodology. Each entry has a status (`open` / `partial` / `resolved`) and a suggested next action. When future-me deep-dives a topic, the first thing to check is whether this log has been updated.

## How to use this file

- **Before claiming "we've covered X comprehensively"** — check whether `gaps.md` lists any open holes under X.
- **When closing a gap** — move it from `open` to `resolved` with a note on how it was closed.
- **When discovering a new gap during deep dive** — add it here. It is better to surface the gap than to silently paper over it.

---

## Literature gaps

### G1. "First green-loan ML credit-scoring framework" claim is unverified
- **Status:** open
- **Theme:** [[themes/4.8-gap-positioning]]
- **Risk:** High — supervisor will press on this.
- **Action:** Run systematic search on Scopus, Web of Science, IEEE Xplore, Google Scholar with strings:
  - `("green loan" OR "green credit") AND ("machine learning" OR "explainable" OR "XGBoost")`
  - `("sustainable lending" OR "ESG lending") AND ("credit scoring" OR "default prediction")`
  - `("green finance" OR "climate finance") AND ("interpretable" OR "SHAP")`
- Document the search protocol and date in the dissertation methodology section so the negative result is defensible.
- Anything found that overlaps must be cited and differentiated, not ignored.

### G2. "Regulatory default for over four decades" claim lacks primary citation
- **Status:** open
- **Theme:** [[themes/4.1-evolution-credit-scoring]]
- **Risk:** Medium — currently leans on [[hand1997statistical]] and [[thomas2000survey]] for the historical claim but not on a specific supervisory document.
- **Action:** Find a primary source — candidates: Fed SR 11-7 (model risk management), Basel II IRB documentation, FICO scorecard methodology papers, BoE PRA SS3/18.

### G3. "Regulators increasingly demand monotonicity" claim is asserted, not cited
- **Status:** open
- **Theme:** [[themes/4.2-gbdt-tabular-sota]]
- **Risk:** Medium.
- **Action:** Find a specific supervisory document mandating monotonicity for credit-scoring features. Candidates: ECB TRIM (Targeted Review of Internal Models), EBA GL/2017/16 (IRB validation), FCA model-validation guidance.

### G4. Green loan market 40%+ CAGR claim needs primary citation
- **Status:** open
- **Theme:** [[themes/4.5-green-finance]] / introduction
- **Risk:** Medium — figure appears in the abstract and introduction.
- **Action:** Verify against the LMA Green Loan Principles document or BNEF green-loan tracker; pin the exact figure and time window.

### G5. Tabular foundation models (TabPFN, TabuLa) not covered
- **Status:** open
- **Theme:** [[themes/4.3-tabular-deep-learning]]
- **Risk:** Low for an MSc proposal, higher if any reviewer is following recent frontier developments.
- **Action:** Add a stub paragraph + paper file for [[hollmann2023tabpfn]] and decide whether to include TabPFN in the experimental panel. Note its current limitation (≤1000 samples) makes it not directly applicable to our 14k-row dataset.

### G6. Explainable Boosting Machine (EBM) and GA²M family missing
- **Status:** open
- **Theme:** [[themes/4.6-xai-finance]]
- **Risk:** Medium — particularly visible since [[rudin2019stop]] is heavily cited and Rudin's group authored InterpretML/EBM.
- **Action:** Add paper file for [[nori2019interpretml]] (InterpretML); consider whether EBM belongs in the section 5.8 model panel as the "interpretable-by-construction" alternative.

### G7. ESG-related labelling provenance of the dataset is unknown
- **Status:** open
- **Theme:** [[themes/4.5-green-finance]] (also methodology)
- **Risk:** Medium — affects external validity of any green-finance-specific conclusion.
- **Action:** Confirm with the data provider which taxonomy was used to classify the 2019 loans as "green" (EU Taxonomy? CBI? Originator-defined?). Document in the data-governance section of the methodology. If the answer is "originator-defined", that itself is a limitation to surface explicitly.

### G8. UK Equality Act 2010 and Basel "model risk management" guidance not cited
- **Status:** open
- **Theme:** [[themes/4.7-fairness-compliance]]
- **Risk:** Low-medium — the regulatory framing would be stronger with UK statutory underpinning rather than only EU + FCA guidance.
- **Action:** Add citations for Equality Act 2010 (where indirect discrimination is defined) and BoE PRA SS3/18 (UK model risk management).

### G9. Causal fairness (Kusner et al. counterfactual fairness) missing
- **Status:** open
- **Theme:** [[themes/4.7-fairness-compliance]]
- **Risk:** Low.
- **Action:** Add stub for Kusner et al. (2017) "Counterfactual fairness" NeurIPS. Decide whether the dissertation engages with the causal fairness branch or stays purely statistical-parity-based.

### G10. "FCA/EBA cite conformal prediction" assertion is too strong
- **Status:** open
- **Theme:** [[themes/4.4-imbalance-calibration]]
- **Risk:** Medium — a sharp reviewer will ask for the source.
- **Action:** Either find the regulatory commentary that mentions conformal prediction, or weaken the claim to "increasingly discussed in regulatory commentary" without citing a specific authority.

---

## Methodology gaps

### M1. Sensitivity analysis on the "current" label inclusion
- **Status:** planned (in proposal 5.2) but not yet executed.
- **Action:** Document the censoring-bias sensitivity analysis as a first-week dissertation deliverable.

### M2. Choice of fairness criterion under impossibility result
- **Status:** open
- **Theme:** [[themes/4.7-fairness-compliance]]
- **Risk:** High — the dissertation cannot duck this question.
- **Action:** Pre-register which parity criterion takes precedence when they conflict (probably calibration-within-group, given the regulatory weight of PD reporting). Document the reasoning.

### M3. Tuning-budget parity across model families
- **Status:** partial (specified as "100 trials per fold" in 5.9)
- **Risk:** Medium — deep-learning models often need much more aggressive HPO than GBDTs; equal trial count is not equal compute.
- **Action:** Either (i) match compute budgets (wall-clock-equivalent) rather than trial counts, or (ii) report the tuning budget explicitly per family and acknowledge the asymmetry.

### M4. Conformal prediction under distribution shift
- **Status:** open
- **Risk:** Medium — exchangeability assumption fails if model is deployed past 2019.
- **Action:** Cite the conformal-under-shift literature (Tibshirani et al. 2019 "Conformal prediction under covariate shift") and discuss whether weighted conformal is implemented or treated as future work.

### M5. Data-license commercial-use restriction
- **Status:** open
- **Action:** Confirm with data provider what open-sourcing the trained model weights would imply. The proposal says code+models will be open-sourced "subject to the data licence's commercial-use restrictions" — need to confirm those restrictions allow weight release.

---

## Search-result harvesting (when G1 is run)

Reserve this section for the systematic-search results when conducted. Format:
- Query: `<exact string>`
- Database: `<Scopus | WoS | IEEE | Scholar>`
- Date run: `YYYY-MM-DD`
- Hits: `<n>`
- Relevant after screening: `<n>`
- Cite as: `[[<key>]]`

(empty until G1 is run)
