# Literature review queue — frontier-method discoveries (2026-05-30)

A focused discovery round (`research discover` across explainable credit
scoring, conformal prediction, FT-Transformer, counterfactual recourse, and
fairness queries) surfaced the papers below. They are **bot-discovered and
unverified** — they live in `auto_index.yaml` with `verified: false` and
**must not be cited until a human reviews them** (BRAIN.md rule 1 + "never
invent citations").

This queue maps each high-relevance discovery to the technique it supports in
this cycle's implementation, so promotion into the curated `index.yaml` is a
quick, evidence-first task: read the paper note, fill the human-judgement
sections, cross-check the DOI via the `search_query` field, then set
`verified: true` and append the key into `index.yaml`.

## Tabular deep learning (supports `models/deep.py` — MLP + FT-Transformer)

| key | score | why it matters |
|---|---|---|
| `bingzhaozhu2023xtab` | 0.62 | XTab: cross-table Transformer pretraining — frames the FT-Transformer choice and a future pretraining extension. |
| `manujoseph2022gandalf` | 0.62 | GANDALF: gated tabular network — a competitive alternative architecture to benchmark against FT-T. |
| `yuhuafan2024tabular` | 0.73 | Comparative study of tabular deep learning — directly informs the §5.8 deep-vs-GBDT framing. |

## Explainability & interpretability (supports `explain/` — SHAP + fidelity)

| key | score | why it matters |
|---|---|---|
| `diogovcarvalho2019machine` | 0.97 | Survey on interpretability methods *and metrics* — grounds the faithfulness-correlation validation in `fidelity.py`. |
| `aminaadadi2018peeking` | 0.88 | Foundational XAI survey — taxonomy for the SHAP/counterfactual split. |
| `michaelbcker2021transparency` | 0.92 | Transparency, auditability, explainability of ML *in credit* — closest prior art to EMERALD-AI's framing. |

## Counterfactual recourse (supports `counterfactual.py` — DiCE + greedy)

| key | score | why it matters |
|---|---|---|
| `amirhosseinkarimi2022towards` | 0.72 | Towards causal algorithmic recourse — the next step beyond DiCE's associational counterfactuals. |
| `shalmalijoshi2019towards` | 0.63 | Realistic individual recourse — plausibility constraints for the actionable-feature list. |
| `sandrawachter2017why` | 0.66 | The "right to explanation" / GDPR Art. 22 grounding for counterfactual recourse. |

## Credit scoring & GBDT (supports `models/trees.py`, the benchmark)

| key | score | why it matters |
|---|---|---|
| `xolanidastile2020statistical` | 0.95 | Systematic review of statistical + ML credit scoring — benchmark-design reference. |
| `husseinaabdou2011credit` | 0.93 | Credit-scoring techniques & evaluation-criteria review — metric-selection precedent. |
| `annaveronikadorogush2018catboost` | 0.76 | The CatBoost paper — primary reference for the CatBoost family now in the benchmark. |
| `swatityagi2022analyzing` | 0.63 | ML credit scoring with XAI + optimisation — overlaps EMERALD-AI's exact intersection. |

---

_Lower-scoring citation-graph neighbours (a tunnel-blast model, a sepsis
predictor, a blockchain-supply-chain paper) were intentionally **not** listed —
they are off-topic noise from the BFS crawl and should be left in
`auto_index.yaml` unreviewed._
