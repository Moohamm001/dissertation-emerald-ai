# Glossary — Domain Terms

Terms that recur in the EMERALD-AI literature and that future-me should disambiguate consistently. Listed alphabetically.

---

**ADASYN** — Adaptive Synthetic Sampling. Imbalance-correction method that generates more synthetic samples for harder-to-learn minority regions. See [[he2008adasyn]].

**AIF360** — AI Fairness 360. IBM-maintained open-source toolkit for fairness metrics and mitigation. Implementation surface for EMERALD-AI's fairness audit. See [[bellamy2018aif360]].

**ALE** — Accumulated Local Effects. Non-linear feature-effect plot more robust to feature dependence than PDP. Used in [[themes/4.6-xai-finance]] as a complement to TreeSHAP global attribution.

**Annex III** — The list in the EU AI Act of "high-risk" AI use cases. Credit scoring is point 5(b). Triggers Articles 9-15 obligations.

**APR** — Annual Percentage Rate. The headline cost-of-credit metric in the EMERALD-AI dataset; pre-funding feature.

**Boruta** — Wrapper feature-selection method using shadow features (random permutations of original features) as a null distribution. See [[kursa2010boruta]].

**Brier score** — Mean squared error between predicted probabilities and outcomes. Decomposes into calibration + refinement components. EMERALD-AI uses it as a calibration metric.

**Calibration** — Property that predicted probabilities match observed frequencies. Distinct from discrimination (AUC); a model can rank correctly yet predict probabilities biased upward or downward.

**Calibration-within-group** — Calibration evaluated separately on each protected group. One of four parity criteria. See [[chouldechova2017fair]].

**CARD** — Climate Action Risk Domain (project-internal coinage, not a literature term). Optional naming alternative; use only if explicitly requested.

**Censoring bias** — When the observation window cuts off an outcome that has not yet occurred. In EMERALD-AI: 'current' loans may yet default and be miscoded as creditworthy.

**Class imbalance** — Skewed class prevalence; default rates in well-underwritten credit portfolios sit in 2-15%.

**CatBoost** — Gradient-boosted decision tree implementation with ordered boosting + target-statistics encoding. Particularly strong on high-cardinality categoricals. See [[prokhorenkova2018catboost]].

**Conformal prediction** — Distribution-free framework producing prediction sets with guaranteed marginal coverage. EMERALD-AI uses split-conformal. See [[angelopoulos2023conformal]], [[vovk2005alrw]].

**Consumer Duty** — FCA UK regulatory framework (PS22/9, in force July 2023) requiring firms to deliver good outcomes for retail customers across four pillars. See [[fcaConsumerDuty2022]].

**Counterfactual explanation** — Minimal feature changes that would flip a model's decision. Actionable in a way attribution alone is not. See [[mothilal2020dice]], [[wachter2017counterfactual]].

**CRISP-DM** — Cross-Industry Standard Process for Data Mining. Process-model framework for ML projects; EMERALD-AI methodology is structured around it. See [[wirth2000crispdm]].

**Deal Status** — Outcome field in the EMERALD-AI dataset; values are paidOff, current, default, behind. Used to construct the binary creditworthiness target Y.

**Demographic parity** — Fairness criterion requiring equal positive-prediction rates across groups. Strictest and most contested of the four; ignores actual differences in base rates.

**DiCE** — Diverse Counterfactual Explanations. Optimisation-based counterfactual generator with diversity and feasibility constraints. See [[mothilal2020dice]].

**DVC** — Data Version Control. Tool used in EMERALD-AI for versioning data, models, and pipeline artefacts.

**EBM** — Explainable Boosting Machine. Inherently interpretable GA²M model from InterpretML. The Rudin-camp alternative to XGBoost+SHAP. See gap G6.

**ECE** — Expected Calibration Error. Bin-averaged absolute deviation between predicted and observed probabilities.

**Equalised odds** — Fairness criterion requiring equal TPR and equal FPR across groups. See [[hardt2016eqodds]].

**Equal opportunity** — Weaker version of equalised odds requiring only equal TPR across groups.

**EU AI Act** — Regulation (EU) 2024/1689. Classifies credit-scoring AI as Annex III high-risk; triggers Articles 9-15 obligations. See [[euAiAct2021]].

**EU Taxonomy** — Regulation (EU) 2020/852 defining sustainability classification criteria. One of three "green" definitions whose heterogeneity is discussed in [[themes/4.5-green-finance]].

**Factor Rate** — Multiplicative-rather-than-percentage interest convention; common in merchant cash advances. Present in EMERALD-AI dataset.

**Focal loss** — Modulated cross-entropy that down-weights easy examples; useful for extreme imbalance. See [[lin2017focal]].

**FT-Transformer** — Feature Tokeniser + Transformer. Strongest current single tabular DL architecture. See [[gorishniy2021revisiting]].

**GBDT** — Gradient-Boosted Decision Tree. Family encompassing XGBoost, LightGBM, CatBoost. Tabular state-of-the-art.

**Green Loan Principles (GLP)** — LMA / APLMA / LSTA voluntary governance standard for green-loan issuance. See [[lma2023glp]].

**Greenwashing** — Labelling debt or activity as green without genuine environmental qualification. Structural risk in green-finance markets. See [[ehlers2017greenbond]].

