"""External-source clients for the autonomous research bot.

Each source implements ``Source`` (see ``base.py``) and is responsible for one
upstream API. The discovery loop in ``discovery.py`` is source-agnostic.

Available sources:
    OpenAlexSource — free, no API key, ~100k req/day with polite mailto identifier.
                     Primary source: works metadata + references + cited_by + concepts.
"""
from __future__ import annotations

from emerald_ai.research.sources.base import (
    CandidatePaper,
    Source,
    SourceError,
    reconstruct_abstract,
)
from emerald_ai.research.sources.openalex import OpenAlexSource

__all__ = [
    "CandidatePaper",
    "OpenAlexSource",
    "Source",
    "SourceError",
    "reconstruct_abstract",
]
