"""Tests for the autonomous discovery bot (no real HTTP)."""
from __future__ import annotations

from collections.abc import Iterable

import pytest

from emerald_ai.research import (
    CandidatePaper,
    DiscoveryConfig,
    Source,
    build_context,
    discover,
    score,
)


# ─────────────────────────────────────────────────────────────
# Fake source — never touches the network
# ─────────────────────────────────────────────────────────────


class _FakeSource(Source):
    """In-memory source backed by a dict[external_id → CandidatePaper]."""

    name = "fake"

    def __init__(self, corpus: dict[str, CandidatePaper]) -> None:
        self.corpus = corpus

    def fetch(self, external_id: str) -> CandidatePaper:
        if external_id not in self.corpus:
            from emerald_ai.research.sources.base import SourceError

            raise SourceError(f"unknown id {external_id}")
        return self.corpus[external_id]

    def fetch_by_doi(self, doi: str) -> CandidatePaper | None:
        for c in self.corpus.values():
            if c.doi == doi:
                return c
        return None

    def search(self, query: str, *, limit: int = 10) -> list[CandidatePaper]:
        ranked = sorted(self.corpus.values(), key=lambda c: c.cited_by_count, reverse=True)
        return ranked[:limit]

    def references(self, external_id: str) -> Iterable[CandidatePaper]:
        c = self.corpus.get(external_id)
        if not c:
            return
        for r in c.referenced_external_ids:
            if r in self.corpus:
                yield self.corpus[r]


def _make_candidate(
    ext_id: str,
    *,
    title: str,
    refs: list[str] | None = None,
    cited_by: int = 100,
    abstract: str = "",
    year: int = 2022,
) -> CandidatePaper:
    return CandidatePaper(
        source="fake",
        external_id=ext_id,
        title=title,
        authors=["Doe, J."],
        year=year,
        abstract=abstract or title,
        referenced_external_ids=refs or [],
        cited_by_count=cited_by,
        external_ids={"fake": ext_id},
    )


# ─────────────────────────────────────────────────────────────
# Relevance scoring
# ─────────────────────────────────────────────────────────────


def test_score_relevant_paper_beats_irrelevant() -> None:
    ctx = build_context(themes=["gbdt-tabular-sota"], keywords=[], known_external_ids=[], known_dois=[])
    relevant = _make_candidate(
        "R1",
        title="XGBoost for credit scoring with SHAP explanations and conformal calibration",
        cited_by=500,
    )
    irrelevant = _make_candidate(
        "R2",
        title="Optical fibre dispersion in submarine cables",
        cited_by=500,
    )
    assert score(relevant, ctx) > score(irrelevant, ctx)


def test_citation_overlap_boosts_score() -> None:
    ctx = build_context(themes=["xai-finance"], keywords=[], known_external_ids=["W_known"], known_dois=[])
    no_overlap = _make_candidate("A", title="Generic paper on something", refs=["W_other"])
    with_overlap = _make_candidate("B", title="Generic paper on something", refs=["W_known"])
    assert score(with_overlap, ctx) > score(no_overlap, ctx)


# ─────────────────────────────────────────────────────────────
# Discovery loop
# ─────────────────────────────────────────────────────────────


@pytest.fixture
def isolated_brain(tmp_path, monkeypatch) -> None:
    """Redirect EVERY brain-write path into a temporary directory for the test run.

    Must cover both discovery.py's module-level path constants AND state.py's
    PAPERS_JSON_DIR (used by State.save_paper) - otherwise the JSON sidecars
    that discover() now writes inline will leak into the real brain.
    """
    fake_root = tmp_path
    fake_papers = fake_root / "literature" / "papers"
    (fake_root / "literature" / "state").mkdir(parents=True)
    fake_papers.mkdir(parents=True)
    # discovery.py constants
    monkeypatch.setattr("emerald_ai.research.discovery.AUTO_INDEX_PATH", fake_root / "literature" / "auto_index.yaml")
    monkeypatch.setattr("emerald_ai.research.discovery.DISCOVERY_SEEN_PATH", fake_root / "literature" / "state" / "discovery_seen.json")
    monkeypatch.setattr("emerald_ai.research.discovery.PAPERS_DIR", fake_papers)
    monkeypatch.setattr("emerald_ai.research.discovery.INDEX_PATH", fake_root / "literature" / "index.yaml")
    # state.py PAPERS_JSON_DIR (used by State.save_paper invoked from discover)
    monkeypatch.setattr("emerald_ai.research.state.PAPERS_JSON_DIR", fake_papers)
    return fake_root


