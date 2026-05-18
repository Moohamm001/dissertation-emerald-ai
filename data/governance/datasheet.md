# Datasheet — 2019 All Funded Green Loan dataset

_Structured per Gebru et al. (2021), "Datasheets for Datasets" (Communications of the ACM, 64(12), 86–92). This datasheet accompanies the EMERALD-AI dissertation (MSc Applied AI, University of Warwick) and is the principal data-governance artefact under proposal §5.3._

Version: 1.0 · Generated: 2026-05-18 · Sibling artefact: [`feature_catalogue.yaml`](feature_catalogue.yaml), [`feature_audit_summary.md`](feature_audit_summary.md).

---

## 1. Motivation

**For what purpose was the dataset created?**
The dataset is an operational snapshot of one calendar year (2019) of funded small-business loans originated through a US commercial lender, retained for internal performance analysis. It is repurposed here for academic research on explainable machine-learning credit scoring in green lending (EMERALD-AI dissertation).

**Who created the dataset and on behalf of which entity?**
The originating institution (proprietary; named only on the dissertation cover sheet). The dataset was provided under a research-use licence to the dissertation author by arrangement with the institution; the author did not collect the data.

**Who funded the creation of the dataset?**
Not applicable — the data is operational rather than commissioned. The MSc research using it is self-funded by the dissertation author.

---

## 2. Composition

**What do the instances represent?**
Each row is one **funded small-business loan transaction**. Every row in the dataset was approved and disbursed; no declined applications are present (this constitutes an accepted-only selection-bias condition, treated explicitly in proposal §5.2).

**How many instances are there in total?**
**14,135 funded transactions** across **166 columns** (mixture of borrower attributes, loan-offer parameters, deal-progression timestamps, post-funding outcomes, and administrative / staff-routing metadata).

**Does the dataset contain all possible instances or is it a sample?**
A full operational snapshot of 2019 funded volume — not a sample. However, it is a population conditional on the prior underwriting policy's accept decisions (see "Accepted-only selection bias" below).

**Is there a label or target?**
Yes. The supervisory signal is the binary creditworthiness target `Y` derived from the `Deal Status` column per proposal §5.2:

| `Deal Status` | `Y` | Count | % of labelled |
|---|:---:|---:|---:|
| `paidOff` | 1 (creditworthy) | 3,848 | 27.4% |
| `current` | 1 (creditworthy) | 10,124 | 72.2% |
| `default` | 0 (delinquent) | 49 | 0.35% |
| `behind` | 0 (delinquent) | 1 | 0.01% |
| (missing) | _excluded_ | 113 | — |

**14,022 of 14,135 rows (99.20%) are labelled.** Class balance is extreme: **0.36% delinquent** — well below the 2–15% range cited in the proposal's §4.4. This necessitates an aggressive imbalance strategy (class-weighting / SMOTE-NC / focal loss, all gated by in-fold-only resampling per Santos et al., 2018), and may invalidate certain metrics (raw accuracy is meaningless; PR-AUC, recall@top-decile, and calibration within the minority class become the primary signals).

**Are there missing values?**
Yes — extensively. Highlights:

- 11 columns are **100% missing** and should be dropped on load: `App Out`, `1st Online Engmnt`, `Used Online Experience`, `Closed Lenders`, `Monthly Credit Card Charges`, `Rep Type`, `Rep Is Active`, `Inactive Status`, `Closed By Type`, `Dead Status`, `Renewal Eligible Date`.
- Per proposal §5.5 Stage 1, features with > 40% missingness are candidates for dropping. Among **permitted** features (i.e., those not excluded by the leakage audit), the following exceed this threshold: `Term` (86.4%), `APR` (59.6%), `Factor` (42.0%), plus the 100%-missing columns above.
- Notable: `Monthly Credit Card Charges`, which proposal §1 and §5.3 list as a key applicant feature, is **100% missing** in the 2019 snapshot. The proposal's feature list will need to be revised; the dissertation should surface this transparently rather than silently dropping the field.

**Does the dataset contain confidential or sensitive information?**
The data is de-identified before release: no applicant names, exact addresses, social-security numbers, or banking identifiers are present. Geography is retained at the US-state level (`Borrower State`, 51 levels including DC) and zip-code level (`Borrower Zip`); zip-code is borderline-identifying for very small applicant pools and is excluded from features by default during preprocessing (see proposal §5.5).

