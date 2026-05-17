        ---
        key: baesens2003benchmark
        title: "Benchmarking state-of-the-art classification algorithms for credit scoring"
        themes: [evolution-credit-scoring, benchmarking]
        ---

        # Baesens et al. (2003) — first systematic ML classifier benchmark on credit data

        ## Key claims
        - Across eight real credit datasets, neural networks and support vector machines consistently outperform logistic regression and other classical methods.
- The accuracy gains are statistically significant but modest; the case for adopting ML is incremental rather than revolutionary.

        ## Method (how the claim was established)
        Compared 17 classifiers (NN, SVM, LR, LDA, k-NN, naive Bayes, decision trees, etc.) on 8 real credit datasets using PCC, AUC, and statistical significance testing (paired t-tests, Wilcoxon).

        ## Relevance to EMERALD-AI
        Founding benchmark for ML in credit scoring; lessmann2015benchmark explicitly updates this study. Cited in section 4.1 to ground the empirical case that ML can outperform LR, and in section 5.8 as justification for including SVM in EMERALD-AI's baseline panel.

        ## Quotable lines
        - 'Both NNs and SVMs yield very good performance on most credit-scoring datasets.'
- The headline AUC comparison table is frequently reproduced in subsequent reviews.

        ## Limitations / counter-evidence
        - Predates GBDTs entirely (XGBoost is 2016).
- Datasets are small by modern standards; cross-validation protocol is single 10-fold, not nested.
- No treatment of calibration or explainability — only classification accuracy.

        ## How EMERALD-AI uses this paper
        Section 4.1 lineage citation. Section 5.8 justification for SVM as historical baseline.

        ## Related entries
        - [[lessmann2015benchmark]] — the 2015 update
- [[dumitrescu2022ml]] — modern reframing of accuracy/interpretability trade-off
- → [[themes/4.1-evolution-credit-scoring]]
