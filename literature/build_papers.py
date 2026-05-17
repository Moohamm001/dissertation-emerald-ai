"""Generate per-paper markdown notes for the EMERALD-AI literature brain.

Each entry is a dict with consistent fields. Adding a new paper file = adding a
new dict entry + running this script.

The template intentionally uses zero leading indentation so that interpolated
list content (which has zero indent) sits flush at column 0, allowing the
research-engine section parser to find ## headings.
"""
from pathlib import Path

OUT = Path(__file__).parent / "papers"
OUT.mkdir(exist_ok=True)


TEMPLATE = """\
---
key: {key}
title: "{title}"
themes: [{themes_csv}]
---

# {citation}

## Key claims
{claims}

## Method (how the claim was established)
{method}

## Relevance to EMERALD-AI
{relevance}

## Quotable lines
{quotes}

## Limitations / counter-evidence
{limitations}

## How EMERALD-AI uses this paper
{used_for}

## Related entries
{related}
"""


def write(key, *, title, citation, themes, claims, method, relevance, quotes,
          limitations, used_for, related):
    body = TEMPLATE.format(
        key=key,
        title=title,
        themes_csv=", ".join(themes),
        citation=citation,
        claims=claims,
        method=method,
        relevance=relevance,
        quotes=quotes,
        limitations=limitations,
        used_for=used_for,
        related=related,
    )
    (OUT / f"{key}.md").write_text(body, encoding="utf-8")


