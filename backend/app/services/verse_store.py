"""
Layer 0 — The Verse Store (M1): the verse-indexed Brihat Jataka source text.

This is the source-of-truth layer the whole product cites from. Built by
`scripts/ingest_verse_store.py` from the OCR layer of the source PDF
(sourcetext/...pdf); OCR-damaged or ambiguous verses are flagged in the
`uncertain` ledger and await Scholar Reviewer clearance (verse-indexer
guardrail: nothing is silently corrected).

Records: {chapter, verse, sanskrit_ref, translation_text, keywords[],
          pages[], notes?, flags[]?}
"""
from __future__ import annotations

import json
import os
import re
from functools import lru_cache
from pathlib import Path

STORE_VERSION = "2026.08.29"
STORE_DIR_NAME = "verse_store"

_VERSION_RE = re.compile(r"^\s*(\d+)")


def _store_dir() -> Path:
    configured = os.getenv("KINGS_VERSE_STORE_DIR")
    if configured:
        return Path(configured).expanduser().resolve()
    return Path(__file__).resolve().parents[2] / "data" / STORE_DIR_NAME


@lru_cache(maxsize=1)
def _load_json(path: str, mtime: float) -> list | dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _read(name: str) -> list | dict:
    path = _store_dir() / name
    return _load_json(str(path), path.stat().st_mtime)


def _verses() -> list[dict]:
    return _read("verses.json")  # type: ignore[return-value]


def _manifest() -> dict:
    return _read("manifest.json")  # type: ignore[return-value]


def manifest() -> dict:
    return dict(_manifest())


def version() -> str:
    return str(_manifest().get("verse_store_version", STORE_VERSION))


def chapter_index() -> list[dict]:
    return _read("chapters.json")  # type: ignore[return-value]


def uncertain() -> list[dict]:
    return _read("uncertain.json")  # type: ignore[return-value]


def verse(chapter: int, verse_no: int) -> dict | None:
    """First record for (chapter, verse). Duplicate numbers (the translation
    restarts numbering for later sections) resolve to the first occurrence,
    which is the canonical stanza for citation purposes."""
    for record in _verses():
        if record["chapter"] == chapter and record["verse"] == verse_no:
            return record
    return None


def verses_for_chapter(chapter: int) -> list[dict]:
    return [record for record in _verses() if record["chapter"] == chapter]


def resolve(chapter: int, verse_expr: str) -> list[dict]:
    """Resolve a citation verse expression ("5", "1-3", "1, 4", "5, note")
    to verse records. Unresolvable numbers return no records."""
    expr = verse_expr.strip()
    numbers: list[int] = []
    for part in expr.split(","):
        part = part.strip()
        if not part:
            continue
        range_match = re.match(r"^(\d+)\s*-\s*(\d+)$", part)
        if range_match:
            start, end = sorted((int(range_match.group(1)), int(range_match.group(2))))
            numbers.extend(range(start, end + 1))
            continue
        num_match = _VERSION_RE.match(part)
        if num_match:
            numbers.append(int(num_match.group(1)))
    if not numbers:
        return []
    by_number: dict[int, dict] = {}
    for record in verses_for_chapter(chapter):   # first occurrence wins
        by_number.setdefault(record["verse"], record)
    return [by_number[n] for n in numbers if n in by_number]


def stats() -> dict:
    verses = _verses()
    by_chapter: dict[int, int] = {}
    for record in verses:
        by_chapter[record["chapter"]] = by_chapter.get(record["chapter"], 0) + 1
    return {
        "verse_store_version": version(),
        "chapter_count": len(by_chapter),
        "verse_count": len(verses),
        "verses_by_chapter": by_chapter,
        "uncertain_count": len(uncertain()),
    }