**Does the dataset contain protected attributes?**
**No direct protected attributes** (no race, gender, age, religion, disability, marital status). Indirect-discrimination testing is performed against three proxy axes per proposal §5.12: `Industry`, `Borrower State`, and a derived business-size segment (computed from `Annual Revenue`).

---

## 3. Collection process

**How was the data acquired?**
The dataset is exported from the originating institution's customer-relationship-management (CRM) system. Column names (`Rep`, `Rep Id`, `Lead Claiming Bucket`, `OcrolusSent/Complete/Errored`, `Touchpoint`, `Channel`, etc.) indicate a Salesforce-style sales pipeline with integrations to a document-processing service (Ocrolus, a real-world bank-statement OCR vendor — informational only, no endorsement).

**Over what timeframe?**
All transactions funded between **2019-01-01 and 2019-12-31** inclusive. Deal-progression timestamps (Start, Offer Received, Contract Signed, Deal Closed) populate the pre-funding observability window. The latest post-funding outcome observations in the snapshot pre-date the 2019-loan term completion for most rows, which materially affects the `current` label (see "Censoring bias" below).

**Were any ethical-review processes (IRB) used?**
The dataset is operational and was not collected with human-subjects research in mind. Use in this dissertation is governed by Warwick's Research Ethics protocol; no additional consent was sought from individual borrowers because (a) the data is de-identified, (b) the research is non-interventional, and (c) the originator's release licence permits academic analysis.

---

## 4. Preprocessing / cleaning / labelling

**Has the data been preprocessed?**
The raw `.xlsx` is unmodified. All preprocessing performed by EMERALD-AI is implemented in `src/emerald_ai/data/` and `src/emerald_ai/features/` and is fully reproducible via `python -m emerald_ai.data.leakage_audit` (current sibling artefacts) and the downstream pipeline (to be implemented per §5.5–5.7).

**Target-leakage audit (the principal preprocessing artefact).**
Every one of the 166 columns is classified into one of six categories. Only the first four are permitted to enter the feature matrix `X`:

| Category | Count | Permitted as feature? |
|---|---:|:---:|
| Pre-funding applicant | 23 | ✓ |
| Pre-funding loan-offer | 15 | ✓ |
| Structural metadata | 9 | ✓ |
| Deal-progression timestamp | 43 | ✓ |
| Post-funding outcome | 28 | ✗ (defines Y or leaks future info) |
| Administrative / staff-routing / free-text | 48 | ✗ |

**Permitted: 90 features. Forbidden: 76.** Full per-column classification is in [`feature_catalogue.yaml`](feature_catalogue.yaml); the human-readable summary including the drop-list is in [`feature_audit_summary.md`](feature_audit_summary.md).

**Particularly load-bearing exclusions** (would inflate metrics if accidentally admitted to `X`):

- `Deal Status` — defines `Y` itself.
- `Term Complete Percentage`, `Percent Paid` — directly encode whether the loan is mature enough to have defaulted.
- `Closed`, `Closed TS`, `Month Closed`, `Original Close Date` — funding-event end-points, post-decision.
- `Is Offer Received/Accepted/Published/...` — Boolean flags realised through the deal lifecycle.
- `Stage`, `Status` — both single-valued in this snapshot (all `Funded` / `Deal Closed`) but realised post hoc.

**Label construction.**
Implemented in `emerald_ai.data.load.label_creditworthiness`: status values are stripped of whitespace, mapped per the §5.2 dictionary, and `pd.NA` is preserved as `<NA>` in the new `Y` column. Rows with `Y` NA are dropped from the supervised pool.

**Known data-quality issues** surfaced by inspection:

- `Credit Score` minimum of 0 (impossible FICO) — sentinel value used for missing; should be re-coded.
- `Time In Business` contains negative values (`min = -3`) and a value of `2013` (probable year-of-founding encoded in error) — needs clipping or per-row sanity-checking before use.
- `Amount Sought` maximum of $1 billion — single-row outlier, almost certainly a data-entry typo; winsorisation per §5.5 Stage 2 should neutralise.
- `Factor` maximum of 1034 — typical factor rates are 1.1–1.5; outlier.
- `Term` (the `pre_funding_loan_offer` field) is 86% missing and the populated values are a mix of marketing search strings ("Business Loans Made Simple Video") and integers — the column has been overloaded with two semantically distinct fields and needs disambiguation before use.