# =============================================================================
PAPERS = [
    dict(
        key="altman1968",
        title="Financial ratios, discriminant analysis and the prediction of corporate bankruptcy",
        citation="Altman (1968) — Z-score / discriminant analysis for bankruptcy prediction",
        themes=["evolution-credit-scoring"],
        claims=(
            "- A linear combination of five financial ratios (working capital / assets, retained earnings / assets, "
            "EBIT / assets, market value equity / book value debt, sales / assets) discriminates bankrupt vs solvent "
            "firms with 95% accuracy one year before failure on the original sample.\n"
            "- The Z-score (Z = 1.2 X1 + 1.4 X2 + 3.3 X3 + 0.6 X4 + 1.0 X5) becomes the founding artefact of statistical "
            "credit / bankruptcy scoring."
        ),
        method=(
            "Multiple discriminant analysis (MDA) on a matched sample of 33 bankrupt manufacturing firms (1946-1965) "
            "vs 33 non-bankrupt controls."
        ),
        relevance=(
            "Context / lineage citation. Establishes the lineage that runs from MDA → logistic regression → modern ML. "
            "Useful to ground the historical narrative in section 4.1; not a methodological dependency for EMERALD-AI."
        ),
        quotes=(
            "- 'The Z-score is a useful summary statistic for distinguishing potentially bankrupt firms…'\n"
            "- The original 95% / 72% one- and two-year-ahead accuracy figures."
        ),
        limitations=(
            "- Sample is small (66 firms), US-only, manufacturing-only, 1946-1965.\n"
            "- Linear model with no provision for non-linearity; later Zeta and Z'' variants attempt repair.\n"
            "- Predates the modern ML treatment of class imbalance and out-of-sample validation."
        ),
        used_for=(
            "Cited in section 4.1 as the lineage origin of statistical credit modelling. No direct methodological use."
        ),
        related=(
            "- [[beaver1966]] — earlier univariate ratio analysis Altman extends\n"
            "- [[hand1997statistical]] — review tracing the lineage forward\n"
            "- → [[themes/4.1-evolution-credit-scoring]]"
        ),
    ),
    dict(
        key="hand1997statistical",
        title="Statistical classification methods in consumer credit scoring: A review",
        citation="Hand & Henley (1997) — review of statistical methods in consumer credit",
        themes=["evolution-credit-scoring"],
        claims=(
            "- Logistic regression, despite available alternatives (neural networks, recursive partitioning, "
            "k-nearest neighbours), remains the practical default in consumer credit scoring.\n"
            "- The differences in classification performance between methods are typically small; the choice is "
            "often driven by interpretability, ease of deployment, and regulatory acceptability rather than accuracy."
        ),
        method=(
            "Narrative review of the consumer credit-scoring literature to 1997, with empirical synthesis across "
            "published comparisons."
        ),
        relevance=(
            "Anchors the claim in section 4.1 that logistic regression has been the regulatory default for decades. "
            "Foundational citation for the interpretability-driven adoption pattern that EMERALD-AI then complicates."
        ),
        quotes=(
            "- 'Practitioners often prefer methods that yield interpretable models, even at some cost in predictive accuracy.'\n"
            "- The 'flat-maximum effect' observation: many methods give similar accuracy, so other criteria dominate."
        ),
        limitations=(
            "- Predates the modern ensemble era (XGBoost, RF) and the rise of SHAP-style post-hoc explanations.\n"
            "- The 'flat-maximum' claim has not held up uniformly under ensemble methods on larger modern datasets [[lessmann2015benchmark]]."
        ),
        used_for=(
            "Section 4.1 anchor citation for the historical interpretability vs accuracy tension."
        ),
        related=(
            "- [[thomas2000survey]] — complementary later review\n"
            "- [[lessmann2015benchmark]] — modern update showing ensembles do outperform\n"
            "- → [[themes/4.1-evolution-credit-scoring]]"
        ),
    ),
    dict(
        key="baesens2003benchmark",
        title="Benchmarking state-of-the-art classification algorithms for credit scoring",
        citation="Baesens et al. (2003) — first systematic ML classifier benchmark on credit data",
        themes=["evolution-credit-scoring", "benchmarking"],
        claims=(
            "- Across eight real credit datasets, neural networks and support vector machines consistently "
            "outperform logistic regression and other classical methods.\n"
            "- The accuracy gains are statistically significant but modest; the case for adopting ML is "
            "incremental rather than revolutionary."
        ),
        method=(
            "Compared 17 classifiers (NN, SVM, LR, LDA, k-NN, naive Bayes, decision trees, etc.) on 8 real credit "
            "datasets using PCC, AUC, and statistical significance testing (paired t-tests, Wilcoxon)."
        ),
        relevance=(
            "Founding benchmark for ML in credit scoring; lessmann2015benchmark explicitly updates this study. "
            "Cited in section 4.1 to ground the empirical case that ML can outperform LR, and in section 5.8 as "
            "justification for including SVM in EMERALD-AI's baseline panel."
        ),
        quotes=(
            "- 'Both NNs and SVMs yield very good performance on most credit-scoring datasets.'\n"
            "- The headline AUC comparison table is frequently reproduced in subsequent reviews."
        ),
        limitations=(
            "- Predates GBDTs entirely (XGBoost is 2016).\n"
            "- Datasets are small by modern standards; cross-validation protocol is single 10-fold, not nested.\n"
            "- No treatment of calibration or explainability — only classification accuracy."
        ),
        used_for=(
            "Section 4.1 lineage citation. Section 5.8 justification for SVM as historical baseline."
        ),
        related=(
            "- [[lessmann2015benchmark]] — the 2015 update\n"
            "- [[dumitrescu2022ml]] — modern reframing of accuracy/interpretability trade-off\n"
            "- → [[themes/4.1-evolution-credit-scoring]]"
        ),
    ),
    dict(
        key="lessmann2015benchmark",
        title="Benchmarking state-of-the-art classification algorithms for credit scoring: An update of research",
        citation="Lessmann et al. (2015) — 41-classifier credit-scoring benchmark",
        themes=["evolution-credit-scoring", "benchmarking", "gbdt-tabular-sota"],
        claims=(
            "- Heterogeneous ensemble methods (random forest, gradient boosting, stacking) dominate single learners.\n"
            "- The marginal accuracy gains from architectural sophistication shrink as dataset size grows.\n"
            "- The choice of evaluation metric matters: AUC, PCC, Brier score, and partial-AUC can rank methods "
            "differently — multi-metric reporting is mandatory."
        ),
        method=(
            "Compared 41 classifiers across 8 real credit datasets using 6 metrics. Applied the Friedman test + "
            "Nemenyi post-hoc to control multiple-comparison error."
        ),
        relevance=(
            "Pillar citation for sections 4.1 and 4.2. Establishes 'ensembles dominate' as a credit-scoring "
            "consensus, motivating EMERALD-AI's primary focus on GBDTs. Methodological exemplar for nested CV "
            "and multi-metric reporting."
        ),
        quotes=(
            "- 'Several heterogeneous ensemble classifiers, namely AvgS, HCES-Bag, MGN-1-stacking, and stacking, "
            "perform significantly better than the industry standard, logistic regression.'\n"
            "- The Friedman-Nemenyi ranking diagrams from Figures 3-4 are widely cited."
        ),
        limitations=(
            "- Datasets are still relatively small (largest ~150k records).\n"
            "- Does not cover XGBoost (2016) or modern tabular DL.\n"
            "- No fairness, calibration, or explainability dimension."
        ),
        used_for=(
            "Sections 4.1 and 4.2 anchor citation. Section 5.13 methodological precedent for multi-metric "
            "reporting with paired statistical testing."
        ),
        related=(
            "- [[baesens2003benchmark]] — the original benchmark being updated\n"
            "- [[dumitrescu2022ml]] — newer reframing\n"
            "- [[chen2016xgboost]] — XGBoost, post-dates this study\n"
            "- → [[themes/4.1-evolution-credit-scoring]]\n"
            "- → [[themes/4.2-gbdt-tabular-sota]]"
        ),
    ),
    dict(
        key="dumitrescu2022ml",
        title="Machine learning for credit scoring: Improving logistic regression with non-linear decision-tree effects",
        citation="Dumitrescu, Hue, Hurlin & Tokpavi (2022) — penalised LR + tree interactions ≈ XGBoost",
        themes=["evolution-credit-scoring", "xai-finance"],
        claims=(
            "- An adaptive lasso logistic regression augmented with decision-tree-derived non-linear interaction "
            "terms ('penalised logistic tree regression', PLTR) matches XGBoost AUC on multiple credit datasets.\n"
            "- The accuracy-interpretability frontier is not fixed: with careful feature construction, interpretable "
            "models can recover most of the predictive gain claimed by opaque ones."
        ),
        method=(
            "Used short shallow CART trees to extract interaction features, then fit an adaptive-lasso LR on the "
            "augmented feature set. Compared to XGBoost, RF, and plain LR on six credit datasets."
        ),
        relevance=(
            "Critical citation for section 4.1's central argument that the accuracy/interpretability trade-off is "
            "a design choice. Strengthens the case for EMERALD-AI's middle-path posture (constrained tree ensemble "
            "+ explanation stack) rather than pure-DL."
        ),
        quotes=(
            "- 'PLTR achieves a performance close to that of more complex algorithms while remaining intrinsically "
            "interpretable.'\n"
            "- 'The interpretability-performance trade-off can be substantially mitigated.'"
        ),
        limitations=(
            "- The 'close to XGBoost' claim still leaves a gap that may matter at scale.\n"
            "- The interaction-extraction step itself uses opaque trees, so the 'interpretable' label applies to the "
            "final LR coefficient surface, not the entire pipeline.\n"
            "- Results are on conventional, not green, credit data."
        ),
        used_for=(
            "Section 4.1 framing citation. Could also justify including a PLTR-style model in the comparison "
            "panel of section 5.8 — currently not, but worth flagging as a possible extension."
        ),
        related=(
            "- [[lessmann2015benchmark]] — the benchmark this paper revisits\n"
            "- [[rudin2019stop]] — adjacent argument for interpretable models in high-stakes settings\n"
            "- → [[themes/4.1-evolution-credit-scoring]]\n"
            "- → [[themes/4.6-xai-finance]]"
        ),
    ),
    dict(
        key="chen2016xgboost",
        title="XGBoost: A scalable tree boosting system",
        citation="Chen & Guestrin (2016) — XGBoost foundational paper",
        themes=["gbdt-tabular-sota"],
        claims=(
            "- A scalable gradient-boosting framework combining (a) second-order Newton boosting, (b) L1/L2 leaf-weight "
            "regularisation, (c) sparsity-aware split finding for missing data, (d) cache-aware out-of-core computation.\n"
            "- Wins or matches state-of-the-art on the majority of Kaggle tabular competitions surveyed at the time."
        ),
        method=(
            "Theoretical derivation of regularised second-order objective + extensive empirical evaluation on "
            "regression, classification, ranking, and large-scale tabular tasks."
        ),
        relevance=(
            "Foundational citation for EMERALD-AI's primary candidate model. Cited 30k+ times. The monotonic-"
            "constraint feature added post-publication (XGBoost ≥0.81) is the specific implementation hook for the "
            "monotonicity argument in section 5.8."
        ),
        quotes=(
            "- 'A novel sparsity-aware algorithm for sparse data and weighted quantile sketch for approximate tree "
            "learning.'\n"
            "- The Kaggle dominance statistic: '17 of 29 winning solutions on Kaggle in 2015 used XGBoost.'"
        ),
        limitations=(
            "- Original paper does not cover monotonic constraints, GPU training, or DART dropout — these are later additions.\n"
            "- Tree ensembles extrapolate poorly; OOD generalisation is a known weakness not addressed here.\n"
            "- No explicit treatment of calibration."
        ),
        used_for=(
            "Section 4.2 anchor. Section 5.8 model specification: XGBoost with monotonic constraints on Credit "
            "Score, Annual Revenue, Time in Business."
        ),
        related=(
            "- [[ke2017lightgbm]] — sibling GBDT implementation\n"
            "- [[prokhorenkova2018catboost]] — CatBoost\n"
            "- [[lundberg2020trees]] — TreeSHAP, the XGBoost-companion explainer\n"
            "- → [[themes/4.2-gbdt-tabular-sota]]"
        ),
    ),
    dict(
        key="ke2017lightgbm",
        title="LightGBM: A highly efficient gradient boosting decision tree",
        citation="Ke et al. (2017) — LightGBM (histogram-based, leaf-wise)",
        themes=["gbdt-tabular-sota"],
        claims=(
            "- Gradient-based One-Side Sampling (GOSS) and Exclusive Feature Bundling (EFB) reduce training cost "
            "by an order of magnitude vs XGBoost without measurable accuracy loss.\n"
            "- Leaf-wise tree growth (vs XGBoost's level-wise) yields lower loss for the same number of leaves at "
            "the cost of higher overfitting risk on small datasets."
        ),
        method=(
            "Algorithmic derivation + benchmark vs XGBoost and sklearn GBM on five public datasets including Allstate, "
            "Flight Delay, and KDD Cup datasets."
        ),
        relevance=(
            "Alternative GBDT implementation in EMERALD-AI's section 5.8 panel. Its differing bias profile (leaf-wise "
            "growth, histogram binning) serves as cross-validation against single-implementation idiosyncrasies."
        ),
        quotes=(
            "- 'LightGBM speeds up the training process of conventional GBDT by up to over 20 times while achieving "
            "almost the same accuracy.'"
        ),
        limitations=(
            "- Leaf-wise growth can overfit on the small-to-moderate datasets typical in finance unless num_leaves "
            "is constrained — a relevant tuning concern for our n ≈ 14k.\n"
            "- Categorical handling via 'categorical_feature' is heuristic; CatBoost's ordered-target encoding is "
            "more principled."
        ),
        used_for=(
            "Section 5.8 GBDT comparison panel."
        ),
        related=(
            "- [[chen2016xgboost]] — sibling\n"
            "- [[prokhorenkova2018catboost]] — sibling\n"
            "- → [[themes/4.2-gbdt-tabular-sota]]"
        ),
    ),
    dict(
        key="prokhorenkova2018catboost",
        title="CatBoost: Unbiased boosting with categorical features",
        citation="Prokhorenkova et al. (2018) — CatBoost / ordered boosting / ordered target statistics",
        themes=["gbdt-tabular-sota"],
        claims=(
            "- Naive target encoding induces 'prediction shift' (a target-leakage-like bias) when used inside "
            "gradient boosting; ordered target statistics eliminate this by training each instance only on "
            "predecessors in a random permutation.\n"
            "- Ordered boosting extends the same principle to the gradient estimates themselves."
        ),
        method=(
            "Theoretical proof of the bias-elimination property + benchmark on multiple datasets including KDD'09 "
            "Appetency, Internet, Adult."
        ),
        relevance=(
            "Best-in-class GBDT for high-cardinality categoricals (Industry ~30 levels, Borrower State ~50 levels in "
            "our dataset). Strong candidate to win the GBDT family comparison; included in section 5.8 panel."
        ),
        quotes=(
            "- 'The proposed scheme guarantees that target statistics for any example are computed only from "
            "previous examples, avoiding target leakage.'"
        ),
        limitations=(
            "- Slower than LightGBM out of the box; ordering overhead can dominate on very large data.\n"
            "- The 'unbiased' guarantee is asymptotic; finite-sample behaviour can still leak signal."
        ),
        used_for=(
            "Section 5.8 GBDT comparison panel; specifically expected to handle Industry and Borrower State without "
            "the leave-one-out target-encoder workaround used for the other learners."
        ),
        related=(
            "- [[chen2016xgboost]] — sibling\n"
            "- [[ke2017lightgbm]] — sibling\n"
            "- [[micciBarreca2001]] — target encoding origin; CatBoost fixes its leakage problem\n"
            "- → [[themes/4.2-gbdt-tabular-sota]]"
        ),
    ),
    dict(
        key="shwartz2022deep",
        title="Tabular data: Deep learning is not all you need",
        citation="Shwartz-Ziv & Armon (2022) — independent benchmark showing GBDT > tabular DL",
        themes=["gbdt-tabular-sota", "tabular-deep-learning"],
        claims=(
            "- On 11 public datasets including those used by the original tabular-DL papers, XGBoost beats every "
            "deep tabular model tested (TabNet, NODE, DNF-Net, 1D-CNN), often by a wide margin.\n"
            "- Even on the deep models' own benchmark datasets, XGBoost wins after careful tuning — suggesting the "
            "original DL claims were partly tuning-effort artefacts."
        ),
        method=(
            "Re-ran each deep tabular model on the union of all benchmark datasets used across the original papers, "
            "with consistent hyperparameter budget for all methods. Reported AUC, RMSE, and ranking."
        ),
        relevance=(
            "Pillar citation for section 4.3's sober positioning on tabular DL. Justifies EMERALD-AI's choice to "
            "include DL models as honest comparators rather than headline approaches."
        ),
        quotes=(
            "- 'Deep models were worse than XGBoost on most of the studied datasets.'\n"
            "- 'An ensemble of deep models and XGBoost performs best.'"
        ),
        limitations=(
            "- The benchmark datasets are small to medium; results may not extend to very large industry datasets.\n"
            "- The hyperparameter search budget is finite; DL methods may benefit disproportionately from more "
            "aggressive tuning.\n"
            "- Does not test FT-Transformer or SAINT (the strongest recent tabular DL methods)."
        ),
        used_for=(
            "Section 4.3 anchor. Justifies the headline of section 5.8 that GBDTs are the primary candidate family."
        ),
        related=(
            "- [[grinsztajn2022trees]] — corroborating recent benchmark with broader model coverage\n"
            "- [[gorishniy2021revisiting]] — FT-Transformer (omitted by Shwartz-Ziv)\n"
            "- → [[themes/4.2-gbdt-tabular-sota]]\n"
            "- → [[themes/4.3-tabular-deep-learning]]"
        ),
    ),
    dict(
        key="grinsztajn2022trees",
        title="Why do tree-based models still outperform deep learning on tabular data?",
        citation="Grinsztajn, Oyallon & Varoquaux (2022) — diagnoses why DL underperforms on tabular",
        themes=["gbdt-tabular-sota", "tabular-deep-learning"],
        claims=(
            "- Tree-based methods outperform DL on 45 tabular datasets across mixed-feature and numerical-only regimes.\n"
            "- Three diagnostic reasons: (1) DL is biased toward overly smooth target functions; (2) uninformative features "
            "hurt DL more than trees; (3) DL is rotationally invariant, but tabular data is not — feature orientation matters."
        ),
        method=(
            "Curated 45 medium-sized tabular benchmark datasets (the Tabular Benchmark). Compared XGBoost, GBM, RF, "
            "FT-Transformer, ResNet, MLP, SAINT with 20k-trial hyperparameter searches each."
        ),
        relevance=(
            "Most-cited recent paper on this question. Anchor for sections 4.2 and 4.3. Its three diagnostic "
            "reasons frame the section 4.3 paragraph about when DL earns its keep."
        ),
        quotes=(
            "- 'On medium-sized data… tree-based models are still state-of-the-art.'\n"
            "- 'Empirical investigation into the differences between deep learning models and tree-based models, "
            "which sheds light on the reasons for the superiority of tree-based models.'"
        ),
        limitations=(
            "- 'Medium-sized' is 1k-50k samples; at 10⁶+ rows the story may differ.\n"
            "- Does not test SOTA pre-trained foundation models for tabular (TabPFN, TabuLa-8B post-date this)."
        ),
        used_for=(
            "Sections 4.2 and 4.3 anchor. The dataset size of our project (~14k) sits squarely in the regime they study, "
            "lending direct external validity."
        ),
        related=(
            "- [[shwartz2022deep]] — corroborating earlier benchmark\n"
            "- [[gorishniy2021revisiting]] — FT-Transformer is one of the DL methods tested here\n"
            "- [[borisov2022dnntabular]] — broader survey\n"
            "- → [[themes/4.2-gbdt-tabular-sota]]\n"
            "- → [[themes/4.3-tabular-deep-learning]]"
        ),
    ),
    dict(
        key="lundberg2020trees",
        title="From local explanations to global understanding with explainable AI for trees",
        citation="Lundberg et al. (2020) — TreeSHAP: exact Shapley values for tree ensembles in polynomial time",
        themes=["gbdt-tabular-sota", "xai-finance"],
        claims=(
            "- For any tree ensemble (RF, GBDT), Shapley values for each prediction can be computed exactly in "
            "O(TLD²) time where T = trees, L = leaves, D = depth — fast enough for production.\n"
            "- SHAP interaction values give principled, model-grounded second-order feature interaction strength.\n"
            "- Aggregating local SHAP across the dataset yields global feature importance with consistency "
            "guarantees that mean-decrease-in-impurity lacks."
        ),
        method=(
            "Algorithmic derivation of TreeSHAP + extensive empirical use on medical risk-prediction case studies "
            "(mortality prediction, hospital re-admission)."
        ),
        relevance=(
            "Core enabling result for EMERALD-AI's explainability stack. Section 5.11 specifies TreeSHAP as the "
            "primary attribution method; this paper is the citation for both speed and consistency."
        ),
        quotes=(
            "- 'The combination of exact computation, interaction effects, and consistent global importance enables "
            "trustworthy explanation of tree-based models.'\n"
            "- 'TreeExplainer's local explanations are consistent and locally accurate.'"
        ),
        limitations=(
            "- Exactness applies to TreeSHAP specifically; KernelSHAP for other model types remains an approximation.\n"
            "- 'Consistency' is a desirable axiom but does not guarantee causal correctness — see [[aas2021explaining]], "
            "[[janzing2020feature]].\n"
            "- Feature dependence is handled via the 'tree_path_dependent' or 'interventional' algorithms; choice affects "
            "attribution magnitude."
        ),
        used_for=(
            "Section 4.2 (regulator-friendliness of GBDT). Section 4.6 (XAI stack). Section 5.11 (TreeSHAP as primary "
            "local + global attribution method)."
        ),
        related=(
            "- [[lundberg2017shap]] — original SHAP paper\n"
            "- [[chen2016xgboost]] — model family this enables explanation of\n"
            "- [[aas2021explaining]] — critique of attribution under dependence\n"
            "- → [[themes/4.2-gbdt-tabular-sota]]\n"
            "- → [[themes/4.6-xai-finance]]"
        ),
    ),
    dict(
        key="arik2021tabnet",
        title="TabNet: Attentive interpretable tabular learning",
        citation="Arik & Pfister (2021) — TabNet: attention-based tabular DL with built-in feature attribution",
        themes=["tabular-deep-learning", "xai-finance"],
        claims=(
            "- Sequential attention over features with a learnable sparse mask at each decision step.\n"
            "- The attention masks double as built-in per-instance feature attribution — no post-hoc SHAP needed.\n"
            "- Competitive with or better than GBDTs on six public tabular datasets in the paper's own benchmark."
        ),
        method=(
            "Architecture combining sequential attention with sparse feature selection, trained with self-supervised "
            "masked feature reconstruction pre-training. Benchmarked on Forest Cover Type, Poker Hand, Sarcos, "
            "Higgs, Rossmann, KDD'99."
        ),
        relevance=(
            "One of the two DL models in EMERALD-AI's section 5.8 panel. The built-in attention attribution is a "
            "design alternative to TreeSHAP — worth empirical comparison even if TreeSHAP remains primary."
        ),
        quotes=(
            "- 'TabNet uses sequential attention to choose which features to reason from at each decision step, "
            "enabling interpretability and better learning.'"
        ),
        limitations=(
            "- Later independent benchmarks (e.g. [[shwartz2022deep]], [[grinsztajn2022trees]]) found TabNet underperforms "
            "well-tuned GBDTs on most datasets — the original paper's headline claims overstated.\n"
            "- The 'attention as attribution' claim is contested in the XAI literature (Jain & Wallace 2019)."
        ),
        used_for=(
            "Section 5.8 DL comparator. Section 4.3 example of attention-as-attribution claim."
        ),
        related=(
            "- [[gorishniy2021revisiting]] — FT-Transformer, the stronger sibling\n"
            "- [[shwartz2022deep]] — independent benchmark showing TabNet underperforms GBDT\n"
            "- → [[themes/4.3-tabular-deep-learning]]"
        ),
    ),
    dict(
        key="gorishniy2021revisiting",
        title="Revisiting deep learning models for tabular data",
        citation="Gorishniy et al. (2021) — FT-Transformer + sober benchmark of tabular DL",
        themes=["tabular-deep-learning"],
        claims=(
            "- A simple MLP with carefully chosen hyperparameters often matches more elaborate tabular DL architectures.\n"
            "- FT-Transformer (feature-tokeniser + standard transformer encoder) is the strongest single tabular DL "
            "method tested.\n"
            "- Across 11 datasets, no single architecture dominates — including GBDTs, which the paper treats as a "
            "tough baseline they often fail to beat."
        ),
        method=(
            "Implemented MLP, ResNet, FT-Transformer, and others under a unified hyperparameter-tuning protocol "
            "(Optuna, identical budgets). Evaluated on 11 tabular benchmarks including California Housing, Adult, "
            "Higgs, Year, Microsoft."
        ),
        relevance=(
            "Strongest credible single tabular DL architecture for inclusion in section 5.8. The paper's own caveats "
            "about GBDT competitiveness inform section 4.3's sober positioning."
        ),
        quotes=(
            "- 'FT-Transformer demonstrates the best performance on most tasks and becomes a new powerful solution for "
            "the field.'\n"
            "- 'GBDT is still a tough-to-beat baseline.'"
        ),
        limitations=(
            "- Benchmark datasets are still medium-sized.\n"
            "- The hyperparameter tuning is exhaustive; production-grade tuning budgets may not reach the same gains.\n"
            "- Does not cover modern self-supervised pre-training approaches."
        ),
        used_for=(
            "Section 5.8 DL panel — FT-Transformer is the chosen instantiation. Section 4.3 anchor."
        ),
        related=(
            "- [[arik2021tabnet]] — included as comparator\n"
            "- [[grinsztajn2022trees]] — corroborates 'GBDT tough to beat'\n"
            "- → [[themes/4.3-tabular-deep-learning]]"
        ),
    ),
    dict(
        key="chawla2002smote",
        title="SMOTE: Synthetic minority over-sampling technique",
        citation="Chawla et al. (2002) — SMOTE foundational paper",
        themes=["imbalance-calibration"],
        claims=(
            "- Synthesise minority-class examples by interpolating between each minority instance and its k nearest "
            "neighbours of the same class.\n"
            "- Combined with majority under-sampling, SMOTE outperforms naive over-sampling (which only duplicates) "
            "on a range of imbalanced classification benchmarks."
        ),
        method=(
            "Algorithmic description + benchmarks on nine imbalanced UCI datasets vs naive over- and under-sampling."
        ),
        relevance=(
            "Foundational citation for section 4.4 + the SMOTE-NC variant used in section 5.7 for mixed numeric/"
            "categorical resampling on green-loan data."
        ),
        quotes=(
            "- 'SMOTE forces focused learning and introduces a bias towards the minority class.'\n"
            "- The original synthetic-sample equation: x_new = x + λ(x_nn - x) for λ ∈ [0,1]."
        ),
        limitations=(
            "- Can generate implausible synthetic minority points in high-dimensional or strongly non-linear feature "
            "spaces.\n"
            "- Originally numeric-only; SMOTE-NC extends it to mixed types.\n"
            "- Does not interact well with overlapping class regions (where minority points lie in majority territory)."
        ),
        used_for=(
            "Section 4.4 anchor. Section 5.7 — SMOTE-NC is one of three head-to-head balancing strategies."
        ),
        related=(
            "- [[he2008adasyn]] — adaptive variant\n"
            "- [[santos2018cvimbalanced]] — the in-fold-only rule for using SMOTE correctly\n"
            "- → [[themes/4.4-imbalance-calibration]]"
        ),
    ),
    dict(
        key="lin2017focal",
        title="Focal loss for dense object detection",
        citation="Lin, Goyal, Girshick, He & Dollár (2017) — focal loss for extreme imbalance",
        themes=["imbalance-calibration"],
        claims=(
            "- A modulating factor (1 - p_t)^γ applied to standard cross-entropy down-weights easy examples and "
            "focuses training on hard, misclassified cases.\n"
            "- Enables one-stage object detectors to match the accuracy of two-stage detectors (RetinaNet result)."
        ),
        method=(
            "Derivation of the focal loss + extensive empirical evaluation on COCO object detection (1:1000 "
            "foreground:background imbalance)."
        ),
        relevance=(
            "Origin paper for focal loss as a loss-level imbalance treatment. Used for the neural baseline in "
            "section 5.7 — particularly relevant given default prevalence in credit data, though less extreme "
            "than object detection."
        ),
        quotes=(
            "- 'A novel loss we term the focal loss that addresses class imbalance by reshaping the standard cross "
            "entropy loss such that it down-weights the loss assigned to well-classified examples.'"
        ),
        limitations=(
            "- The γ hyperparameter must be tuned; γ=2 is the common default but data-dependent.\n"
            "- Does not address the calibration question — focal-loss models can be poorly calibrated and need "
            "post-hoc fix.\n"
            "- Originally for dense detection; transfer to tabular classification is the by-now-standard "
            "extrapolation but not what the paper actually studied."
        ),
        used_for=(
            "Section 5.7 loss-level imbalance treatment for the MLP and FT-Transformer baselines."
        ),
        related=(
            "- [[chawla2002smote]] — resampling-based alternative\n"
            "- → [[themes/4.4-imbalance-calibration]]"
        ),
    ),
    dict(
        key="santos2018cvimbalanced",
        title="Cross-validation for imbalanced datasets: Avoiding overoptimistic and overfitting approaches",
        citation="Santos et al. (2018) — the in-fold-only resampling rule",
        themes=["imbalance-calibration"],
        claims=(
            "- Applying SMOTE or any resampling before the CV split contaminates the validation folds and produces "
            "systematically overoptimistic performance estimates.\n"
            "- The correct protocol is to apply resampling only inside each training fold, never on the validation/test "
            "fold.\n"
            "- This error is widespread in published imbalanced-classification work — including credit scoring."
        ),
        method=(
            "Surveyed published imbalanced-classification studies for the methodological error; conducted controlled "
            "experiments quantifying the inflation in reported AUC."
        ),
        relevance=(
            "Authority citation for the hard rule in EMERALD-AI's section 5.7: SMOTE-NC is applied strictly inside "
            "the CV training fold, never on the validation or test fold."
        ),
        quotes=(
            "- 'A high percentage of works… apply SMOTE before performing cross-validation, which leads to "
            "overoptimistic results.'\n"
            "- 'A correct approach is to apply SMOTE only on the training set within each cross-validation iteration.'"
        ),
        limitations=(
            "- Focuses on SMOTE specifically; the same principle applies to any resampling/cleaning that uses target "
            "labels.\n"
            "- The recommended protocol does not address the related question of how to evaluate the resampling "
            "method itself — that requires nested CV."
        ),
        used_for=(
            "Section 5.7 hard rule. Section 5.9 nested CV protocol citation."
        ),
        related=(
            "- [[chawla2002smote]] — the method this paper warns about misusing\n"
            "- → [[themes/4.4-imbalance-calibration]]"
        ),
    ),
    dict(
        key="angelopoulos2023conformal",
        title="Conformal prediction: A gentle introduction",
        citation="Angelopoulos & Bates (2023) — modern tutorial on split-conformal prediction",
        themes=["imbalance-calibration"],
        claims=(
            "- Split-conformal prediction wraps any black-box model to produce prediction sets with guaranteed "
            "marginal coverage at user-specified confidence levels, distribution-free, finite-sample.\n"
            "- The only requirement is exchangeability of the calibration and test data.\n"
            "- Adaptive variants (Mondrian, conformalised quantile regression) extend the guarantee to conditional "
            "coverage in specific regimes."
        ),
        method=(
            "Tutorial paper synthesising the conformal prediction literature into a practitioner-accessible reference."
        ),
        relevance=(
            "Primary citation for EMERALD-AI's section 5.10 conformal prediction implementation. The modern reference "
            "if a reviewer asks 'why is this distribution-free?'"
        ),
        quotes=(
            "- 'Conformal prediction is a user-friendly paradigm for creating statistically rigorous uncertainty sets "
            "for the predictions of any black-box model.'"
        ),
        limitations=(
            "- Marginal coverage guarantee does not imply conditional coverage — a high-risk applicant may still get "
            "an overconfident interval. Mondrian conformal addresses this partially.\n"
            "- Requires a held-out calibration set, reducing data available for training/validation.\n"
            "- The exchangeability assumption fails under distribution shift — a real concern for credit data."
        ),
        used_for=(
            "Section 4.4 anchor. Section 5.10 implementation citation."
        ),
        related=(
            "- [[vovk2005alrw]] — foundational textbook\n"
            "- [[platt1999probabilistic]], [[zadrozny2002isotonic]] — point-calibration counterparts\n"
            "- → [[themes/4.4-imbalance-calibration]]"
        ),
    ),
    dict(
        key="lma2023glp",
        title="Green Loan Principles",
        citation="Loan Market Association, APLMA & LSTA (2023) — Green Loan Principles",
        themes=["green-finance"],
        claims=(
            "- Defines four pillars for green-loan governance: use of proceeds, process for project evaluation and "
            "selection, management of proceeds, and reporting.\n"
            "- Voluntary, market-led standard; widely adopted by syndicated-loan participants but not legally binding."
        ),
        method=(
            "Industry consensus document maintained jointly by LMA, APLMA, and LSTA."
        ),
        relevance=(
            "Authority on what 'green loan' means in practice. Useful framing in introduction and section 4.5. The "
            "'use of proceeds' pillar is the closest thing to a definition we have for the dataset's labelling."
        ),
        quotes=(
            "- The four-pillar structure is the standard citable reference for green-loan governance."
        ),
        limitations=(
            "- Voluntary; compliance is not externally audited.\n"
            "- Project-evaluation criteria are intentionally non-prescriptive, leaving wide variance across lenders.\n"
            "- Updated periodically; ensure citation uses the current (Feb 2023) version."
        ),
        used_for=(
            "Introduction (market growth claim). Section 4.5 (governance framing). The dataset's 'green' provenance "
            "may or may not align with GLP — flagged as a known data-governance question in [[gaps]]."
        ),
        related=(
            "- [[euTaxonomy2020]] — regulatory taxonomy alternative\n"
            "- [[ehlers2017greenbond]] — greenwashing critique\n"
            "- → [[themes/4.5-green-finance]]"
        ),
    ),
    dict(
        key="ehlers2017greenbond",
        title="Green bond finance and certification",
        citation="Ehlers & Packer (2017) — BIS Quarterly Review on information asymmetry in green debt",
        themes=["green-finance"],
        claims=(
            "- The green-debt market is characterised by significant information asymmetry between issuers and "
            "investors over the genuine environmental quality of funded projects.\n"
            "- Third-party certification (Climate Bonds Initiative, second-party opinions) partially mitigates "
            "but does not fully resolve the asymmetry.\n"
            "- Greenwashing — labelling debt as green without genuine eligibility — is a structural risk for the "
            "asset class."
        ),
        method=(
            "Descriptive analysis of the global green-bond market and the certification ecosystem, with case studies."
        ),
        relevance=(
            "Authority citation for section 4.5's greenwashing argument and for the introduction's framing of "
            "structural information gaps in green lending."
        ),
        quotes=(
            "- 'Green bond finance and certification: third parties verify that the proceeds will fund genuinely "
            "environmental projects.'\n"
            "- The information-asymmetry framing is the most-cited contribution."
        ),
        limitations=(
            "- Pre-dates the EU Taxonomy Regulation and SFDR; regulatory landscape has evolved.\n"
            "- Focus is on green bonds, not green loans — the structural argument transfers but with caveats."
        ),
        used_for=(
            "Introduction and section 4.5 anchor for greenwashing / asymmetry framing."
        ),
        related=(
            "- [[flammer2021corporate]] — empirical follow-up on rigorous green issuance\n"
            "- [[berg2022esg]] — ESG-rating divergence as a symptom\n"
            "- → [[themes/4.5-green-finance]]"
        ),
    ),
    dict(
        key="flammer2021corporate",
        title="Corporate green bonds",
        citation="Flammer (2021) — empirical evidence on corporate green bond issuance and environmental performance",
        themes=["green-finance"],
        claims=(
            "- Companies that issue green bonds subsequently improve environmental performance (lower CO₂ emissions, "
            "higher environmental ratings), particularly when the issuance is third-party-certified.\n"
            "- Stock-market reaction to green-bond announcements is positive, indicating investor belief in the "
            "credibility signal.\n"
            "- Green-bond issuance attracts a higher share of long-term and 'green' investors."
        ),
        method=(
            "Difference-in-differences event study on a global sample of corporate green bonds 2013-2018; tested "
            "subsequent environmental and financial performance."
        ),
        relevance=(
            "Premier empirical evidence on green-finance effectiveness when issuance is rigorous. Supports section "
            "4.5's argument that accurate, well-calibrated credit assessment of green loans matters because the "
            "environmental impact is real and conditional on credibility."
        ),
        quotes=(
            "- 'Companies improve their environmental performance after the issuance of green bonds.'\n"
            "- 'The increase in environmental performance is concentrated in green bonds that are certified by an "
            "independent third party.'"
        ),
        limitations=(
            "- Sample is corporate green bonds, not commercial green loans — extrapolation needed.\n"
            "- Difference-in-differences identification rests on parallel-trends assumption; sceptical readers should "
            "weight accordingly.\n"
            "- 'Environmental performance' measured via E-pillar ESG scores, which are themselves contested [[berg2022esg]]."
        ),
        used_for=(
            "Section 4.5 anchor for 'rigorous green issuance has real environmental effect → accurate credit scoring matters'."
        ),
        related=(
            "- [[tang2020shareholders]] — companion empirical study\n"
            "- [[berg2022esg]] — caveat on E-pillar measurement\n"
            "- → [[themes/4.5-green-finance]]"
        ),
    ),
    dict(
        key="berg2022esg",
        title="Aggregate confusion: The divergence of ESG ratings",
        citation="Berg, Kölbel & Rigobon (2022) — ESG ratings disagree systematically across providers",
        themes=["green-finance"],
        claims=(
            "- Correlations across six major ESG-rating providers average only 0.54 (vs ~0.99 for credit ratings).\n"
            "- The divergence decomposes into scope (which categories matter), measurement (how each is operationalised), "
            "and weights — measurement is the dominant driver.\n"
            "- ESG ratings are not interchangeable; using one provider's score as a feature embeds that provider's "
            "methodological priors."
        ),
        method=(
            "Decomposition of disagreement across six ESG-rating providers on a large overlap sample using a novel "
            "scope/measurement/weight framework."
        ),
        relevance=(
            "Pillar citation justifying EMERALD-AI's design choice NOT to use third-party ESG scores as model features. "
            "Anchor for section 4.5's claim that ESG ratings are unreliable as direct inputs."
        ),
        quotes=(
            "- 'ESG ratings from six prominent rating agencies have an average correlation of 0.54, which is "
            "significantly lower than the correlation of credit ratings (around 0.99).'\n"
            "- 'Measurement divergence is the most important source.'"
        ),
        limitations=(
            "- The 0.54 figure has been refined in later work; the directional claim is robust but the exact magnitude "
            "depends on overlap sample and provider mix.\n"
            "- Does not address the question of which ESG score, if any, is most accurate — only that they disagree."
        ),
        used_for=(
            "Section 4.5 anchor for the 'do not use ESG scores as features' design choice."
        ),
        related=(
            "- [[ehlers2017greenbond]] — adjacent information-asymmetry argument\n"
            "- [[flammer2021corporate]] — uses E-pillar ESG scores; this paper is the caveat\n"
            "- → [[themes/4.5-green-finance]]"
        ),
    ),
    dict(
        key="lundberg2017shap",
        title="A unified approach to interpreting model predictions",
        citation="Lundberg & Lee (2017) — SHAP unifies feature attribution under a game-theoretic axiom set",
        themes=["xai-finance"],
        claims=(
            "- Six existing attribution methods (LIME, DeepLIFT, Layer-wise relevance propagation, classic Shapley, "
            "QII, Shapley sampling) are special cases of a single 'additive feature attribution' framework.\n"
            "- Within that framework, only Shapley values uniquely satisfy three desirable axioms: local accuracy, "
            "missingness, and consistency.\n"
            "- KernelSHAP estimates Shapley values via a weighted linear regression on perturbation samples — "
            "model-agnostic and computationally tractable."
        ),
        method=(
            "Theoretical unification (axiom-satisfaction proofs) + empirical comparison with LIME and DeepLIFT on "
            "MNIST and a medical risk-prediction case study."
        ),
        relevance=(
            "Foundational citation for EMERALD-AI's entire XAI stack. The axiomatic uniqueness argument is what "
            "lets reviewers know SHAP is not just one explainer among many — it is the unique one satisfying its axiom set."
        ),
        quotes=(
            "- 'We propose SHAP values as a unified measure of feature importance.'\n"
            "- 'SHAP values are the unique solution to the class of additive feature attribution methods that "
            "satisfies the three desirable properties of local accuracy, missingness, and consistency.'"
        ),
        limitations=(
            "- The 'unique under the axioms' claim depends on accepting the axioms — see [[aas2021explaining]], "
            "[[janzing2020feature]] for causal-inference critiques.\n"
            "- KernelSHAP scales poorly with feature count and is biased under feature dependence — TreeSHAP "
            "[[lundberg2020trees]] is the relevant production tool."
        ),
        used_for=(
            "Section 4.6 axiomatic-grounding citation. Section 5.11 KernelSHAP cross-check citation."
        ),
        related=(
            "- [[lundberg2020trees]] — TreeSHAP follow-up\n"
            "- [[ribeiro2016lime]] — LIME, the perturbation predecessor unified here\n"
            "- [[aas2021explaining]] — critique under feature dependence\n"
            "- → [[themes/4.6-xai-finance]]"
        ),
    ),
    dict(
        key="ribeiro2016lime",
        title="'Why should I trust you?': Explaining the predictions of any classifier",
        citation="Ribeiro, Singh & Guestrin (2016) — LIME: local interpretable model-agnostic explanations",
        themes=["xai-finance"],
        claims=(
            "- Approximate any classifier's local behaviour with a sparse linear model fit on perturbed neighbours, "
            "weighted by proximity to the instance.\n"
            "- The linear surrogate is interpretable and faithful in the neighbourhood, even when the global model is "
            "complex.\n"
            "- The SP-LIME extension selects a small set of instances whose collective explanation provides global "
            "understanding."
        ),
        method=(
            "Algorithmic description + user studies comparing LIME-aided judgements vs no-explanation baseline on "
            "text and image classification tasks."
        ),
        relevance=(
            "Section 4.6 reference point as the perturbation-based predecessor to SHAP. Section 5.11 uses LIME as a "
            "secondary local explanation method to cross-check TreeSHAP attributions."
        ),
        quotes=(
            "- 'If the user cannot trust the model or a prediction, they will not use it.'\n"
            "- 'A novel explanation technique that explains the predictions of any classifier in an interpretable and "
            "faithful manner.'"
        ),
        limitations=(
            "- The choice of perturbation distribution affects the explanation; results can be unstable across runs.\n"
            "- Demonstrably attackable [[slack2020fooling]] — adversarially trained models can hide bias.\n"
            "- Local linear approximation can mislead when the model's decision surface is highly non-linear nearby."
        ),
        used_for=(
            "Section 4.6 lineage. Section 5.11 secondary explanation method."
        ),
        related=(
            "- [[lundberg2017shap]] — SHAP unifies and supersedes LIME for additive attribution\n"
            "- [[slack2020fooling]] — adversarial attack\n"
            "- → [[themes/4.6-xai-finance]]"
        ),
    ),
    dict(
        key="mothilal2020dice",
        title="Explaining machine learning classifiers through diverse counterfactual explanations",
        citation="Mothilal, Sharma & Tan (2020) — DiCE: diverse, feasible counterfactual explanations",
        themes=["xai-finance"],
        claims=(
            "- A counterfactual explanation tells a declined applicant the minimal feature changes that would flip "
            "their decision — actionable in a way attribution alone is not.\n"
            "- DiCE optimises for both proximity to the original instance AND diversity among the generated "
            "counterfactuals, so users receive multiple distinct recourse options.\n"
            "- Feasibility constraints (mutable features only, value ranges, monotonic directions) ensure "
            "counterfactuals are actionable rather than merely mathematically valid."
        ),
        method=(
            "Optimisation-based counterfactual generation with diversity (determinantal point process) and feasibility "
            "constraints. Evaluated on Adult, COMPAS, German Credit, Lending Club."
        ),
        relevance=(
            "Core citation for EMERALD-AI's counterfactual layer in section 5.11. Directly addresses the GDPR Article "
            "22 / FCA Consumer Duty 'support' outcome requirement that automated decisions be actionable."
        ),
        quotes=(
            "- 'Counterfactual explanations provide actionable feedback on what users can do to obtain a different "
            "outcome from a machine learning model.'\n"
            "- 'DiCE generates diverse and feasible counterfactual explanations.'"
        ),
        limitations=(
            "- Optimisation can be slow at inference time; not ideal for high-QPS production.\n"
            "- Counterfactual instability under model retraining [[rawal2020beyond]] is a known concern.\n"
            "- 'Feasibility' constraints encode value judgements about which features are actionable — must be "
            "explicit and reviewed."
        ),
        used_for=(
            "Section 4.6 + section 5.11 counterfactual generation. Surfaced in the web app's Single Predict page as "
            "'what would change this decision?'"
        ),
        related=(
            "- [[wachter2017counterfactual]] — legal foundation\n"
            "- [[rawal2020beyond]] — counterfactual instability\n"
            "- → [[themes/4.6-xai-finance]]"
        ),
    ),
    dict(
        key="wachter2017counterfactual",
        title="Counterfactual explanations without opening the black box: Automated decisions and the GDPR",
        citation="Wachter, Mittelstadt & Russell (2017) — legal/technical case for counterfactuals under GDPR",
        themes=["xai-finance", "fairness-compliance"],
        claims=(
            "- The 'right to explanation' read into GDPR Article 22 is more meaningfully discharged by counterfactual "
            "explanations than by feature-attribution explanations.\n"
            "- Counterfactuals require no access to the model internals — model-agnostic by construction.\n"
            "- A formal definition of counterfactual: the closest possible world (in feature space) in which the "
            "decision would have differed."
        ),
        method=(
            "Legal-technical analysis of GDPR Articles 13-15 and 22 + algorithmic definition of counterfactual "
            "explanation."
        ),
        relevance=(
            "Legal foundation citation for EMERALD-AI's counterfactual layer. Justifies the design choice to make "
            "counterfactuals a first-class output, not an optional add-on."
        ),
        quotes=(
            "- 'Counterfactual explanations of automated decisions... are appropriate for assessing the lawfulness of "
            "automated individual decision-making.'\n"
            "- 'Counterfactual explanations do not require opening the black box.'"
        ),
        limitations=(
            "- The 'right to explanation' reading of GDPR is contested (Edwards & Veale 2017, Selbst & Powles 2017 "
            "argue it is more limited).\n"
            "- Closest counterfactual is not always the most useful — Mothilal et al. (2020) argue for diversity.\n"
            "- Predates the EU AI Act; new framework will partly supersede GDPR analysis for credit-scoring AI."
        ),
        used_for=(
            "Section 4.6 + section 5.11 legal justification for counterfactual layer."
        ),
        related=(
            "- [[mothilal2020dice]] — implementation, with diversity\n"
            "- [[euAiAct2021]] — newer overlapping regulatory framework\n"
            "- → [[themes/4.6-xai-finance]]\n"
            "- → [[themes/4.7-fairness-compliance]]"
        ),
    ),
    dict(
        key="rudin2019stop",
        title="Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead",
        citation="Rudin (2019) — argues for inherently interpretable models in high-stakes settings",
        themes=["xai-finance"],
        claims=(
            "- Post-hoc explanations of opaque models can be unreliable, unstable, or actively misleading.\n"
            "- For high-stakes decisions (criminal justice, medicine, credit), modellers should use inherently "
            "interpretable models (constrained additive models, sparse decision lists, EBMs) instead of explaining "
            "black boxes after the fact.\n"
            "- The 'accuracy vs interpretability trade-off' is often illusory at high-stakes data sizes: interpretable "
            "models frequently match black-box accuracy."
        ),
        method=(
            "Position paper with worked counter-examples from criminal recidivism prediction (COMPAS), medical "
            "imaging, and tabular finance."
        ),
        relevance=(
            "Critical-perspective citation in section 4.6. EMERALD-AI's pragmatic middle path (constrained tree ensemble "
            "+ multi-method explanation stack) is explicitly positioned as Rudin's argument acknowledged but not adopted "
            "in pure form."
        ),
        quotes=(
            "- 'Trying to explain black box models, rather than creating models that are interpretable in the first "
            "place, is likely to perpetuate bad practice.'\n"
            "- 'There is no scientific evidence for a general trade-off between accuracy and interpretability.'"
        ),
        limitations=(
            "- The 'interpretable models match black-box accuracy' claim has notable exceptions, particularly for "
            "very high-dimensional data and certain non-linear-interaction regimes.\n"
            "- Rudin's preferred model class (EBM, GA²M) has its own engineering and tuning costs."
        ),
        used_for=(
            "Section 4.6 critical-perspective anchor. Counter-position EMERALD-AI must engage with rather than ignore."
        ),
        related=(
            "- [[dumitrescu2022ml]] — adjacent argument (interpretable can match black-box)\n"
            "- [[slack2020fooling]] — supporting evidence for Rudin's critique\n"
            "- → [[themes/4.6-xai-finance]]"
        ),
    ),
    dict(
        key="aas2021explaining",
        title="Explaining individual predictions when features are dependent: More accurate approximations to Shapley values",
        citation="Aas, Jullum & Løland (2021) — KernelSHAP under feature dependence",
        themes=["xai-finance"],
        claims=(
            "- Standard KernelSHAP assumes feature independence — an assumption almost always violated in real "
            "tabular data, especially financial data with correlated ratios.\n"
            "- Under dependence, KernelSHAP attributions can be biased: the magnitude and even the sign of "
            "individual feature attributions can be wrong.\n"
            "- Conditional-distribution-based estimators (using Gaussian, copula, or empirical conditional sampling) "
            "produce more accurate attributions."
        ),
        method=(
            "Theoretical analysis of the bias + empirical comparison of four conditional-sampling approaches on "
            "synthetic and real-data benchmarks."
        ),
        relevance=(
            "Critical-perspective citation in section 4.6. Justifies the section 5.11 design choice to cross-check "
            "TreeSHAP attributions with KernelSHAP on a held-out sample, AND to use conditional rather than "
            "marginal feature distributions where feasible."
        ),
        quotes=(
            "- 'When features are dependent, KernelSHAP can give biased estimates of the true conditional Shapley "
            "values.'\n"
            "- 'Conditional sampling approaches produce more accurate Shapley value estimates.'"
        ),
        limitations=(
            "- Conditional sampling is computationally more expensive than marginal sampling.\n"
            "- The 'true' Shapley value under dependence is itself contested — see [[janzing2020feature]] for a "
            "causal-inference-based alternative ('interventional' SHAP)."
        ),
        used_for=(
            "Section 4.6 critical perspective. Section 5.11 motivates KernelSHAP cross-check + interventional-SHAP "
            "for TreeSHAP."
        ),
        related=(
            "- [[lundberg2017shap]] — paper this critiques\n"
            "- [[lundberg2020trees]] — TreeSHAP, which offers tree_path_dependent vs interventional algorithms\n"
            "- [[janzing2020feature]] — causal-inference framing\n"
            "- → [[themes/4.6-xai-finance]]"
        ),
    ),
    dict(
        key="slack2020fooling",
        title="Fooling LIME and SHAP: Adversarial attacks on post hoc explanation methods",
        citation="Slack et al. (2020) — adversarial attacks on post-hoc explanations",
        themes=["xai-finance"],
        claims=(
            "- A model can be constructed that uses a sensitive attribute (race, gender) in its decisions while "
            "LIME and SHAP attributions hide this dependence completely.\n"
            "- The attack works by training a 'scaffolding' model that behaves differently on perturbed neighbours "
            "(seen by the explainer) vs real instances.\n"
            "- Post-hoc explanations are therefore not a sufficient defence against deliberate bias hiding."
        ),
        method=(
            "Constructed adversarial scaffolding models on COMPAS and German Credit datasets; demonstrated that "
            "LIME and KernelSHAP attribute the discriminatory decisions to innocuous features."
        ),
        relevance=(
            "Critical-perspective citation in section 4.6. Strengthens the case for EMERALD-AI's multi-method "
            "explanation stack + monotonic-constraint verification + fidelity evaluation rather than trust-by-default "
            "in a single explainer."
        ),
        quotes=(
            "- 'Adversaries can construct biased classifiers that LIME and SHAP fail to detect as biased.'\n"
            "- 'Post hoc explanation methods can be unreliable in adversarial settings.'"
        ),
        limitations=(
            "- The attack requires deliberate construction; honest practitioners following standard training are "
            "unlikely to reproduce it accidentally.\n"
            "- TreeSHAP on transparent tree ensembles is harder to fool than KernelSHAP on opaque scaffolds.\n"
            "- Monotonic constraints and structural inspection (which EMERALD-AI uses) would detect the attack."
        ),
        used_for=(
            "Section 4.6 critical perspective. Justifies multi-method + structural-verification approach in section 5.11."
        ),
        related=(
            "- [[rudin2019stop]] — adjacent critique of post-hoc explanations\n"
            "- [[hedstrom2023quantus]] — fidelity evaluation as countermeasure\n"
            "- → [[themes/4.6-xai-finance]]"
        ),
    ),
    dict(
        key="hedstrom2023quantus",
        title="Quantus: An explainable AI toolkit for responsible evaluation of neural network explanations",
        citation="Hedström et al. (2023) — Quantus: empirical evaluation of XAI methods",
        themes=["xai-finance"],
        claims=(
            "- Explanation quality is not self-evident: explanations should be evaluated against measurable "
            "properties (faithfulness, robustness, complexity, randomisation, axiomatic, localisation).\n"
            "- Quantus operationalises 30+ such metrics into a single toolkit.\n"
            "- Different XAI methods score very differently on different metrics — reporting a single number is "
            "insufficient."
        ),
        method=(
            "Toolkit paper. Implements published evaluation metrics from the XAI literature in a unified API; "
            "demonstrates on image-classification case studies."
        ),
        relevance=(
            "Core citation for EMERALD-AI's section 5.11 explanation-fidelity validation. Moves the project past "
            "the assumption that an explanation is reliable simply because it was generated."
        ),
        quotes=(
            "- 'Quantus is the first toolkit to provide a comprehensive collection of evaluation metrics for "
            "explanations.'\n"
            "- 'Different evaluation metrics emphasise different desirable properties.'"
        ),
        limitations=(
            "- Primarily targeted at neural network explanations and image data; tabular adaptation requires care.\n"
            "- The metrics themselves are contested (e.g., faithfulness has multiple competing definitions).\n"
            "- Reporting many metrics shifts the interpretation burden onto the reader."
        ),
        used_for=(
            "Section 4.6 + section 5.11 explanation-fidelity validation."
        ),
        related=(
            "- [[slack2020fooling]] — motivates the need for empirical fidelity evaluation\n"
            "- [[aas2021explaining]] — fidelity-under-dependence concern\n"
            "- → [[themes/4.6-xai-finance]]"
        ),
    ),
    dict(
        key="hardt2016eqodds",
        title="Equality of opportunity in supervised learning",
        citation="Hardt, Price & Srebro (2016) — equalised odds and equal opportunity",
        themes=["fairness-compliance"],
        claims=(
            "- 'Equalised odds' requires the true-positive rate AND false-positive rate to be equal across protected "
            "groups; 'equal opportunity' requires only TPR equality.\n"
            "- Both criteria can be enforced post-hoc by learning a group-conditional threshold from a calibrated "
            "score.\n"
            "- These criteria are weaker than demographic parity and avoid demographic-parity's failure mode of "
            "underwriting on protected-group membership rather than risk."
        ),
        method=(
            "Theoretical derivation of post-hoc threshold-adjustment procedure + empirical demonstration on the FICO "
            "credit-scoring dataset."
        ),
        relevance=(
            "Foundational citation for section 4.7's parity-definition framework. Equalised-odds gap is one of the "
            "four metrics EMERALD-AI's section 5.12 fairness audit reports."
        ),
        quotes=(
            "- 'We propose a criterion for discrimination against a specified sensitive attribute in supervised "
            "learning: that the prediction be independent of the protected attribute, conditional on the true label.'\n"
            "- The FICO case study showing the trade-off between equal opportunity and aggregate accuracy."
        ),
        limitations=(
            "- The post-hoc threshold approach assumes the underlying score is well-calibrated within each group — "
            "often false in practice.\n"
            "- Equalised odds is incompatible with calibration when base rates differ [[chouldechova2017fair]].\n"
            "- 'Protected group' must be observable at inference time, which is often not the case in credit."
        ),
        used_for=(
            "Section 4.7 anchor. Section 5.12 equalised-odds gap metric."
        ),
        related=(
            "- [[chouldechova2017fair]] — impossibility result\n"
            "- [[kleinberg2017inherent]] — same result from a different angle\n"
            "- [[bellamy2018aif360]] — toolkit implementation\n"
            "- → [[themes/4.7-fairness-compliance]]"
        ),
    ),
    dict(
        key="chouldechova2017fair",
        title="Fair prediction with disparate impact: A study of bias in recidivism prediction instruments",
        citation="Chouldechova (2017) — impossibility theorem: calibration and equal error rates incompatible",
        themes=["fairness-compliance"],
        claims=(
            "- For any binary classifier, if base rates differ across protected groups, the following three properties "
            "cannot simultaneously hold: (i) calibration within groups, (ii) equal false-positive rates, (iii) equal "
            "false-negative rates.\n"
            "- This is a mathematical impossibility, not a tuning failure — applies to any classifier.\n"
            "- The choice of which fairness criterion to optimise is therefore a value judgement, not a technical one."
        ),
        method=(
            "Analytic proof + case study using ProPublica's COMPAS recidivism data."
        ),
        relevance=(
            "Pillar citation for section 4.7's core argument that the four parity definitions are incompatible and "
            "modellers must choose. Cited alongside [[kleinberg2017inherent]] for the same result."
        ),
        quotes=(
            "- 'When the recidivism prevalence differs across groups, an instrument that satisfies predictive "
            "parity… cannot simultaneously satisfy equal false-positive rates and equal false-negative rates.'\n"
            "- 'No risk-assessment instrument can satisfy all of the fairness criteria simultaneously.'"
        ),
        limitations=(
            "- The impossibility holds in the worst case; in specific regimes (similar base rates, calibration "
            "interventions) the practical trade-off can be small.\n"
            "- The result does not dictate which criterion to choose — that is left to the deploying institution."
        ),
        used_for=(
            "Section 4.7 anchor. Section 5.12 underpins the explicit acknowledgement that multiple criteria are "
            "reported rather than one optimised."
        ),
        related=(
            "- [[hardt2016eqodds]] — defines equalised odds\n"
            "- [[kleinberg2017inherent]] — same impossibility from a different angle\n"
            "- → [[themes/4.7-fairness-compliance]]"
        ),
    ),
    dict(
        key="bellamy2018aif360",
        title="AI Fairness 360: An extensible toolkit for detecting, understanding, and mitigating unwanted algorithmic bias",
        citation="Bellamy et al. (2018) — AIF360 toolkit",
        themes=["fairness-compliance"],
        claims=(
            "- AIF360 provides a unified Python API for 70+ fairness metrics and 10+ bias-mitigation algorithms "
            "(pre-, in-, post-processing).\n"
            "- Designed for production deployment with documentation, examples, and integration with major ML "
            "frameworks."
        ),
        method=(
            "Toolkit paper. Implements the published fairness and mitigation literature in a unified API."
        ),
        relevance=(
            "Implementation citation for EMERALD-AI's section 5.12 fairness audit. AIF360 is the toolkit; "
            "[[hardt2016eqodds]] and [[chouldechova2017fair]] are the underlying theoretical basis."
        ),
        quotes=(
            "- 'A comprehensive open-source library… containing a comprehensive set of fairness metrics for datasets "
            "and models, explanations for these metrics, and algorithms to mitigate bias.'"
        ),
        limitations=(
            "- The toolkit does not choose which fairness criterion to optimise for the user — choosing remains a "
            "domain decision.\n"
            "- Many mitigation algorithms degrade accuracy substantially; cost-benefit must be assessed empirically."
        ),
        used_for=(
            "Section 4.7 + section 5.12 implementation citation."
        ),
        related=(
            "- [[hardt2016eqodds]] — equalised odds theory\n"
            "- [[chouldechova2017fair]] — impossibility result\n"
            "- [[kamiran2012preprocessing]] — reweighting mitigation (implemented in AIF360)\n"
            "- → [[themes/4.7-fairness-compliance]]"
        ),
    ),
    dict(
        key="euAiAct2021",
        title="Proposal for a Regulation laying down harmonised rules on artificial intelligence (Artificial Intelligence Act)",
        citation="European Commission (2021) — EU AI Act proposal (COM/2021/206 final)",
        themes=["fairness-compliance"],
        claims=(
            "- Annex III lists credit scoring as a 'high-risk' AI application.\n"
            "- High-risk providers must comply with Articles 9 (risk management), 10 (data governance), 11 "
            "(technical documentation), 12 (record-keeping), 13 (transparency), 14 (human oversight), 15 (accuracy "
            "and robustness), 17 (quality management), 61 (post-market monitoring).\n"
            "- Penalties up to €30M or 6% of global annual turnover for non-compliance with the most serious "
            "obligations."
        ),
        method=(
            "Legislative proposal text; subsequent amendments and final adoption (2024) tighten and extend specific "
            "obligations but retain the credit-scoring-as-high-risk classification."
        ),
        relevance=(
            "Pillar regulatory citation. The Annex III classification is the single most-important external pressure "
            "shaping EMERALD-AI's design choices around calibration, explainability, fairness audit, monitoring, "
            "and documentation."
        ),
        quotes=(
            "- Annex III, point 5(b): 'AI systems intended to be used to evaluate the creditworthiness of natural "
            "persons or establish their credit score.'\n"
            "- Article 13(1): 'High-risk AI systems shall be designed and developed in such a way to ensure that "
            "their operation is sufficiently transparent.'"
        ),
        limitations=(
            "- The 2021 proposal has been amended through the legislative process; final 2024 text differs on "
            "specifics (notably definition of 'AI system' and treatment of general-purpose AI). Cite the final "
            "Regulation when published.\n"
            "- Applies only to systems placed on EU market; UK regime (FCA, ICO) is parallel."
        ),
        used_for=(
            "Sections 2.3, 4.7, 5.11, 5.12, 5.14 — almost every part of the dissertation traces a design choice "
            "back to a specific Article of this Regulation."
        ),
        related=(
            "- [[fcaConsumerDuty2022]] — UK parallel regulatory pressure\n"
            "- [[ebaGL2020]] — sector-specific loan-origination guidance\n"
            "- [[wachter2017counterfactual]] — older GDPR Article 22 analysis being partly superseded\n"
            "- → [[themes/4.7-fairness-compliance]]"
        ),
    ),
    dict(
        key="fcaConsumerDuty2022",
        title="Consumer Duty: Final rules and guidance (Policy Statement PS22/9)",
        citation="Financial Conduct Authority (2022) — UK Consumer Duty PS22/9",
        themes=["fairness-compliance"],
        claims=(
            "- Firms must act to deliver good outcomes for retail customers, evaluated against four outcomes: "
            "products and services, price and value, consumer understanding, consumer support.\n"
            "- Automated decisions (including credit-scoring AI) fall within scope and must be evidenced as fair, "
            "explainable, and supportive.\n"
            "- Applies from 31 July 2023 for new and existing products; 31 July 2024 for closed-book products."
        ),
        method=(
            "FCA Policy Statement summarising consultation responses and finalising the rulebook changes."
        ),
        relevance=(
            "UK-side regulatory pillar paired with the EU AI Act. The 'consumer understanding' outcome anchors "
            "EMERALD-AI's web-application explainability design (section 5.14); 'consumer support' anchors the "
            "counterfactual-recourse layer in section 5.11."
        ),
        quotes=(
            "- 'Firms must consider the needs, characteristics and objectives of their customers — including those "
            "with characteristics of vulnerability — and how they behave, at every stage of the customer journey.'"
        ),
        limitations=(
            "- Outcome-based (not rule-based) — compliance is harder to evidence than checklist-based regimes.\n"
            "- Applies only to FCA-regulated retail; commercial green-loan lending may sit outside in specific cases."
        ),
        used_for=(
            "Section 2.3 + section 4.7 regulatory framing. Section 5.11 anchor for counterfactual layer ('support'). "
            "Section 5.14 anchor for web-app explainability surface ('consumer understanding')."
        ),
        related=(
            "- [[euAiAct2021]] — EU-side parallel regulation\n"
            "- [[wachter2017counterfactual]] — actionable explanation as 'support'\n"
            "- → [[themes/4.7-fairness-compliance]]"
        ),
    ),
]

# =============================================================================

for entry in PAPERS:
    write(**entry)

print(f"Wrote {len(PAPERS)} paper files to {OUT}")
