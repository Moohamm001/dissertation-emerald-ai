import { useEffect, useState } from "react";
import { api, GlobalImportanceRow, ModelCard, RawColumnSchema } from "../api";

type Detail = "plain" | "technical";

export default function AboutModel() {
  const [card, setCard] = useState<ModelCard | null>(null);
  const [imp, setImp] = useState<GlobalImportanceRow[]>([]);
  const [schema, setSchema] = useState<RawColumnSchema[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [detail, setDetail] = useState<Detail>("plain");

  useEffect(() => {
    api.modelCard().then(setCard).catch((e) => setErr(String(e)));
    api.globalImportance(15).then(setImp).catch(() => { /* optional */ });
    api.rawSchema().then(setSchema).catch(() => { /* optional */ });
  }, []);

  const headlineRaw = card?.headline_raw_features ?? [];
  const schemaByName = new Map(schema.map((c) => [c.name, c] as const));

  return (
    <>
      <h1>🧠 About the Model</h1>
      <div className="subtitle">
        What algorithm is under the hood, which fields it actually looks at, and the exact steps we ran to train it —
        explained twice: once in plain English, once in the technical register.
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

      {card && (
        <>
          {/* ----------------------------------------------------------- */}
          <div className="card">
            <h2>🤖 The algorithm we picked</h2>
            <div className="row">
              <label>Family</label>
              <div>
                <strong>{card.algorithm_label ?? card.best_family ?? "—"}</strong>
                <div className="muted" style={{ marginTop: 4, fontFamily: "monospace", fontSize: 12 }}>
                  internal name: <code>{card.best_family ?? "—"}</code>
                </div>
              </div>
            </div>
            {card.algorithm_plain && (
              <div className="result-explainer" style={{ marginTop: 12 }}>
                <strong>In plain English:</strong> {card.algorithm_plain}
              </div>
            )}
            <div className="row" style={{ marginTop: 14 }}>
              <label>Why this one</label>
              <div>
                Five algorithm families competed (logistic regression L1/L2, RBF-SVM, random forest, XGBoost) under
                nested 5×3 cross-validation. <strong>{card.algorithm_label?.split(" —")[0] ?? card.best_family}</strong>{" "}
                topped the league table on the headline metric (PR-AUC against the rare default class).
              </div>
            </div>
            <div className="row" style={{ marginTop: 14 }}>
              <label>How well it scored</label>
              <div className="muted">
                See <code>data/governance/training_report.md</code> for the full per-family table
                (mean ± std over the 5 outer folds).
              </div>
            </div>
            {card.risk_band_thresholds?.high_risk_cut != null && (
              <div className="row" style={{ marginTop: 14 }}>
                <label>Risk-band cut-offs</label>
                <div>
                  <table style={{ marginTop: 0 }}>
                    <thead>
                      <tr><th>Band</th><th>Rule</th><th>P(creditworthy) ≥</th></tr>
                    </thead>
                    <tbody>
                      <tr><td><span className="badge high_risk">high risk</span></td><td>bottom 5% of pool</td><td>—</td></tr>
                      <tr>
                        <td><span className="badge watch">watch</span></td>
                        <td>5th – 20th percentile</td>
                        <td><code>{card.risk_band_thresholds.high_risk_cut.toFixed(6)}</code></td>
                      </tr>
                      <tr>
                        <td><span className="badge approve">approve</span></td>
                        <td>top 80%</td>
                        <td><code>{card.risk_band_thresholds.watch_cut?.toFixed(6)}</code></td>
                      </tr>
                    </tbody>
                  </table>
                  <div className="muted" style={{ marginTop: 6 }}>
                    Because only ~0.36% of training loans defaulted, raw probabilities cluster very close to 1.
                    These percentile-based cut-offs preserve the badges' information value.
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* ----------------------------------------------------------- */}
          <div className="card">
            <h2>🧩 Which features the model uses</h2>
            <div className="muted" style={{ marginBottom: 12 }}>
              The model was trained on <strong>{card.feature_names.length}</strong> processed features derived from{" "}
              <strong>{schema.length || "~70"}</strong> raw applicant fields. Below: the fields you actually need
              to think about for any single applicant.
            </div>

            <h3 style={{ marginTop: 0, fontSize: 14, color: "var(--text-dim)" }}>Headline inputs (the "basics")</h3>
            <table>
              <thead><tr><th>Raw field</th><th>What it is</th>{detail === "technical" && <th>Typical range</th>}</tr></thead>
              <tbody>
                {headlineRaw.map((name) => {
                  const meta = schemaByName.get(name);
                  return (
                    <tr key={name}>
                      <td><code>{name}</code></td>
                      <td>{meta?.hint ?? "—"}</td>
                      {detail === "technical" && (
                        <td className="muted">
                          {meta?.kind === "numeric" && meta.p25 != null && meta.p75 != null
                            ? `${meta.p25.toLocaleString()} – ${meta.p75.toLocaleString()} ${meta.unit ?? ""}`
                            : meta?.kind === "categorical"
                            ? `${meta.top_values?.length ?? 0} categories`
                            : "—"}
                        </td>
                      )}
                    </tr>
                  );
                })}
              </tbody>
            </table>

            {imp.length > 0 && (
              <>
                <h3 style={{ marginTop: 24, fontSize: 14, color: "var(--text-dim)" }}>
                  Top-{imp.length} features by global importance (permutation, post-processing)
                </h3>
                <div className="muted" style={{ marginBottom: 8 }}>
                  These names are the model's <em>processed</em> features (after encoding/scaling) — not the raw
                  fields you fill in. Some raw fields blow up into multiple processed features (e.g.{" "}
                  <code>Payment Frequency_weekly</code>).
                </div>
                <table>
                  <thead><tr><th>Processed feature</th><th>Importance</th></tr></thead>
                  <tbody>
                    {imp.map((r) => (
                      <tr key={r.feature}>
                        <td><code>{r.feature}</code></td>
                        <td>{r.importance_mean.toFixed(4)} <span className="muted">± {r.importance_std.toFixed(4)}</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </>
            )}
          </div>

          {/* ----------------------------------------------------------- */}
          <div className="card">
            <h2>🛠️ Step-by-step: how the model was trained</h2>
            <div className="muted" style={{ marginBottom: 16 }}>
              Toggle the buttons above to switch between the plain and technical narration.
              Every step writes a governance report to <code>data/governance/</code> for full traceability.
            </div>
            <ol className="steps">
              {card.training_pipeline.map((s, i) => (
                <li className="step" key={i}>
                  <div className="step-num">{i + 1}</div>
                  <div>
                    <div className="step-title">{s.step.replace(/^\d+\.\s*/, "")}</div>
                    <div className="step-body">
                      {detail === "plain" ? s.plain : s.technical}
                    </div>
                  </div>
                </li>
              ))}
            </ol>
          </div>

          {/* ----------------------------------------------------------- */}
          <div className="card">
            <h2>📜 Governance & regulatory alignment</h2>
            <div className="row" style={{ alignItems: "start" }}>
              <label>Headline metrics</label>
              <div>{card.primary_metrics.join(", ")}</div>
            </div>
            <div className="row" style={{ alignItems: "start" }}>
              <label>Regulations</label>
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
        </>
      )}

      {!card && !err && <div className="muted">Loading model card…</div>}
    </>
  );
}