**HPO** — Hyperparameter Optimisation. EMERALD-AI uses Optuna's TPE + HyperBand. See [[akiba2019optuna]].

**Internal Ratings-Based (IRB) approach** — Basel II/III framework allowing banks to use internal models for credit-risk capital calculation. Requires calibrated PD estimates — the regulatory motivation for EMERALD-AI's calibration emphasis.

**Isotonic regression** — Non-parametric monotone calibrator. Alternative to Platt scaling. See [[zadrozny2002isotonic]].

**KernelSHAP** — Model-agnostic SHAP estimator via weighted linear regression on perturbed neighbours. Biased under feature dependence [[aas2021explaining]]. Used in EMERALD-AI as cross-check on TreeSHAP.

**KS statistic** — Kolmogorov-Smirnov. Maximum vertical distance between two CDFs. Industry-standard credit-risk discrimination metric.

**Label leakage** — Including features whose values are only knowable after the outcome is observed. Catastrophic — produces overoptimistic offline performance that vanishes in production.

**LightGBM** — GBDT implementation with histogram-based binning and leaf-wise growth. ~10x faster than XGBoost. See [[ke2017lightgbm]].

**LIME** — Local Interpretable Model-agnostic Explanations. Perturbation-based local surrogate. See [[ribeiro2016lime]].

**MLOps** — Machine Learning Operations. Practices for productionising and monitoring ML systems. EMERALD-AI uses MLflow, DVC, Docker, GitHub Actions, Prometheus, Evidently.

**Monotonic constraint** — Constraint enforcing that the model's predicted probability move in a specified direction with a specified feature. Native in XGBoost/LightGBM/CatBoost. EMERALD-AI applies monotonic constraints to Credit Score, Annual Revenue, Time in Business.

**MCC** — Matthews Correlation Coefficient. Balanced metric for binary classification that is robust to class imbalance. EMERALD-AI reports it alongside PR-AUC.

**Nested cross-validation** — Outer loop estimates generalisation; inner loop tunes hyperparameters. Avoids the over-optimism of single-loop CV with hyperparameter selection. See section 5.9.

**Optuna** — Bayesian hyperparameter optimisation framework using TPE + pruning. See [[akiba2019optuna]].

**Ordered boosting** — CatBoost technique that trains each instance's gradient estimate only on its predecessors in a random permutation, eliminating target leakage. See [[prokhorenkova2018catboost]].

**PDP** — Partial Dependence Plot. Marginal effect of a feature on the model's prediction, averaging over the joint distribution of other features. Used in EMERALD-AI's SHAP Explorer.

**Platt scaling** — Sigmoid post-hoc calibrator originally proposed for SVMs. See [[platt1999probabilistic]].

**PR-AUC** — Precision-Recall Area Under Curve. Robust to class imbalance; EMERALD-AI's primary discrimination metric.

**Predictive parity** — Fairness criterion requiring equal precision across groups.

**PSI** — Population Stability Index. Distribution-shift metric used in EMERALD-AI for both training-time stratification audit and production drift monitoring.

**Recall@top-decile** — Recall computed on the top 10% of risk-scored applicants. Regulator-relevant for adverse-action volume estimation.

**Quantus** — Toolkit for empirically evaluating explanation quality (faithfulness, robustness, complexity, randomisation). EMERALD-AI uses it for explanation-fidelity validation in section 5.11. See [[hedstrom2023quantus]].

**Reproducibility** — In EMERALD-AI: containerised env + pinned uv lockfile + DVC-versioned data and artefacts + MLflow-tracked runs + `make reproduce` target ≤8h.

**SAINT** — Self-Attention and Intersample Attention Transformer for tabular data. See [[somepalli2021saint]].

**SFDR** — Sustainable Finance Disclosure Regulation. EU regulation requiring sustainability-disclosure obligations for financial-market participants.

**SHAP** — SHapley Additive exPlanations. Unique attribution method satisfying local accuracy, missingness, and consistency. See [[lundberg2017shap]] and [[lundberg2020trees]] for the tree-specific TreeSHAP.

**SMOTE / SMOTE-NC** — Synthetic Minority Over-sampling Technique; NC variant handles mixed numeric/categorical features. See [[chawla2002smote]].

**Split-conformal prediction** — Conformal prediction using a held-out calibration split. Distribution-free, finite-sample, marginal-coverage-guaranteed. See [[angelopoulos2023conformal]].

**TabNet** — Tabular DL architecture with sequential attention and built-in feature attribution. See [[arik2021tabnet]].

**Target encoding** — Encoding a categorical feature by its mean target value. Powerful but leak-prone; CatBoost's ordered target statistics eliminate the leak. See [[micciBarreca2001]].

**TPE** — Tree-structured Parzen Estimator. Bayesian optimisation sampler used by Optuna.

**TreeSHAP** — Exact polynomial-time Shapley-value algorithm for tree ensembles. See [[lundberg2020trees]].

**uv lockfile** — Modern Python dependency-pinning format used in EMERALD-AI for reproducibility.

**XGBoost** — Gradient-boosted decision tree implementation with regularisation and sparsity-aware splits. EMERALD-AI's primary candidate model. See [[chen2016xgboost]].

**Z-score** — Altman's 1968 linear combination of five financial ratios; founding artefact of statistical credit/bankruptcy scoring. See [[altman1968]].
