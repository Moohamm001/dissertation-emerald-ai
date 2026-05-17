"""ResearchEngine: orchestrates the research-automation workflow.

Idempotent: re-running over an unchanged brain is a no-op except for the
manifest timestamp. Adding a new paper key to ``literature/index.yaml``
schedules it for analysis on the next run.
"""
from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path

import yaml

from emerald_ai.config import PATHS
from emerald_ai.research.schema import (
    AuthorRollup,
    Confidence,
    GraphEdge,
    PaperRecord,
    ProcessingStatus,
    ResearchQuestion,
    TermRollup,
)
from emerald_ai.research.state import State

INDEX_PATH = PATHS.literature / "index.yaml"
AUTO_INDEX_PATH = PATHS.literature / "auto_index.yaml"
PAPERS_MD_DIR = PATHS.literature / "papers"
THEMES_DIR = PATHS.literature / "themes"
GAPS_PATH = PATHS.literature / "gaps.md"

WIKI_LINK = re.compile(r"\[\[([a-zA-Z0-9_\-]+)\]\]")


def _load_index() -> list[dict]:
    """Merge the human-curated index with the bot-discovered auto_index.

    Manual entries take precedence on key collision so a human edit always wins
    over the bot's auto-generated record.
    """
    manual: list[dict] = []
    if INDEX_PATH.exists():
        manual = yaml.safe_load(INDEX_PATH.read_text(encoding="utf-8")) or []
    auto: list[dict] = []
    if AUTO_INDEX_PATH.exists():
        auto = yaml.safe_load(AUTO_INDEX_PATH.read_text(encoding="utf-8")) or []
    seen_keys = {e["key"] for e in manual}
    return manual + [e for e in auto if e.get("key") and e["key"] not in seen_keys]


