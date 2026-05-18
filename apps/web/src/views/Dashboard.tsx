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
      <h1>Dashboard</h1>
      <div className="subtitle">Portfolio-level KPIs over the 2019 funded green-loan pool.</div>

      {err && <div className="error">{err}</div>}

      {kpi && (
        <>
          <div className="kpi-grid">
            <div className="kpi"><div className="kpi-label">Rows</div><div className="kpi-value">{kpi.n_rows.toLocaleString()}</div></div>
            <div className="kpi"><div className="kpi-label">Labelled</div><div className="kpi-value">{kpi.n_labelled.toLocaleString()}</div></div>
            <div className="kpi"><div className="kpi-label">Delinquent prevalence</div><div className="kpi-value">{(kpi.prevalence * 100).toFixed(2)}%</div></div>
            <div className="kpi"><div className="kpi-label">Mean P(creditworthy)</div><div className="kpi-value">{kpi.mean_score.toFixed(3)}</div></div>
          </div>

          <div className="card">
            <h2>Approve-rate sensitivity by threshold</h2>
            <table>
              <thead><tr><th>Threshold</th><th>Approve rate</th></tr></thead>
              <tbody>
                {Object.entries(kpi.approve_rate_at_threshold).map(([k, v]) => (
                  <tr key={k}><td>{k.replace("thr_", "≥ ")}</td><td>{(v * 100).toFixed(2)}%</td></tr>
                ))}
              </tbody>
            </table>
            <div className="muted" style={{ marginTop: 12 }}>
              At threshold 0.5 the model approves essentially every applicant — moving the threshold up is how the lending officer trades approval volume against expected loss.
            </div>
          </div>

          <div className="card">
            <h2>Top industries by volume</h2>
            <table>
              <thead><tr><th>Industry</th><th>Volume</th><th>Mean score</th></tr></thead>
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
          <h2>Model card</h2>
          <div className="row"><label>Best family</label><div>{card.best_family ?? "—"}</div></div>
          <div className="row"><label>Proposal version</label><div>{card.proposal_version}</div></div>
          <div className="row"><label>Primary metrics</label><div>{card.primary_metrics.join(", ")}</div></div>
          <div className="row"><label>Feature count</label><div>{card.feature_names.length}</div></div>
          <div className="row" style={{ alignItems: "start" }}>
            <label>Regulatory alignment</label>
            <ul style={{ margin: 0, paddingLeft: 16 }}>
              {card.regulatory_alignment.map((r) => <li key={r}>{r}</li>)}
            </ul>
          </div>
          <div className="row" style={{ alignItems: "start" }}>
            <label>Governance artefacts</label>
            <ul style={{ margin: 0, paddingLeft: 16, color: "var(--text-dim)", fontFamily: "monospace", fontSize: 12 }}>
              {card.governance_artefacts.map((g) => <li key={g}>{g}</li>)}
            </ul>
          </div>
        </div>
      )}
    </>
  );
}
