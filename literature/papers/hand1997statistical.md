        ---
        key: hand1997statistical
        title: "Statistical classification methods in consumer credit scoring: A review"
        themes: [evolution-credit-scoring]
        ---

        # Hand & Henley (1997) — review of statistical methods in consumer credit

        ## Key claims
        - Logistic regression, despite available alternatives (neural networks, recursive partitioning, k-nearest neighbours), remains the practical default in consumer credit scoring.
- The differences in classification performance between methods are typically small; the choice is often driven by interpretability, ease of deployment, and regulatory acceptability rather than accuracy.

        ## Method (how the claim was established)
        Narrative review of the consumer credit-scoring literature to 1997, with empirical synthesis across published comparisons.

        ## Relevance to EMERALD-AI
        Anchors the claim in section 4.1 that logistic regression has been the regulatory default for decades. Foundational citation for the interpretability-driven adoption pattern that EMERALD-AI then complicates.

        ## Quotable lines
        - 'Practitioners often prefer methods that yield interpretable models, even at some cost in predictive accuracy.'
- The 'flat-maximum effect' observation: many methods give similar accuracy, so other criteria dominate.

        ## Limitations / counter-evidence
        - Predates the modern ensemble era (XGBoost, RF) and the rise of SHAP-style post-hoc explanations.
- The 'flat-maximum' claim has not held up uniformly under ensemble methods on larger modern datasets [[lessmann2015benchmark]].

        ## How EMERALD-AI uses this paper
        Section 4.1 anchor citation for the historical interpretability vs accuracy tension.

        ## Related entries
        - [[thomas2000survey]] — complementary later review
- [[lessmann2015benchmark]] — modern update showing ensembles do outperform
- → [[themes/4.1-evolution-credit-scoring]]
