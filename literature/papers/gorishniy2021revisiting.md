        ---
        key: gorishniy2021revisiting
        title: "Revisiting deep learning models for tabular data"
        themes: [tabular-deep-learning]
        ---

        # Gorishniy et al. (2021) — FT-Transformer + sober benchmark of tabular DL

        ## Key claims
        - A simple MLP with carefully chosen hyperparameters often matches more elaborate tabular DL architectures.
- FT-Transformer (feature-tokeniser + standard transformer encoder) is the strongest single tabular DL method tested.
- Across 11 datasets, no single architecture dominates — including GBDTs, which the paper treats as a tough baseline they often fail to beat.

        ## Method (how the claim was established)
        Implemented MLP, ResNet, FT-Transformer, and others under a unified hyperparameter-tuning protocol (Optuna, identical budgets). Evaluated on 11 tabular benchmarks including California Housing, Adult, Higgs, Year, Microsoft.

        ## Relevance to EMERALD-AI
        Strongest credible single tabular DL architecture for inclusion in section 5.8. The paper's own caveats about GBDT competitiveness inform section 4.3's sober positioning.

        ## Quotable lines
        - 'FT-Transformer demonstrates the best performance on most tasks and becomes a new powerful solution for the field.'
- 'GBDT is still a tough-to-beat baseline.'

        ## Limitations / counter-evidence
        - Benchmark datasets are still medium-sized.
- The hyperparameter tuning is exhaustive; production-grade tuning budgets may not reach the same gains.
- Does not cover modern self-supervised pre-training approaches.

        ## How EMERALD-AI uses this paper
        Section 5.8 DL panel — FT-Transformer is the chosen instantiation. Section 4.3 anchor.

        ## Related entries
        - [[arik2021tabnet]] — included as comparator
- [[grinsztajn2022trees]] — corroborates 'GBDT tough to beat'
- → [[themes/4.3-tabular-deep-learning]]
