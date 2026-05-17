        ---
        key: wachter2017counterfactual
        title: "Counterfactual explanations without opening the black box: Automated decisions and the GDPR"
        themes: [xai-finance, fairness-compliance]
        ---

        # Wachter, Mittelstadt & Russell (2017) — legal/technical case for counterfactuals under GDPR

        ## Key claims
        - The 'right to explanation' read into GDPR Article 22 is more meaningfully discharged by counterfactual explanations than by feature-attribution explanations.
- Counterfactuals require no access to the model internals — model-agnostic by construction.
- A formal definition of counterfactual: the closest possible world (in feature space) in which the decision would have differed.

        ## Method (how the claim was established)
        Legal-technical analysis of GDPR Articles 13-15 and 22 + algorithmic definition of counterfactual explanation.

        ## Relevance to EMERALD-AI
        Legal foundation citation for EMERALD-AI's counterfactual layer. Justifies the design choice to make counterfactuals a first-class output, not an optional add-on.

        ## Quotable lines
        - 'Counterfactual explanations of automated decisions... are appropriate for assessing the lawfulness of automated individual decision-making.'
- 'Counterfactual explanations do not require opening the black box.'

        ## Limitations / counter-evidence
        - The 'right to explanation' reading of GDPR is contested (Edwards & Veale 2017, Selbst & Powles 2017 argue it is more limited).
- Closest counterfactual is not always the most useful — Mothilal et al. (2020) argue for diversity.
- Predates the EU AI Act; new framework will partly supersede GDPR analysis for credit-scoring AI.

        ## How EMERALD-AI uses this paper
        Section 4.6 + section 5.11 legal justification for counterfactual layer.

        ## Related entries
        - [[mothilal2020dice]] — implementation, with diversity
- [[euAiAct2021]] — newer overlapping regulatory framework
- → [[themes/4.6-xai-finance]]
- → [[themes/4.7-fairness-compliance]]
