        ---
        key: berg2022esg
        title: "Aggregate confusion: The divergence of ESG ratings"
        themes: [green-finance]
        ---

        # Berg, Kölbel & Rigobon (2022) — ESG ratings disagree systematically across providers

        ## Key claims
        - Correlations across six major ESG-rating providers average only 0.54 (vs ~0.99 for credit ratings).
- The divergence decomposes into scope (which categories matter), measurement (how each is operationalised), and weights — measurement is the dominant driver.
- ESG ratings are not interchangeable; using one provider's score as a feature embeds that provider's methodological priors.

        ## Method (how the claim was established)
        Decomposition of disagreement across six ESG-rating providers on a large overlap sample using a novel scope/measurement/weight framework.

        ## Relevance to EMERALD-AI
        Pillar citation justifying EMERALD-AI's design choice NOT to use third-party ESG scores as model features. Anchor for section 4.5's claim that ESG ratings are unreliable as direct inputs.

        ## Quotable lines
        - 'ESG ratings from six prominent rating agencies have an average correlation of 0.54, which is significantly lower than the correlation of credit ratings (around 0.99).'
- 'Measurement divergence is the most important source.'

        ## Limitations / counter-evidence
        - The 0.54 figure has been refined in later work; the directional claim is robust but the exact magnitude depends on overlap sample and provider mix.
- Does not address the question of which ESG score, if any, is most accurate — only that they disagree.

        ## How EMERALD-AI uses this paper
        Section 4.5 anchor for the 'do not use ESG scores as features' design choice.

        ## Related entries
        - [[ehlers2017greenbond]] — adjacent information-asymmetry argument
- [[flammer2021corporate]] — uses E-pillar ESG scores; this paper is the caveat
- → [[themes/4.5-green-finance]]
