// Thin fetch wrapper. Uses Vite's dev proxy at /api -> http://localhost:8000.
// In production builds, set VITE_API_BASE to the absolute URL.

const BASE = (import.meta as any).env?.VITE_API_BASE ?? "/api";

async function _request<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`${BASE}${path}`, init);
  if (!r.ok) {
    const text = await r.text().catch(() => "");
    throw new Error(`${r.status} ${r.statusText}: ${text}`);
  }
  return r.json() as Promise<T>;
}

export type HealthResponse = {
  status: string;
  version: string;
  artefacts_present: boolean;
};

export type TrainingStep = {
  step: string;
  plain: string;
  technical: string;
};

export type ModelCard = {
  name: string;
  version: string;
  proposal_version: string;
  primary_metrics: string[];
  governance_artefacts: string[];
  regulatory_alignment: string[];
  feature_names: string[];
  best_family: string | null;
  algorithm_label: string | null;
  algorithm_plain: string | null;
  headline_raw_features: string[];
  training_pipeline: TrainingStep[];
  risk_band_thresholds: {
    high_risk_cut?: number;
    watch_cut?: number;
    high_risk_percentile?: number;
    watch_percentile?: number;
  };
};

export type RawColumnSchema = {
  name: string;
  kind: "numeric" | "categorical";
  default: number | string;
  headline: boolean;
  label: string;
  hint: string | null;
  unit: string | null;
  p05?: number | null;
  p25?: number | null;
  p75?: number | null;
  p95?: number | null;
  top_values?: string[] | null;
};

export type ScoreResponse = {
  probability_creditworthy: number;
  risk_band: "approve" | "watch" | "high_risk";
  score_percentile?: number | null;
  conformal_interval_alpha: number;
  conformal_includes_creditworthy: boolean;
  conformal_includes_delinquent: boolean;
};

export type FeatureContrib = {
  feature: string;
  value: number;
  contribution: number;
  direction: "increases" | "decreases" | "neutral";
};

export type ExplainResponse = {
  top_contributions: FeatureContrib[];
  counterfactual: {
    feature: string;
    original_value: number;
    new_value: number;
    delta: number;
    original_prediction: number;
    new_prediction: number;
    flipped: boolean;
  } | null;
  note: string;
};

export type PortfolioKPIs = {
  n_rows: number;
  n_labelled: number;
  prevalence: number;
  mean_score: number;
  approve_rate_at_threshold: Record<string, number>;
  top_industries_by_volume: { Industry: string; volume: number; mean_score: number }[];
};

export type GlobalImportanceRow = {
  feature: string;
  importance_mean: number;
  importance_std: number;
};

export type FairnessAxis = {
  axis: string;
  gaps: {
    dp_gap: number;
    tpr_gap: number;
    fpr_gap: number;
    precision_gap: number;
    ece_gap: number;
  };
  groups: {
    group: string;
    n: number;
    selection_rate: number;
    tpr: number;
    fpr: number;
    precision: number;
    ece: number;
  }[];
};

export const api = {
  health: () => _request<HealthResponse>("/healthz"),
  modelCard: () => _request<ModelCard>("/model_card"),
  portfolio: () => _request<PortfolioKPIs>("/portfolio"),
  globalImportance: (top_k = 20) =>
    _request<GlobalImportanceRow[]>(`/global_importance?top_k=${top_k}`),
  fairnessAudit: () => _request<FairnessAxis[]>("/fairness_audit"),
  rawSchema: () =>
    _request<{ columns: RawColumnSchema[] }>("/raw_schema").then((r) => r.columns),
  scoreRaw: (raw: Record<string, number | string | null>) =>
    _request<ScoreResponse>("/score_raw", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ raw }),
    }),
  explainRaw: (raw: Record<string, number | string | null>) =>
    _request<ExplainResponse>("/explain_raw", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ raw }),
    }),
  score: (features: Record<string, number>) =>
    _request<ScoreResponse>("/score", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ features }),
    }),
  explain: (features: Record<string, number>) =>
    _request<ExplainResponse>("/explain", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ features }),
    }),
  batchScore: async (file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    const r = await fetch(`${BASE}/batch_score`, { method: "POST", body: fd });
    if (!r.ok) throw new Error(`${r.status}: ${await r.text()}`);
    return r.blob();
  },
};
