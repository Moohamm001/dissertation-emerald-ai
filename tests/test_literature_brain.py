"""Integrity checks for the literature brain (literature/).

Run on every commit so a broken bibliography is caught in CI, not at write-up time.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from emerald_ai.config import PATHS

LIT_DIR = PATHS.literature
PAPERS_DIR = LIT_DIR / "papers"
THEMES_DIR = LIT_DIR / "themes"
INDEX_PATH = LIT_DIR / "index.yaml"


@pytest.fixture(scope="module")
def index() -> list[dict]:
    """Load index.yaml once for the module."""
    return yaml.safe_load(INDEX_PATH.read_text(encoding="utf-8"))


def test_brain_exists() -> None:
    """The brain's entrypoint and core directories all exist."""
    assert (LIT_DIR / "BRAIN.md").exists()
    assert INDEX_PATH.exists()
    assert PAPERS_DIR.is_dir()
    assert THEMES_DIR.is_dir()
    assert (LIT_DIR / "gaps.md").exists()
    assert (LIT_DIR / "glossary.md").exists()


def test_eight_theme_files_present() -> None:
    """Each lit-review subsection 4.1–4.8 has a theme file."""
    files = sorted(p.name for p in THEMES_DIR.glob("4.*-*.md"))
    assert len(files) == 8, files


def test_every_flagged_paper_has_a_file(index: list[dict]) -> None:
    """Every index entry with paper_file: true has a corresponding markdown file."""
    flagged = {e["key"] for e in index if e.get("paper_file")}
    present = {p.stem for p in PAPERS_DIR.glob("*.md")}
    missing = flagged - present
    assert not missing, f"Flagged but missing paper files: {missing}"


def test_no_orphan_paper_files(index: list[dict]) -> None:
    """No paper file exists for a key not flagged in index.yaml."""
    flagged = {e["key"] for e in index if e.get("paper_file")}
    present = {p.stem for p in PAPERS_DIR.glob("*.md")}
    orphans = present - flagged
    assert not orphans, f"Paper files without index entry: {orphans}"


def test_index_keys_unique(index: list[dict]) -> None:
    """Every index entry has a unique key."""
    keys = [e["key"] for e in index]
    assert len(keys) == len(set(keys)), "Duplicate keys in index.yaml"


def test_index_relevance_values_valid(index: list[dict]) -> None:
    """relevance: must be one of critical | high | medium | context."""
    allowed = {"critical", "high", "medium", "context"}
    for entry in index:
        assert entry["relevance"] in allowed, f"{entry['key']} bad relevance {entry['relevance']!r}"


# ─────────────────────────────────────────────────────────────
# Research-automation state integrity
# ─────────────────────────────────────────────────────────────

STATE_DIR = LIT_DIR / "state"


def test_state_directory_exists() -> None:
    """After running the engine, literature/state/ exists with the expected files."""
    assert STATE_DIR.is_dir()
    for name in ("processed.json", "citations.json", "questions.json", "authors.json",
                 "institutions.json", "methods.json", "datasets.json", "keywords.json",
                 "manifest.json"):
        assert (STATE_DIR / name).exists(), f"missing state file: {name}"


def test_every_paper_md_has_a_json_sidecar() -> None:
    """For every papers/<key>.md there is a papers/<key>.json with valid schema."""
    import json

    from emerald_ai.research.schema import PaperRecord

    md_keys = {p.stem for p in PAPERS_DIR.glob("*.md")}
    for key in md_keys:
        sidecar = PAPERS_DIR / f"{key}.json"
        assert sidecar.exists(), f"missing JSON sidecar for {key}"
        # Schema must round-trip
        record = PaperRecord(**json.loads(sidecar.read_text(encoding="utf-8")))
        assert record.key == key


def test_citation_graph_edges_resolve(index: list[dict]) -> None:
    """Every edge in the citation graph references a key that exists in the index."""
    import json

    edges = json.loads((STATE_DIR / "citations.json").read_text(encoding="utf-8"))
    keys = {e["key"] for e in index}
    for edge in edges:
        assert edge["source"] in keys, f"edge source {edge['source']} not in index"
        assert edge["target"] in keys, f"edge target {edge['target']} not in index"


def test_engine_run_is_idempotent() -> None:
    """A no-force run after a prior run must not change the manifest counts."""
    import json

    from emerald_ai.research import ResearchEngine

    before = json.loads((STATE_DIR / "manifest.json").read_text(encoding="utf-8"))
    ResearchEngine().run()
    after = json.loads((STATE_DIR / "manifest.json").read_text(encoding="utf-8"))
    assert before["papers_count"] == after["papers_count"]
    assert before["schema_version"] == after["schema_version"]
