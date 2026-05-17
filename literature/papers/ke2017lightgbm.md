        ---
        key: ke2017lightgbm
        title: "LightGBM: A highly efficient gradient boosting decision tree"
        themes: [gbdt-tabular-sota]
        ---

        # Ke et al. (2017) — LightGBM (histogram-based, leaf-wise)

        ## Key claims
        - Gradient-based One-Side Sampling (GOSS) and Exclusive Feature Bundling (EFB) reduce training cost by an order of magnitude vs XGBoost without measurable accuracy loss.
- Leaf-wise tree growth (vs XGBoost's level-wise) yields lower loss for the same number of leaves at the cost of higher overfitting risk on small datasets.

        ## Method (how the claim was established)
        Algorithmic derivation + benchmark vs XGBoost and sklearn GBM on five public datasets including Allstate, Flight Delay, and KDD Cup datasets.

        ## Relevance to EMERALD-AI
        Alternative GBDT implementation in EMERALD-AI's section 5.8 panel. Its differing bias profile (leaf-wise growth, histogram binning) serves as cross-validation against single-implementation idiosyncrasies.

        ## Quotable lines
        - 'LightGBM speeds up the training process of conventional GBDT by up to over 20 times while achieving almost the same accuracy.'

        ## Limitations / counter-evidence
        - Leaf-wise growth can overfit on the small-to-moderate datasets typical in finance unless num_leaves is constrained — a relevant tuning concern for our n ≈ 14k.
- Categorical handling via 'categorical_feature' is heuristic; CatBoost's ordered-target encoding is more principled.

        ## How EMERALD-AI uses this paper
        Section 5.8 GBDT comparison panel.

        ## Related entries
        - [[chen2016xgboost]] — sibling
- [[prokhorenkova2018catboost]] — sibling
- → [[themes/4.2-gbdt-tabular-sota]]
