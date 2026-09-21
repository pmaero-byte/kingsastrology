"""Tests for the source matrices (docs/18-source-matrices.md).

The one guarantee these tests enforce above all: every classified cell is
VERBATIM source text from the verse it cites — nothing invented. Plus the
structural invariants (grids complete, citations resolve, gaps declared not
silent) and byte-identical determinism of the build.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[1]
ROOT = BACKEND.parent
STORE_DIR = BACKEND / "data" / "verse_store"
MAT_DIR = BACKEND / "data" / "matrices"

MATRIX_NAMES = ["signs", "houses", "ascendants", "nakshatras", "planet_in_sign",
                "planet_in_house", "moon_sign_aspects", "moon_navamsa_aspects",
                "conjunctions", "house_lord_rules"]


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


@pytest.fixture(scope="module")
def verses() -> dict[tuple[int, int], list[str]]:
    vs = json.loads((STORE_DIR / "verses.json").read_text())
    out: dict[tuple[int, int], list[str]] = {}
    for v in vs:
        out.setdefault((v["chapter"], v["verse"]), []).append(v["translation_text"])
    return out


@pytest.fixture(scope="module")
def matrices() -> dict[str, dict]:
    return {name: json.loads((MAT_DIR / f"{name}.json").read_text())
            for name in MATRIX_NAMES}


@pytest.fixture(scope="module")
def manifest() -> dict:
    return json.loads((MAT_DIR / "manifest.json").read_text())


# --------------------------------------------------------------- structure

def test_all_matrix_files_present(matrices):
    assert set(matrices) == set(MATRIX_NAMES)


def test_manifest_counts_match_files(matrices, manifest):
    for name, m in matrices.items():
        cov = manifest["matrices"][name]
        n = len(m["cells"])
        assert cov["cells"] == n, f"{name}: manifest says {cov['cells']}, file has {n}"
        by = {"auto-draft": 0, "derived": 0, "draft": 0, "needs_review": 0, "gap": 0}
        for c in m["cells"]:
            by[c["status"]] += 1
        assert cov["gaps"] == by["gap"], name
        assert cov["needs_review"] == by["needs_review"], name
        assert cov["classified"] == by["auto-draft"] + by["derived"] + by["draft"], name


def test_grids_complete_and_unique(matrices):
    for name, m in matrices.items():
        if name == "house_lord_rules":
            continue  # a rule list, not a cross-grid
        rows, cols = m["axes"]["rows"], m["axes"]["columns"]
        seen = set()
        for c in m["cells"]:
            assert c["row"] in rows, f"{name}: unknown row {c['row']}"
            assert c["col"] in cols, f"{name}: unknown col {c['col']}"
            key = (c["row"], c["col"])
            assert key not in seen, f"{name}: duplicate cell {key}"
            seen.add(key)
        if name != "conjunctions":  # triangular pair list, 21 of 49
            assert len(seen) == len(rows) * len(cols), \
                f"{name}: {len(seen)} cells, expected {len(rows) * len(cols)}"


# --------------------------------------------------------------- citations

def test_every_citation_resolves(matrices, verses):
    for name, m in matrices.items():
        for c in m["cells"]:
            for cit in c.get("citations", []):
                key = (cit["chapter"], cit["verse"])
                assert key in verses, f"{name} {c['row']}x{c['col']}: dangling {key}"


def test_excerpts_are_verbatim_source(matrices, verses):
    """The source-fidelity guarantee: every excerpt is a whitespace-normalised
    substring of a record behind its citation (Jupiter's positional list cells
    carry 'prefix: item' — the item must appear)."""
    checked = 0
    for name, m in matrices.items():
        for c in m["cells"]:
            ex = c.get("excerpt")
            if not isinstance(ex, str) or not ex.strip():
                continue
            bodies = [_norm(b) for (ch, vv) in
                      [(x["chapter"], x["verse"]) for x in c.get("citations", [])]
                      for b in verses.get((ch, vv), [])]
            assert bodies, f"{name} {c['row']}x{c['col']}: no verse text behind citation"
            probe = _norm(ex)
            head = probe.split(": ", 1)[0]
            if ": " in probe and "occupying the" in head:
                probe = probe.split(": ", 1)[1]  # composed positional-list prefix
            ok = any(probe in b for b in bodies)
            assert ok, (f"{name} {c['row']}x{c['col']}: excerpt is not verbatim "
                        f"of its cited verse: {probe[:70]!r}")
            checked += 1
    assert checked > 300  # the guarantee covers essentially the whole dataset


def test_gap_cells_carry_no_doctrine(matrices):
    """A gap must be empty — no excerpt, no citation, just the honest note."""
    for name, m in matrices.items():
        for c in m["cells"]:
            if c["status"] == "gap":
                assert not c.get("excerpt"), f"{name}: gap cell {c['row']}x{c['col']} has text"
                assert not c.get("citations"), f"{name}: gap cell cites a verse"
                assert c.get("note"), f"{name}: gap cell without a note"


# --------------------------------------------------------------- known facts

def test_node_rows_are_declared_gaps(matrices):
    m = matrices["planet_in_sign"]
    for node in ("Rahu", "Ketu"):
        cells = [c for c in m["cells"] if c["row"] == node]
        assert len(cells) == 12
        assert all(c["status"] == "gap" for c in cells)


def test_seven_grahas_fully_placed_in_signs(matrices):
    m = matrices["planet_in_sign"]
    for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        cells = [c for c in m["cells"] if c["row"] == p]
        assert len(cells) == 12
        assert all(c["status"] == "auto-draft" for c in cells), \
            f"{p}: {[c['status'] for c in cells]}"


def test_planet_in_house_complete_with_source_references(matrices):
    m = matrices["planet_in_house"]
    for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        cells = [c for c in m["cells"] if c["row"] == p]
        assert len(cells) == 12
        assert all(c["status"] == "auto-draft" for c in cells), p
    composed = [c for c in m["cells"] if c.get("via_reference")]
    assert composed, "source-composed cells (via_reference) expected"
    for c in composed:
        # composed cells cite BOTH the composing verse and the referenced cell's verse
        assert len(c["citations"]) >= 2


def test_conjunctions_all_21_pairs(matrices):
    m = matrices["conjunctions"]
    assert len(m["cells"]) == 21
    assert all(c["status"] == "auto-draft" for c in m["cells"])


def test_nakshatras_27_with_honest_reviews(matrices):
    m = matrices["nakshatras"]
    assert len(m["cells"]) == 27
    review = [c for c in m["cells"] if c["status"] == "needs_review"]
    assert len(review) == 3  # Jyeshta, Uttarashadha, Dhanishta (OCR-dropped names)
    assert {c["col"] for c in review} == {"Jyeshta", "Uttarashadha", "Dhanishta"}


def test_ascendants_are_derived_not_invented(matrices):
    m = matrices["ascendants"]
    assert all(c["status"] == "derived" for c in m["cells"])
    for c in m["cells"]:
        assert "derivation" in c
        assert c["sign_qualities_ref"] and c["moon_sign_effects_ref"]
    # at least some lagna sub-cases from Ch 20 must have landed
    n_sub = sum(len(c.get("lagna_subcases", [])) for c in m["cells"])
    assert n_sub >= 6


def test_house_lord_rules_cited(matrices):
    m = matrices["house_lord_rules"]
    assert len(m["cells"]) >= 12
    for r in m["cells"]:
        assert r["citations"], f"{r['id']} without citation"
        assert r["classification"] in ("strength", "tend", "neutral", "table")


def test_chapter_map_exists_and_covers_27():
    cm = json.loads((STORE_DIR / "chapter_map.json").read_text())
    assert len(cm["chapters"]) == 27
    assert any("Upasamhara" in d or "Upasamharadhyaya" in d
               for d in cm["known_divergences"])
    assert any("misnumbered" in d for d in cm["known_divergences"])


# --------------------------------------------------------------- determinism

def test_rebuild_is_byte_identical(tmp_path):
    r = subprocess.run([sys.executable, str(BACKEND / "scripts" / "build_matrices.py"),
                        "--out", str(tmp_path)], capture_output=True, text=True, cwd=str(ROOT))
    assert r.returncode == 0, r.stderr[-500:]
    for f in sorted(MAT_DIR.glob("*.json")):
        h1 = hashlib.sha256(f.read_bytes()).hexdigest()
        f2 = tmp_path / f.name
        assert f2.exists(), f"{f.name} missing from rebuild"
        h2 = hashlib.sha256(f2.read_bytes()).hexdigest()
        assert h1 == h2, f"{f.name} differs on rebuild — the build is not deterministic"
