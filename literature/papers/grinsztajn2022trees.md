        ---
        key: grinsztajn2022trees
        title: "Why do tree-based models still outperform deep learning on tabular data?"
        themes: [gbdt-tabular-sota, tabular-deep-learning]
        ---

        # Grinsztajn, Oyallon & Varoquaux (2022) — diagnoses why DL underperforms on tabular

        ## Key claims
        - Tree-based methods outperform DL on 45 tabular datasets across mixed-feature and numerical-only regimes.
- Three diagnostic reasons: (1) DL is biased toward overly smooth target functions; (2) uninformative features hurt DL more than trees; (3) DL is rotationally invariant, but tabular data is not — feature orientation matters.

        ## Method (how the claim was established)
        Curated 45 medium-sized tabular benchmark datasets (the Tabular Benchmark). Compared XGBoost, GBM, RF, FT-Transformer, ResNet, MLP, SAINT with 20k-trial hyperparameter searches each.

        ## Relevance to EMERALD-AI
        Most-cited recent paper on this question. Anchor for sections 4.2 and 4.3. Its three diagnostic reasons frame the section 4.3 paragraph about when DL earns its keep.

        ## Quotable lines
        - 'On medium-sized data… tree-based models are still state-of-the-art.'
- 'Empirical investigation into the differences between deep learning models and tree-based models, which sheds light on the reasons for the superiority of tree-based models.'

        ## Limitations / counter-evidence
        - 'Medium-sized' is 1k-50k samples; at 10⁶+ rows the story may differ.
- Does not test SOTA pre-trained foundation models for tabular (TabPFN, TabuLa-8B post-date this).

        ## How EMERALD-AI uses this paper
        Sections 4.2 and 4.3 anchor. The dataset size of our project (~14k) sits squarely in the regime they study, lending direct external validity.

        ## Related entries
        - [[shwartz2022deep]] — corroborating earlier benchmark
- [[gorishniy2021revisiting]] — FT-Transformer is one of the DL methods tested here
- [[borisov2022dnntabular]] — broader survey
- → [[themes/4.2-gbdt-tabular-sota]]
- → [[themes/4.3-tabular-deep-learning]]
