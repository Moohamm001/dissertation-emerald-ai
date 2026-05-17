        ---
        key: hedstrom2023quantus
        title: "Quantus: An explainable AI toolkit for responsible evaluation of neural network explanations"
        themes: [xai-finance]
        ---

        # Hedström et al. (2023) — Quantus: empirical evaluation of XAI methods

        ## Key claims
        - Explanation quality is not self-evident: explanations should be evaluated against measurable properties (faithfulness, robustness, complexity, randomisation, axiomatic, localisation).
- Quantus operationalises 30+ such metrics into a single toolkit.
- Different XAI methods score very differently on different metrics — reporting a single number is insufficient.

        ## Method (how the claim was established)
        Toolkit paper. Implements published evaluation metrics from the XAI literature in a unified API; demonstrates on image-classification case studies.

        ## Relevance to EMERALD-AI
        Core citation for EMERALD-AI's section 5.11 explanation-fidelity validation. Moves the project past the assumption that an explanation is reliable simply because it was generated.

        ## Quotable lines
        - 'Quantus is the first toolkit to provide a comprehensive collection of evaluation metrics for explanations.'
- 'Different evaluation metrics emphasise different desirable properties.'

        ## Limitations / counter-evidence
        - Primarily targeted at neural network explanations and image data; tabular adaptation requires care.
- The metrics themselves are contested (e.g., faithfulness has multiple competing definitions).
- Reporting many metrics shifts the interpretation burden onto the reader.

        ## How EMERALD-AI uses this paper
        Section 4.6 + section 5.11 explanation-fidelity validation.

        ## Related entries
        - [[slack2020fooling]] — motivates the need for empirical fidelity evaluation
- [[aas2021explaining]] — fidelity-under-dependence concern
- → [[themes/4.6-xai-finance]]
