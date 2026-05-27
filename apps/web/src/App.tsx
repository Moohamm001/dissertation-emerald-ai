import { useEffect, useState } from "react";
import { api, HealthResponse } from "./api";
import Welcome from "./views/Welcome";
import Dashboard from "./views/Dashboard";
import AboutModel from "./views/AboutModel";
import DataAndAnalyses from "./views/DataAndAnalyses";
import SinglePredict from "./views/SinglePredict";
import BatchScore from "./views/BatchScore";
import ShapExplorer from "./views/ShapExplorer";
import FairnessPanel from "./views/FairnessPanel";

type View = "welcome" | "about" | "data" | "dashboard" | "single" | "batch" | "shap" | "fairness";

const NAV: { id: View; icon: string; label: string; subtitle: string }[] = [
  { id: "welcome",   icon: "🏡", label: "Home",                subtitle: "Start here" },
  { id: "about",     icon: "🧠", label: "About the Model",     subtitle: "Algorithm + training" },
  { id: "data",      icon: "🗄️", label: "Data & Analyses",     subtitle: "Dataset + every stage" },
  { id: "dashboard", icon: "📊", label: "Dashboard",           subtitle: "The big picture" },
  { id: "single",    icon: "👤", label: "Score an Applicant",  subtitle: "Try one example" },
  { id: "batch",     icon: "📂", label: "Score a Whole CSV",   subtitle: "Upload a spreadsheet" },
  { id: "shap",      icon: "🔍", label: "What the Model Looks At", subtitle: "Feature ranking" },
  { id: "fairness",  icon: "⚖️", label: "Fairness Check",      subtitle: "Bias audit" },
];

export default function App() {
  const [view, setView] = useState<View>("welcome");
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.health().then(setHealth).catch((e) => setError(String(e)));
  }, []);

  const apiStatus =
    error ? { cls: "bad" as const, text: "API offline" } :
    health == null ? { cls: "warn" as const, text: "Connecting…" } :
    health.artefacts_present ? { cls: "ok" as const, text: "Ready" } :
    { cls: "warn" as const, text: "No model yet" };

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <span className="leaf">🌿</span>
          <div>
            EMERALD-AI
            <small>Green-Loan Console · v{health?.version ?? "?"}</small>
          </div>
        </div>
        {NAV.map((n) => (
          <button
            key={n.id}
            className={`nav-btn${view === n.id ? " active" : ""}`}
            onClick={() => setView(n.id)}
          >
            <span className="nav-icon">{n.icon}</span>
            <span className="nav-text">
              <span>{n.label}</span>
              <span className="nav-sub">{n.subtitle}</span>
            </span>
          </button>
        ))}
        <div className="sidebar-footer">
          <div className="muted" style={{ marginBottom: 6 }}>Backend status</div>
          <div className={`status-pill ${apiStatus.cls}`}>
            <span className="dot" />
            {apiStatus.text}
          </div>
          {error && (
            <div className="muted" style={{ marginTop: 8, fontSize: 10.5 }}>
              Start it with <code>python -m emerald_ai api</code>
            </div>
          )}
        </div>
      </aside>

      <main className="main">
        {!health?.artefacts_present && health !== null && view !== "welcome" && (
          <div className="warn-banner">
            <span className="icon">⚠️</span>
            <div>
              <strong>The model is not trained yet.</strong> Run{" "}
              <code>python -m emerald_ai train</code> in the project folder, then refresh this page.
            </div>
          </div>
        )}
        {error && view !== "welcome" && (
          <div className="warn-banner">
            <span className="icon">🔌</span>
            <div>
              <strong>Cannot reach the backend.</strong> Open a terminal and run{" "}
              <code>python -m emerald_ai api</code>, then refresh. <span className="muted">({error})</span>
            </div>
          </div>
        )}
        {view === "welcome"   && <Welcome onNavigate={setView} />}
        {view === "about"     && <AboutModel />}
        {view === "data"      && <DataAndAnalyses />}
        {view === "dashboard" && <Dashboard />}
        {view === "single"    && <SinglePredict />}
        {view === "batch"     && <BatchScore />}
        {view === "shap"      && <ShapExplorer />}
        {view === "fairness"  && <FairnessPanel />}
      </main>
    </div>
  );
}
