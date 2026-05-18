# `docs/proposal/` — Dissertation Proposal

Working files for the MSc Applied AI dissertation proposal.

## Files

| File | Purpose |
|---|---|
| `proposal_first_draft.docx` | Original draft authored by the student |
| `proposal_second_draft.docx` | Elevated rewrite (v0.2, ~6,750 words, 61 refs) — kept for diff against v0.3 |
| `proposal_third_draft.docx` | Brain-driven rewrite (v0.3, ~8,500 words, 74 refs) — **current draft for supervisor review** |
| `build_proposal.py` | `python-docx` script that renders the current draft from inline content. Edit + rerun to iterate. |
| `proposal_prompt.txt` | The reusable elevation prompt (role + scope + style) used to drive the rewrite |
| `proposal_tatphong.pdf` | Supervisor reference proposal (**gitignored** — not redistributed) |

## Rebuilding the current draft

```bash
make proposal
# or:
cd docs/proposal && python build_proposal.py
```

The script writes `proposal_third_draft.docx` next to itself. The .docx is git-tracked so the supervisor can diff successive versions.

## Editing protocol

1. Major restructuring → edit `build_proposal.py`, rerun, review docx, commit both.
2. Theme-level content → consider editing the corresponding `research/literature/themes/4.X-*.md` first (which is the source of truth for argumentative prose), then mirror into `build_proposal.py`.
3. New citation → add to `research/literature/index.yaml`, optionally add a `research/literature/papers/<key>.md`, then cite from the proposal.

## Versions

- `v0.1 (first draft)` — student original, ~2,000 words
- `v0.2 (second draft, 2026-05-17)` — elevated rewrite, ~6,750 words, 61 references, expanded §4 (literature) and §5 (methodology) per supervisor's prompt
- `v0.3 (third draft, 2026-05-18)` — brain-driven rewrite, ~8,500 words, 74 references; integrates 14 newly-promoted papers (climate–credit channel, sociotechnical fairness critique, reject-inference, MLOps deployment evidence, opacity-of-finance framing); adds §8 "Scope Boundaries and Future Work" listing federated/DP/MPC/survival/online learning as explicitly out-of-scope
