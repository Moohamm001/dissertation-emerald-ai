import { useEffect, useMemo, useState } from "react";
import { api, ExplainResponse, RawColumnSchema, ScoreResponse } from "../api";

type Mode = "basic" | "all";

// One ready-made applicant (raw values, not z-scores). The form falls back to
// dataset medians/modes for anything not listed here.
const EXAMPLE_RAW: Record<string, number | string> = {
  "Credit Score": 720,
  "Revenue": 350000,
  "Amount Funded": 75000,
  "Payment Amount": 850,
  "Payback": 1.32,
  "Closed Max Term": 365,
  "# Offers Received": 3,
  "Industry": "Retail Trade",
  "Borrower State": "TX",
  "Average Monthly Sales": 28000,
  "Commission": 4500,
  "Points": 8,
  "Prod Rank": 1,
};

export default function SinglePredict() {
  const [schema, setSchema] = useState<RawColumnSchema[]>([]);
  const [vals, setVals] = useState<Record<string, number | string>>({});
  const [score, setScore] = useState<ScoreResponse | null>(null);
  const [explain, setExplain] = useState<ExplainResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [mode, setMode] = useState<Mode>("basic");

  useEffect(() => {
    api.rawSchema().then(setSchema).catch((e) => setErr(String(e)));
  }, []);

  const visible = useMemo(
    () => (mode === "basic" ? schema.filter((c) => c.headline) : schema),
    [schema, mode],
  );

  function update(name: string, v: string) {
    setVals((s) => ({ ...s, [name]: v }));
  }

  function loadExample() {
    const next: Record<string, number | string> = {};
    for (const col of schema) {
      if (col.name in EXAMPLE_RAW) {
        next[col.name] = EXAMPLE_RAW[col.name];
      } else {
        // dataset default (median for numeric, mode for categorical)
        next[col.name] = col.default;
      }
    }
    setVals(next);
    setScore(null);
    setExplain(null);
  }

  function clearAll() {
    setVals({});
    setScore(null);
    setExplain(null);
  }

  async function submit() {
    setBusy(true);
    setErr(null);
    try {
      // Coerce numeric strings -> numbers; leave categoricals as strings.
      const payload: Record<string, number | string | null> = {};
      for (const col of schema) {
        const raw = vals[col.name];
        if (raw === undefined || raw === "") {
          payload[col.name] = null;
        } else if (col.kind === "numeric") {
          const n = Number(raw);
          payload[col.name] = Number.isFinite(n) ? n : null;
        } else {
          payload[col.name] = String(raw);
        }
      }
      const s = await api.scoreRaw(payload);
      const e = await api.explainRaw(payload);
      setScore(s);
      setExplain(e);
    } catch (e) {
      setErr(String(e));
    } finally {
      setBusy(false);
    }
  }

  function placeholder(col: RawColumnSchema): string {
    if (col.kind === "numeric" && col.default !== null && col.default !== undefined) {
      return String(col.default);
    }
    return "";
  }

  const filledCount = Object.keys(vals).filter((k) => vals[k] !== "" && vals[k] !== undefined).length;

  return (
    <>
      <h1>👤 Score an Applicant</h1>
      <div className="subtitle">
        Type the applicant's <em>real numbers</em> (FICO score, dollar amounts, industry…) and the model returns
        the chance of repayment plus the reasons. No need to pre-process anything — the server does that for you.
      </div>

      <div className="help-card">
        <div className="help-icon">💡</div>
        <div className="help-body">
          <h3>How to use this page</h3>
          <p>
            Just <strong>click "Fill with example"</strong> to load a sample applicant, then press{" "}
            <strong>Score + Explain</strong>. You can edit any value afterwards to see how the prediction shifts.
            Empty fields are auto-filled with the dataset median (numeric) or most common value (categorical).
          </p>
          <p style={{ marginTop: 8 }}>
            <strong>Heads-up on the probability:</strong> only ~0.36% of training loans defaulted, so the model
            outputs very high probabilities for almost everyone. The <em>risk band</em> next to the score is the
            decision-useful number — it ranks the applicant against the training-pool distribution
            (bottom 5% = high-risk, next 15% = watch, top 80% = approve).
          </p>
        </div>
      </div>

      <div className="card">
        <h2>1. Applicant inputs</h2>
        <div className="btn-row" style={{ marginBottom: 16 }}>
          <button className="secondary" onClick={loadExample} disabled={!schema.length}>
            ✨ Fill with example
          </button>
          <button className="ghost" onClick={clearAll}>Clear all</button>
          <button className="ghost" onClick={() => setMode(mode === "basic" ? "all" : "basic")}>
            {mode === "basic" ? "Show advanced fields" : "Show only basics"}
          </button>
          <span className="muted" style={{ marginLeft: "auto" }}>
            {filledCount > 0 ? `${filledCount} filled · ` : ""}
            {visible.length} of {schema.length} fields shown
          </span>
        </div>
        {!schema.length && !err && (
          <div className="muted">Loading the input schema from the trained model…</div>
        )}
        <div className="input-grid">
          {visible.map((col) => {
            const value = vals[col.name] ?? "";
            if (col.kind === "categorical") {
              const opts = col.top_values ?? [];
              return (
                <div className="input-field" key={col.name}>
                  <label title={col.name}>
                    {col.label}
                    {col.headline && <span className="badge approve" style={{ marginLeft: 6, fontSize: 9 }}>basic</span>}
                  </label>
                  <select value={String(value)} onChange={(e) => update(col.name, e.target.value)}>
                    <option value="">— pick one —</option>
                    {opts.map((o) => (
                      <option key={o} value={o}>{o}</option>
                    ))}
                  </select>
                  {col.hint && <div className="hint">{col.hint}</div>}
                </div>
              );
            }
            return (
              <div className="input-field" key={col.name}>
                <label title={col.name}>
                  {col.label}
                  {col.unit && <span className="muted" style={{ marginLeft: 6, fontSize: 11 }}>({col.unit})</span>}
                  {col.headline && <span className="badge approve" style={{ marginLeft: 6, fontSize: 9 }}>basic</span>}
                </label>
                <input
                  type="number"
                  step="any"
                  placeholder={placeholder(col)}
                  value={String(value)}
                  onChange={(e) => update(col.name, e.target.value)}
                />
                {col.hint && (
                  <div className="hint">
                    {col.hint}
                    {col.p25 != null && col.p75 != null && (
                      <span className="muted" style={{ marginLeft: 6 }}>
                        · typical: {col.p25.toLocaleString()} – {col.p75.toLocaleString()}
                      </span>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
        <div style={{ marginTop: 20 }}>
          <button className="primary" disabled={busy || !schema.length} onClick={submit}>
            {busy ? "Scoring…" : "🎯 Score + Explain"}
          </button>
        </div>
        {err && <div className="error">⚠️ {err}</div>}
      </div>

      {score && (
        <div className="card">
          <h2>2. Decision</h2>
          <div className="row">
            <label>Chance of repayment</label>
            <div>
              <strong style={{ fontSize: 20 }}>{(score.probability_creditworthy * 100).toFixed(1)}%</strong>
              <div className="bar" style={{ marginTop: 8, maxWidth: 320 }}>
                <div className="fill" style={{ width: `${score.probability_creditworthy * 100}%` }} />
              </div>
            </div>
          </div>
          <div className="row">
            <label>Risk band</label>
            <div>
              <span className={`badge ${score.risk_band}`}>{score.risk_band.replace("_", " ")}</span>
              {score.score_percentile != null && (
                <div className="muted" style={{ marginTop: 4, fontSize: 12 }}>
                  Score sits at the <strong>{score.score_percentile.toFixed(1)}th percentile</strong> of the
                  historical pool — i.e. ~{score.score_percentile.toFixed(0)}% of past applicants scored at or below this.
                  Bands: bottom 5% = high-risk, next 15% = watch, top 80% = approve.
                </div>
              )}
            </div>
          </div>
          <div className="row">
            <label>How confident is the model?</label>
            <div>
              {score.conformal_includes_creditworthy && score.conformal_includes_delinquent
                ? "🤷 Uncertain — the model can't rule out either outcome at the chosen confidence level."
                : score.conformal_includes_creditworthy
                ? "✅ Confident: applicant is creditworthy."
                : score.conformal_includes_delinquent
                ? "❌ Confident: applicant is likely to default."
                : "⚠️ The model rejects both labels (very rare — investigate)."}
              <div className="muted" style={{ marginTop: 4 }}>
                Based on a {((1 - score.conformal_interval_alpha) * 100).toFixed(0)}% confidence
                conformal prediction set.
              </div>
            </div>
          </div>

          <div className="result-explainer">
            <strong>What this means in plain English:</strong>{" "}
            {score.risk_band === "approve"
              ? "The model thinks this applicant is a safe bet — high chance they'll repay."
              : score.risk_band === "watch"
              ? "The model is unsure. Repayment is more likely than not, but you should review the case manually."
              : "The model thinks this applicant is risky. Probably decline, or attach extra conditions."}
          </div>
        </div>
      )}

      {explain && (
        <div className="card">
          <h2>3. Why did the model decide this?</h2>
          <div className="muted" style={{ marginBottom: 12 }}>
            These are the features that pushed the score the most.{" "}
            <strong>Increases</strong> = made the applicant look <em>more</em> creditworthy.{" "}
            <strong>Decreases</strong> = made them look <em>less</em> creditworthy.
          </div>
          <table>
            <thead><tr><th>Feature</th><th>Processed value</th><th>Pull on score</th><th>Direction</th></tr></thead>
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
            <div className="result-explainer" style={{ marginTop: 16 }}>
              <strong>🔄 What would change the decision?</strong> If{" "}
              <strong>{explain.counterfactual.feature}</strong> went from{" "}
              <code>{explain.counterfactual.original_value.toFixed(3)}</code> to{" "}
              <code>{explain.counterfactual.new_value.toFixed(3)}</code>{" "}
              (a change of {explain.counterfactual.delta.toFixed(3)}), the prediction would flip from{" "}
              {(explain.counterfactual.original_prediction * 100).toFixed(1)}% to{" "}
              {(explain.counterfactual.new_prediction * 100).toFixed(1)}%.
            </div>
          )}
        </div>
      )}

      {!score && !err && (
        <div className="empty-state">
          <div className="big-icon">👆</div>
          <div>Click <strong>Fill with example</strong> and then <strong>Score + Explain</strong> to see the model in action.</div>
        </div>
      )}
    </>
  );
}
