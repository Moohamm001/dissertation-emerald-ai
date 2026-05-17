        ---
        key: chawla2002smote
        title: "SMOTE: Synthetic minority over-sampling technique"
        themes: [imbalance-calibration]
        ---

        # Chawla et al. (2002) — SMOTE foundational paper

        ## Key claims
        - Synthesise minority-class examples by interpolating between each minority instance and its k nearest neighbours of the same class.
- Combined with majority under-sampling, SMOTE outperforms naive over-sampling (which only duplicates) on a range of imbalanced classification benchmarks.

        ## Method (how the claim was established)
        Algorithmic description + benchmarks on nine imbalanced UCI datasets vs naive over- and under-sampling.

        ## Relevance to EMERALD-AI
        Foundational citation for section 4.4 + the SMOTE-NC variant used in section 5.7 for mixed numeric/categorical resampling on green-loan data.

        ## Quotable lines
        - 'SMOTE forces focused learning and introduces a bias towards the minority class.'
- The original synthetic-sample equation: x_new = x + λ(x_nn - x) for λ ∈ [0,1].

        ## Limitations / counter-evidence
        - Can generate implausible synthetic minority points in high-dimensional or strongly non-linear feature spaces.
- Originally numeric-only; SMOTE-NC extends it to mixed types.
- Does not interact well with overlapping class regions (where minority points lie in majority territory).

        ## How EMERALD-AI uses this paper
        Section 4.4 anchor. Section 5.7 — SMOTE-NC is one of three head-to-head balancing strategies.

        ## Related entries
        - [[he2008adasyn]] — adaptive variant
- [[santos2018cvimbalanced]] — the in-fold-only rule for using SMOTE correctly
- → [[themes/4.4-imbalance-calibration]]
