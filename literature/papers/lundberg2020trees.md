        ---
        key: lundberg2020trees
        title: "From local explanations to global understanding with explainable AI for trees"
        themes: [gbdt-tabular-sota, xai-finance]
        ---

        # Lundberg et al. (2020) — TreeSHAP: exact Shapley values for tree ensembles in polynomial time

        ## Key claims
        - For any tree ensemble (RF, GBDT), Shapley values for each prediction can be computed exactly in O(TLD²) time where T = trees, L = leaves, D = depth — fast enough for production.
- SHAP interaction values give principled, model-grounded second-order feature interaction strength.
- Aggregating local SHAP across the dataset yields global feature importance with consistency guarantees that mean-decrease-in-impurity lacks.

        ## Method (how the claim was established)
        Algorithmic derivation of TreeSHAP + extensive empirical use on medical risk-prediction case studies (mortality prediction, hospital re-admission).

        ## Relevance to EMERALD-AI
        Core enabling result for EMERALD-AI's explainability stack. Section 5.11 specifies TreeSHAP as the primary attribution method; this paper is the citation for both speed and consistency.

        ## Quotable lines
        - 'The combination of exact computation, interaction effects, and consistent global importance enables trustworthy explanation of tree-based models.'
- 'TreeExplainer's local explanations are consistent and locally accurate.'

        ## Limitations / counter-evidence
        - Exactness applies to TreeSHAP specifically; KernelSHAP for other model types remains an approximation.
- 'Consistency' is a desirable axiom but does not guarantee causal correctness — see [[aas2021explaining]], [[janzing2020feature]].
- Feature dependence is handled via the 'tree_path_dependent' or 'interventional' algorithms; choice affects attribution magnitude.

        ## How EMERALD-AI uses this paper
        Section 4.2 (regulator-friendliness of GBDT). Section 4.6 (XAI stack). Section 5.11 (TreeSHAP as primary local + global attribution method).

        ## Related entries
        - [[lundberg2017shap]] — original SHAP paper
- [[chen2016xgboost]] — model family this enables explanation of
- [[aas2021explaining]] — critique of attribution under dependence
- → [[themes/4.2-gbdt-tabular-sota]]
- → [[themes/4.6-xai-finance]]
