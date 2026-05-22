import { useEffect, useState } from "react";
import { api } from "../api";

export default function BatchScore() {
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [featureNames, setFeatureNames] = useState<string[]>([]);

  useEffect(() => {
    api.modelCard().then((c) => setFeatureNames(c.feature_names)).catch(() => {});
  }, []);

  async function submit() {
    if (!file) return;
    setBusy(true); setErr(null); setDownloadUrl(null);
    try {
      const blob = await api.batchScore(file);
      setDownloadUrl(URL.createObjectURL(blob));
    } catch (e) {
      setErr(String(e));
    } finally {
      setBusy(false);
    }
  }

  function downloadTemplate() {
    // Build a one-row CSV with the model's exact column headers and zeroes.
    if (!featureNames.length) return;
    const header = featureNames.join(",");
    const zeros = featureNames.map(() => "0").join(",");
    const csv = `${header}\n${zeros}\n`;
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "emerald_template.csv";
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <>
      <h1>📂 Score a Whole CSV</h1>
      <div className="subtitle">
        Got many applicants in a spreadsheet? Upload it here and the app will return the same file
        with a risk score added to every row.
      </div>

      <div className="help-card">
        <div className="help-icon">💡</div>
        <div className="help-body">
          <h3>New here? Follow the three steps below.</h3>
          <p>
            The CSV needs one row per applicant and one column per feature. The column names
            <strong> must match exactly</strong> what the model expects. The easiest way to get this right
            is to <strong>download the template</strong> in step 1 and fill in your data.
          </p>
        </div>
      </div>

      <ol className="steps">
        <li className="step">
          <div className="step-num">1</div>
          <div style={{ width: "100%" }}>
            <div className="step-title">Get a template with the right columns</div>
            <div className="step-body" style={{ marginBottom: 10 }}>
              This downloads a CSV with all {featureNames.length || "—"} required column names already in place
              and one row of zeroes you can replace with your data.
            </div>
            <button className="secondary" onClick={downloadTemplate} disabled={!featureNames.length}>
              ⬇ Download CSV template
            </button>
          </div>
        </li>

        <li className="step">
          <div className="step-num">2</div>
          <div style={{ width: "100%" }}>
            <div className="step-title">Pick your filled-in CSV</div>
            <div className="step-body" style={{ marginBottom: 10 }}>
              Open the template in Excel or Google Sheets, paste your applicant rows in, and save as CSV.
              Then pick that file here.
            </div>
            <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
            {file && <div className="muted" style={{ marginTop: 8 }}>✓ Selected: <code>{file.name}</code> ({(file.size / 1024).toFixed(1)} KB)</div>}
          </div>
        </li>

        <li className="step">
          <div className="step-num">3</div>
          <div style={{ width: "100%" }}>
            <div className="step-title">Run the scoring</div>
            <div className="step-body" style={{ marginBottom: 10 }}>
              The app sends every row through the model and gives you back the file with four extra columns
              added at the end.
            </div>
            <button className="primary" disabled={!file || busy} onClick={submit}>
              {busy ? "Scoring…" : "🎯 Score CSV"}
            </button>
            {err && <div className="error">⚠️ {err}</div>}
            {downloadUrl && (
              <div style={{ marginTop: 14 }}>
                <a
                  href={downloadUrl}
                  download={`scored_${file?.name ?? "batch.csv"}`}
                  className="primary"
                  style={{ textDecoration: "none", display: "inline-block" }}
                >
                  ⬇ Download scored CSV
                </a>
                <div className="result-explainer" style={{ marginTop: 12 }}>
                  <strong>Each row now has 4 new columns:</strong>
                  <ul style={{ margin: "6px 0 0", paddingLeft: 18 }}>
                    <li><code>probability_creditworthy</code> — 0 to 1, the chance the applicant repays.</li>
                    <li><code>risk_band</code> — approve / watch / high-risk.</li>
                    <li><code>conformal_includes_creditworthy</code> — true if the confident set contains "creditworthy".</li>
                    <li><code>conformal_includes_delinquent</code> — true if the confident set contains "delinquent".</li>
                  </ul>
                </div>
              </div>
            )}
          </div>
        </li>
      </ol>

      <div className="help-card tip" style={{ marginTop: 18 }}>
        <div className="help-icon">⚠️</div>
        <div className="help-body">
          <h3>Heads up about the numbers</h3>
          <p>
            Values must already be on the model's <em>standardised scale</em> (~0 = average).
            If your spreadsheet has raw dollar amounts, you need to run them through{" "}
            <code>python -m emerald_ai preprocess</code> first, otherwise the predictions won't be meaningful.
            A future update will let this page accept raw applicant rows directly.
          </p>
        </div>
      </div>
    </>
  );
}
