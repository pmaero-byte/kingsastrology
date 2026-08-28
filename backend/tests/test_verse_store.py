"""M1 — Verse Store: the verse-indexed source text and the citation gate.

Covers: store manifest/chapter index, canonical verse lookups (incl. the
OCR-marker recovery cases), range/list resolution, first-occurrence
semantics for duplicated numbers, the /api/v1/verse endpoints, and the
citation-check gate over the loaded rule-base.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.services import verse_store


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(create_app())


# ------------------------------------------------------------------ service

def test_manifest_shape() -> None:
    m = verse_store.manifest()
    assert m["verse_count"] > 400
    assert m["chapter_count"] == 27
    assert m["verse_store_version"].startswith("2026")


def test_chapter_index_covers_all_chapters() -> None:
    chapters = {entry["chapter"] for entry in verse_store.chapter_index()}
    assert chapters == set(range(1, 28))


def test_canonical_verse_lookups() -> None:
    # Famous opening of Chapter I (zodiacal definitions).
    assert "May the Sun give us speech" in verse_store.verse(1, 1)["translation_text"]
    # Nisheka opening.
    assert "menses" in verse_store.verse(4, 1)["translation_text"].lower()
    # OCR-recovered markers: "B." for 8 in ch13, "S." for 5 in ch19,
    # "\ 6." in ch20, "23," in ch7, "' 7." in ch12.
    assert verse_store.verse(13, 8) is not None
    assert verse_store.verse(19, 5) is not None
    assert verse_store.verse(20, 6) is not None
    assert verse_store.verse(7, 23) is not None
    assert verse_store.verse(12, 7) is not None


def test_missing_verse_returns_none() -> None:
    assert verse_store.verse(4, 23) is None      # the book's ch4 ends at v22
    assert verse_store.verse(99, 1) is None
    assert verse_store.verse(1, 999) is None


def test_resolve_single_range_and_list() -> None:
    assert [v["verse"] for v in verse_store.resolve(7, "1-3")] == [1, 2, 3]
    assert [v["verse"] for v in verse_store.resolve(19, "1, 4")] == [1, 4]
    assert [v["verse"] for v in verse_store.resolve(7, "5, note")] == [5]
    assert verse_store.resolve(7, "") == []
    assert verse_store.resolve(7, "not-a-verse") == []


def test_resolve_uses_first_occurrence_for_duplicates() -> None:
    # ch9 renumbers its later sections; the canonical first occurrence is the
    # "benefic places" stanza, which is what rules citing Ch 9 cite.
    first = verse_store.resolve(9, "1")[0]
    assert "benefic places of the Sun" in first["translation_text"]


def test_uncertain_ledger_nonempty() -> None:
    entries = verse_store.uncertain()
    assert len(entries) > 0
    issues = {entry["issue"] for entry in entries}
    assert issues & {"ocr", "ambiguous", "truncated", "fragment"}


# ------------------------------------------------------------------- API

def test_verse_manifest_endpoint(client: TestClient) -> None:
    r = client.get("/api/v1/verse-store/manifest")
    assert r.status_code == 200
    body = r.json()
    assert body["chapter_count"] == 27
    assert "policy" in body


def test_verse_chapter_endpoint(client: TestClient) -> None:
    r = client.get("/api/v1/verse/17")
    assert r.status_code == 200
    body = r.json()
    assert body["title"] == "Moon in the Several Signs"
    assert body["verse_count"] > 5
    assert all(v["chapter"] == 17 for v in body["verses"])


def test_verse_lookup_endpoint(client: TestClient) -> None:
    r = client.get("/api/v1/verse/4/1")
    assert r.status_code == 200
    assert "menses" in r.json()["verses"][0]["translation_text"].lower()

    r = client.get("/api/v1/verse/7/1-2")
    assert r.status_code == 200
    assert [v["verse"] for v in r.json()["verses"]] == [1, 2]

    r = client.get("/api/v1/verse/99/1")
    assert r.status_code == 404

    r = client.get("/api/v1/verse/4/23")
    assert r.status_code == 404


def test_uncertain_endpoint(client: TestClient) -> None:
    r = client.get("/api/v1/verse-store/uncertain")
    assert r.status_code == 200
    assert r.json()["count"] > 0


# --------------------------------------------------- citation gate (build-time)

def test_citation_check_resolution_rate(client: TestClient) -> None:
    r = client.get("/api/v1/citation-check")
    assert r.status_code == 200
    body = r.json()
    assert body["citations_checked"] >= 300
    # M1 exit: >=95% of rule citations resolve to the verse store.
    assert body["resolution_rate"] >= 0.95


def test_citation_check_surfaces_known_gaps(client: TestClient) -> None:
    """The unresolved citations are a known, enumerated set — the gate exists
    to surface them, not to hide them. These are verse-store gaps awaiting
    re-extraction (the cited stanzas are missing from the store), not rules
    that may be frozen. If this list changes, a scholar must explain why."""
    r = client.get("/api/v1/citation-check")
    unresolved = sorted(
        (entry["rule_id"], entry["raw"])
        for entry in r.json()["unresolved_citations"]
    )
    assert unresolved == [
        ("R-18.Saturn.Aries", "Ch 18, v 17"),
        ("R-18.Saturn.Gemini", "Ch 18, v 17"),
        ("R-18.Saturn.Scorpio", "Ch 18, v 17"),
        ("R-18.Saturn.Virgo", "Ch 18, v 17"),
        ("R-8.18", "Ch 8, v 18"),
    ]


def test_reviewed_rules_frozen() -> None:
    """M3: the first scholar-reviewed rules are frozen — the composer's
    production gate must now count verified rules and serve readings."""
    from app.main import create_app
    from fastapi.testclient import TestClient

    client = TestClient(create_app())
    health = client.get("/health").json()
    assert health["total_rules"] >= 290
    rules = client.get("/rules?status=verified").json()
    assert len(rules) >= 19
    ids = {rule["id"] for rule in rules}
    for rid in ("R-20.1", "R-20.9", "R-18.Sun.Aquarius", "R-16.12", "R-12.1"):
        assert rid in ids, rid
    # R-20.10 was rejected by review: its effect over-claims Ch 20 v 11.
    assert "R-20.10" not in ids
