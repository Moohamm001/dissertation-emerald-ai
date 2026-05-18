import { useEffect, useState } from "react";
import { api, ExplainResponse, ScoreResponse } from "../api";

type Mode = "all" | "selected";

export default function SinglePredict() {
  const [featureNames, setFeatureNames] = useState<string[]>([]);
  const [vals, setVals] = useState<Record<string, number>>({});
  const [score, setScore] = useState<ScoreResponse | null>(null);
  const [explain, setExplain] = useState<ExplainResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [mode, setMode] = useState<Mode>("selected");

  useEffect(() => {
    api.modelCard().then((c) => setFeatureNames(c.feature_names)).catch((e) => setErr(String(e)));
  }, []);

  // Suggest a sensible default subset — the §5.6-selected features by name
  const headlineFeatures = [
    "Credit Score", "Revenue", "Payback", "Payment Amount", "Amount Funded",
    "# Offers Received", "Closed Max Term", "Commission", "Prod Rank",
  ];
  const display = mode === "all"
    ? featureNames
    : featureNames.filter((n) => headlineFeatures.some((h) => n.includes(h)));

  function update(name: string, v: string) {
    const num = v === "" ? 0 : Number(v);
    setVals((s) => ({ ...s, [name]: Number.isFinite(num) ? num : 0 }));
  }

  async function submit() {
    setBusy(true); setErr(null);
    try {
      const s = await api.score(vals);
      const e = await api.explain(vals);
      setScore(s); setExplain(e);
    } catch (e) {
      setErr(String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <h1>Single Predict</h1>
      <div className="subtitle">Score one applicant — feature values are on the standardised post-preprocessing scale.</div>

      <div className="card">
        <h2>Inputs</h2>
        <div style={{ marginBottom: 12 }}>
          <button className="nav-btn" onClick={() => setMode(mode === "all" ? "selected" : "all")}>
            {mode === "all" ? "↩ show §5.6-selected only" : "↳ show all features"}
          </button>
          <span className="muted" style={{ marginLeft: 12 }}>
            {display.length} of {featureNames.length} fields
          </span>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 10 }}>
          {display.map((name) => (
            <div className="row" key={name}>
              <label title={name}>{name.length > 28 ? name.slice(0, 25) + "…" : name}</label>
              <input
                type="number"
                step="0.1"
                placeholder="0.0"
                value={vals[name] ?? ""}
                onChange={(e) => update(name, e.target.value)}
              />
            </div>
          ))}
        </div>
        <button className="primary" disabled={busy} onClick={submit} style={{ marginTop: 16 }}>
          {busy ? "Scoring…" : "Score + Explain"}
        </button>
        {err && <div className="error">{err}</div>}
      </div>

      {score && (
        <div className="card">
          <h2>Decision</h2>
          <div className="row">
            <label>Predicted P(creditworthy)</label>
            <div>
              <strong>{(score.probability_creditworthy * 100).toFixed(2)}%</strong>
              <div className="bar" style={{ marginTop: 6, maxWidth: 240 }}>
                <div className="fill" style={{ width: `${score.probability_creditworthy * 100}%` }} />
              </div>
            </div>
          </div>
          <div className="row">
            <label>Risk band</label>
            <div><span className={`badge ${score.risk_band}`}>{score.risk_band}</span></div>
          </div>
          <div className="row">
            <label>Conformal ({((1 - score.conformal_interval_alpha) * 100).toFixed(0)}% coverage)</label>
            <div>
              Set ={" "}
              {score.conformal_includes_creditworthy && score.conformal_includes_delinquent
                ? "{ 0, 1 } — uncertain"
                : score.conformal_includes_creditworthy
                ? "{ 1 } — creditworthy"
                : score.conformal_includes_delinquent
                ? "{ 0 } — delinquent"
                : "{ } — neither (rare)"}
            </div>
          </div>
        </div>
      )}

      {explain && (
        <div className="card">
          <h2>Top contributing features</h2>
          <table>
            <thead><tr><th>Feature</th><th>Value</th><th>Contribution</th><th>Direction</th></tr></thead>
            <tbody>
              {explain.top_contributions.map((c) => (
                <tr key={c.feature}>
                  <td>{c.feature}</td>
                  <td>{c.value.toFixed(3)}</td>
                  <td>{c.contribution.toFixed(4)}</td>
                  <td>
                    <span className={`badge ${c.direction === "increases" ? "approve" : c.direction === "decreases" ? "high_risk" : "watch"}`}>
                      {c.direction}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="muted" style={{ marginTop: 8 }}>{explain.note}</div>
          {explain.counterfactual && explain.counterfactual.flipped && explain.counterfactual.feature !== "__none__" && (
            <div style={{ marginTop: 16 }}>
              <h3 style={{ fontSize: 14, color: "var(--accent)" }}>Counterfactual recourse</h3>
              <div>
                Change <strong>{explain.counterfactual.feature}</strong> from{" "}
                <code>{explain.counterfactual.original_value.toFixed(3)}</code> to{" "}
                <code>{explain.counterfactual.new_value.toFixed(3)}</code>{" "}
                (Δ = {explain.counterfactual.delta.toFixed(3)}) to flip the prediction from{" "}
                {(explain.counterfactual.original_prediction * 100).toFixed(1)}% →{" "}
                {(explain.counterfactual.new_prediction * 100).toFixed(1)}%.
              </div>
            </div>
          )}
        </div>
      )}
    </>
  );
}
