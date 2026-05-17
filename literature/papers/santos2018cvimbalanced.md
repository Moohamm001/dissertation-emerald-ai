        ---
        key: santos2018cvimbalanced
        title: "Cross-validation for imbalanced datasets: Avoiding overoptimistic and overfitting approaches"
        themes: [imbalance-calibration]
        ---

        # Santos et al. (2018) — the in-fold-only resampling rule

        ## Key claims
        - Applying SMOTE or any resampling before the CV split contaminates the validation folds and produces systematically overoptimistic performance estimates.
- The correct protocol is to apply resampling only inside each training fold, never on the validation/test fold.
- This error is widespread in published imbalanced-classification work — including credit scoring.

        ## Method (how the claim was established)
        Surveyed published imbalanced-classification studies for the methodological error; conducted controlled experiments quantifying the inflation in reported AUC.

        ## Relevance to EMERALD-AI
        Authority citation for the hard rule in EMERALD-AI's section 5.7: SMOTE-NC is applied strictly inside the CV training fold, never on the validation or test fold.

        ## Quotable lines
        - 'A high percentage of works… apply SMOTE before performing cross-validation, which leads to overoptimistic results.'
- 'A correct approach is to apply SMOTE only on the training set within each cross-validation iteration.'

        ## Limitations / counter-evidence
        - Focuses on SMOTE specifically; the same principle applies to any resampling/cleaning that uses target labels.
- The recommended protocol does not address the related question of how to evaluate the resampling method itself — that requires nested CV.

        ## How EMERALD-AI uses this paper
        Section 5.7 hard rule. Section 5.9 nested CV protocol citation.

        ## Related entries
        - [[chawla2002smote]] — the method this paper warns about misusing
- → [[themes/4.4-imbalance-calibration]]
