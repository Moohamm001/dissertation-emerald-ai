"""Relevance scoring for candidate papers.

Pure-Python, no LLM, no API key. Scores combine:

    1. **Keyword overlap** between the candidate's title + abstract + concepts
       and the brain's existing themes + keywords.
    2. **Citation overlap** — does the candidate cite (or get cited by) papers
       already in the brain? Strong signal of relevance.
    3. **Recency bonus** — modest preference for recent work (decay over decades).
    4. **Quality signal** — log(cited_by_count) capped contribution.

Returns a normalised score in [0, 1]. Threshold for acceptance is set by the
discovery loop (default 0.45 — accept anything plausibly on-topic).
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass

from emerald_ai.research.sources.base import CandidatePaper

# Domain seed keywords — combined with each theme's tokens at scoring time.
DOMAIN_KEYWORDS: set[str] = {
    "credit", "scoring", "loan", "lending", "default", "risk",
    "green", "esg", "sustainable", "climate",
    "explainable", "interpretable", "shap", "xai", "counterfactual",
    "tabular", "xgboost", "lightgbm", "catboost", "gradient", "boosting", "ensemble",
    "calibration", "conformal", "uncertainty",
    "fairness", "bias", "discrimination", "audit",
    "transformer", "tabnet", "neural", "deep",
}

WORD_RE = re.compile(r"[a-z][a-z0-9\-]{2,}")


def _tokens(text: str) -> set[str]:
    return set(WORD_RE.findall(text.lower()))


@dataclass(frozen=True)
class RelevanceContext:
    """The brain state a scorer uses for context."""

    theme_tokens: set[str]
    brain_keywords: set[str]
    known_external_ids: set[str]
    known_dois: set[str]


def build_context(
    themes: list[str],
    keywords: list[str],
    known_external_ids: list[str],
    known_dois: list[str],
) -> RelevanceContext:
    """Construct a context from the live brain — used by the discovery loop."""
    theme_tokens: set[str] = set()
    for t in themes:
        theme_tokens |= _tokens(t)
    keyword_tokens: set[str] = set()
    for k in keywords:
        keyword_tokens |= _tokens(k)
    return RelevanceContext(
        theme_tokens=theme_tokens | DOMAIN_KEYWORDS,
        brain_keywords=keyword_tokens,
        known_external_ids=set(known_external_ids),
        known_dois={d.lower() for d in known_dois if d},
    )


def score(candidate: CandidatePaper, ctx: RelevanceContext) -> float:
    """Score a candidate in [0, 1]. Higher means more relevant to the brain."""

    # 1. Keyword overlap
    text_tokens = _tokens(
        " ".join([candidate.title, candidate.abstract, " ".join(candidate.concepts)])
    )
    if not text_tokens:
        keyword_score = 0.0
    else:
        overlap_themes = len(text_tokens & ctx.theme_tokens)
        overlap_brain = len(text_tokens & ctx.brain_keywords)
        # diminishing returns
        keyword_score = min(
            1.0, (overlap_themes / 8.0) + (overlap_brain / 12.0)
        )

    # 2. Citation overlap — does it cite stuff we already have?
    citation_overlap = sum(
        1 for r in candidate.referenced_external_ids if r in ctx.known_external_ids
    )
    citation_score = min(1.0, citation_overlap / 3.0)

    # 3. Recency (mild)
    if candidate.year:
        age = max(0, 2025 - candidate.year)
        recency = max(0.0, 1.0 - (age / 60.0))  # full credit ≤ this year, zero at 60y old
    else:
        recency = 0.3

    # 4. Quality (mild) — log scale, capped
    quality = min(1.0, math.log10(max(1, candidate.cited_by_count) + 1) / 4.0)

    # Weighted sum (weights chosen so keyword+citation dominate)
    return round(
        0.45 * keyword_score
        + 0.30 * citation_score
        + 0.15 * recency
        + 0.10 * quality,
        4,
    )
