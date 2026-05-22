import { useEffect, useState } from "react";
import { api, ModelCard, PortfolioKPIs } from "../api";

export default function Dashboard() {
  const [card, setCard] = useState<ModelCard | null>(null);
  const [kpi, setKpi] = useState<PortfolioKPIs | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    api.modelCard().then(setCard).catch((e) => setErr(String(e)));
    api.portfolio().then(setKpi).catch((e) => setErr(String(e)));
  }, []);

  return (
    <>
      <h1>📊 Dashboard</h1>
      <div className="subtitle">
        The big picture of the 2019 funded green-loan pool and how the model behaves across it.
      </div>

      <div className="help-card">
        <div className="help-icon">💡</div>
        <div className="help-body">
          <h3>What am I looking at?</h3>
          <p>
            These are summary statistics over the whole dataset, not a single applicant.
            <strong> Delinquent prevalence</strong> = % of loans that defaulted historically.{" "}
            <strong>Mean P(creditworthy)</strong> = the model's average predicted repayment probability across all loans.{" "}
            The <em>approve-rate</em> table below tells you how strict the model becomes when you raise the cut-off bar.
          </p>
        </div>
      </div>

      {err && <div className="error">⚠️ {err}</div>}

      {kpi && (
        <>
          <div className="kpi-grid">
            <div className="kpi">
              <div className="kpi-label">Total loans</div>
              <div className="kpi-value">{kpi.n_rows.toLocaleString()}</div>
              <div className="kpi-hint">rows in the dataset</div>
            </div>
            <div className="kpi">
              <div className="kpi-label">Labelled</div>
              <div className="kpi-value">{kpi.n_labelled.toLocaleString()}</div>
              <div className="kpi-hint">have a known repay/default outcome</div>
            </div>
            <div className="kpi">
              <div className="kpi-label">Default rate</div>
              <div className="kpi-value">{(kpi.prevalence * 100).toFixed(2)}%</div>
              <div className="kpi-hint">historically went delinquent</div>
            </div>
            <div className="kpi">
              <div className="kpi-label">Mean score</div>
              <div className="kpi-value">{kpi.mean_score.toFixed(3)}</div>
              <div className="kpi-hint">avg. P(creditworthy) the model assigns</div>
            </div>
          </div>

          <div className="card">
            <h2>📐 If you only approve loans above this score…</h2>
            <table>
              <thead><tr><th>Cut-off (P ≥)</th><th>Approve rate</th></tr></thead>
              <tbody>
                {Object.entries(kpi.approve_rate_at_threshold).map(([k, v]) => (
                  <tr key={k}>
                    <td>{k.replace("thr_", "≥ ")}</td>
                    <td>{(v * 100).toFixed(2)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="result-explainer">
              <strong>How to read this:</strong> at the default cut-off of <code>0.5</code> the model approves
              almost everyone — so the cut-off has to move higher to actually deny anyone. Raising it trades approval
              <em> volume</em> against expected <em>loss</em>. The right number is a policy choice, not a model choice.
            </div>
          </div>

          <div className="card">
            <h2>🏭 Where the loans are going</h2>
            <table>
              <thead><tr><th>Industry</th><th>Volume</th><th>Average model score</th></tr></thead>
              <tbody>
                {kpi.top_industries_by_volume.map((r) => (
                  <tr key={r.Industry}>
                    <td>{r.Industry}</td>
                    <td>{r.volume.toLocaleString()}</td>
                    <td>{r.mean_score.toFixed(3)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {card && (
        <div className="card">
          <h2>📜 Model card</h2>
          <div className="muted" style={{ marginBottom: 12 }}>
            The "ID card" of the trained model — what algorithm it is, what it's measured against,
            and which audit reports it's accompanied by.
          </div>
          <div className="row"><label>Algorithm family</label><div>{card.best_family ?? "—"}</div></div>
          <div className="row"><label>Proposal version</label><div>{card.proposal_version}</div></div>
          <div className="row"><label>Headline metrics</label><div>{card.primary_metrics.join(", ")}</div></div>
          <div className="row"><label>Number of features</label><div>{card.feature_names.length}</div></div>
          <div className="row" style={{ alignItems: "start" }}>
            <label>Regulations it aligns with</label>
            <ul style={{ margin: 0, paddingLeft: 16 }}>
              {card.regulatory_alignment.map((r) => <li key={r}>{r}</li>)}
            </ul>
          </div>
          <div className="row" style={{ alignItems: "start" }}>
            <label>Audit documents</label>
            <ul style={{ margin: 0, paddingLeft: 16, color: "var(--text-dim)", fontFamily: "monospace", fontSize: 12 }}>
              {card.governance_artefacts.map((g) => <li key={g}>{g}</li>)}
            </ul>
          </div>
        </div>
      )}
    </>
  );
}
