"""Autonomous discovery loop — the "bot" that grows the brain.

Implements rule 4-5 of ``research_automation.txt``:
    * Build connections between papers.
    * Traverse references recursively.
    * Detect saturation, stop early when discoveries thin out.

Algorithm (breadth-first):

    queue = seed_external_ids
    while queue and budget remaining:
        cand = queue.pop()
        if cand seen -> skip                    # rule 3: never reprocess
        meta = source.fetch(cand)
        score = relevance.score(meta, ctx)
        if score >= threshold:
            write papers/<key>.{md,json}, add to auto_index.yaml,
            enqueue meta.referenced_external_ids[:fanout]   # recursion
            saturation_streak = 0
        else:
            saturation_streak += 1
            if saturation_streak >= saturation_window:
                stop

Provenance:
    * Bot-discovered papers go into ``literature/auto_index.yaml`` (separate
      from the human-curated ``index.yaml``) so the manual brain stays clean.
    * Their markdown frontmatter carries ``auto_discovered: true`` and the
      source ID for traceability.

Persistence:
    * ``literature/state/discovery_seen.json`` records every external_id ever
      considered, with its score + outcome, so reruns skip them.
    * Raw API responses cached under ``literature/state/cache/openalex/``.
"""
from __future__ import annotations

import json
import re
from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import yaml
from rich.console import Console

from emerald_ai.config import PATHS
from emerald_ai.research.relevance import RelevanceContext, build_context, score as score_fn
from emerald_ai.research.sources.base import CandidatePaper, Source, SourceError

AUTO_INDEX_PATH = PATHS.literature / "auto_index.yaml"
DISCOVERY_SEEN_PATH = PATHS.literature / "state" / "discovery_seen.json"
PAPERS_DIR = PATHS.literature / "papers"
INDEX_PATH = PATHS.literature / "index.yaml"
# Note: all paths resolve via emerald_ai.config.PATHS.literature so they
# automatically follow the project layout (research/literature/...).

KEY_RE = re.compile(r"[^a-z0-9]+")

console = Console()


# ─────────────────────────────────────────────────────────────
# Persistence helpers
# ─────────────────────────────────────────────────────────────


def _load_seen() -> dict[str, dict]:
    if not DISCOVERY_SEEN_PATH.exists():
        return {}
    return json.loads(DISCOVERY_SEEN_PATH.read_text(encoding="utf-8"))


def _save_seen(seen: dict[str, dict]) -> None:
    DISCOVERY_SEEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(seen, indent=2, sort_keys=True) + "\n"
    if DISCOVERY_SEEN_PATH.exists() and DISCOVERY_SEEN_PATH.read_text(encoding="utf-8") == payload:
        return
    DISCOVERY_SEEN_PATH.write_text(payload, encoding="utf-8")


