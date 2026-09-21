"""Tests for the practitioner-lore corpus and its Laya classification (docs/19).

The core guarantees: every entry is sourced; the corpus is FIREWALLED from the
verse store (no doctrinal citations ever); statuses follow the docs/17 ladder;
and the classical-agreement check is deterministic and reviewable.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[1]
LORE_DIR = BACKEND / "data" / "practitioner_lore"

VALID_KINDS = {"mantra", "charity", "gemstone", "behavioral", "ritual",
               "worship", "technique", "caution"}
VALID_STATUSES = {"auto-draft", "scholar-assist", "escalated"}
VALID_VERDICTS = {"consistent", "partial", "contradicts", "no-basis"}


@pytest.fixture(scope="module")
def corpus() -> list[dict]:
    lines = (LORE_DIR / "corpus.jsonl").read_text().splitlines()
    return [json.loads(l) for l in lines if l.strip()]


@pytest.fixture(scope="module")
def classified() -> dict:
    return json.loads((LORE_DIR / "classified.json").read_text())


@pytest.fixture(scope="module")
def manifest() -> dict:
    return json.loads((LORE_DIR / "manifest.json").read_text())


def test_corpus_is_sourced(corpus):
    assert len(corpus) >= 50
    ids = set()
    for e in corpus:
        assert e["id"] not in ids, "duplicate lore id"
        ids.add(e["id"])
        assert e["text"].strip()
        src = e["source"]
        assert src["site"] and src["url"].startswith("http")
        assert src["kind"] in {"forum-consensus", "astrologer-site", "media-astrology",
                               "remedy-compilation", "remedy-portal", "astrologer-consensus"}
        assert e["source_confidence"] in {"high", "medium", "low"}


def test_forum_consensus_entries_are_flagged_low_confidence(corpus):
    """Entries whose thread URL could not be retained must say so honestly."""
    for e in corpus:
        if e["source"]["kind"] == "forum-consensus":
            assert e["source_confidence"] == "low"


def test_classification_covers_every_entry(corpus, classified):
    entries = classified["entries"]
    assert len(entries) == len(corpus)
    assert {e["id"] for e in entries} == {e["id"] for e in corpus}


def test_statuses_and_kinds_are_valid(classified):
    for e in classified["entries"]:
        cl = e["classification"]
        assert cl["kind"] in VALID_KINDS, e["id"]
        assert cl["status"] in VALID_STATUSES, e["id"]
        assert cl["kind_status"] in VALID_STATUSES, e["id"]
        assert cl["classical_agreement"]["verdict"] in VALID_VERDICTS, e["id"]
        for g in cl["grahas"]:
            assert g["graha"] in {"Surya", "Chandra", "Mangala", "Budha", "Guru",
                                  "Shukra", "Shani", "Rahu", "Ketu", "general"}


def test_ethics_flags_force_human_review(classified):
    for e in classified["entries"]:
        cl = e["classification"]
        if cl["ethics"]["flag"]:
            assert cl["status"] == "scholar-assist", \
                f"{e['id']}: ethics-flagged entry must not be auto-drafted"


def test_firewall_no_doctrinal_citations(classified):
    """Practitioner lore must never carry verse citations — it is living
    tradition, not Brihat Jataka doctrine."""
    for e in classified["entries"]:
        assert "citations" not in e, e["id"]
        assert "chapter" not in json.dumps(e).lower() or "classical_agreement" in json.dumps(e)


def test_manifest_records_engine_and_firewall(manifest):
    assert manifest["engine"] in {"convaiinnovations/laya", "fallback-lexicon-v1"}
    assert "firewall" in manifest
    assert manifest["counts"]["entries"] >= 50
    assert sum(manifest["by_kind"].values()) == manifest["counts"]["entries"]


def test_rebuild_is_deterministic(tmp_path):
    r = subprocess.run([sys.executable, str(BACKEND / "scripts" / "classify_lore_laya.py"),
                        "--out", str(tmp_path)], capture_output=True, text=True,
                       cwd=str(BACKEND.parent))
    assert r.returncode == 0, r.stderr[-400:]
    for name in ("classified.json", "manifest.json"):
        assert (tmp_path / name).read_bytes() == (LORE_DIR / name).read_bytes(), \
            f"{name} differs on rebuild — the classification is not deterministic"
