"""Autonomous research-automation engine for the EMERALD-AI literature brain.

Implements the workflow specified in ``research_automation.txt``:

    1. Read existing research memory first.
    2. Check the processed-papers database before analysing new ones.
    3. For every new paper, extract the 10-field schema (see ``schema.PaperRecord``).
    4. Persist as both markdown (human-readable) and JSON (machine-readable).
    5. Record citation edges in the graph (``state/citations.json``).
    6. Roll up authors, institutions, methods, datasets, keywords.
    7. Generate research questions from gaps discovered.
    8. Mark every uncertain claim explicitly; never invent citations.

The engine treats the existing markdown files under ``literature/papers/`` and
``literature/themes/`` as the source of truth for prose, and writes
machine-readable state into ``literature/state/`` for downstream automation.
"""
from __future__ import annotations

from emerald_ai.research.engine import ResearchEngine
from emerald_ai.research.schema import (
    Confidence,
    GraphEdge,
    PaperRecord,
    ProcessingStatus,
    ResearchQuestion,
)
from emerald_ai.research.state import State

__all__ = [
    "Confidence",
    "GraphEdge",
    "PaperRecord",
    "ProcessingStatus",
    "ResearchEngine",
    "ResearchQuestion",
    "State",
]