def _load_yaml_list(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return yaml.safe_load(path.read_text(encoding="utf-8")) or []


def _append_to_auto_index(entry: dict) -> None:
    entries = _load_yaml_list(AUTO_INDEX_PATH)
    if any(e.get("key") == entry["key"] for e in entries):
        return
    entries.append(entry)
    AUTO_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    AUTO_INDEX_PATH.write_text(yaml.safe_dump(entries, sort_keys=False, allow_unicode=True), encoding="utf-8")


def _slug(s: str) -> str:
    s = re.sub(r"\s+", "-", s.strip().lower())
    return KEY_RE.sub("-", s).strip("-")[:60]


def candidate_to_key(c: CandidatePaper) -> str:
    """Generate a stable filename-safe key from author + year + title."""
    first_author_surname = (c.authors[0].split(",")[0] if c.authors else "anon").lower()
    first_author_surname = KEY_RE.sub("", first_author_surname) or "anon"
    year = c.year or 0
    title_token = _slug(c.title.split(":")[0]).split("-")[0] or "untitled"
    return f"{first_author_surname}{year}{title_token}"


def _write_paper_markdown(record: CandidatePaper, key: str, relevance_score: float) -> None:
    PAPERS_DIR.mkdir(parents=True, exist_ok=True)
    md_path = PAPERS_DIR / f"{key}.md"
    if md_path.exists():
        return  # don't clobber human-edited notes
    body = (
        f"---\n"
        f"key: {key}\n"
        f'title: "{record.title.replace(chr(34), chr(39))}"\n'
        f"auto_discovered: true\n"
        f"auto_source: {record.source}\n"
        f"auto_external_id: {record.external_id}\n"
        f"auto_score: {relevance_score}\n"
        f"---\n\n"
        f"# {', '.join(record.authors[:3])}{' et al.' if len(record.authors) > 3 else ''} "
        f"({record.year}) — {record.title}\n\n"
        f"## Key claims\n_(auto-extracted from abstract; human review pending)_\n\n"
        f"> {record.abstract[:1200] + ('…' if len(record.abstract) > 1200 else '')}\n\n"
        f"## Method (how the claim was established)\n_(to be filled in)_\n\n"
        f"## Relevance to EMERALD-AI\n_(auto_score={relevance_score} — review and re-classify)_\n\n"
        f"## Quotable lines\n_(to be filled in)_\n\n"
        f"## Limitations / counter-evidence\n_(to be filled in)_\n\n"
        f"## How EMERALD-AI uses this paper\n_(to be filled in)_\n\n"
        f"## Related entries\n_(auto-generated from references at discovery time; "
        f"see auto_index.yaml for full reference list)_\n"
    )
    md_path.write_text(body, encoding="utf-8")


# ─────────────────────────────────────────────────────────────
# Discovery loop
# ─────────────────────────────────────────────────────────────


@dataclass
class DiscoveryConfig:
    """Tunable parameters for one discovery run."""

    max_depth: int = 2
    max_papers: int = 20
    fanout: int = 10
    threshold: float = 0.45
    saturation_window: int = 8
    relevance_for_recursion: float = 0.55


@dataclass
class DiscoveryReport:
    """Summary of a discovery run."""

    seeds_processed: int = 0
    candidates_seen: int = 0
    accepted: list[tuple[str, float]] = field(default_factory=list)
    rejected: list[tuple[str, float]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    saturated: bool = False
    depth_reached: int = 0


def discover(
    source: Source,
    seeds: list[str],
    *,
    config: DiscoveryConfig | None = None,
) -> DiscoveryReport:
    """Run one BFS discovery sweep, persisting acceptances and seen-records."""

    cfg = config or DiscoveryConfig()
    report = DiscoveryReport()
    seen = _load_seen()

    # build relevance context from the live brain
    manual = _load_yaml_list(INDEX_PATH)
    auto = _load_yaml_list(AUTO_INDEX_PATH)
    all_entries = manual + auto
    themes = sorted({t for e in all_entries for t in (e.get("themes") or [])})
    keywords = sorted({k for e in all_entries for k in (e.get("notes", "").split() or [])})
    known_external_ids = [e.get("openalex_id", "") for e in all_entries if e.get("openalex_id")]
    known_dois = [e.get("doi", "") for e in all_entries if e.get("doi")]
    ctx = build_context(themes, keywords, known_external_ids, known_dois)

    # BFS frontier: (depth, external_id)
    frontier: deque[tuple[int, str]] = deque()
    for s in seeds:
        frontier.append((0, s))
    saturation_streak = 0

    while frontier and len(report.accepted) < cfg.max_papers:
        depth, ext_id = frontier.popleft()
        if depth > cfg.max_depth:
            continue
        report.depth_reached = max(report.depth_reached, depth)
        if ext_id in seen:
            continue
        report.candidates_seen += 1
        try:
            candidate = source.fetch(ext_id)
        except SourceError as e:
            seen[ext_id] = {
                "source": source.name,
                "outcome": "error",
                "error": str(e)[:200],
                "seen_at": datetime.now(UTC).isoformat(timespec="seconds"),
            }
            report.errors.append(f"{ext_id}: {e}")
            continue

        s = score_fn(candidate, ctx)
        outcome_record = {
            "source": candidate.source,
            "doi": candidate.doi,
            "title": candidate.title[:200],
            "score": s,
            "depth": depth,
            "seen_at": datetime.now(UTC).isoformat(timespec="seconds"),
        }

        if s >= cfg.threshold:
            key = candidate_to_key(candidate)
            _write_paper_markdown(candidate, key, s)
            _append_to_auto_index(
                {
                    "key": key,
                    "authors": candidate.authors,
                    "year": candidate.year,
                    "title": candidate.title,
                    "venue": candidate.venue,
                    "doi": candidate.doi,
                    "themes": [],  # human/engine assigns later
                    "relevance": "medium",
                    "status": "auto-discovered",
                    "verified": False,
                    "paper_file": True,
                    "openalex_id": candidate.external_id if candidate.source == "openalex" else None,
                    "auto_discovered": True,
                    "auto_score": s,
                    "auto_depth": depth,
                    "notes": (candidate.abstract[:280] + "…") if len(candidate.abstract) > 280 else candidate.abstract,
                    "search_query": candidate.title,
                }
            )
            report.accepted.append((key, s))
            outcome_record["outcome"] = "accepted"
            outcome_record["key"] = key
            saturation_streak = 0
            console.print(
                f"  [green]+ ACCEPT[/green] depth={depth} score={s:.2f}  [cyan]{key}[/cyan]  {candidate.title[:80]}"
            )
            # only recurse from sufficiently relevant accepts
            if depth < cfg.max_depth and s >= cfg.relevance_for_recursion:
                for ref in candidate.referenced_external_ids[: cfg.fanout]:
                    if ref not in seen:
                        frontier.append((depth + 1, ref))
        else:
            report.rejected.append((ext_id, s))
            outcome_record["outcome"] = "rejected"
            saturation_streak += 1
            if saturation_streak >= cfg.saturation_window:
                report.saturated = True
                seen[ext_id] = outcome_record
                console.print(
                    f"  [yellow]saturated[/yellow] — {cfg.saturation_window} consecutive rejects, stopping"
                )
                break

        seen[ext_id] = outcome_record
        report.seeds_processed = report.seeds_processed if depth > 0 else report.seeds_processed + 1

    _save_seen(seen)
    return report


# ─────────────────────────────────────────────────────────────
# Seed selection helpers
# ─────────────────────────────────────────────────────────────


def seeds_from_index(*, only_with_openalex_id: bool = True, limit: int | None = None) -> list[str]:
    """Pull seed external IDs from the existing brain (manual + auto)."""
    entries = _load_yaml_list(INDEX_PATH) + _load_yaml_list(AUTO_INDEX_PATH)
    ids = [e.get("openalex_id") for e in entries if e.get("openalex_id")]
    if not only_with_openalex_id:
        # fall back to DOI-based seeds (caller must resolve via Source.fetch_by_doi)
        ids += [e.get("doi") for e in entries if e.get("doi") and not e.get("openalex_id")]
    ids = [i for i in ids if i]
    return ids[:limit] if limit else ids


def seeds_from_search(source: Source, queries: list[str], *, per_query: int = 5) -> list[str]:
    """Use a source's search to obtain seed external IDs from free-text queries."""
    seeds: list[str] = []
    for q in queries:
        try:
            for c in source.search(q, limit=per_query):
                if c.external_id and c.external_id not in seeds:
                    seeds.append(c.external_id)
        except SourceError:  # pragma: no cover
            continue
    return seeds
