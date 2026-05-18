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
      <h1>SHAP Explorer</h1>
      <div className="subtitle">
        Global feature importance via permutation importance against PR-AUC. TreeSHAP swap-in lands once the <code>shap</code> dep is added.
      </div>

      <div className="card">
        <h2>Configuration</h2>
        <div className="row">
          <label>Top-K</label>
          <input type="number" min={5} max={50} value={topK} onChange={(e) => setTopK(Number(e.target.value))} />
        </div>
        <button className="primary" onClick={load} disabled={busy}>
          {busy ? "Computing…" : "Recompute"}
        </button>
        {err && <div className="error">{err}</div>}
      </div>

      <div className="card">
        <h2>Ranking</h2>
        <table>
          <thead><tr><th>Rank</th><th>Feature</th><th>Importance ± std</th><th style={{ width: "30%" }}>Magnitude</th></tr></thead>
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
          <div className="muted" style={{ marginTop: 12 }}>
            Top-3: <strong>{rows.slice(0, 3).map((r) => r.feature).join(" / ")}</strong>.
            Deal-context features (Lender, Prod Rank, deal-flow counts) tend to dominate borrower-attribute signals on this dataset — see <code>data/governance/explain_report.md</code>.
          </div>
        )}
      </div>
    </>
  );
}
