# `web/` — React Frontend (SPA)

Lending-officer-facing single-page application that consumes the FastAPI backend (`../api/`).

## Stack (planned)

- React 18 + TypeScript + Vite
- TanStack Query for data fetching
- Recharts for visualisation
- Tailwind CSS for styling

## Pages

| Page | Purpose |
|---|---|
| **Dashboard** | Portfolio-level KPIs, distributions, fairness panel |
| **Single Predict** | Borrower form → score + conformal interval + SHAP waterfall + counterfactual ("what would change this decision?") |
| **Batch Score** | CSV upload → scored output table → downloadable CSV |
| **SHAP Explorer** | Global feature importance, SHAP interaction matrix, PDP/ALE plots, plain-language feature descriptions |

## Local development

```bash
cd web
pnpm install
pnpm dev    # opens http://localhost:5173
```

Frontend reads the API base URL from `VITE_API_BASE_URL` (defaults to `http://localhost:8000`).

## Status

Scaffold to come once the ML pipeline produces a registered model.
