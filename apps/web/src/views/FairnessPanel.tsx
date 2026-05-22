import { useEffect, useState } from "react";
import { api, FairnessAxis } from "../api";

const GAP_HINTS: Record<string, string> = {
  dp_gap:        "Demographic parity gap — difference in approval rate between groups.",
  tpr_gap:       "True-positive gap — does the model catch good applicants equally well across groups?",
  fpr_gap:       "False-positive gap — does the model wrongly approve risky applicants more often in some groups?",
  precision_gap: "Precision gap — when the model approves, is it equally right across groups?",
  ece_gap:       "Calibration gap — do predicted probabilities mean the same thing in every group? (This is the binding one.)",
};

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
      <h1>⚖️ Fairness Check</h1>
      <div className="subtitle">
        Does the model treat different groups (industry, region) the same?
        This page compares how the model behaves group-by-group so you can spot bias.
      </div>

      <div className="help-card">
        <div className="help-icon">💡</div>
        <div className="help-body">
          <h3>What am I looking at?</h3>
          <p>
            For each grouping (called an <em>axis</em>), we measure how the model's behaviour differs
            between groups. A small <em>gap</em> means the model treats groups similarly; a large gap means
            it doesn't. <strong>Calibration (ECE) gap</strong> is the one we care about most — it tells you
            whether a "70% chance of repayment" really means the same thing in every group.
          </p>
        </div>
      </div>

      {busy && <div className="muted">⏳ Computing the audit…</div>}
      {err && <div className="error">⚠️ {err}</div>}

      {axes.map((ax) => (
        <div key={ax.axis} className="card">
          <h2>Grouped by: <code>{ax.axis}</code></h2>
          <div className="kpi-grid">
            {Object.entries(ax.gaps).map(([k, v]) => (
              <div className="kpi" key={k}>
                <div className="kpi-label">{k.replace("_", " ")}</div>
                <div className="kpi-value">{v.toFixed(3)}</div>
                <div className="kpi-hint">{GAP_HINTS[k] ?? ""}</div>
              </div>
            ))}
          </div>
          <h3 style={{ marginTop: 18, marginBottom: 8 }}>Per-group breakdown</h3>
          <table>
            <thead>
              <tr>
                <th>Group</th>
                <th>Applicants</th>
                <th>Approved %</th>
                <th>True-pos rate</th>
                <th>False-pos rate</th>
                <th>Precision</th>
                <th>Calibration err</th>
              </tr>
            </thead>
            <tbody>
              {ax.groups.map((g) => (
                <tr key={g.group}>
                  <td>{g.group}</td>
                  <td>{g.n.toLocaleString()}</td>
                  <td>{(g.selection_rate * 100).toFixed(1)}%</td>
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
        <h2>📌 Policy notes (Selbst et al. 2019)</h2>
        <ul style={{ margin: 0, paddingLeft: 20, lineHeight: 1.7 }}>
          <li>The audit is reported as a value judgement, not a portable claim.</li>
          <li>Calibration-within-group is the binding constraint under IRB PD reporting.</li>
          <li>Base-rate decompositions are published so reviewers can disagree on visible grounds.</li>
          <li>Fairness claims are conditional on the deployment context (US 2019 funded loans).</li>
        </ul>
        <div className="result-explainer">
          <strong>One thing to keep in mind:</strong> at the default cut-off of 0.5 the model approves nearly
          everyone, so DP / TPR gaps look tiny. Re-run the audit at the §5.7 risk-band thresholds to see the
          gaps that actually bite. A future version of the app will let you slide the threshold here.
        </div>
      </div>
    </>
  );
}
