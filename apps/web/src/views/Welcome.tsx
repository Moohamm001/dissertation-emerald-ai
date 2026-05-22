import { useEffect, useState } from "react";
import { api, HealthResponse } from "../api";

type Props = {
  onNavigate: (view: "about" | "dashboard" | "single" | "batch" | "shap" | "fairness") => void;
};

export default function Welcome({ onNavigate }: Props) {
  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    api.health().then(setHealth).catch(() => setHealth(null));
  }, []);

  const ready = health?.artefacts_present === true;

  return (
    <>
      <h1>Hi! Welcome to EMERALD-AI 🌿</h1>
      <div className="subtitle">
        This little tool helps a loan officer decide whether a green-loan applicant is likely to pay back,
        and — just as importantly — <em>why</em> the model thinks so.
        Pick what you want to do below. You don't need to be a data scientist to use it.
      </div>

      <div className="help-card">
        <div className="help-icon">💡</div>
        <div className="help-body">
          <h3>First time here? Read this.</h3>
          <p>
            The app has five pages on the left. The most useful place to start is <strong>Score an Applicant</strong> —
            it shows what the model does on a single example. Then try <strong>Score a Whole CSV</strong> if you
            have many applicants in a spreadsheet. The other pages explain <em>how</em> the model thinks.
          </p>
        </div>
      </div>

      {!ready && (
        <div className="warn-banner">
          <span className="icon">⚠️</span>
          <div>
            <strong>The model is not trained yet.</strong> Open a terminal in the project folder and run{" "}
            <code>python -m emerald_ai train</code>. After it finishes, refresh this page.
          </div>
        </div>
      )}

      <div className="card">
        <h2>🚀 What can I do here?</h2>
        <div className="tile-grid">
          <button className="tile" onClick={() => onNavigate("about")}>
            <div className="tile-icon">🧠</div>
            <div className="tile-title">About the Model</div>
            <div className="tile-desc">
              Which algorithm we picked, the fields it looks at, and the step-by-step training pipeline —
              explained in both plain English and the technical register. Read this first.
            </div>
            <div className="tile-cta">See the model card →</div>
          </button>

          <button className="tile" onClick={() => onNavigate("dashboard")}>
            <div className="tile-icon">📊</div>
            <div className="tile-title">Dashboard</div>
            <div className="tile-desc">
              The big picture: how many loans, how risky the pool looks, which industries borrow most.
              Open this first if you want to understand the data.
            </div>
            <div className="tile-cta">Open dashboard →</div>
          </button>

          <button className="tile" onClick={() => onNavigate("single")}>
            <div className="tile-icon">👤</div>
            <div className="tile-title">Score an Applicant</div>
            <div className="tile-desc">
              Type the applicant's real numbers (FICO score, dollar amounts, industry…) — no pre-processing,
              no z-scores. The model returns a probability of repayment and the top reasons.
            </div>
            <div className="tile-cta">Try a single score →</div>
          </button>

          <button className="tile" onClick={() => onNavigate("batch")}>
            <div className="tile-icon">📂</div>
            <div className="tile-title">Score a Whole CSV</div>
            <div className="tile-desc">
              Got many applicants in a spreadsheet? Upload the CSV here and get it back with a
              risk score added to every row.
            </div>
            <div className="tile-cta">Upload a file →</div>
          </button>

          <button className="tile" onClick={() => onNavigate("shap")}>
            <div className="tile-icon">🔍</div>
            <div className="tile-title">What the Model Looks At</div>
            <div className="tile-desc">
              A ranking of the features that matter most to the model across all applicants.
              Helpful for understanding what's driving decisions.
            </div>
            <div className="tile-cta">See the ranking →</div>
          </button>

          <button className="tile" onClick={() => onNavigate("fairness")}>
            <div className="tile-icon">⚖️</div>
            <div className="tile-title">Fairness Check</div>
            <div className="tile-desc">
              Does the model treat different groups (industry, region) the same?
              This page shows gaps between groups so you can spot bias.
            </div>
            <div className="tile-cta">Run the audit →</div>
          </button>
        </div>
      </div>

      <div className="card">
        <h2>📖 A quick 4-step walkthrough</h2>
        <ol className="steps">
          <li className="step">
            <div className="step-num">1</div>
            <div>
              <div className="step-title">Read "About the Model"</div>
              <div className="step-body">
                Tells you which algorithm is under the hood, which raw applicant fields it cares about,
                and the eight-step training pipeline — in plain English or technical register.
              </div>
            </div>
          </li>
          <li className="step">
            <div className="step-num">2</div>
            <div>
              <div className="step-title">Look at the Dashboard</div>
              <div className="step-body">
                It shows the dataset (~14,000 funded green loans from 2019) and how the model behaves overall.
                The <em>approve-rate-by-threshold</em> table tells you how strict the model is when you raise the bar.
              </div>
            </div>
          </li>
          <li className="step">
            <div className="step-num">3</div>
            <div>
              <div className="step-title">Try scoring one applicant</div>
              <div className="step-body">
                Go to <strong>Score an Applicant</strong>. Click <code>Fill with example</code> to load a
                ready-made applicant — no need to invent numbers. Press <code>Score + Explain</code>.
                You'll see the probability of repayment, a risk band (approve / watch / high-risk), and the
                top features that pushed the decision either way.
              </div>
            </div>
          </li>
          <li className="step">
            <div className="step-num">4</div>
            <div>
              <div className="step-title">Check the explanations</div>
              <div className="step-body">
                The <strong>What the Model Looks At</strong> page shows which features matter most overall.
                The <strong>Fairness Check</strong> page compares groups so you can see whether the model is
                even-handed. Both are required reading before trusting any decision.
              </div>
            </div>
          </li>
        </ol>
      </div>

      <div className="help-card tip">
        <div className="help-icon">🎓</div>
        <div className="help-body">
          <h3>What does "creditworthy" mean?</h3>
          <p>
            A creditworthy applicant is one the model believes will repay the loan. Higher probability
            (closer to 100%) is safer; lower probability (closer to 0%) is riskier. The risk bands are:{" "}
            <strong>approve</strong> ≥ 80% chance of repayment, <strong>watch</strong> 50–80%,{" "}
            <strong>high-risk</strong> below 50%. You can change those cut-offs later in the proposal.
          </p>
        </div>
      </div>
    </>
  );
}
