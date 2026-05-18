import { useEffect, useState } from "react";
import { api, HealthResponse } from "./api";
import Dashboard from "./views/Dashboard";
import SinglePredict from "./views/SinglePredict";
import BatchScore from "./views/BatchScore";
import ShapExplorer from "./views/ShapExplorer";
import FairnessPanel from "./views/FairnessPanel";

type View = "dashboard" | "single" | "batch" | "shap" | "fairness";

const NAV: { id: View; label: string; subtitle: string }[] = [
  { id: "dashboard", label: "Dashboard", subtitle: "Portfolio + KPIs" },
  { id: "single", label: "Single Predict", subtitle: "Score one applicant" },
  { id: "batch", label: "Batch Score", subtitle: "CSV upload" },
  { id: "shap", label: "SHAP Explorer", subtitle: "Global importance" },
  { id: "fairness", label: "Fairness Panel", subtitle: "Per-axis audit" },
];

export default function App() {
  const [view, setView] = useState<View>("dashboard");
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.health().then(setHealth).catch((e) => setError(String(e)));
  }, []);

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          EMERALD-AI
          <small>Lending Officer Console · v{health?.version ?? "?"}</small>
        </div>
        {NAV.map((n) => (
          <button
            key={n.id}
            className={`nav-btn${view === n.id ? " active" : ""}`}
            onClick={() => setView(n.id)}
          >
            {n.label}
            <div className="muted" style={{ fontSize: 10, marginTop: 2 }}>{n.subtitle}</div>
          </button>
        ))}
        <div style={{ marginTop: "auto", paddingTop: 16, borderTop: "1px solid var(--border)", fontSize: 11 }}>
          <div className="muted">API:</div>
          <div style={{ color: health?.artefacts_present ? "var(--good)" : "var(--warn)" }}>
            {health
              ? health.artefacts_present
                ? "✓ artefacts loaded"
                : "⚠ no model — run `train`"
              : error
              ? "✗ unreachable"
              : "…"}
          </div>
        </div>
      </aside>

      <main className="main">
        {!health?.artefacts_present && health !== null && (
          <div className="warn-banner">
            No trained model found. Run <code>python -m emerald_ai train</code> in the project root, then refresh.
          </div>
        )}
        {error && <div className="warn-banner">Could not reach the API: {error}. Start it with <code>python -m emerald_ai api</code>.</div>}
        {view === "dashboard" && <Dashboard />}
        {view === "single" && <SinglePredict />}
        {view === "batch" && <BatchScore />}
        {view === "shap" && <ShapExplorer />}
        {view === "fairness" && <FairnessPanel />}
      </main>
    </div>
  );
}
