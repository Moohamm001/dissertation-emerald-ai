        ---
        key: ribeiro2016lime
        title: "'Why should I trust you?': Explaining the predictions of any classifier"
        themes: [xai-finance]
        ---

        # Ribeiro, Singh & Guestrin (2016) — LIME: local interpretable model-agnostic explanations

        ## Key claims
        - Approximate any classifier's local behaviour with a sparse linear model fit on perturbed neighbours, weighted by proximity to the instance.
- The linear surrogate is interpretable and faithful in the neighbourhood, even when the global model is complex.
- The SP-LIME extension selects a small set of instances whose collective explanation provides global understanding.

        ## Method (how the claim was established)
        Algorithmic description + user studies comparing LIME-aided judgements vs no-explanation baseline on text and image classification tasks.

        ## Relevance to EMERALD-AI
        Section 4.6 reference point as the perturbation-based predecessor to SHAP. Section 5.11 uses LIME as a secondary local explanation method to cross-check TreeSHAP attributions.

        ## Quotable lines
        - 'If the user cannot trust the model or a prediction, they will not use it.'
- 'A novel explanation technique that explains the predictions of any classifier in an interpretable and faithful manner.'

        ## Limitations / counter-evidence
        - The choice of perturbation distribution affects the explanation; results can be unstable across runs.
- Demonstrably attackable [[slack2020fooling]] — adversarially trained models can hide bias.
- Local linear approximation can mislead when the model's decision surface is highly non-linear nearby.

        ## How EMERALD-AI uses this paper
        Section 4.6 lineage. Section 5.11 secondary explanation method.

        ## Related entries
        - [[lundberg2017shap]] — SHAP unifies and supersedes LIME for additive attribution
- [[slack2020fooling]] — adversarial attack
- → [[themes/4.6-xai-finance]]
