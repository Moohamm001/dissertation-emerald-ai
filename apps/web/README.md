# `web/` — Lending-Officer Console (React + Vite SPA)

Single-page application that consumes the FastAPI backend in `../api/`. Built with React 18 + TypeScript + Vite — no extra UI framework or state-management library, just CSS and `useState`/`useEffect`.

## Views

| View | Purpose |
|---|---|
| **Dashboard** | Portfolio KPIs (rows, prevalence, mean score), threshold-sensitivity table, top industries by volume, model card. |
| **Single Predict** | Form for one applicant → P(creditworthy) + risk band + conformal set + top-10 local contributions + nearest counterfactual. |
| **Batch Score** | CSV upload → scored CSV download (adds `probability_creditworthy`, `risk_band`, conformal flags). |
| **SHAP Explorer** | Global permutation-importance ranking with a magnitude bar chart. |
| **Fairness Panel** | Per-axis demographic-parity / equalised-odds / predictive-parity / calibration-within-group gaps, per-group breakdowns, Selbst et al. (2019) policy notes. |

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
    ├── App.tsx               ← layout shell + nav + view switch
    ├── api.ts                ← typed fetch wrapper
    ├── styles.css            ← global styles (dark theme)
    └── views/
        ├── Dashboard.tsx
        ├── SinglePredict.tsx
        ├── BatchScore.tsx
        ├── ShapExplorer.tsx
        └── FairnessPanel.tsx
```

## Backend contract

All endpoints under `/api/*`:

| Endpoint | Method | Used by |
|---|---|---|
| `/healthz` | GET | App shell (status badge) |
| `/model_card` | GET | Dashboard, SinglePredict (feature names) |
| `/portfolio` | GET | Dashboard |
| `/global_importance` | GET | ShapExplorer |
| `/fairness_audit` | GET | FairnessPanel |
| `/score` | POST | SinglePredict |
| `/explain` | POST | SinglePredict |
| `/batch_score` | POST | BatchScore |

## Status

✅ All five views functional against the v0.1 backend. TreeSHAP swap-in (replace permutation importance) and DiCE counterfactuals land alongside the proposal v0.5 patch.
