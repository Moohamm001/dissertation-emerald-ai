# `research/literature/state/` — Machine-Readable Brain State

This directory is **generated** by `emerald research run` (alias: `make research`). Every file is committed so the brain remains reproducible across sessions and machines.

> **Don't hand-edit these files.** Edit `index.yaml`, the theme files, the paper notes, or `gaps.md`, then re-run the engine.

## Contents

| File | What it is |
|---|---|
| `processed.json` | `{paper_key: status}` map. Idempotency gate — engine skips already-processed papers on re-run. Statuses: `stub` / `indexed` / `analysed` / `failed`. |
| `citations.json` | Directed citation graph as `[{source, target, relationship, confidence}, …]`. Edges only between papers that exist in the brain (no dangling references). |
| `questions.json` | Auto-generated research questions, one per gap in `gaps.md`. Each carries an `id`, `priority`, and `source_gap` traceback. |
| `authors.json` | `{name: {paper_keys, themes, institutions}}` rollup. |
| `institutions.json` | Same shape, keyed by institution. |
| `methods.json` | Method/algorithm rollup (XGBoost, SHAP, SMOTE, …) — detected by keyword match across each paper's content. |
| `datasets.json` | Dataset rollup (COMPAS, FICO, KDD, …) — same detection. |
| `keywords.json` | Free-form keyword rollup from `important_keywords`. |
| `manifest.json` | Last-run timestamp + paper count + schema version. |

## Schema

All records use the pydantic schemas in `src/emerald_ai/research/schema.py`:

- `PaperRecord` — the 10-field record (title, authors, year, abstract, methodology, contributions, weaknesses, future_works, referenced_papers, important_keywords + project-specific additions).
- `GraphEdge` — citation graph edge.
- `ResearchQuestion` — generated question with traceback to a gap.
- `AuthorRollup`, `TermRollup` — aggregation records.

JSON sidecars per paper live next to the markdown: `research/literature/papers/<key>.json` matches `research/literature/papers/<key>.md`.

## Per-paper JSON sidecars

Every paper with `paper_file: true` in `index.yaml` gets a `<key>.json` next to its `<key>.md`. The JSON is the machine-readable view; the markdown is the human-readable view. Both are committed.

Confidence field rules:
- `high` — index entry `verified: true` AND paper markdown has parsed contributions
- `medium` — paper markdown exists but lacks parsed contributions, or unverified index entry
- `low` — index only, no markdown
- `unknown` — never been touched by the engine

## Workflow (from `research/automation.txt`)

1. **Read existing memory** → `State.load()` pulls everything in this directory.
2. **Check processed DB** → engine skips keys already at `analysed` or `indexed` status unless `--force`.
3. **For every new paper** → engine extracts the 10 fields by parsing `papers/<key>.md` sections.
4. **Persist** → markdown stays the source of truth; JSON sidecar is regenerated; rollups updated.
5. **Citation graph** → wiki-links `[[key]]` in paper bodies become edges (intra-brain only — no invented external refs).
6. **Roll up** → authors, institutions, methods, datasets, keywords.
7. **Generate questions** → one `ResearchQuestion` per `G#`/`M#` entry in `gaps.md`.
8. **Save manifest** → timestamp + counts.

## Running

```bash
make research            # one-shot sweep
emerald research run     # same, via CLI
emerald research run --force   # re-process everything (after schema change)
emerald research status  # current counts + manifest
```
