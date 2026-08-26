"""
Layer 2 — The Tribunal (Mahkama): the falsification ledger.

Loads the append-only ledger of verifications, limitations, retractions and
pre-registrations. The Tribunal is a first-class surface (a page and an API),
not a footnote: failures are published louder than successes.
"""
from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

LEDGER_VERSION = "tribunal-1.0.0"
VALID_TYPES = {"verification", "limitation", "retraction", "pre_registration"}


def _ledger_path() -> Path:
    configured = os.getenv("KINGS_TRIBUNAL_LEDGER")
    if configured:
        return Path(configured).expanduser().resolve()
    return Path(__file__).resolve().parents[2] / "data" / "tribunal" / "ledger.json"


@lru_cache(maxsize=1)
def _load_cached(path: str, mtime: float) -> dict:
    with open(path) as fh:
        return json.load(fh)


def ledger() -> dict:
    path = _ledger_path()
    data = _load_cached(str(path), path.stat().st_mtime)
    counts: dict[str, int] = {}
    for entry in data.get("entries", []):
        counts[entry.get("type", "unknown")] = counts.get(entry.get("type", "unknown"), 0) + 1
    return {
        "ledger_version": data.get("ledger_version"),
        "policy": data.get("policy"),
        "counts": counts,
        "entries": data.get("entries", []),
        "provenance": {"engine": LEDGER_VERSION, "source_file": str(path.name)},
    }
