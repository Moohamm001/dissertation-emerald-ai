        ---
        key: mothilal2020dice
        title: "Explaining machine learning classifiers through diverse counterfactual explanations"
        themes: [xai-finance]
        ---

        # Mothilal, Sharma & Tan (2020) — DiCE: diverse, feasible counterfactual explanations

        ## Key claims
        - A counterfactual explanation tells a declined applicant the minimal feature changes that would flip their decision — actionable in a way attribution alone is not.
- DiCE optimises for both proximity to the original instance AND diversity among the generated counterfactuals, so users receive multiple distinct recourse options.
- Feasibility constraints (mutable features only, value ranges, monotonic directions) ensure counterfactuals are actionable rather than merely mathematically valid.

        ## Method (how the claim was established)
        Optimisation-based counterfactual generation with diversity (determinantal point process) and feasibility constraints. Evaluated on Adult, COMPAS, German Credit, Lending Club.

        ## Relevance to EMERALD-AI
        Core citation for EMERALD-AI's counterfactual layer in section 5.11. Directly addresses the GDPR Article 22 / FCA Consumer Duty 'support' outcome requirement that automated decisions be actionable.

        ## Quotable lines
        - 'Counterfactual explanations provide actionable feedback on what users can do to obtain a different outcome from a machine learning model.'
- 'DiCE generates diverse and feasible counterfactual explanations.'

        ## Limitations / counter-evidence
        - Optimisation can be slow at inference time; not ideal for high-QPS production.
- Counterfactual instability under model retraining [[rawal2020beyond]] is a known concern.
- 'Feasibility' constraints encode value judgements about which features are actionable — must be explicit and reviewed.

        ## How EMERALD-AI uses this paper
        Section 4.6 + section 5.11 counterfactual generation. Surfaced in the web app's Single Predict page as 'what would change this decision?'

        ## Related entries
        - [[wachter2017counterfactual]] — legal foundation
- [[rawal2020beyond]] — counterfactual instability
- → [[themes/4.6-xai-finance]]
