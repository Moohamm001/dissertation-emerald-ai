"""File-backed state for the research engine.

All machine-readable state lives under ``literature/state/`` and is committed to
git so the brain remains reproducible across sessions and machines.

Layout:
    literature/state/
        processed.json       - {key: status} map; idempotency gate (rule 6)
        citations.json       - directed citation graph as a list of GraphEdge
        questions.json       - generated research questions
        authors.json         - author rollups
        institutions.json    - institution rollups
        methods.json         - method/algorithm rollups
        datasets.json        - dataset rollups
        keywords.json        - free-form keyword rollups
        manifest.json        - last-run timestamp + paper-count + version
"""
from __future__ import annotations

import json
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel

from emerald_ai.config import PATHS
from emerald_ai.research.schema import (
    AuthorRollup,
    GraphEdge,
    PaperRecord,
    ProcessingStatus,
    ResearchQuestion,
    TermRollup,
)

STATE_DIR: Path = PATHS.literature / "state"
PAPERS_JSON_DIR: Path = PATHS.literature / "papers"  # JSON sidecars live next to .md


def _read_json(path: Path, default: object) -> object:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )


def _to_jsonable(items: Iterable[BaseModel]) -> list[dict]:
    return [it.model_dump(mode="json") for it in items]


class State:
    """In-memory view of literature/state/, with explicit load() / save() calls."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or STATE_DIR
        self.processed: dict[str, str] = {}
        self.citations: list[GraphEdge] = []
        self.questions: list[ResearchQuestion] = []
        self.authors: dict[str, AuthorRollup] = {}
        self.institutions: dict[str, TermRollup] = {}
        self.methods: dict[str, TermRollup] = {}
        self.datasets: dict[str, TermRollup] = {}
        self.keywords: dict[str, TermRollup] = {}

    # ---------- load ----------
    def load(self) -> State:
        self.processed = dict(_read_json(self.root / "processed.json", {}))  # type: ignore[arg-type]
        self.citations = [
            GraphEdge(**e) for e in _read_json(self.root / "citations.json", [])  # type: ignore[arg-type]
        ]
        self.questions = [
            ResearchQuestion(**q) for q in _read_json(self.root / "questions.json", [])  # type: ignore[arg-type]
        ]
        self.authors = {
            k: AuthorRollup(**v)
            for k, v in _read_json(self.root / "authors.json", {}).items()  # type: ignore[union-attr]
        }
        for term_kind in ("institutions", "methods", "datasets", "keywords"):
            payload = _read_json(self.root / f"{term_kind}.json", {})
            setattr(
                self,
                term_kind,
                {k: TermRollup(**v) for k, v in payload.items()},  # type: ignore[union-attr]
            )
        return self

    # ---------- save ----------
    @staticmethod
    def _write_if_changed(path: Path, payload: object) -> None:
        """Skip the write if the on-disk payload is byte-identical."""
        new = json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n"
        if path.exists() and path.read_text(encoding="utf-8") == new:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(new, encoding="utf-8")

    def save(self, *, papers_count: int | None = None) -> None:
        self._write_if_changed(self.root / "processed.json", self.processed)
        self._write_if_changed(self.root / "citations.json", _to_jsonable(self.citations))
        self._write_if_changed(self.root / "questions.json", _to_jsonable(self.questions))
        self._write_if_changed(
            self.root / "authors.json",
            {k: v.model_dump(mode="json") for k, v in self.authors.items()},
        )
        for term_kind in ("institutions", "methods", "datasets", "keywords"):
            rollups: dict[str, TermRollup] = getattr(self, term_kind)
            self._write_if_changed(
                self.root / f"{term_kind}.json",
                {k: v.model_dump(mode="json") for k, v in rollups.items()},
            )
        # manifest.json is the one file that genuinely should bump every run
        manifest = {
            "last_run": datetime.now(UTC).isoformat(timespec="seconds"),
            "papers_count": papers_count if papers_count is not None else len(self.processed),
            "schema_version": 1,
        }
        _write_json(self.root / "manifest.json", manifest)

    # ---------- per-paper sidecars ----------
    @staticmethod
    def paper_json_path(key: str) -> Path:
        return PAPERS_JSON_DIR / f"{key}.json"

    @staticmethod
    def load_paper(key: str) -> PaperRecord | None:
        path = State.paper_json_path(key)
        if not path.exists():
            return None
        return PaperRecord(**json.loads(path.read_text(encoding="utf-8")))

    @staticmethod
    def save_paper(record: PaperRecord) -> None:
        """Persist a paper record, skipping the write if nothing material changed.

        ``last_updated`` and ``first_seen`` are stripped from the equality check so
        re-running the engine over an unchanged brain produces a clean git diff.
        """
        path = State.paper_json_path(record.key)
        path.parent.mkdir(parents=True, exist_ok=True)

        new_payload = record.model_dump(mode="json")
        compare_keys = {k: v for k, v in new_payload.items() if k not in {"last_updated", "first_seen"}}

        if path.exists():
            existing = json.loads(path.read_text(encoding="utf-8"))
            existing_keys = {k: v for k, v in existing.items() if k not in {"last_updated", "first_seen"}}
            if existing_keys == compare_keys:
                return  # nothing material changed → skip write

        record.last_updated = datetime.now(UTC)
        path.write_text(record.model_dump_json(indent=2) + "\n", encoding="utf-8")

    def mark_processed(self, key: str, status: ProcessingStatus) -> None:
        self.processed[key] = status.value if isinstance(status, ProcessingStatus) else status

    def is_processed(self, key: str) -> bool:
        """Rule 3: never repeat already-processed papers."""
        return self.processed.get(key) in (ProcessingStatus.ANALYSED.value, ProcessingStatus.INDEXED.value)
