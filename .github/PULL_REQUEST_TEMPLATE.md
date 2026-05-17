## Summary
<!-- 1–3 bullets: what changed and why -->

## Scope
- [ ] Code (`src/emerald_ai/`, `api/`, `web/`)
- [ ] Tests (`tests/`)
- [ ] Documentation (`docs/`, `README.md`)
- [ ] Literature brain (`research/literature/`)
- [ ] Proposal (`docs/proposal/`)
- [ ] CI / tooling / config

## Pre-merge checklist
- [ ] `make check` passes locally (lint + typecheck + tests)
- [ ] If a new citation was added → `research/literature/index.yaml` updated; `research/literature/papers/<key>.md` written (or stubbed); theme file updated
- [ ] If a proposal section changed → `build_proposal.py` updated and `proposal_second_draft.docx` regenerated
- [ ] If a new gap surfaced → recorded in `research/literature/gaps.md`
- [ ] No proprietary data, model artefacts, or supervisor PDF accidentally staged

## Notes for reviewer
<!-- Anything the reviewer should know that isn't obvious from the diff -->