---

## 5. Uses

**Intended uses.**
This dataset is used to:

1. Train and benchmark six classifier families (LR, SVM, RF, XGBoost, LightGBM, CatBoost, MLP, FT-Transformer) for binary creditworthiness prediction on green-loan transactions (proposal §5.8).
2. Validate post-hoc probability calibration and split-conformal uncertainty quantification on the calibration split (proposal §5.10).
3. Audit explanation fidelity, fairness across industry/geography/size proxies, and prediction robustness under perturbation and drift (proposal §5.11–5.12).
4. Operate the EMERALD-AI decision-support web application against held-out test data (proposal §5.14).

**Known limitations that affect external validity.**

- **Accepted-only selection bias.** The dataset contains only funded loans. Applicants the prior underwriting policy declined are absent, so the empirical distribution of `(X, Y)` is conditional on prior acceptance. Conventional reject-inference techniques (Banasik & Crook, 2007; Kang et al., 2021; Shen et al., 2022) require access to declined applicants' features and cannot be exercised here. The dissertation reports this limitation explicitly and frames the model as conditional on the originator's prior accept-policy rather than as a portable underwriting function.
- **Censoring bias.** Many `current` loans have not yet completed their term in the 2019 snapshot, so the favourable label is right-censored. Proposal §5.2 specifies a sensitivity analysis that re-runs the headline benchmark on the `paidOff`-only subset and reports both numbers.
- **Definition heterogeneity of "green" labelling.** The originating institution's taxonomy for classifying these 2019 loans as "green" is not documented in the snapshot. The dissertation flags this as an external-validity limitation (proposal §4.5).
- **Severe class imbalance (0.36% delinquent).** Far below typical credit-default prevalence (2–15%), making the minority-class signal extremely scarce. Modelling protocols (in-fold-only resampling, focal loss, calibration-within-minority-group) become load-bearing rather than optional.
- **Single-year, single-originator, US-only snapshot.** Generalisation across years, originators, and jurisdictions is not testable from this dataset.

**Uses that the dataset should not be used for.**

- Underwriting *new* applicants (no rejected-applicant counterfactual; selection bias unaddressed).
- Inferring credit-risk patterns for borrower types absent from the 2019 snapshot.
- Cross-jurisdiction generalisation without re-validation on the target jurisdiction.

---

## 6. Distribution

**Will the dataset be distributed?**
**No.** The data is proprietary to the originating institution and is not redistributed in the dissertation repository. The repository's `.gitignore` excludes `data/raw/` to enforce this. Researchers wishing to replicate the dissertation results must approach the originating institution directly. See [`data/README.md`](../README.md) for current acquisition status.

**Licence.**
Proprietary; research-use only by individual arrangement with the originating institution. Redistribution prohibited.

---

## 7. Maintenance

**Who maintains the dataset?**
The originating institution maintains the upstream source; the dissertation author maintains the local snapshot at version 1.0 (frozen for the duration of the MSc).

**Will the dataset be updated?**
No updates are expected during the dissertation period. If future originator-supplied refreshes arrive, the `data/governance/feature_catalogue.yaml` schema versioning supports forward-compatibility — rerun `python -m emerald_ai.data.leakage_audit` to regenerate.

**Are there errata?**
Documented in §4 above (negative `Time In Business`, $1 B `Amount Sought`, etc.); these are surfaced rather than silently corrected so the dissertation's preprocessing pipeline can show its work.

---

## References

- Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J. W., Wallach, H., Daumé III, H., & Crawford, K. (2021). Datasheets for datasets. _Communications of the ACM_, 64(12), 86–92.
- Banasik, J., & Crook, J. (2007). Reject inference, augmentation, and sample selection. _EJOR_, 183(3), 1582–1594.
- Kang, Y., Jia, N., Cui, R., & Deng, J. (2021). A graph-based semi-supervised reject inference framework. _Applied Soft Computing_, 105, 107259.
- Shen, F., Yang, Z., Zhao, X., & Lan, D. (2022). Reject inference in credit scoring using a three-way decision and safe SSVM. _Information Sciences_, 606, 614–627.
- Santos, M. S., Soares, J. P., Abreu, P. H., Araújo, H., & Santos, J. (2018). Cross-validation for imbalanced datasets. _IEEE Computational Intelligence Magazine_, 13(4).
