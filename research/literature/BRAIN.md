# EMERALD-AI Literature Brain

This directory is the **knowledge core** of the EMERALD-AI dissertation. It exists so that future-me (Claude, in a later session) can read it, deep-dive into any theme or paper, and extend the literature review without re-doing primary research from scratch.

## How to read this brain

If you (Claude in a future session) are asked anything about the literature, citations, or "the argument for X" — start here, not from a blank slate.

| You are asked… | Read this first |
|---|---|
| "Expand subsection 4.X" | `themes/4.X-*.md` |
| "What does paper Y say?" | `papers/<key>.md` (key from `index.yaml`) |
| "What hasn't been covered?" | `gaps.md` |
| "What does <term> mean here?" | `glossary.md` |
| "List all papers on calibration" | grep `themes` for the topic, or filter `index.yaml` by `themes:` field |
| "Are these citations real?" | `index.yaml` — check `verified:` and `search_query:` fields |

## Conventions

**Wiki links.** Internal references use `[[key]]` where `key` matches the `key:` field in `index.yaml` and the filename (without `.md`) under `papers/`. A `[[key]]` that doesn't yet resolve is a known stub — write the file when needed.

**Verification status.** Every entry in `index.yaml` has a `verified:` boolean and a `relevance:` rating (`critical | high | medium | context`). The proposal currently uses placeholder citations per the supervisor's prompt — `verified: false` means the author/year is plausible but the exact title/venue/DOI has not been cross-checked. Use the `search_query:` field to verify.

**Theme files.** Each theme file (e.g. `themes/4.2-gbdt-tabular-sota.md`) contains:
- `Thesis` — the single-sentence argument
- `Argumentative arc` — numbered claims building to the thesis
- `Key sources` — `[[wiki-link]]` list of supporting papers
- `Counter-evidence` — what would weaken the argument
- `Open holes` — what's missing from the current draft
- `Drafted prose` — the prose currently in `proposal_second_draft.docx`

**Paper files.** Each paper file contains: key claims, method, EMERALD-AI relevance, quotable lines, limitations, and links to related entries.

## Why this structure

- **Markdown + YAML, no DB.** Diff-friendly, greppable, no engine dependency. If/when scale demands SQLite, the per-paper frontmatter is already schema-compatible.
- **Themes are first-class, not derived.** The argumentative structure of the lit review is the spine. Papers are citations supporting themes — not the other way around.
- **Stub-tolerant.** Wiki links can point to files that don't exist yet. That's the to-write queue.
- **Verifiable.** Every claim traces to a paper key; every paper key traces to a search query that can verify the reference.

## Current status (snapshot 2026-05-17)

- 8/8 themes drafted (matching `proposal_second_draft.docx` §4.1–4.8)
- 34/62 paper files written with full structured notes; the remaining 28 are stubbed in `index.yaml` with metadata only — expand on demand
- Gap log seeded with 10 literature gaps + 5 methodology gaps
- Machine-readable state (`research/literature/state/`) auto-populated by the research engine: 34 JSON sidecars, 80 citation edges, 179 authors, 22 methods, 9 datasets, 15 research questions

## Automation

The brain is driven by `src/emerald_ai/research/` — an idempotent engine + an autonomous discovery bot, jointly implementing the workflow in `research/automation.txt`.

**Engine** (`engine.py`): reads the existing brain, parses paper markdowns into the 10-field schema (title/authors/year/abstract/methodology/contributions/weaknesses/future_works/referenced_papers/keywords), writes JSON sidecars per paper, builds the citation graph from `[[wiki-links]]`, rolls up authors/institutions/methods/datasets/keywords, and generates research questions from `gaps.md`.

**Discovery bot** (`discovery.py` + `sources/openalex.py`): grows the brain by BFS-traversing the OpenAlex citation graph from seeds (existing papers, a free-text query, or an explicit `--seed` ID). Pure-Python relevance scoring (keyword + citation overlap + recency + quality), saturation-aware, politeness-throttled, on-disk-cached. Bot-discovered papers go into a **separate** `research/literature/auto_index.yaml` and carry `auto_discovered: true` in their frontmatter, so the human-curated `index.yaml` is never modified by the bot.

```bash
# Engine — consume the existing brain
python -m emerald_ai research run       # one-shot sweep, idempotent
python -m emerald_ai research status    # current counts
python -m emerald_ai research show <key>

# Discovery bot — grow the brain
python -m emerald_ai research discover --query "explainable green credit scoring"
python -m emerald_ai research discover --depth 2 --max 20
python -m emerald_ai research bot --rounds 5
```

Hand-edit the markdown + YAML; never hand-edit `research/literature/state/*.json` — they regenerate.

## Operational rules for future-me

1. **Before adding a new claim to the proposal, find or add its supporting paper file.** If `verified: false`, flag it to the user when surfacing.
2. **Before deleting a theme paragraph, check `themes/*.md` for the drafted prose** and update it there too. The theme file is the source of truth for prose; the docx is a render.
3. **When the user asks for "literature on X", first search themes by `themes:` field in index.yaml, then return both the supporting papers and the open holes.** Never invent citations.
4. **When verifying a placeholder citation, update `verified: true` and add the resolved DOI/URL to the paper file.** Don't silently change author/year — record the diff.