def test_discovery_accepts_relevant_paper_and_recurses(isolated_brain) -> None:
    corpus = {
        "S1": _make_candidate(
            "S1",
            title="Explainable XGBoost credit scoring for green loans",
            refs=["R1", "R2"],
            abstract="Tabular gradient boosting with SHAP for credit risk in sustainable finance.",
            cited_by=300,
        ),
        "R1": _make_candidate(
            "R1",
            title="SHAP for interpretable credit risk models",
            abstract="A unified approach to explainable credit scoring using Shapley values.",
            cited_by=200,
        ),
        "R2": _make_candidate(
            "R2",
            title="Lighthouse architecture for offshore renewables",
            abstract="Marine engineering of fixed-platform lighthouses unrelated to credit.",
            cited_by=50,
        ),
    }
    source = _FakeSource(corpus)
    report = discover(source, ["S1"], config=DiscoveryConfig(max_depth=2, max_papers=5))

    accepted_keys = [k for k, _ in report.accepted]
    # The seed and the SHAP paper should be accepted; the lighthouse paper should be rejected.
    assert any("xgboost" in k or "explainable" in k for k in accepted_keys)
    rejected_ids = [r[0] for r in report.rejected]
    assert "R2" in rejected_ids


def test_discovery_is_idempotent_via_discovery_seen(isolated_brain) -> None:
    """A second run with the same seed produces zero new accepts."""
    corpus = {
        "S1": _make_candidate(
            "S1",
            title="Conformal prediction for credit scoring under distribution shift",
            abstract="Distribution-free uncertainty quantification for tabular credit models.",
            cited_by=120,
        ),
    }
    source = _FakeSource(corpus)
    r1 = discover(source, ["S1"], config=DiscoveryConfig(max_depth=0, max_papers=5))
    r2 = discover(source, ["S1"], config=DiscoveryConfig(max_depth=0, max_papers=5))
    assert len(r1.accepted) >= 1
    assert len(r2.accepted) == 0  # already seen


def test_openalex_to_candidate_tolerates_null_fields() -> None:
    """Regression: OpenAlex returns null for many optional fields (preprints, anonymised works).

    Without defensive handling, _to_candidate crashed with
    AttributeError: 'NoneType' object has no attribute 'get'
    on any work where primary_location.source was null (typical for arXiv preprints).
    """
    from emerald_ai.research.sources.openalex import OpenAlexSource

    work_with_nulls = {
        "id": "https://openalex.org/W1234567890",
        "doi": "https://doi.org/10.48550/arxiv.2401.00001",
        "title": "An arXiv preprint with no venue",
        "publication_year": 2024,
        "cited_by_count": None,                 # null
        "abstract_inverted_index": None,        # null
        "primary_location": {"source": None},   # source null - the original crash
        "authorships": [
            {"author": None},                                # null author object
            {"author": {"display_name": "Smith, A."}},
            None,                                            # null authorship entry
        ],
        "concepts": [
            {"display_name": "Credit scoring"},
            None,                                            # null concept
            {"display_name": None},                          # null name
        ],
        "referenced_works": None,                            # null list
    }
    candidate = OpenAlexSource._to_candidate(work_with_nulls)

    assert candidate.external_id == "W1234567890"
    assert candidate.doi == "10.48550/arxiv.2401.00001"
    assert candidate.title == "An arXiv preprint with no venue"
    assert candidate.year == 2024
    assert candidate.venue == ""                             # gracefully empty
    assert candidate.authors == ["Smith, A."]                # nulls filtered
    assert candidate.concepts == ["Credit scoring"]          # nulls filtered
    assert candidate.referenced_external_ids == []           # null list -> empty
    assert candidate.cited_by_count == 0                     # null -> 0


def test_openalex_to_candidate_with_missing_keys() -> None:
    """A near-empty payload should also normalise without crashing."""
    from emerald_ai.research.sources.openalex import OpenAlexSource

    minimal = {"id": "https://openalex.org/W9", "title": "Minimal work"}
    candidate = OpenAlexSource._to_candidate(minimal)
    assert candidate.external_id == "W9"
    assert candidate.title == "Minimal work"
    assert candidate.authors == []
    assert candidate.venue == ""


def test_discovery_saturation_stops_loop(isolated_brain) -> None:
    """A relevant seed surrounded by off-topic citations triggers saturation early-exit."""
    # 20 unrelated papers reachable from S1
    corpus = {f"X{i}": _make_candidate(f"X{i}", title=f"Marine biology study {i}") for i in range(20)}
    # Relevant seed so it accepts and enqueues the 20 off-topic refs
    corpus["S1"] = _make_candidate(
        "S1",
        title="Explainable XGBoost credit scoring for green loans with SHAP and conformal",
        abstract="Tabular gradient boosting for credit risk with SHAP explanations and calibration.",
        refs=[f"X{i}" for i in range(20)],
        cited_by=200,
    )
    source = _FakeSource(corpus)
    report = discover(
        source, ["S1"],
        config=DiscoveryConfig(
            max_depth=2, max_papers=50, threshold=0.5,
            relevance_for_recursion=0.5, saturation_window=4,
        ),
    )
    assert report.saturated is True, f"expected saturation, got {report}"
    # Should have stopped after the seed + ~4 saturation rejects, well before all 20 X's.
    assert report.candidates_seen <= 8
