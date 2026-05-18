import { useEffect, useState } from "react";
import { api, FairnessAxis } from "../api";

export default function FairnessPanel() {
  const [axes, setAxes] = useState<FairnessAxis[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(true);

  useEffect(() => {
    api.fairnessAudit()
      .then((a) => setAxes(a))
      .catch((e) => setErr(String(e)))
      .finally(() => setBusy(false));
  }, []);

  return (
    <>
      <h1>Fairness Panel</h1>
      <div className="subtitle">
        Per-axis demographic-parity / equalised-odds / predictive-parity / calibration-within-group gaps.
        Calibration-within-group is the binding constraint (proposal §5.12).
      </div>

      {busy && <div className="muted">Computing audit…</div>}
      {err && <div className="error">{err}</div>}

      {axes.map((ax) => (
        <div key={ax.axis} className="card">
          <h2>Axis: {ax.axis}</h2>
          <div className="kpi-grid">
            <div className="kpi"><div className="kpi-label">DP gap</div><div className="kpi-value">{ax.gaps.dp_gap.toFixed(3)}</div></div>
            <div className="kpi"><div className="kpi-label">TPR gap</div><div className="kpi-value">{ax.gaps.tpr_gap.toFixed(3)}</div></div>
            <div className="kpi"><div className="kpi-label">FPR gap</div><div className="kpi-value">{ax.gaps.fpr_gap.toFixed(3)}</div></div>
            <div className="kpi"><div className="kpi-label">Precision gap</div><div className="kpi-value">{ax.gaps.precision_gap.toFixed(3)}</div></div>
            <div className="kpi"><div className="kpi-label">ECE gap</div><div className="kpi-value">{ax.gaps.ece_gap.toFixed(3)}</div></div>
          </div>
          <table>
            <thead><tr><th>Group</th><th>n</th><th>Sel rate</th><th>TPR</th><th>FPR</th><th>Precision</th><th>ECE</th></tr></thead>
            <tbody>
              {ax.groups.map((g) => (
                <tr key={g.group}>
                  <td>{g.group}</td>
                  <td>{g.n.toLocaleString()}</td>
                  <td>{g.selection_rate.toFixed(3)}</td>
                  <td>{g.tpr.toFixed(3)}</td>
                  <td>{Number.isNaN(g.fpr) ? "—" : g.fpr.toFixed(3)}</td>
                  <td>{g.precision.toFixed(3)}</td>
                  <td>{g.ece.toFixed(3)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}

      <div className="card">
        <h2>Selbst et al. (2019) traps — policy notes</h2>
        <ul style={{ margin: 0, paddingLeft: 20 }}>
          <li>The audit is reported as a value judgement, not a portable claim.</li>
          <li>Calibration-within-group is the binding constraint under IRB PD reporting.</li>
          <li>Base-rate decompositions are published so reviewers can disagree on visible grounds.</li>
          <li>Fairness claims are conditional on the deployment context (US 2019 funded loans).</li>
        </ul>
        <div className="muted" style={{ marginTop: 12 }}>
          v0.5 patch on the proposal side: re-run this audit at the §5.7 risk-band thresholds rather than the default 0.5 — at 0.5 the model approves ~100% of applicants and the DP/TPR gaps collapse.
        </div>
      </div>
    </>
  );
}
