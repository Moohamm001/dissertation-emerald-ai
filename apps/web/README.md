# `web/` — Lending-Officer Console (React + Vite SPA)

Single-page application that consumes the FastAPI backend in `../api/`. Built with React 18 + TypeScript + Vite — no extra UI framework or state-management library, just CSS and `useState`/`useEffect`.

The UI is written for a non-expert reader: every page leads with a plain-English help card, every metric has a one-line tooltip, and the Single-Predict page ships with a one-click "Fill with example applicant" button so a first-time user can get a working prediction without inventing numbers.

## Views

| View | Friendly name in nav | Purpose |
|---|---|---|
| `Welcome` | 🏡 Home | Greeting page with what-can-I-do tiles and a 4-step walkthrough. The default view on first load. |
| `AboutModel` | 🧠 About the Model | Algorithm card (which family won + plain-English description), headline raw features (with units and typical ranges), top-15 processed-feature importances, and the full 8-step training pipeline narrated twice — plain English vs. technical register — via a toggle. |
| `Dashboard` | 📊 Dashboard | Portfolio KPIs (rows, default rate, mean score), threshold-sensitivity table, top industries by volume, model card. |
| `SinglePredict` | 👤 Score an Applicant | Form for one applicant in **raw values** (FICO score, dollar amounts, industry…) — no z-scores. Pulls `/raw_schema` from the backend to render numeric inputs (with `p25–p75` typical-range hints) and `<select>` dropdowns for categoricals. Basic-mode shows ~9 headline fields; Advanced mode shows every column the preprocessor consumes. Returns P(creditworthy) + risk band + conformal set + top-10 local contributions + nearest counterfactual. |
| `BatchScore` | 📂 Score a Whole CSV | Three-step uploader: download template → pick file → score. Returns the same CSV with score columns appended. |
| `ShapExplorer` | 🔍 What the Model Looks At | Global permutation-importance ranking with a magnitude bar chart. |
| `FairnessPanel` | ⚖️ Fairness Check | Per-axis demographic-parity / equalised-odds / predictive-parity / calibration-within-group gaps, per-group breakdowns, Selbst et al. (2019) policy notes. |

## Local development

```bash
# 1. start the FastAPI backend in one terminal (from repo root)
python -m emerald_ai train       # only required once — produces models/*.joblib
python -m emerald_ai api          # serves on http://localhost:8000

# 2. start the SPA in another terminal
cd apps/web
npm install                       # one-off; pulls react / vite / typescript
npm run dev                       # opens http://localhost:5173
```

The Vite dev server proxies `/api/*` → `http://localhost:8000` (configured in `vite.config.ts`), so the SPA hits relative `/api/score`, `/api/explain`, etc.

## Production build

```bash
npm run build           # outputs to dist/
npm run preview         # serves dist/ for sanity-check
```

For production deployment, set `VITE_API_BASE` (build-time env var) to the absolute URL of the API.

## File layout

```
apps/web/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── README.md                 ← this file
└── src/
    ├── main.tsx              ← entry point
    ├── App.tsx               ← layout shell + sidebar nav + view switch
    ├── api.ts                ← typed fetch wrapper
    ├── styles.css            ← global styles (soft mint/cream light theme)
    └── views/
        ├── Welcome.tsx       ← landing page with tiles + walkthrough
        ├── AboutModel.tsx    ← algorithm + features + 8-step training pipeline
        ├── Dashboard.tsx
        ├── SinglePredict.tsx
        ├── BatchScore.tsx
        ├── ShapExplorer.tsx
        └── FairnessPanel.tsx
```

## Design conventions

- **Help cards.** Every view opens with a blue `.help-card` ("💡 What am I looking at?") translating the page's purpose into plain English. `.help-card.tip` (amber) is used for caveats and hazards.
- **Result explainers.** Mint-coloured `.result-explainer` boxes sit under every result, paraphrasing what the numbers mean for a lending officer.
- **Step lists.** Multi-step flows (BatchScore, Welcome walkthrough) use the `.step` component with a numbered circle.
- **Tiles.** The Welcome page uses `.tile` buttons for navigation — clicking a tile calls `onNavigate(view)` from the parent `App`.
- **Status pill.** The sidebar footer shows backend status as a coloured pill (`Ready` / `No model yet` / `API offline`) rather than raw error text.

## Backend contract

All endpoints under `/api/*`:

| Endpoint | Method | Used by |
|---|---|---|
| `/healthz` | GET | App shell (status pill), Welcome (training-required banner) |
| `/model_card` | GET | Dashboard, AboutModel (algorithm + training-pipeline steps), BatchScore (template generator) |
| `/raw_schema` | GET | SinglePredict (renders form), AboutModel (typical-range hints) |
| `/portfolio` | GET | Dashboard |
| `/global_importance` | GET | ShapExplorer, AboutModel |
| `/fairness_audit` | GET | FairnessPanel |
| `/score_raw` | POST | SinglePredict (raw applicant → preprocessor → score) |
| `/explain_raw` | POST | SinglePredict (raw applicant → preprocessor → local explanation) |
| `/score`, `/explain` | POST | Legacy post-preprocessing endpoints (kept for diagnostics) |
| `/batch_score` | POST | BatchScore |

## Status

✅ Seven views functional against the v0.2 backend. SinglePredict now accepts **raw** applicant data — the FastAPI service runs `preprocessor.transform()` server-side, so loan officers no longer have to type standardised z-scores. The new AboutModel view answers "which model, which features, how was it trained" with a plain/technical toggle. TreeSHAP swap-in (replace permutation importance) and DiCE counterfactuals land alongside the proposal v0.5 patch. A future patch will add a threshold slider to FairnessPanel and accept raw applicant rows in BatchScore.
