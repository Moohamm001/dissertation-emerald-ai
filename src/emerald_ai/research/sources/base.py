"""Abstract source interface + shared utilities.

A ``Source`` returns ``CandidatePaper`` records — normalised across upstream
APIs — that the discovery loop scores and either accepts (writes into the
brain) or rejects (records in ``discovery_seen.json`` to avoid re-fetching).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

from pydantic import BaseModel, ConfigDict, Field


class SourceError(RuntimeError):
    """Raised when an upstream source returns an unrecoverable error."""


class CandidatePaper(BaseModel):
    """Normalised paper record returned by any ``Source``.

    Source-specific IDs (OpenAlex W-IDs, Semantic Scholar paper IDs) are kept
    in ``external_ids`` so the discovery loop can de-duplicate across sources.
    """

    model_config = ConfigDict(extra="forbid")

    source: str = Field(..., description="Source name, e.g. 'openalex'")
    external_id: str = Field(..., description="Source-native ID, e.g. 'W2964121823'")
    doi: str | None = None
    title: str = ""
    authors: list[str] = Field(default_factory=list)
    year: int | None = None
    venue: str = ""
    abstract: str = ""
    concepts: list[str] = Field(default_factory=list, description="Topic labels from the source")
    referenced_external_ids: list[str] = Field(
        default_factory=list,
        description="External IDs of papers this one cites (drives recursion)",
    )
    cited_by_count: int = 0
    external_ids: dict[str, str] = Field(
        default_factory=dict,
        description="Cross-source ID map, e.g. {'openalex': 'W...', 'doi': '10.1145/...'}",
    )


def reconstruct_abstract(inverted_index: dict[str, list[int]] | None) -> str:
    """OpenAlex returns abstracts as an inverted index; reassemble linear text.

    Returns an empty string when no inverted index is available (some works do
    not carry abstracts due to copyright).
    """
    if not inverted_index:
        return ""
    positions: dict[int, str] = {}
    for word, indices in inverted_index.items():
        for i in indices:
            positions[i] = word
    return " ".join(positions[i] for i in sorted(positions))


class Source(ABC):
    """Abstract source. Concrete sources implement fetch / search / references."""

    name: str

    @abstractmethod
    def fetch(self, external_id: str) -> CandidatePaper:
        """Fetch a single paper by the source's native ID."""

    @abstractmethod
    def fetch_by_doi(self, doi: str) -> CandidatePaper | None:
        """Fetch a paper by DOI; return None if not found."""

    @abstractmethod
    def search(self, query: str, *, limit: int = 10) -> list[CandidatePaper]:
        """Free-text search; results ranked by source-side relevance."""

    @abstractmethod
    def references(self, external_id: str) -> Iterable[CandidatePaper]:
        """Iterate references of the given paper.

        Implementations should de-duplicate and respect the source's rate limit.
        Use ``yield`` to allow the consumer to stop early.
        """
