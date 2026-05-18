import { useState } from "react";
import { api } from "../api";

export default function BatchScore() {
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);

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

  return (
    <>
      <h1>Batch Score</h1>
      <div className="subtitle">Upload a CSV with one applicant per row. The columns should match the post-preprocessing feature names — see the Dashboard's model-card.</div>

      <div className="card">
        <h2>Upload</h2>
        <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
        <div style={{ marginTop: 16 }}>
          <button className="primary" disabled={!file || busy} onClick={submit}>
            {busy ? "Scoring…" : "Score CSV"}
          </button>
        </div>
        {err && <div className="error">{err}</div>}
        {downloadUrl && (
          <div style={{ marginTop: 16 }}>
            <a href={downloadUrl} download={`scored_${file?.name ?? "batch.csv"}`} className="primary" style={{ textDecoration: "none", padding: "8px 16px", display: "inline-block" }}>
              ↓ Download scored CSV
            </a>
            <div className="muted" style={{ marginTop: 8 }}>
              Each row gains: <code>probability_creditworthy</code>, <code>risk_band</code>, <code>conformal_includes_creditworthy</code>, <code>conformal_includes_delinquent</code>.
            </div>
          </div>
        )}
      </div>

      <div className="card">
        <h2>CSV format</h2>
        <div className="muted">
          Headers should match the post-preprocessing feature names produced by <code>python -m emerald_ai preprocess</code>.
          Missing columns are filled with <code>0.0</code> (standardised-scale default). The server does not re-apply the preprocessor — feed it pre-transformed values, or extend this endpoint in a v0.5 patch to accept raw .xlsx applicant rows and run them through the full pipeline.
        </div>
      </div>
    </>
  );
}
