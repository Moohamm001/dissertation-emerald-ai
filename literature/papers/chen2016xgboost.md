        ---
        key: chen2016xgboost
        title: "XGBoost: A scalable tree boosting system"
        themes: [gbdt-tabular-sota]
        ---

        # Chen & Guestrin (2016) — XGBoost foundational paper

        ## Key claims
        - A scalable gradient-boosting framework combining (a) second-order Newton boosting, (b) L1/L2 leaf-weight regularisation, (c) sparsity-aware split finding for missing data, (d) cache-aware out-of-core computation.
- Wins or matches state-of-the-art on the majority of Kaggle tabular competitions surveyed at the time.

        ## Method (how the claim was established)
        Theoretical derivation of regularised second-order objective + extensive empirical evaluation on regression, classification, ranking, and large-scale tabular tasks.

        ## Relevance to EMERALD-AI
        Foundational citation for EMERALD-AI's primary candidate model. Cited 30k+ times. The monotonic-constraint feature added post-publication (XGBoost ≥0.81) is the specific implementation hook for the monotonicity argument in section 5.8.

        ## Quotable lines
        - 'A novel sparsity-aware algorithm for sparse data and weighted quantile sketch for approximate tree learning.'
- The Kaggle dominance statistic: '17 of 29 winning solutions on Kaggle in 2015 used XGBoost.'

        ## Limitations / counter-evidence
        - Original paper does not cover monotonic constraints, GPU training, or DART dropout — these are later additions.
- Tree ensembles extrapolate poorly; OOD generalisation is a known weakness not addressed here.
- No explicit treatment of calibration.

        ## How EMERALD-AI uses this paper
        Section 4.2 anchor. Section 5.8 model specification: XGBoost with monotonic constraints on Credit Score, Annual Revenue, Time in Business.

        ## Related entries
        - [[ke2017lightgbm]] — sibling GBDT implementation
- [[prokhorenkova2018catboost]] — CatBoost
- [[lundberg2020trees]] — TreeSHAP, the XGBoost-companion explainer
- → [[themes/4.2-gbdt-tabular-sota]]
