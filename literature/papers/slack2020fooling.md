        ---
        key: slack2020fooling
        title: "Fooling LIME and SHAP: Adversarial attacks on post hoc explanation methods"
        themes: [xai-finance]
        ---

        # Slack et al. (2020) — adversarial attacks on post-hoc explanations

        ## Key claims
        - A model can be constructed that uses a sensitive attribute (race, gender) in its decisions while LIME and SHAP attributions hide this dependence completely.
- The attack works by training a 'scaffolding' model that behaves differently on perturbed neighbours (seen by the explainer) vs real instances.
- Post-hoc explanations are therefore not a sufficient defence against deliberate bias hiding.

        ## Method (how the claim was established)
        Constructed adversarial scaffolding models on COMPAS and German Credit datasets; demonstrated that LIME and KernelSHAP attribute the discriminatory decisions to innocuous features.

        ## Relevance to EMERALD-AI
        Critical-perspective citation in section 4.6. Strengthens the case for EMERALD-AI's multi-method explanation stack + monotonic-constraint verification + fidelity evaluation rather than trust-by-default in a single explainer.

        ## Quotable lines
        - 'Adversaries can construct biased classifiers that LIME and SHAP fail to detect as biased.'
- 'Post hoc explanation methods can be unreliable in adversarial settings.'

        ## Limitations / counter-evidence
        - The attack requires deliberate construction; honest practitioners following standard training are unlikely to reproduce it accidentally.
- TreeSHAP on transparent tree ensembles is harder to fool than KernelSHAP on opaque scaffolds.
- Monotonic constraints and structural inspection (which EMERALD-AI uses) would detect the attack.

        ## How EMERALD-AI uses this paper
        Section 4.6 critical perspective. Justifies multi-method + structural-verification approach in section 5.11.

        ## Related entries
        - [[rudin2019stop]] — adjacent critique of post-hoc explanations
- [[hedstrom2023quantus]] — fidelity evaluation as countermeasure
- → [[themes/4.6-xai-finance]]
