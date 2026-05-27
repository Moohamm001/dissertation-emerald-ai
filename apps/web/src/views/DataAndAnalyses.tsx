import { useEffect, useState } from "react";
import { api, PortfolioKPIs } from "../api";

type Detail = "plain" | "technical";

export default function DataAndAnalyses() {
  const [kpi, setKpi] = useState<PortfolioKPIs | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [detail, setDetail] = useState<Detail>("plain");

  useEffect(() => {
    api.portfolio().then(setKpi).catch((e) => setErr(String(e)));
  }, []);

  return (
    <>
      <h1>🗄️ The Data &amp; What We Analysed</h1>
      <div className="subtitle">
        A guided tour of the dataset the model was trained on, and every analysis stage we ran on it —
        from the raw 14,135 funded loans through to the fairness audit. Each stage emits a governance
        report under <code>data/governance/</code> for full traceability.
      </div>

      <div className="btn-row" style={{ marginBottom: 20 }}>
        <button
          className={detail === "plain" ? "primary" : "ghost"}
          onClick={() => setDetail("plain")}
        >
          🗣️ Plain English
        </button>
        <button
          className={detail === "technical" ? "primary" : "ghost"}
          onClick={() => setDetail("technical")}
        >
          🔬 Technical
        </button>
      </div>

      {err && <div className="error">⚠️ {err}</div>}

      {/* =========================================================== */}
      <div className="card">
        <h2>📚 The dataset</h2>
        <div className="muted" style={{ marginBottom: 12 }}>
          One row per funded loan transaction; the population is the entire 2019 funded book of a US
          marketplace lender that offers green-purpose financing for small and medium businesses.
        </div>

        <table>
          <thead>
            <tr><th>Property</th><th>Value</th></tr>
          </thead>
          <tbody>
            <tr><td>Source file</td><td><code>data/raw/All_Funded_2019_Green Loan.xlsx</code></td></tr>
            <tr><td>Shape</td><td><strong>14,135 rows × 166 columns</strong></td></tr>
            <tr>
              <td>Labelled rows</td>
              <td>
                <strong>{kpi ? kpi.n_labelled.toLocaleString() : "14,022"}</strong>
                {" "}({kpi ? ((kpi.n_labelled / kpi.n_rows) * 100).toFixed(2) : "99.20"}%
                {" "}— have a usable repay / default outcome)
              </td>
            </tr>
            <tr><td>Calendar period</td><td>1 Jan 2019 – 31 Dec 2019</td></tr>
            <tr><td>Granularity</td><td>One row per funded loan transaction</td></tr>
            <tr><td>Sensitivity</td><td><strong>Proprietary</strong> — gitignored; not redistributed</td></tr>
            <tr>
              <td>Class balance</td>
              <td>
                <strong>{kpi ? (kpi.prevalence * 100).toFixed(2) : "0.36"}%</strong> delinquent
                ({detail === "technical" ? "50 defaults + behind / 14,022 labelled — heavy minority class" : "very rare default events"})
              </td>
            </tr>
          </tbody>
        </table>

        <div className="help-card" style={{ marginTop: 16 }}>
          <div className="help-icon">🏷️</div>
          <div className="help-body">
            <h3>How we labelled "creditworthy" vs "delinquent"</h3>
            <p>
              {detail === "plain" ? (
                <>
                  Each loan has a <code>Deal Status</code>. We treat <em>paidOff</em> and{" "}
                  <em>current</em> as "creditworthy" (Y = 1) and <em>default</em> and <em>behind</em> as
                  "delinquent" (Y = 0). The 113 rows with a missing status are dropped from the labelled set.
                </>
              ) : (
                <>
                  Y = 1 if <code>Deal Status ∈ {"{paidOff, current}"}</code>; Y = 0 if{" "}
                  <code>Deal Status ∈ {"{default, behind}"}</code>; otherwise excluded from the labelled
                  frame (113 rows). Mapping <em>current</em> to the positive class introduces
                  right-censoring bias — addressed via the §5.2 sensitivity analysis flagged in{" "}
                  <code>research/literature/gaps.md</code> (entry M1).
                </>
              )}
            </p>
          </div>
        </div>
      </div>

      {/* =========================================================== */}
      <div className="card">
        <h2>🛡️ Stage 0 — Target-leakage audit</h2>
        <div className="muted" style={{ marginBottom: 12 }}>
          {detail === "plain"
            ? "Before any modelling, we sorted every one of the 166 columns into a category and decided whether it can legitimately be used to predict an outcome that hasn't happened yet."
            : "Per proposal §5.3, each column is classified into one of six categories and routed to either the permitted feature set or the forbidden set. Post-funding observations and administrative routing fields are forbidden because they encode the outcome variable."}
        </div>

        <table>
          <thead>
            <tr><th>Category</th><th>Count</th><th>Permitted?</th></tr>
          </thead>
          <tbody>
            <tr><td>Pre-funding applicant attributes</td><td>23</td><td>✓</td></tr>
            <tr><td>Pre-funding loan-offer attributes</td><td>15</td><td>✓</td></tr>
            <tr><td>Structural metadata</td><td>9</td><td>✓</td></tr>
            <tr><td>Deal-progression timestamps</td><td>43</td><td>✓ (with care)</td></tr>
            <tr><td>Post-funding outcome</td><td>28</td><td>✗ defines Y</td></tr>
            <tr><td>Administrative / staff-routing / free-text</td><td>48</td><td>✗</td></tr>
            <tr>
              <td><strong>Total</strong></td>
              <td><strong>166</strong></td>
              <td><strong>90 permitted · 76 forbidden</strong></td>
            </tr>
          </tbody>
        </table>

        <div className="result-explainer" style={{ marginTop: 12 }}>
          <strong>Why it matters:</strong> training on a forbidden column (e.g. <code>Percent Paid</code> or{" "}
          <code>Closed TS</code>) would produce a near-perfect classifier that knows the answer already —
          a textbook target-leak. Audit emits the canonical <code>feature_catalogue.yaml</code> + audit
          summary under <code>data/governance/</code>.
        </div>
      </div>

      {/* =========================================================== */}
      <div className="card">
        <h2>🔭 Stage 1 — Exploratory data analysis (EDA)</h2>
        <div className="muted" style={{ marginBottom: 12 }}>
          Four sub-layers run over the 90 permitted features: univariate distributions, bivariate
          association with the label, segment-conditional default rates with Wilson 95% CIs, and
          quarterly Population Stability Index (PSI) for distribution drift.
        </div>

        <h3 style={{ marginTop: 0, fontSize: 14, color: "var(--text-dim)" }}>What we found</h3>
        <ul style={{ paddingLeft: 18 }}>
          <li>
            <strong>Industry risk gradient</strong> — <code>firearms</code> at 9.09 % (n = 11, small-N
            flagged); the rest fall in 0.08 % – 1.35 %, a ~17× range. <code>retail</code> is the safest
            sizeable industry; <code>manufacturing</code> the riskiest.
          </li>
          <li>
            <strong>State cluster</strong> — WV / AR / CT / IN / SC sit at 1.43 % – 2.08 %, all ~4–6×
            the base rate. Used directly by the §5.12 fairness audit.
          </li>
          <li>
            <strong>Material temporal drift</strong> — quarterly PSI vs Q1 is 13–14 on{" "}
            <code>Lender Identifier</code>, 10–12 on <code>Published</code>, 8–9 on{" "}
            <code>Attempted</code> / <code>Assigned</code>. <code>Start Month</code> and{" "}
            <code>Start Annual Day</code> show PSI ≈ 16 by construction (pure-time columns) — both are
            dropped at preprocessing to prevent the model from learning "January".
          </li>
          <li>
            <strong>Heavy skew</strong> — most numeric features have skewness {">"} 3 (Amount Sought
            ≈ 109; Payment Amount ≈ 69), motivating tree-based learners and the StandardScaler choice.
          </li>
        </ul>
        <div className="muted">
          Artefact: <code>data/governance/eda_report.md</code>. Re-run: <code>python -m emerald_ai eda</code>.
        </div>
      </div>

      {/* =========================================================== */}
      <div className="card">
        <h2>🧪 Stage 2 — Preprocessing pipeline</h2>
        <div className="muted" style={{ marginBottom: 12 }}>
          A single <code>ColumnTransformer</code> shared across every downstream model, so all
          algorithm-comparison results are on identical feature representations.
        </div>

        <ol className="steps">
          <li className="step">
            <div className="step-num">1</div>
            <div>
              <div className="step-title">Drop list (10 columns)</div>
              <div className="step-body">
                8 columns over the 40 % missingness threshold (<code>Term</code>, <code>APR</code>,{" "}
                <code>Factor</code>, plus the five 100 %-missing-but-permitted fields), and 2
                time-leaking columns (<code>Start Month</code>, <code>Start Annual Day</code>) from
                the EDA PSI diagnostic.
              </div>
            </div>
          </li>
          <li className="step">
            <div className="step-num">2</div>
            <div>
              <div className="step-title">Missing-data treatment</div>
              <div className="step-body">
                Numerics → median imputation + a binary <em>missing-indicator</em> column per feature.
                Categoricals → explicit <code>__missing__</code> level before encoding.
              </div>
            </div>
          </li>
          <li className="step">
            <div className="step-num">3</div>
            <div>
              <div className="step-title">Encoding</div>
              <div className="step-body">
                Low-cardinality categoricals (≤10 levels) → OneHotEncoder.
                High-cardinality (<code>Industry</code>, <code>Borrower State</code>, <code>Lender</code>,{" "}
                <code>Loan Purpose</code>, <code>Prod Type</code>, <code>Product</code>,{" "}
                <code>Borrower City</code>) → TargetEncoder with internal cross-fitting (no test-fold leak).
              </div>
            </div>
          </li>
          <li className="step">
            <div className="step-num">4</div>
            <div>
              <div className="step-title">Scaling</div>
              <div className="step-body">
                StandardScaler on all surviving numerics. Tree learners are scale-invariant, but the
                shared preprocessor keeps linear / SVM / boosted-tree comparisons strictly comparable.
              </div>
            </div>
          </li>
        </ol>

        <div className="result-explainer" style={{ marginTop: 8 }}>
          <strong>Shape change:</strong> 90 permitted input columns → <strong>90 processed features</strong>{" "}
          on 14,022 labelled rows. 35 raw datetime columns deferred to §5.6 feature engineering.
          Artefact: <code>data/governance/preprocess_report.md</code>.
        </div>
      </div>

      {/* =========================================================== */}
      <div className="card">
        <h2>🎯 Stage 3 — Feature selection</h2>
        <div className="muted" style={{ marginBottom: 12 }}>
          Two-stage selection (proposal §5.6): a fast Mutual-Information filter narrows the field, then
          a bootstrap-stability wrapper over Random-Forest importance keeps only the features that
          repeatedly survive resampling.
        </div>

        <table>
          <thead><tr><th>Stage</th><th>Method</th><th>Features in → out</th></tr></thead>
          <tbody>
            <tr>
              <td>1</td>
              <td>MI filter (drop bottom decile vs Y)</td>
              <td><code>90 → 71</code></td>
            </tr>
            <tr>
              <td>2</td>
              <td>Bootstrap-stability RF MDI (10 rounds, ≥60 % selection frequency)</td>
              <td><code>71 → 20</code></td>
            </tr>
          </tbody>
        </table>

        <div className="muted" style={{ marginTop: 12 }}>
          <strong>Survivors (selected at ≥60 % frequency):</strong> Credit Score, Revenue, Payback,
          Payment Amount, Amount Funded, # Offers Received, Closed Max Term, Lender, Prod Rank,
          Average Monthly Sales, Borrower State, Commission, Is Lender Renewal, Max Offer Received $,
          Points, Payment Frequency (weekly), Prod Id, Prod Type, Product, missing-indicator on Payment Amount.
        </div>
        <div className="muted">
          Artefact: <code>data/governance/selection_report.md</code>. Re-run:{" "}
          <code>python -m emerald_ai select</code>.
        </div>
      </div>

      {/* =========================================================== */}
      <div className="card">
        <h2>⚖️ Stage 4 — Class-imbalance harness</h2>
        <div className="muted" style={{ marginBottom: 12 }}>
          With only 50 delinquent loans in 14,022 (0.36 %), every classifier risks collapsing to "predict
          paidOff." We compared three strategies under stratified 5-fold CV on a Logistic-Regression baseline.
        </div>

        <table>
          <thead>
            <tr>
              <th>Strategy</th>
              <th>Minority PR-AUC</th>
              <th>Within-minority ECE</th>
              <th>Joint score</th>
            </tr>
          </thead>
          <tbody>
            <tr><td><code>no_resample</code></td><td>0.053 ± 0.024</td><td>0.973 ± 0.008</td><td>0.001</td></tr>
            <tr><td><code>class_weighted</code></td><td>0.060 ± 0.028</td><td>0.313 ± 0.147</td><td>0.041</td></tr>
            <tr><td><strong><code>smote</code> ✓</strong></td><td><strong>0.086 ± 0.047</strong></td><td>0.321 ± 0.162</td><td><strong>0.058</strong></td></tr>
          </tbody>
        </table>

        <div className="result-explainer" style={{ marginTop: 12 }}>
          <strong>Reading the result:</strong> SMOTE narrowly wins the joint score
          (PR-AUC × (1 − ECE)), but all three strategies leave the minority Expected Calibration Error
          ≈ 0.32 — i.e. resampling alone <em>does not</em> solve calibration at 0.36 % prevalence. That
          empirically motivates the §5.10 conformal + post-hoc calibration layer.
        </div>
        <div className="muted">
          Artefact: <code>data/governance/imbalance_report.md</code>.
        </div>
      </div>

      {/* =========================================================== */}
      <div className="card">
        <h2>🏋️ Stage 5 — Model training &amp; comparison</h2>
        <div className="muted" style={{ marginBottom: 12 }}>
          Five classifier families competed under nested cross-validation (5 outer × 3 inner folds,
          12 RandomizedSearch candidates per family-fold). Primary metric is PR-AUC against the
          minority class; ROC-AUC, within-minority ECE, and recall@top-decile are co-headline per
          proposal §5.13.
        </div>

        <table>
          <thead>
            <tr>
              <th>Family</th>
              <th>PR-AUC</th>
              <th>ROC-AUC</th>
              <th>Recall@top-decile</th>
            </tr>
          </thead>
          <tbody>
            <tr><td><code>lr_l1</code></td><td>0.032 ± 0.011</td><td>0.902 ± 0.047</td><td>0.70 ± 0.14</td></tr>
            <tr><td><code>lr_l2</code></td><td>0.100 ± 0.052</td><td>0.923 ± 0.055</td><td>0.80 ± 0.17</td></tr>
            <tr><td><code>svm_rbf</code></td><td>0.050 ± 0.025</td><td>0.900 ± 0.093</td><td>0.78 ± 0.23</td></tr>
            <tr><td><code>rf</code></td><td>0.137 ± 0.069</td><td>0.945 ± 0.078</td><td>0.90 ± 0.12</td></tr>
            <tr>
              <td><strong><code>xgboost</code> ✓</strong></td>
              <td><strong>0.185 ± 0.118</strong></td>
              <td><strong>0.966 ± 0.034</strong></td>
              <td><strong>0.92 ± 0.13</strong></td>
            </tr>
          </tbody>
        </table>

        <div className="result-explainer" style={{ marginTop: 12 }}>
          <strong>Reading the result:</strong> XGBoost tops the league on every headline metric.
          PR-AUC ≈ 0.19 looks small in absolute terms but is ~52× the random-baseline at 0.36 %
          prevalence. Recall@top-decile = 0.92 means that if you score the whole pool and only review
          the top 10 % most-risky, you catch <em>92 %</em> of the actual defaulters.
        </div>
        <div className="muted">
          Artefact: <code>data/governance/training_report.md</code>. LightGBM / CatBoost gated on
          optional deps; MLP / FT-Transformer deferred to v0.5 (require torch).
        </div>
      </div>

      {/* =========================================================== */}
      <div className="card">
        <h2>📏 Stage 6 — Calibration &amp; conformal uncertainty</h2>
        <div className="muted" style={{ marginBottom: 12 }}>
          Three post-hoc calibrators (Platt, isotonic, temperature scaling) compete on a dedicated
          calibration split, then a <strong>split-conformal predictor</strong> wraps the calibrated
          probabilities to yield distribution-free prediction sets with finite-sample marginal coverage.
        </div>
        <div className="muted">
          The v0.4.1 framing is wired structurally: <em>marginal coverage</em> is the headline guarantee,
          <em> Mondrian (class-conditional) coverage</em> is a diagnostic reported with bootstrap CIs, and
          interval width is deliberately excluded from the primary metrics — small-N (50 minority
          observations) makes width unstable.
        </div>
        <div className="muted">
          Persisted to <code>models/conformal_marginal.joblib</code>; served by the FastAPI{" "}
          <code>/score</code> endpoint.
        </div>
      </div>

      {/* =========================================================== */}
      <div className="card">
        <h2>🔍 Stage 7 — Explainability</h2>
        <div className="muted" style={{ marginBottom: 12 }}>
          Three layers per proposal §5.11: global permutation importance, a local
          coefficient/importance proxy for the chosen applicant, and a nearest-feature greedy
          counterfactual ("what is the smallest change that flips the decision?").
        </div>
        <div className="muted">
          <strong>Top-3 features by permutation importance:</strong> Lender, Prod Rank, Closed Max Term
          — deal-context dominates borrower attributes. (TreeSHAP / KernelSHAP / DiCE / Quantus are
          deferred — they require the <code>shap</code> and <code>dice-ml</code> dependencies.)
        </div>
        <div className="muted">
          Artefact: <code>data/governance/explain_report.md</code>. The Single-Predict view runs the
          local explainer per applicant.
        </div>
      </div>

      {/* =========================================================== */}
      <div className="card">
        <h2>⚖️ Stage 8 — Fairness audit</h2>
        <div className="muted" style={{ marginBottom: 12 }}>
          For each protected proxy (Industry, Borrower State, business-size proxies) we compute
          demographic-parity gap, equalised-odds (TPR / FPR) gap, predictive-parity (precision) gap,
          and calibration-within-group (ECE) gap.
        </div>
        <div className="result-explainer">
          <strong>Honest finding:</strong> at the hard-coded 0.5 threshold the model approves ~99.7 %
          of applicants in every group, so DP and TPR gaps look tiny (0.01–0.08) but for the wrong
          reason — the model isn't <em>doing</em> anything yet. The v0.4 patch introduced
          percentile-based risk bands (bottom 5 % → high-risk, 5th–20th → watch) under which 100 %
          of actual defaulters land in high-risk; the v0.5 patch will re-run the audit at those
          operating points and is the meaningful audit.
        </div>
        <div className="muted">
          Artefact: <code>data/governance/fairness_report.md</code>. Selbst et al. (2019) sociotechnical
          traps are flagged in the emitted report.
        </div>
      </div>

      {/* =========================================================== */}
      <div className="help-card tip" style={{ marginTop: 24 }}>
        <div className="help-icon">📂</div>
        <div className="help-body">
          <h3>Where the audit trail lives</h3>
          <p>
            Every stage above writes a markdown report to <code>data/governance/</code> next to a
            machine-readable <code>feature_catalogue.yaml</code> and the Gebru et al. (2021)
            <code> datasheet.md</code>. The "Traceability" table in the top-level <code>README.md</code> ties
            each empirical finding here back to its proposal § and its source module under{" "}
            <code>src/emerald_ai/</code>.
          </p>
        </div>
      </div>
    </>
  );
}
