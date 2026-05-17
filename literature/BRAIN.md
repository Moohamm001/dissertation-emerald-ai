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
- ~20/61 paper files written; the remaining 41 are stubbed in `index.yaml` with metadata only — expand on demand
- Gap log seeded with 6 known open questions; expect this to grow as deep dives uncover more

## Operational rules for future-me

1. **Before adding a new claim to the proposal, find or add its supporting paper file.** If `verified: false`, flag it to the user when surfacing.
2. **Before deleting a theme paragraph, check `themes/*.md` for the drafted prose** and update it there too. The theme file is the source of truth for prose; the docx is a render.
3. **When the user asks for "literature on X", first search themes by `themes:` field in index.yaml, then return both the supporting papers and the open holes.** Never invent citations.
4. **When verifying a placeholder citation, update `verified: true` and add the resolved DOI/URL to the paper file.** Don't silently change author/year — record the diff.
