        ---
        key: prokhorenkova2018catboost
        title: "CatBoost: Unbiased boosting with categorical features"
        themes: [gbdt-tabular-sota]
        ---

        # Prokhorenkova et al. (2018) — CatBoost / ordered boosting / ordered target statistics

        ## Key claims
        - Naive target encoding induces 'prediction shift' (a target-leakage-like bias) when used inside gradient boosting; ordered target statistics eliminate this by training each instance only on predecessors in a random permutation.
- Ordered boosting extends the same principle to the gradient estimates themselves.

        ## Method (how the claim was established)
        Theoretical proof of the bias-elimination property + benchmark on multiple datasets including KDD'09 Appetency, Internet, Adult.

        ## Relevance to EMERALD-AI
        Best-in-class GBDT for high-cardinality categoricals (Industry ~30 levels, Borrower State ~50 levels in our dataset). Strong candidate to win the GBDT family comparison; included in section 5.8 panel.

        ## Quotable lines
        - 'The proposed scheme guarantees that target statistics for any example are computed only from previous examples, avoiding target leakage.'

        ## Limitations / counter-evidence
        - Slower than LightGBM out of the box; ordering overhead can dominate on very large data.
- The 'unbiased' guarantee is asymptotic; finite-sample behaviour can still leak signal.

        ## How EMERALD-AI uses this paper
        Section 5.8 GBDT comparison panel; specifically expected to handle Industry and Borrower State without the leave-one-out target-encoder workaround used for the other learners.

        ## Related entries
        - [[chen2016xgboost]] — sibling
- [[ke2017lightgbm]] — sibling
- [[micciBarreca2001]] — target encoding origin; CatBoost fixes its leakage problem
- → [[themes/4.2-gbdt-tabular-sota]]
