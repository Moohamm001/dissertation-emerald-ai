"""OpenAlex API client — free, no API key, ~100k requests/day.

Politeness:
    * mailto= query parameter (and User-Agent) joins the OpenAlex "polite pool"
      which receives higher quotas and more stable latency.
    * 1 req/sec default rate limit (well under their 10 req/sec polite ceiling).
    * Exponential backoff on 429 / 5xx.
    * On-disk cache keyed by URL → JSON response, so re-running discovery is
      cheap and predictable.

Reference: https://docs.openalex.org/
"""
from __future__ import annotations

import json
import os
import time
from collections.abc import Iterable
from pathlib import Path

import requests

from emerald_ai.config import PATHS
from emerald_ai.research.sources.base import (
    CandidatePaper,
    Source,
    SourceError,
    reconstruct_abstract,
)

OPENALEX_BASE = "https://api.openalex.org"
CACHE_DIR = PATHS.literature / "state" / "cache" / "openalex"


def _safe_filename(url: str) -> str:
    """Map a URL to a deterministic, filesystem-safe cache filename."""
    import hashlib

    return hashlib.sha1(url.encode("utf-8")).hexdigest() + ".json"


class OpenAlexSource(Source):
    """OpenAlex client with on-disk caching + polite throttling."""

    name = "openalex"

    def __init__(
        self,
        mailto: str | None = None,
        *,
        min_interval_s: float = 1.0,
        cache_dir: Path | None = None,
        session: requests.Session | None = None,
        timeout_s: float = 20.0,
    ) -> None:
        self.mailto = mailto or os.environ.get("EMERALD_OPENALEX_MAILTO", "")
        self.min_interval_s = min_interval_s
        self.cache_dir = cache_dir or CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._session = session or requests.Session()
        self._session.headers["User-Agent"] = (
            f"emerald-ai-bot/0.1 (https://github.com/; mailto:{self.mailto or 'unset'})"
        )
        self._timeout = timeout_s
        self._last_request_at = 0.0

    # ---------- HTTP ----------
    def _get(self, path: str, params: dict[str, object] | None = None) -> dict:
        params = dict(params or {})
        if self.mailto and "mailto" not in params:
            params["mailto"] = self.mailto
        url = f"{OPENALEX_BASE}{path}"
        cache_key = url + "?" + "&".join(f"{k}={v}" for k, v in sorted(params.items()))
        cache_path = self.cache_dir / _safe_filename(cache_key)

        if cache_path.exists():
            return json.loads(cache_path.read_text(encoding="utf-8"))

        # politeness throttle
        wait = self.min_interval_s - (time.monotonic() - self._last_request_at)
        if wait > 0:
            time.sleep(wait)

        for attempt in range(4):
            try:
                response = self._session.get(url, params=params, timeout=self._timeout)
            except requests.RequestException as e:  # pragma: no cover (network errors)
                if attempt == 3:
                    raise SourceError(f"OpenAlex GET {url} failed: {e}") from e
                time.sleep(2**attempt)
                continue
            self._last_request_at = time.monotonic()

            if response.status_code == 429 or response.status_code >= 500:
                if attempt == 3:
                    raise SourceError(
                        f"OpenAlex {response.status_code} for {url}: {response.text[:200]}"
                    )
                time.sleep(2 ** (attempt + 1))
                continue
            if response.status_code == 404:
                cache_path.write_text(json.dumps({"_not_found": True}), encoding="utf-8")
                return {"_not_found": True}
            if not response.ok:
                raise SourceError(f"OpenAlex {response.status_code} for {url}: {response.text[:200]}")

            payload = response.json()
            cache_path.write_text(json.dumps(payload), encoding="utf-8")
            return payload

        raise SourceError(f"OpenAlex GET {url} exhausted retries")  # pragma: no cover

    # ---------- normalisation ----------
    @staticmethod
    def _to_candidate(work: dict) -> CandidatePaper:
        """Convert an OpenAlex /works JSON payload into a normalised CandidatePaper.

        Defensive against OpenAlex's frequent null-valued fields:
            - primary_location may be null (some works lack one)
            - primary_location.source may be null (preprints with no journal)
            - authorships[i].author may be null (anonymised works)
            - referenced_works may be missing on older records
        The ``(d.get(k) or {})`` pattern handles both "key missing" and
        "key present with value None" uniformly; ``d.get(k, {})`` does not.
        """
        if work.get("_not_found"):
            raise SourceError("Work not found")

        oa_id = (work.get("id") or "").rsplit("/", 1)[-1]
        doi = (work.get("doi") or "").removeprefix("https://doi.org/") or None

        # Venue: walk primary_location -> source -> display_name, tolerating nulls at each step.
        primary_location = work.get("primary_location") or {}
        source_obj = primary_location.get("source") or {}
        venue = source_obj.get("display_name") or ""

        # Authors: filter out null authorships and null author objects.
        authors: list[str] = []
        for a in work.get("authorships") or []:
            author_obj = (a or {}).get("author") or {}
            name = author_obj.get("display_name")
            if name:
                authors.append(name)

        # Concepts.
        concepts: list[str] = []
        for c in work.get("concepts") or []:
            name = (c or {}).get("display_name")
            if name:
                concepts.append(name)

        # Referenced works -> OpenAlex IDs.
        referenced_ids: list[str] = []
        for w in work.get("referenced_works") or []:
            if isinstance(w, str) and w:
                referenced_ids.append(w.rsplit("/", 1)[-1])

        return CandidatePaper(
            source="openalex",
            external_id=oa_id,
            doi=doi,
            title=work.get("title") or "",
            authors=authors,
            year=work.get("publication_year"),
            venue=venue,
            abstract=reconstruct_abstract(work.get("abstract_inverted_index")),
            concepts=concepts,
            referenced_external_ids=referenced_ids,
            cited_by_count=int(work.get("cited_by_count") or 0),
            external_ids={"openalex": oa_id, **({"doi": doi} if doi else {})},
        )

    # ---------- Source API ----------
    def fetch(self, external_id: str) -> CandidatePaper:
        work = self._get(f"/works/{external_id}")
        if work.get("_not_found"):
            raise SourceError(f"OpenAlex {external_id} not found")
        return self._to_candidate(work)

    def fetch_by_doi(self, doi: str) -> CandidatePaper | None:
        work = self._get(f"/works/doi:{doi}")
        if work.get("_not_found"):
            return None
        return self._to_candidate(work)

    def search(self, query: str, *, limit: int = 10) -> list[CandidatePaper]:
        payload = self._get("/works", params={"search": query, "per-page": limit})
        results = payload.get("results") or []
        return [self._to_candidate(w) for w in results]

    def references(self, external_id: str) -> Iterable[CandidatePaper]:
        # OpenAlex exposes referenced_works as a list of IDs; resolve each.
        work = self._get(f"/works/{external_id}")
        if work.get("_not_found"):
            return
        for ref_url in work.get("referenced_works") or []:
            ref_id = ref_url.rsplit("/", 1)[-1]
            try:
                yield self.fetch(ref_id)
            except SourceError:  # pragma: no cover — skip unresolvable refs
                continue