def _extract_section(markdown: str, heading: str) -> str:
    """Return the body of a `## <heading>` section, until the next `##`.

    Tolerant of leading whitespace before ``##`` (some markdown writers indent),
    and matches the heading as a prefix so suffixes like ``(qualifier)`` are OK.
    """
    pattern = re.compile(
        rf"^[ \t]*##\s+{re.escape(heading)}\b.*?$(.+?)(?=^[ \t]*##\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    m = pattern.search(markdown)
    return m.group(1).strip() if m else ""


def _bullet_list(section: str) -> list[str]:
    items: list[str] = []
    for line in section.splitlines():
        line = line.strip()
        if line.startswith(("- ", "* ", "• ")):
            items.append(line[2:].strip())
    return items


class ResearchEngine:
    """Workflow steps 1-8 from research_automation.txt."""

    def __init__(self) -> None:
        self.state = State().load()

    # ---------- 1: read existing memory ----------
    def index_entries(self) -> list[dict]:
        return _load_index()

    # ---------- 2-4: ingest a paper ----------
    def ingest(self, entry: dict, *, force: bool = False) -> PaperRecord:
        """Build a PaperRecord from an index entry, parsing the existing .md if present.

        Rule 3 (idempotent): skipped if already processed unless force=True.
        """
        key: str = entry["key"]
        if not force and self.state.is_processed(key):
            existing = self.state.load_paper(key)
            if existing is not None:
                return existing

        md_path = PAPERS_MD_DIR / f"{key}.md"
        markdown = md_path.read_text(encoding="utf-8") if md_path.exists() else ""

        contributions = _bullet_list(_extract_section(markdown, "Key claims"))
        weaknesses = _bullet_list(_extract_section(markdown, "Limitations / counter-evidence"))
        emerald = _extract_section(markdown, "Relevance to EMERALD-AI") or _extract_section(
            markdown, "How EMERALD-AI uses this paper"
        )
        methodology = _extract_section(markdown, "Method (how the claim was established)") or _extract_section(
            markdown, "Method"
        )

        # references = wiki-links found in the body (excluding the paper's own key)
        refs = sorted({m for m in WIKI_LINK.findall(markdown) if m != key and "/" not in m})

        # confidence: derived from the index `verified` flag + presence of a paper file
        verified = bool(entry.get("verified", False))
        has_md = md_path.exists()
        if verified and has_md and contributions:
            confidence = Confidence.HIGH
        elif has_md:
            confidence = Confidence.MEDIUM
        else:
            confidence = Confidence.LOW

        status = ProcessingStatus.ANALYSED if has_md and contributions else (
            ProcessingStatus.INDEXED if has_md else ProcessingStatus.STUB
        )

        # parse "Author1, A. & Author2, B. (YEAR)" → institutions are usually absent in our brain
        record = PaperRecord(
            key=key,
            title=entry.get("title", ""),
            authors=list(entry.get("authors", []) or []),
            year=entry.get("year") if isinstance(entry.get("year"), int) else None,
            abstract="",  # not stored in the brain currently — left blank, low-confidence
            methodology=methodology,
            contributions=contributions,
            weaknesses=weaknesses,
            future_works=[],  # not stored explicitly in our markdown — flagged for future enrichment
            referenced_papers=refs,
            important_keywords=list(entry.get("themes", []) or []),
            venue=entry.get("venue", "") or "",
            doi=entry.get("doi"),
            themes=list(entry.get("themes", []) or []),
            relevance=entry.get("relevance", "medium") or "medium",
            emerald_relevance=emerald,
            confidence=confidence,
            verified=verified,
            status=status,
            search_query=entry.get("search_query", "") or "",
            notes=entry.get("notes", "") or "",
            source_files=[str(md_path.relative_to(PATHS.root))] if md_path.exists() else [],
        )

        self.state.save_paper(record)
        self.state.mark_processed(key, status)
        return record

    # ---------- 5: citation graph ----------
    def build_graph(self, records: Iterable[PaperRecord]) -> None:
        edges: list[GraphEdge] = []
        keys = {r.key for r in records}
        for r in records:
            for cited in r.referenced_papers:
                if cited in keys:
                    edges.append(GraphEdge(source=r.key, target=cited))
        # de-duplicate
        seen: set[tuple[str, str, str]] = set()
        unique: list[GraphEdge] = []
        for e in edges:
            sig = (e.source, e.target, e.relationship)
            if sig not in seen:
                seen.add(sig)
                unique.append(e)
        self.state.citations = unique

    # ---------- 6: rollups ----------
    def roll_up(self, records: Iterable[PaperRecord]) -> None:
        authors: dict[str, AuthorRollup] = {}
        institutions: dict[str, TermRollup] = {}
        methods: dict[str, TermRollup] = {}
        datasets: dict[str, TermRollup] = {}
        keywords: dict[str, TermRollup] = {}

        method_terms = {
            "xgboost", "lightgbm", "catboost", "random forest", "logistic regression", "svm",
            "treeshap", "kernelshap", "lime", "dice", "smote", "smote-nc", "adasyn",
            "focal loss", "platt scaling", "isotonic regression", "conformal prediction",
            "ft-transformer", "tabnet", "saint", "node", "mlp", "boruta", "optuna",
        }
        dataset_terms = {
            "compas", "german credit", "lending club", "kaggle", "uci", "fico",
            "adult", "higgs", "covertype", "kdd",
        }

        for r in records:
            for a in r.authors:
                roll = authors.setdefault(a, AuthorRollup(name=a))
                if r.key not in roll.paper_keys:
                    roll.paper_keys.append(r.key)
                for t in r.themes:
                    if t not in roll.themes:
                        roll.themes.append(t)

            for inst in r.institutions:
                roll_i = institutions.setdefault(inst, TermRollup(term=inst, kind="institution"))
                if r.key not in roll_i.paper_keys:
                    roll_i.paper_keys.append(r.key)

            haystack = " ".join([r.title, r.methodology, r.emerald_relevance, " ".join(r.contributions)]).lower()
            for term in method_terms:
                if term in haystack:
                    roll_m = methods.setdefault(term, TermRollup(term=term, kind="method"))
                    if r.key not in roll_m.paper_keys:
                        roll_m.paper_keys.append(r.key)
            for term in dataset_terms:
                if term in haystack:
                    roll_d = datasets.setdefault(term, TermRollup(term=term, kind="dataset"))
                    if r.key not in roll_d.paper_keys:
                        roll_d.paper_keys.append(r.key)

            for kw in r.important_keywords:
                roll_k = keywords.setdefault(kw, TermRollup(term=kw, kind="keyword"))
                if r.key not in roll_k.paper_keys:
                    roll_k.paper_keys.append(r.key)

        self.state.authors = authors
        self.state.institutions = institutions
        self.state.methods = methods
        self.state.datasets = datasets
        self.state.keywords = keywords

    # ---------- 7: questions from gaps ----------
    def generate_questions(self) -> None:
        """Generate one ResearchQuestion per G#/M# heading in gaps.md.

        Preserves the ``created`` timestamp of existing questions so re-running
        the engine over an unchanged gap log produces a clean git diff.
        """
        if not GAPS_PATH.exists():
            return
        existing_by_id = {q.id: q for q in self.state.questions}
        text = GAPS_PATH.read_text(encoding="utf-8")
        pattern = re.compile(r"^###\s+([GM]\d+)\.\s+(.+?)$", re.MULTILINE)
        questions: list[ResearchQuestion] = []
        for gap_id, headline in pattern.findall(text):
            qid = f"RQ-{gap_id}"
            new_question_text = f"Resolve {gap_id}: {headline.strip().rstrip('.')}"
            prior = existing_by_id.get(qid)
            if prior is not None and prior.question == new_question_text:
                # nothing changed for this RQ — keep the original record (preserving created)
                questions.append(prior)
            else:
                questions.append(
                    ResearchQuestion(
                        id=qid,
                        question=new_question_text,
                        source_gap=gap_id,
                        priority="high" if gap_id.startswith("G1") else "medium",
                    )
                )
        self.state.questions = questions

    # ---------- 8: run the full sweep ----------
    def run(self, *, force: bool = False) -> dict[str, int]:
        index = self.index_entries()
        records: list[PaperRecord] = [self.ingest(e, force=force) for e in index]
        self.build_graph(records)
        self.roll_up(records)
        self.generate_questions()
        self.state.save(papers_count=len(records))
        return {
            "total": len(records),
            "analysed": sum(1 for r in records if r.status == ProcessingStatus.ANALYSED.value),
            "indexed": sum(1 for r in records if r.status == ProcessingStatus.INDEXED.value),
            "stub": sum(1 for r in records if r.status == ProcessingStatus.STUB.value),
            "citations": len(self.state.citations),
            "questions": len(self.state.questions),
            "authors": len(self.state.authors),
            "methods": len(self.state.methods),
            "datasets": len(self.state.datasets),
        }
