"""Pydantic schemas for the 10-field paper record + supporting types.

Field set is fixed by ``research_automation.txt``:
    title, authors, year, abstract, methodology, contributions, weaknesses,
    future_works, referenced_papers, important_keywords.

Two project-specific additions:
    - confidence on each subjective field (rule: "mark uncertain claims clearly")
    - emerald_relevance (how this paper feeds the dissertation)
"""
from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class Confidence(str, Enum):
    """How confidently a field has been extracted / verified."""

    HIGH = "high"        # primary-source verified, or paper is verified=true in index
    MEDIUM = "medium"    # paraphrased from the brain or canonical secondary sources
    LOW = "low"          # plausible-but-unverified placeholder; needs human check
    UNKNOWN = "unknown"  # not yet attempted


class ProcessingStatus(str, Enum):
    """Where a paper sits in the research pipeline."""

    STUB = "stub"            # index entry only, no JSON record yet
    INDEXED = "indexed"      # JSON sidecar exists, fields populated from brain
    ANALYSED = "analysed"    # full deep-dive done; all fields high/medium confidence
    FAILED = "failed"        # tried and could not extract enough; needs human


class PaperRecord(BaseModel):
    """The 10-field per-paper record mandated by ``research_automation.txt``."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    # Identity
    key: str = Field(..., description="Stable filename-safe slug; matches papers/<key>.md")
    title: str
    authors: list[str] = Field(default_factory=list)
    year: int | None = None

    # The eight content fields
    abstract: str = ""
    methodology: str = ""
    contributions: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    future_works: list[str] = Field(default_factory=list)
    referenced_papers: list[str] = Field(
        default_factory=list,
        description="Internal [[key]] references to other papers in the brain",
    )
    important_keywords: list[str] = Field(default_factory=list)

    # Bibliographic metadata
    venue: str = ""
    doi: str | None = None
    institutions: list[str] = Field(default_factory=list)

    # Project-specific
    themes: list[str] = Field(default_factory=list, description="Maps to themes/4.*-*.md")
    relevance: str = Field("medium", description="critical | high | medium | context")
    emerald_relevance: str = Field("", description="How this paper feeds EMERALD-AI specifically")

    # Audit trail
    confidence: Confidence = Confidence.UNKNOWN
    verified: bool = False
    status: ProcessingStatus = ProcessingStatus.STUB
    search_query: str = Field(
        "",
        description="Search string for verifying the citation if author/year is placeholder",
    )
    notes: str = ""

    # Provenance
    source_files: list[str] = Field(
        default_factory=list,
        description="Repo-relative paths the record was extracted from (e.g. papers/<key>.md)",
    )
    first_seen: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_updated: datetime = Field(default_factory=lambda: datetime.now(UTC))


class GraphEdge(BaseModel):
    """A directed citation relationship: source paper → cited paper."""

    model_config = ConfigDict(extra="forbid")

    source: str = Field(..., description="key of the citing paper")
    target: str = Field(..., description="key of the cited paper")
    relationship: str = Field(
        "cites",
        description="cites | extends | critiques | corroborates | predates",
    )
    confidence: Confidence = Confidence.MEDIUM


class ResearchQuestion(BaseModel):
    """A research question auto-generated from gap traversal or theme inspection."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Stable slug, e.g. RQ-001-gbdt-monotonicity-empirical")
    question: str
    source_gap: str = Field("", description="ID from literature/gaps.md, e.g. G3 or M2")
    related_themes: list[str] = Field(default_factory=list)
    related_papers: list[str] = Field(default_factory=list)
    priority: str = Field("medium", description="critical | high | medium | low")
    status: str = Field("open", description="open | investigating | resolved | rejected")
    notes: str = ""
    created: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AuthorRollup(BaseModel):
    """Aggregated record of an author across the brain."""

    model_config = ConfigDict(extra="forbid")

    name: str
    paper_keys: list[str] = Field(default_factory=list)
    themes: list[str] = Field(default_factory=list)
    institutions: list[str] = Field(default_factory=list)


class TermRollup(BaseModel):
    """Aggregated record of a method, dataset, or keyword across the brain."""

    model_config = ConfigDict(extra="forbid")

    term: str
    kind: str = Field("keyword", description="method | dataset | keyword | institution")
    paper_keys: list[str] = Field(default_factory=list)
    themes: list[str] = Field(default_factory=list)
