        ---
        key: aas2021explaining
        title: "Explaining individual predictions when features are dependent: More accurate approximations to Shapley values"
        themes: [xai-finance]
        ---

        # Aas, Jullum & Løland (2021) — KernelSHAP under feature dependence

        ## Key claims
        - Standard KernelSHAP assumes feature independence — an assumption almost always violated in real tabular data, especially financial data with correlated ratios.
- Under dependence, KernelSHAP attributions can be biased: the magnitude and even the sign of individual feature attributions can be wrong.
- Conditional-distribution-based estimators (using Gaussian, copula, or empirical conditional sampling) produce more accurate attributions.

        ## Method (how the claim was established)
        Theoretical analysis of the bias + empirical comparison of four conditional-sampling approaches on synthetic and real-data benchmarks.

        ## Relevance to EMERALD-AI
        Critical-perspective citation in section 4.6. Justifies the section 5.11 design choice to cross-check TreeSHAP attributions with KernelSHAP on a held-out sample, AND to use conditional rather than marginal feature distributions where feasible.

        ## Quotable lines
        - 'When features are dependent, KernelSHAP can give biased estimates of the true conditional Shapley values.'
- 'Conditional sampling approaches produce more accurate Shapley value estimates.'

        ## Limitations / counter-evidence
        - Conditional sampling is computationally more expensive than marginal sampling.
- The 'true' Shapley value under dependence is itself contested — see [[janzing2020feature]] for a causal-inference-based alternative ('interventional' SHAP).

        ## How EMERALD-AI uses this paper
        Section 4.6 critical perspective. Section 5.11 motivates KernelSHAP cross-check + interventional-SHAP for TreeSHAP.

        ## Related entries
        - [[lundberg2017shap]] — paper this critiques
- [[lundberg2020trees]] — TreeSHAP, which offers tree_path_dependent vs interventional algorithms
- [[janzing2020feature]] — causal-inference framing
- → [[themes/4.6-xai-finance]]
