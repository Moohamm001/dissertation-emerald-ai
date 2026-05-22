import { useEffect, useState } from "react";
import { api, GlobalImportanceRow } from "../api";

export default function ShapExplorer() {
  const [rows, setRows] = useState<GlobalImportanceRow[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [topK, setTopK] = useState(20);
  const [busy, setBusy] = useState(false);

  async function load() {
    setBusy(true); setErr(null);
    try {
      setRows(await api.globalImportance(topK));
    } catch (e) {
      setErr(String(e));
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => { load(); /* eslint-disable-next-line */ }, []);

  const maxAbs = rows.length ? Math.max(...rows.map((r) => Math.abs(r.importance_mean))) : 1;

  return (
    <>
      <h1>🔍 What the Model Looks At</h1>
      <div className="subtitle">
        A ranking of the features that matter most to the model across the whole dataset.
      </div>

      <div className="help-card">
        <div className="help-icon">💡</div>
        <div className="help-body">
          <h3>What is this page?</h3>
          <p>
            We measure how much the model's accuracy <em>drops</em> when each feature is shuffled randomly.
            A big drop means the feature is important — the model relies on it. Features near the top
            of the ranking drive most decisions; features near the bottom barely matter.
            (Technical name: <em>permutation importance against PR-AUC</em>.)
          </p>
        </div>
      </div>

      <div className="card">
        <h2>⚙️ Settings</h2>
        <div className="row">
          <label>How many top features to show?</label>
          <input type="number" min={5} max={50} value={topK} onChange={(e) => setTopK(Number(e.target.value))} />
        </div>
        <button className="primary" onClick={load} disabled={busy}>
          {busy ? "Computing…" : "🔄 Recompute"}
        </button>
        {err && <div className="error">⚠️ {err}</div>}
      </div>

      <div className="card">
        <h2>🏆 Ranking</h2>
        <table>
          <thead><tr><th>Rank</th><th>Feature</th><th>Importance ± std</th><th style={{ width: "30%" }}>How much it matters</th></tr></thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={r.feature}>
                <td>{i + 1}</td>
                <td><code>{r.feature}</code></td>
                <td>{r.importance_mean.toFixed(4)} ± {r.importance_std.toFixed(4)}</td>
                <td>
                  <div className="bar">
                    <div className="fill" style={{ width: `${(Math.abs(r.importance_mean) / maxAbs) * 100}%` }} />
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {rows.length > 0 && (
          <div className="result-explainer">
            <strong>Top 3 most important features:</strong>{" "}
            {rows.slice(0, 3).map((r) => r.feature).join(" · ")}.
            <br />
            On this dataset, deal-context features (lender, product rank, deal-flow counts) tend to
            outweigh borrower-attribute signals. The full write-up is in{" "}
            <code>data/governance/explain_report.md</code>.
          </div>
        )}
      </div>
    </>
  );
}
