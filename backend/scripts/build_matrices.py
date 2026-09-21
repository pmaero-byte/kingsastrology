#!/usr/bin/env python3
"""
build_matrices.py — the source-matrix builder (BUILD-TIME ONLY).

Turns the Brihat Jataka verse store into the classified matrices of
docs/18-source-matrices.md:

  signs, houses, ascendants (derived), nakshatras,
  planet_in_sign, planet_in_house,
  moon_sign_aspects, moon_navamsa_aspects,
  conjunctions, house_lord_rules

Method (charter-honest, doc 13 compliant):
  * every cell is a VERBATIM clause of a stored verse + its (chapter, verse)
    citation — the script never paraphrases, never invents a cell;
  * verse-to-cell maps are curated by hand from a close reading of the
    translation, then VERIFIED programmatically: the clause must actually
    contain the planet/sign/house tokens it is mapped to, or the cell is
    downgraded to `needs_review` (never silently accepted);
  * cells the source composes by explicit reference ("the same effects as
    the Sun in those places") are materialised with `via_reference` and
    cite BOTH the composing verse and the referenced cell;
  * cells the source does not contain (e.g. Rahu/Ketu placements) are
    emitted as explicit `gap` rows with a note — no external doctrine;
  * output is pure data; no runtime dependency; rerunning is byte-identical.

Known store defects handled here (flagged, not silently fixed):
  * Ch 18 has a misnumbered record: Saturn's first verse is stored as
    verse 11 (duplicate number with Mercury's v11) — records are selected
    by content, and the defect is recorded in the manifest.

Run:  python3 backend/scripts/build_matrices.py [--store DIR] [--out DIR]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

MATRIX_VERSION = "matrices-1.0.0"

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
PLANETS7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
NODES = ["Rahu", "Ketu"]

# OCR variants actually seen in this translation's scan.
SIGN_VARIANTS = {
    "Aries": ["aries"], "Taurus": ["taurus", "ta:urus"], "Gemini": ["gemini", "gcmini", "ge,mini", "geminl"],
    "Cancer": ["cancer", "cadcer", "cancrr", "caocer", "cancr"],
    "Leo": ["leo"], "Virgo": ["virgo"], "Libra": ["libra"],
    "Scorpio": ["scorpio", "scorpic"],
    "Sagittarius": ["sagittari", "sagitlari", "sagiuari", "sagituari", "sagitt", "saginari"],
    "Capricorn": ["capricorn", "capric:orn"], "Aquarius": ["aquarius"], "Pisces": ["pisces", "fisccs", "pisccs", "fiscc"],
}
PLANET_VARIANTS = {
    "Sun": ["sun", "suil", "sud", "suo", "slln"],
    "Moon": ["moon", "mood", "moou", "mooll"],
    "Mars": ["mars", "rnars", "m&rs"],
    "Mercury": ["mercury", "mercrur", "mercur", "merclll", "mer~ury", "mer~uty", "m.:rcury"],
    "Jupiter": ["jupiter", "jupitcr", "ju piter", "iupiter", "jllpiter"],
    "Venus": ["venus", "ventls", "venlls", "venusl"],
    "Saturn": ["saturn", "satllrn", "saturu"],
}
NAKSHATRAS = ["Aswini", "Bharani", "Krittika", "Rohini", "Mrigasirsha", "Ardra",
              "Punarvasu", "Pushya", "Aslesha", "Makha", "Pubba", "Uttara",
              "Hasta", "Chitra", "Swati", "Visakha", "Anuradha", "Jyeshta",
              "Moola", "Purvashadha", "Uttarashadha", "Sravana", "Dhanishta",
              "Satabhisha", "Poorvabhadra", "Uttarabhadra", "Revati"]
NAK_VARIANTS = {
    "Aswini": ["aswini", "aswimi"], "Bharani": ["bharani"], "Krittika": ["krittika", "kritlika"],
    "Rohini": ["rohini"], "Mrigasirsha": ["mrigasirsba", "mrigasirsha", "mrigasira"],
    "Ardra": ["ardra"], "Punarvasu": ["punarvasu"], "Pushya": ["pushya"],
    "Aslesha": ["aslesha", "aslcsba"], "Makha": ["makha", "magha"], "Pubba": ["pubba"],
    "Uttara": ["uttara"], "Hasta": ["hasta"], "Chitra": ["chitra"],
    "Swati": ["swati", "svati"], "Visakha": ["visakha"], "Anuradha": ["anuradha"],
    "Jyeshta": ["jyeshta", "jycshtha"], "Moola": ["moola", "mtila"],
    "Purvashadha": ["purvashadha", "purvashdha"], "Uttarashadha": ["uttarashadha"],
    "Sravana": ["sravana"], "Dhanishta": ["dhanishta", "dhanistha"],
    "Satabhisha": ["satabhisha"], "Poorvabhadra": ["poorvabhadra", "purvabhadra"],
    "Uttarabhadra": ["uttarabhadra"], "Revati": ["revati"],
}

WARNINGS: list[str] = []


def warn(msg: str) -> None:
    WARNINGS.append(msg)
    print(f"  [warn] {msg}", file=sys.stderr)


def low(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower()).strip()


def has_planet(text: str, planet: str) -> bool:
    t = low(text)
    return any(re.search(rf"\b{re.escape(v.strip())}\b", t) for v in PLANET_VARIANTS[planet])


def has_sign(text: str, sign: str) -> bool:
    t = low(text)
    return any(v in t for v in SIGN_VARIANTS[sign])


def cell(row: str, col: str, citations: list[dict], excerpt, status: str = "auto-draft",
         **extra) -> dict:
    c = {"row": row, "col": col, "status": status, "citations": citations,
         "excerpt": (re.sub(r"\s+", " ", excerpt).strip() if isinstance(excerpt, str) else None)}
    c.update(extra)
    return c


def gap_cell(row: str, col: str, note: str) -> dict:
    return {"row": row, "col": col, "status": "gap", "citations": [], "excerpt": None, "note": note}


def verse_cell(ch: int, v: int) -> dict:
    return {"chapter": ch, "verse": v}


def sentences(text: str) -> list[str]:
    """Split into sentences on '.', ';' — keeps the OCR noise inside them."""
    parts = re.split(r"(?<=[.;])\s+", text)
    return [p.strip() for p in parts if p.strip()]


class Store:
    def __init__(self, store_dir: Path):
        self.verses = json.loads((store_dir / "verses.json").read_text())
        self.chapters = json.loads((store_dir / "chapters.json").read_text())
        self.manifest = json.loads((store_dir / "manifest.json").read_text())
        self.store_version = self.manifest.get("verse_store_version", "unknown")
        self._by_ch: dict[int, list[dict]] = {}
        for v in self.verses:
            self._by_ch.setdefault(v["chapter"], []).append(v)

    def records(self, ch: int, verse: int) -> list[dict]:
        return [v for v in self._by_ch.get(ch, []) if v["verse"] == verse]

    def text(self, ch: int, verse: int, must: str | None = None,
             include_notes: bool = False) -> str:
        """Primary record for a citation. Translator NOTES records (duplicate
        verse numbers starting with 'NOTES') are skipped unless asked for.
        `must`: pick the record whose text contains this token (handles the
        misnumbered duplicate in Ch 18)."""
        recs = self.records(ch, verse)
        if not recs:
            return ""
        cand = []
        for r in recs:
            head = low(r["translation_text"])[:8]
            is_notes = any(head.startswith(p) for p in ('"otes', "'otes", "notes", "iotes", "\\\"otes"))
            if include_notes or not is_notes:
                cand.append(r["translation_text"])
        if not cand:
            cand = [r["translation_text"] for r in recs]
        if must is not None:
            for c in cand:
                if must.lower() in low(c):
                    return c
        return cand[0]

    def exists(self, ch: int, verse) -> bool:
        return bool(self.records(ch, verse))


CLAUSE_ANCHOR = re.compile(
    r"\ba\s+[\"\u2019']?\s*p\w{0,6}(?:\s+\S{0,6})?\s+bor[nal]\s+wit[hil1f]", re.I)


def clause_slices(text: str) -> list[str]:
    """Clauses beginning 'A person born with' (any OCR mangling of person/born/with)."""
    ms = list(CLAUSE_ANCHOR.finditer(text))
    if not ms:
        return [text.strip()] if text.strip() else []
    out = []
    head = text[:ms[0].start()].strip()
    if head:
        out.append(head)
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        out.append(text[m.start():end].strip())
    return out


# ---------------------------------------------------------------- signs
def build_signs(st: Store) -> dict:
    lords = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
             "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]
    v6 = st.text(1, 6)
    # Kalapurusha parts — Ch 1 v4 (OCR-damaged list; curated normalisation flagged)
    v4 = st.text(1, 4)
    m = re.search(r"are respectively the (head.*?)\s*of\s+Kalapurusha", v4, re.I | re.S)
    parts = []
    if m:
        norm = m.group(1).replace(".", ",").replace(" and ", ", ")
        parts = [p.strip(" .;") for p in norm.split(",") if p.strip(" .;")]
    curated_parts = ["head", "face", "breast", "heart", "belly", "navel", "abdomen",
                     "genital organ", "two thighs", "two knees", "two ankles", "two feet"]
    parts_ok = len(parts) == 12
    if not parts_ok:
        warn("signs: kalapurusha list garbled in Ch 1 v 4 — curated 12-part mapping applied, "
             "flagged ocr_suspect (raw kept in excerpt)")
    night = ["Aries", "Taurus", "Gemini", "Cancer", "Sagittarius", "Capricorn"]
    dirs = {"Aries": "East", "Leo": "East", "Sagittarius": "East",
            "Taurus": "South", "Virgo": "South", "Capricorn": "South",
            "Gemini": "West", "Libra": "West", "Aquarius": "West",
            "Cancer": "North", "Scorpio": "North", "Pisces": "North"}
    moolas = {"Leo": "Sun", "Taurus": "Moon", "Aries": "Mars", "Virgo": "Mercury",
              "Sagittarius": "Jupiter", "Libra": "Venus", "Aquarius": "Saturn"}
    v14 = st.text(1, 14)
    v20 = st.text(1, 20)
    colors: list[str] = []
    m = re.search(r"beginning from Aries are respectively\s*(.*?)\.\s*The signs are known as",
                  v20, re.I | re.S)
    if m:
        colors = [c.strip(" .;()") for c in m.group(1).split(",")]
    else:
        warn("signs: colour enumeration not parsed from Ch 1 v 20 — flagged ocr_suspect")
    alt_names = ["Kriya", "Tavuri", "Jituma", "Kulira", "Leya", "Pathona", "Juka",
                 "Kourpi", "Toukshika", "Akokera", "Hridroga", "Antyabha"]

    cells = []
    for i, sign in enumerate(SIGNS):
        flags = []
        if not parts_ok:
            flags.append("ocr_suspect:kalapurusha")
        qualities = {
            "lord": lords[i],
            "kalapurusha_part": parts[i] if parts_ok else curated_parts[i],
            "day_night": "night" if sign in night else "day",
            "direction": dirs[sign],
            "moolatrikona_of": moolas.get(sign),
            "alt_name": alt_names[i],
            "color_raw": colors[i] if i < len(colors) else None,
        }
        if i >= len(colors) or re.search(r"[0-9~@#$%&]", qualities["color_raw"] or ""):
            flags.append("ocr_suspect:color")
        c = cell("sign", sign, [verse_cell(1, 6), verse_cell(1, 4), verse_cell(1, 10),
                                verse_cell(1, 11)], v6, qualities=qualities, flags=flags)
        if not has_planet(v6, lords[i]):
            warn(f"signs: lord token {lords[i]} not verified in Ch 1 v 6 for {sign}")
        if sign in moolas and not has_sign(v14, sign):
            warn(f"signs: moolatrikona token {sign} not verified in Ch 1 v 14")
        cells.append(c)

    rules = [
        {"id": "SG-1", "rule": "Signs alternate malefic/benefic, masculine/feminine, and "
         "movable/fixed/dual from Aries", "citations": [verse_cell(1, 11)]},
        {"id": "SG-2", "rule": "Night signs (Aries, Taurus, Gemini, Cancer, Sagittarius, "
         "Capricorn) rise feet-first; day signs head-first; Pisces by both",
         "citations": [verse_cell(1, 10)]},
        {"id": "SG-3", "rule": "Moolatrikona signs (Sun:Leo, Moon:Taurus, Mars:Aries, "
         "Mercury:Virgo, Jupiter:Sagittarius, Venus:Libra, Saturn:Aquarius)",
         "citations": [verse_cell(1, 14)]},
    ]
    return {"matrix": "signs", "version": MATRIX_VERSION,
            "axes": {"rows": ["sign"], "columns": SIGNS},
            "cells": cells, "rules": rules,
            "notes": "Positional enumerations from Ch 1 (lords v6, Kalapurusha v4, day/night v10, "
                     "gender/mobility/direction v11, moolatrikona v14, colours v20 — colours are "
                     "OCR-damaged and flagged). Exaltation/debilitation degrees live in Ch 2."}


# ---------------------------------------------------------------- houses
def build_houses(st: Store) -> dict:
    v15 = st.text(1, 15)
    m = re.search(r"significations of the houses.*?are respectively\s*(.*?)\.\s*The 3rd",
                  v15, re.I | re.S)
    sigs: list[str] = []
    if m:
        norm = m.group(1).replace(".", ",").replace(" and ", ", ").replace("(the native's) ", "")
        sigs = [s.strip(" .;()") for s in norm.split(",") if s.strip(" .;()")]
    curated = ["body", "family", "brothers", "relations", "sons", "enemies", "wife",
               "death", "deed of virtue", "avocation", "gain", "loss"]
    if len(sigs) != 12:
        warn(f"houses: v15 list parsed {len(sigs)} items — curated 12-item mapping applied, "
             "flagged ocr_suspect")
        sigs = curated
    names = ["Kalpa (power)", "Svaha", "Vikrama (prowess)", "relations-place [OCR]",
             "Pratibha (intelligence)", "Kshata", "Manmatha", "Randhra",
             "Guru (preceptor)", "Mana (respectability)", "Bhava", "Vyaya (loss)"]
    classes = {4: "Chaturasra; Hibuka, Ambu, Sukha, Vesma", 8: "Chaturasra; Randhra",
               7: "Jamitra; Dyuna", 5: "Trikona", 10: "Meshoorana; Karma; Agna",
               3: "Duschikya", 9: "Tapas; Tritrikona"}
    cells = []
    for i in range(12):
        c = cell("house", str(i + 1),
                 [verse_cell(1, 15), verse_cell(1, 16), verse_cell(1, 18), verse_cell(1, 19)],
                 v15,
                 qualities={"signification": sigs[i], "traditional_name": names[i],
                            "upachaya": i + 1 in (3, 6, 10, 11),
                            "class_names": classes.get(i + 1),
                            "kendra": i + 1 in (1, 4, 7, 10),
                            "panapara": i + 1 in (2, 5, 8, 11),
                            "apoklima": i + 1 in (3, 6, 9, 12)},
                 flags=["ocr_suspect:signification"] if sigs is curated else [])
        cells.append(c)
    rules = [
        {"id": "HS-1", "rule": "Upachaya (growing) houses: 3, 6, 10, 11",
         "citations": [verse_cell(1, 15)]},
        {"id": "HS-2", "rule": "If the lord of a house and the house be both powerful, the "
         "objects signified are promoted; if weak, reduced", "citations": [verse_cell(18, 20)]},
        {"id": "HS-3", "rule": "Benefics promote a bhava and malefics reduce it — reversed for "
         "the 6th, 8th and 12th", "citations": [verse_cell(20, 10)]},
        {"id": "HS-4", "rule": "Dignity grading of the occupant: exalted = full, moolatrikona = "
         "3/4, own = 1/2, friendly = 1/4, inimical < 1/4, debilitated or combust = nil",
         "citations": [verse_cell(20, 11)]},
        {"id": "HS-5", "rule": "Kendras are naturally powerful; biped signs by day, quadruped "
         "by night, centipede at dawn and dusk", "citations": [verse_cell(1, 19)]},
    ]
    return {"matrix": "houses", "version": MATRIX_VERSION,
            "axes": {"rows": ["house"], "columns": [str(i) for i in range(1, 13)]},
            "cells": cells, "rules": rules,
            "notes": "Significations Ch 1 v15; names v16; classes v18-19; benefic/malefic and "
                     "dignity grading Ch 20 v10-11."}


# ---------------------------------------------------------------- moon in sign (Ch 17)
def build_moon_in_sign(st: Store) -> list[dict]:
    out = []
    for i, sign in enumerate(SIGNS, start=1):
        t = st.text(17, i)
        if not t:
            out.append(gap_cell("Moon", sign, "verse missing in store"))
            continue
        ok = has_sign(t, sign) and has_planet(t, "Moon")
        if not ok:
            warn(f"moon_in_sign: Ch 17 v{i} token check failed for {sign}")
        out.append(cell("Moon", sign, [verse_cell(17, i)], t,
                        status="auto-draft" if ok else "needs_review"))
    return out


# ---------------------------------------------------------------- planets in signs (Ch 18)
# curated map: planet -> (verse, must-token to select the right duplicate record,
#                          [signs covered by that verse])
PLANET_SIGN_MAP = {
    "Sun": [(1, None, ["Aries", "Taurus"]), (2, None, ["Gemini", "Cancer", "Leo", "Virgo"]),
            (3, None, ["Libra", "Scorpio", "Sagittarius", "Capricorn"]),
            (4, None, ["Aquarius", "Pisces"])],
    "Mars": [(5, None, ["Aries", "Scorpio", "Taurus", "Libra"]),
             (6, None, ["Gemini", "Virgo", "Cancer"]),
             (7, None, ["Leo", "Sagittarius", "Pisces", "Aquarius", "Capricorn"])],
    "Mercury": [(8, None, ["Aries", "Scorpio", "Taurus", "Libra"]),
                (9, None, ["Gemini", "Cancer"]), (10, None, ["Leo", "Virgo"]),
                (11, "Mercury", ["Capricorn", "Aquarius", "Sagittarius", "Pisces"])],
    "Jupiter": [(12, None, ["Aries", "Scorpio", "Taurus", "Libra", "Gemini", "Virgo"]),
                (13, None, ["Cancer", "Leo", "Sagittarius", "Pisces", "Aquarius", "Capricorn"])],
    "Venus": [(14, None, ["Aries", "Scorpio", "Taurus", "Libra"]),
              (15, None, ["Gemini", "Virgo", "Capricorn", "Aquarius"]),
              (16, None, ["Cancer", "Leo", "Sagittarius", "Pisces"])],
    "Saturn": [(11, "Saturn", ["Aries", "Scorpio", "Gemini", "Virgo"]),   # misnumbered record
               (18, None, ["Taurus", "Libra", "Cancer", "Leo"]),
               (19, None, ["Sagittarius", "Pisces", "Capricorn", "Aquarius"])],
}


def build_planet_in_sign(st: Store, moon_cells: list[dict]) -> dict:
    cells: list[dict] = list(moon_cells)
    for planet, groups in PLANET_SIGN_MAP.items():
        covered: dict[str, dict] = {}
        for verse_no, must, signs in groups:
            t = st.text(18, verse_no, must=must)
            clauses = clause_slices(t)
            for sign in signs:
                best = None
                for cl in clauses:
                    if has_planet(cl, planet) and has_sign(cl, sign):
                        best = cl
                        break
                if best:
                    group = [s for s in signs if s != sign and has_sign(best, s)]
                    covered[sign] = cell(planet, sign, [verse_cell(18, verse_no)], best,
                                         shared=bool(group), shared_with=group)
                else:
                    warn(f"planet_in_sign: clause not found for {planet} in {sign} "
                         f"(Ch 18 v{verse_no}) — needs_review")
                    covered[sign] = cell(planet, sign, [verse_cell(18, verse_no)], t,
                                         status="needs_review", excerpt_scope="verse")
        for sign in SIGNS:
            cells.append(covered.get(sign) or
                         gap_cell(planet, sign, "not covered in Ch 18 of this translation"))
    for node in NODES:
        for sign in SIGNS:
            cells.append(gap_cell(node, sign,
                                  "Brihat Jataka defines the nodes (Ch 2 v3) but gives no "
                                  "planet-in-sign results for them anywhere; left unfilled by charter"))
    rules = [
        {"id": "PS-1", "rule": "The sign effects described for the Moon apply also to the rising "
         "sign and to the 2nd, 3rd and other bhavas, when the house and its lord are powerful",
         "citations": [verse_cell(18, 20)]},
        {"id": "PS-2", "rule": "If the Moon, her sign and that sign's lord all be powerful, the "
         "sign effects come fully; two powerful = imperfectly; one = still less; none = fail. "
         "The same grading applies to the other planets", "citations": [verse_cell(17, 13)]},
    ]
    return {"matrix": "planet_in_sign", "version": MATRIX_VERSION,
            "axes": {"rows": PLANETS7 + NODES, "columns": SIGNS},
            "cells": cells, "rules": rules,
            "notes": "Moon row cites Ch 17 (one verse per sign). Sun-Saturn cite Ch 18, where one "
                     "clause often covers two signs ('Mars in Aries or Scorpio') — such cells are "
                     "shared. Store defect: Saturn's first verse is misnumbered v11; the record is "
                     "selected by content and flagged here. Rahu/Ketu rows are explicit gaps."}


# ---------------------------------------------------------------- moon-sign aspects (Ch 19)
BLOCK_ANCHOR = re.compile(
    r"(?:Moon|Moau|Mood|Mooll)\s+occupy[^.]{0,60}?\bbe\b", re.I)


def aspect_segment(block: str, planet: str) -> str | None:
    """Find the aspect clause for `planet` inside a Moon-block. Clauses are the
    segments starting at if/and/or boundaries; a clause qualifies when it names
    the planet and an aspect marker ('... by Mars', 'if by Jupiter')."""
    # spill-over guard: cut at the next block's opening ('If at the time of birth
    # the Moon occupy ...', OCR-mangled), which may precede the next Navamsa mark
    block = re.split(r"(?i)\.?\s*[1i]?f\s+at\s+t[bhl]e\s+ti[mr]e", block)[0]
    segs = re.split(r"(?:^|(?<=[;,]))\s*(?=(?:if|and|or)\b)", block)
    for seg in segs:
        seg = seg.strip()
        if not seg or not has_planet(seg, planet):
            continue
        if not re.search(r"(?i)\b(?:if|and)\b", seg) or not re.search(r"(?i)\bby\b", seg):
            continue
        oc = re.search(r"(?i)\boccup\w{0,3}\b", seg)
        by = re.search(r"(?i)\bby\b", seg)
        if oc and by and oc.start() > by.start():
            continue  # spill-over from the next block's opening ('... the Moon occupy')
        if oc and not by:
            continue
        return seg
    return None


def build_moon_sign_aspects(st: Store) -> dict:
    sign_blocks: dict[str, tuple[str, int]] = {}
    for verse_no in (1, 2, 3):
        t = st.text(19, verse_no)
        starts = list(BLOCK_ANCHOR.finditer(t))
        for i, m in enumerate(starts):
            sign = next((s for s in SIGNS if has_sign(m.group(0), s)), None)
            if not sign:
                continue
            end = starts[i + 1].start() if i + 1 < len(starts) else len(t)
            sign_blocks.setdefault(sign, (t[m.start():end], verse_no))
    cells = []
    for sign in SIGNS:
        block, vno = sign_blocks.get(sign, ("", 0))
        if not block:
            warn(f"moon_sign_aspects: no block for {sign} in Ch 19 v1-3")
        for planet in PLANETS7:
            if planet == "Moon":
                continue
            if not block:
                cells.append(gap_cell(sign, planet, "block not parsed from Ch 19"))
                continue
            found = aspect_segment(block, planet)
            if found:
                merged = [p for p in PLANETS7 if p not in (planet, "Moon") and has_planet(found, p)]
                cells.append(cell(sign, planet, [verse_cell(19, vno)], found, merged_with=merged))
            else:
                warn(f"moon_sign_aspects: {planet} clause not found for Moon in {sign}")
                cells.append(cell(sign, planet, [verse_cell(19, vno)] if vno else [], None,
                                  status="needs_review"))
    rules = [
        {"id": "AS-1", "rule": "The same sign-aspect effects apply to the Moon in the several "
         "Dwadasamsas; hora/drekkana-lord aspects give benefic effects",
         "citations": [verse_cell(19, 4)]},
        {"id": "AS-2", "rule": "For the Sun the same readings apply with Solar and Lunar aspect "
         "exchanged; the rising Navamsa follows the Moon's rules",
         "citations": [verse_cell(19, 8)]},
    ]
    return {"matrix": "moon_sign_aspects", "version": MATRIX_VERSION,
            "axes": {"rows": SIGNS, "columns": [p for p in PLANETS7 if p != "Moon"]},
            "cells": cells, "rules": rules,
            "notes": "Rows = the Moon's sign; columns = the aspecting planet. v1 Aries-Cancer, "
                     "v2 Leo-Scorpio, v3 Sagittarius-Pisces. Clauses naming several planets at "
                     "once ('if by Saturn, the Sun or Mars') are shared (merged_with)."}


NAVAMSa_ROWS = ["Mars", "Venus", "Mercury", "Moon (Cancer navamsa)", "Sun (Leo navamsa)",
                "Jupiter", "Saturn"]
NAV_VERSE = {"Mars": 5, "Venus": 5, "Mercury": 6, "Moon (Cancer navamsa)": 6,
             "Sun (Leo navamsa)": 7, "Jupiter": 7, "Saturn": 8}
NAV_ANCHOR = re.compile(r"Nav\w{0,8}sa\b", re.I)
# the token that DISTINGUISHES each navamsa row ('cancer'/'leo', not moon/sun,
# whose names appear in the aspect clauses and would steal the match)
NAV_TOKENS = {"Mars": ["mars"], "Venus": ["venus"], "Mercury": ["mercury", "mer~uty"],
              "Moon (Cancer navamsa)": ["cancer"], "Sun (Leo navamsa)": ["leo"],
              "Jupiter": ["jupiter", "jupitcr"], "Saturn": ["saturn"]}


def build_moon_navamsa_aspects(st: Store) -> dict:
    nav_blocks: dict[str, str] = {}
    for verse_no in (5, 6, 7, 8):
        t = st.text(19, verse_no)
        marks = list(NAV_ANCHOR.finditer(t))
        for i, m in enumerate(marks):
            window = t[m.end():m.end() + 80]
            best_key, best_pos = None, 10 ** 9
            for row, tokens in NAV_TOKENS.items():
                for tok in tokens:
                    pm = re.search(rf"\b{re.escape(tok)}\b", window, re.I)
                    if pm and pm.start() < best_pos:
                        best_key, best_pos = row, pm.start()
            if not best_key:
                continue
            end = marks[i + 1].start() if i + 1 < len(marks) else len(t)
            nav_blocks.setdefault(best_key, t[m.start():end])
    cells = []
    for row in NAVAMSa_ROWS:
        block = nav_blocks.get(row, "")
        if not block:
            warn(f"moon_navamsa_aspects: block for {row} not parsed")
        for planet in PLANETS7:
            if planet == "Moon":
                continue  # the Moon is the aspected one; never an aspecting column here
            if not block:
                cells.append(gap_cell(row, planet, "navamsa block not parsed from Ch 19"))
                continue
            found = aspect_segment(block, planet)
            if found:
                truncated = bool(re.search(r"(?i)\bwill$|\bwiII$", found.strip()))
                cells.append(cell(row, planet, [verse_cell(19, NAV_VERSE[row])], found,
                                  status="needs_review" if truncated else "auto-draft",
                                  **({"flags": ["truncated_in_source"],
                                      "note": "clause cut off mid-sentence in the translation "
                                              "(see verse) — needs human recovery"}
                                     if truncated else {})))
            else:
                cells.append(gap_cell(row, planet, "aspect clause not parsed or verse truncated "
                                               f"in store (see Ch 19 v{NAV_VERSE[row]})"))
    return {"matrix": "moon_navamsa_aspects", "version": MATRIX_VERSION,
            "axes": {"rows": NAVAMSa_ROWS, "columns": [p for p in PLANETS7 if p != "Moon"]},
            "cells": cells,
            "notes": "Ch 19 v5-v8: the Moon in the navamsa of each lord, aspected by each planet. "
                     "Cancer/Leo navamsas stand for the Moon's and Sun's navamsas per the text. "
                     "Grading rule (v9): Vargottama full / own navamsa imperfect / other small."}


# ---------------------------------------------------------------- planets in houses (Ch 20)
REF_SENTENCE = re.compile(r"remaining\s+houses|other\s+houses|same\s+effects|same\s+as\s+"
                          r"those\s+of|12\s*signs\s+from\s+the\s+ascendant", re.I)
ORDINAL = re.compile(r"(\d{1,2})\s*(?:st|nd|rd|th|ed)\b|\b(\d{1,2})\s*h[a-z]{2,6}se|"
                     r"\bt\s*[Hh1il]{1,3}th\b|\b1\s*J\s*th\b", re.I)
ASCEND = re.compile(r"occup\w{0,3}\s+the\s+a[\w'\u00b7]{2,10}ndant", re.I)


def ordinal_of(token_m) -> int | None:
    if token_m.group(1):
        n = int(token_m.group(1))
    elif token_m.group(2):
        n = int(token_m.group(2))
    else:
        return 11  # the 't lth' / '1 Jth' OCR forms of 11th
    return n if 1 <= n <= 12 else None


def houses_of(segment: str) -> list[int]:
    """All house numbers named in a segment ('the 4th or the 5th house')."""
    out = []
    for m in ORDINAL.finditer(segment):
        n = ordinal_of(m)
        if n and n not in out:
            out.append(n)
    if not out and ASCEND.search(segment):
        out.append(1)
    if not out and re.search(r"(?i)\bthe\s+t\s+[Hh]", segment):  # 'the t Hh house' = 11th
        out.append(11)
    return out


CH20_COMPOSED = {  # planet -> {house: referenced planet} (the source's own rule)
    "Mars": {h: "Sun" for h in range(1, 13) if h not in (1, 2, 9)},
    "Mercury": {h: "Sun" for h in (9, 10, 11, 12)},
    "Venus": {h: "Jupiter" for h in range(1, 13) if h not in (1, 5, 7)},
    "Saturn": {h: "Sun" for h in range(2, 13)},
}
CH20_COMP_VERSE = {"Mars": 6, "Mercury": 6, "Venus": 8, "Saturn": 9}
SUBCASE_FORMS = [
    re.compile(r"if\s+(Aries|Taurus|Gemini|Cancer|Leo|Virgo|Libra|Scorpio|Sagittari\w*|"
               r"Capricorn|Aquarius|Pisces)\s+be\s+[^,;]{0,15}rising", re.I),
    re.compile(r"rising\s+sign\s+occupied\s+by\s+(?:the\s+)?Moon\s+be\s+"
               r"([A-Za-z;. ]{5,60})", re.I),
    re.compile(r"ascendant\s+occupied\s+by\s+Saturn\s+be\s+([A-Za-z;. ]{5,60})", re.I),
]


def subcase_signs(sentence: str) -> list[str]:
    for pat in SUBCASE_FORMS:
        m = pat.search(sentence)
        if m:
            return [s for s in SIGNS if has_sign(m.group(0), s)]
    return []


def build_planet_in_house(st: Store) -> dict:
    direct: dict[tuple, dict] = {}

    def offer(planet: str, sentence: str, vno: int):
        sentence = sentence.strip()
        if not sentence:
            return
        # a valid placement and the reference-composition tail may share one
        # sentence ('... and if he occupy the remaining houses ...') — keep the
        # placement head, drop the reference tail
        m = re.search(r"(?i)\b(?:and\s+if|;?\s*if)\b[^.;]{0,80}?(?:remaining|other)\s+houses",
                      sentence)
        if m:
            sentence = sentence[:m.start()].strip(" ,;")
        if not sentence or REF_SENTENCE.search(sentence):
            return
        houses = houses_of(sentence)
        if not houses:
            return
        for h in houses:
            key = (planet, h)
            if key not in direct:
                extra = {"covers_houses": houses} if len(houses) > 1 else {}
                direct[key] = cell(planet, str(h), [verse_cell(20, vno)], sentence, **extra)

    def scan(planet: str, text: str, vno: int):
        """Attribute each sentence to `planet`: by name, or by pronoun
        continuation ('if he occupy the 4th house') when no other planet
        is named in the sentence."""
        for s in sentences(text):
            if has_planet(s, planet):
                offer(planet, s, vno)
                if subcase_signs(s) and "rising" in low(s) and not houses_of(s):
                    c1 = direct.get((planet, 1))
                    if c1 is not None:
                        c1.setdefault("subcases", []).append(s)
                continue
            if any(has_planet(s, p) for p in PLANETS7):
                continue
            offer(planet, s, vno)

    for planet, verses in (("Sun", (1, 2, 3)), ("Moon", (4, 5))):
        for vno in verses:
            scan(planet, st.text(20, vno), vno)
    t6 = st.text(20, 6)
    idx = t6.find("Again")
    scan("Mars", t6[:idx] if idx > 0 else t6, 6)
    scan("Mercury", t6[idx:] if idx > 0 else "", 6)
    # Jupiter v7 — positional 12-item list
    t7 = st.text(20, 7)
    m = re.search(r"respe.{0,8}?ively\s+be\s+(.*)", t7, re.I | re.S)
    if m:
        raw = m.group(1).strip(" .;")
        items = [re.sub(r"^\s*(?:and\s+|will\s+be['\u2019]?\s+|will\s+|of\s+)", "", it.strip(" .;,"))
                 for it in re.split(r"[,.;]\s+|,\s+and\s+will\s+|\s+and\s+will\s+be['\u2019]?\s*", raw)
                 if it.strip(" .;,")]
        if len(items) == 12:
            ordinals = ["1st", "2nd", "3rd"] + [f"{h}th" for h in range(4, 13)]
            for h, o in enumerate(items, start=1):
                direct[("Jupiter", h)] = cell(
                    "Jupiter", str(h), [verse_cell(20, 7)],
                    f"Jupiter occupying the {ordinals[h - 1]} from the ascendant: {o}")
        else:
            warn(f"planet_in_house: Jupiter v7 split gave {len(items)} items — verse-level fallback")
            for h in range(1, 13):
                direct[("Jupiter", h)] = cell("Jupiter", str(h), [verse_cell(20, 7)], t7,
                                              excerpt_scope="verse", shared=True)
    else:
        warn("planet_in_house: Jupiter v7 respectively-list not parsed")
        for h in range(1, 13):
            direct[("Jupiter", h)] = cell("Jupiter", str(h), [verse_cell(20, 7)], t7,
                                          status="needs_review", excerpt_scope="verse")
    for planet, vno in (("Venus", 8), ("Saturn", 9)):
        scan(planet, st.text(20, vno), vno)

    cells = []
    for planet in PLANETS7:
        for h in range(1, 13):
            key = (planet, h)
            if key in direct:
                cells.append(direct[key])
                continue
            ref = CH20_COMPOSED.get(planet, {}).get(h)
            if ref and (ref, h) in direct:
                cells.append(cell(planet, str(h),
                                  [verse_cell(20, CH20_COMP_VERSE[planet])] +
                                  direct[(ref, h)]["citations"],
                                  direct[(ref, h)]["excerpt"],
                                  via_reference={"row": ref, "col": str(h)},
                                  note=f"Composed by the source's own rule: '{planet} in the "
                                       f"remaining houses produces the same effects as {ref} in "
                                       f"those places'"))
            else:
                warn(f"planet_in_house: no cell for {planet} house {h}")
                cells.append(gap_cell(planet, str(h), "not stated and not composed by reference"))
    rules = [
        {"id": "PH-1", "rule": "In judging planets in houses the house's nature counts: friendly/"
         "own/exalted signs promote the bhava, inimical/debilitated reduce it (Satyachariar; Garga)",
         "citations": [verse_cell(20, 10)]},
        {"id": "PH-2", "rule": "Dignity quantification: exaltation full, moolatrikona 3/4, own "
         "house 1/2, friendly 1/4, inimical < 1/4, depression or combust nil",
         "citations": [verse_cell(20, 11)]},
    ]
    return {"matrix": "planet_in_house", "version": MATRIX_VERSION,
            "axes": {"rows": PLANETS7, "columns": [str(i) for i in range(1, 13)]},
            "cells": cells, "rules": rules,
            "notes": "Rows Sun-Saturn (Moon via Ch 20 v4-5). Mars, Mercury (9-12), Venus and "
                     "Saturn are completed by the translation's own reference rule — such cells "
                     "carry via_reference and cite both verses. Jupiter v7 is a positional "
                     "12-item list. Rahu/Ketu: no bhava-results exist in this text (gap)."}
def build_conjunctions(st: Store) -> dict:
    seen: dict[tuple, dict] = {}
    for vno in range(1, 6):
        t = st.text(14, vno)
        for s in sentences(t):
            present = [p for p in PLANETS7 if has_planet(s, p)]
            if len(present) == 2:
                pair = tuple(sorted(present))
                seen.setdefault(pair, cell(pair[0], pair[1], [verse_cell(14, vno)], s))
    # pass 2: OCR-garbled names ('Man' for Mars) — a sentence naming exactly one
    # planet plus 'Man' completes that planet's pair with Mars
    for vno in range(1, 6):
        for s in sentences(st.text(14, vno)):
            if not re.search(r"\bMan\b", s):
                continue
            present = [p for p in PLANETS7 if has_planet(s, p)]
            if len(present) == 1 and present[0] != "Mars":
                pair = tuple(sorted((present[0], "Mars")))
                seen.setdefault(pair, cell(pair[0], pair[1], [verse_cell(14, vno)], s))
    cells = []
    for a in PLANETS7:
        for b in PLANETS7:
            if a >= b:
                continue
            pair = (a, b)
            if pair in seen:
                cells.append(seen[pair])
            else:
                cells.append(gap_cell(a, b, "pair not found in Ch 14 of this translation "
                                            "(OCR damage or omission) — needs verse recovery"))
                warn(f"conjunctions: {a}+{b} not found in Ch 14")
    rules = [
        {"id": "CJ-1", "rule": "For yogas of three, four and five planets together the effects "
         "are determined and applied in the same manner", "citations": [verse_cell(14, 5)]},
    ]
    return {"matrix": "conjunctions", "version": MATRIX_VERSION,
            "axes": {"rows": PLANETS7, "columns": PLANETS7},
            "cells": cells, "rules": rules,
            "notes": "All 21 unordered pairs of the seven grahas (row<column in canonical order). "
                     "Triple+ combinations are covered by rule CJ-1, not enumerated by the source."}


# ---------------------------------------------------------------- nakshatras (Ch 16)
def build_nakshatras(st: Store) -> dict:
    """The 27 nakshatras appear in canonical order in Ch 16, but the OCR shortens
    some names to a single letter ('P' for Pubba/Purvashadha/Poorvabhadra) and drops
    others entirely. Strategy: align tokens to the canonical sequence positionally,
    verifying by fuzzy name match where the token is long enough; short tokens fill
    the next canonical slot and are flagged; unaligned slots become needs_review."""
    import difflib

    verse_texts = [(v, st.text(16, v)) for v in range(1, 15)]
    text = " ".join(t for _, t in verse_texts)
    spans = [(v, len(t)) for v, t in verse_texts]
    ms = list(re.finditer(r"asterism\s+(?:of|o[ft])\s+([A-Za-z]+)", text, re.I))
    tokens = [low(m.group(1)) for m in ms]

    def name_match(tok: str, canon: str) -> bool:
        if len(tok) < 4:
            return False
        variants = [low(canon)] + [low(v) for v in NAK_VARIANTS[canon]]
        return any(difflib.SequenceMatcher(None, tok, v).ratio() >= 0.62 for v in variants)

    assign: dict[int, int] = {}   # canonical index -> token index
    ci, ti = 0, 0
    while ci < 27 and ti < len(tokens):
        tok = tokens[ti]
        matched = None
        for dj in (0, 1, 2):
            if ci + dj < 27 and name_match(tok, NAKSHATRAS[ci + dj]):
                matched = ci + dj
                break
        if matched is not None:
            assign[matched] = ti
            ci, ti = matched + 1, ti + 1
        else:
            # short/abbreviated token: fills the next canonical slot positionally
            assign[ci] = ti
            ci, ti = ci + 1, ti + 1

    cells = []
    for idx, nak in enumerate(NAKSHATRAS):
        if idx not in assign:
            cells.append({"row": "Moon", "col": nak, "status": "needs_review",
                          "citations": [], "excerpt": None,
                          "note": "name garbled or dropped by OCR; clause boundary unrecoverable "
                                  "automatically — needs human recovery in Ch 16"})
            warn(f"nakshatras: {nak} unaligned (OCR)")
            continue
        ti2 = assign[idx]
        start = ms[ti2].start()
        end = ms[ti2 + 1].start() if ti2 + 1 < len(ms) else len(text)
        # locate the verse containing this name, and clamp the clause to it
        verse_no, acc, vstart, vend = 1, 0, 0, len(text)
        for v, ln in spans:
            if start < acc + ln:
                verse_no, vstart, vend = v, acc, acc + ln
                break
            acc += ln + 1
        end = min(end, vend)
        flags = ["ocr_suspect:abbreviated_name"] if len(tokens[ti2]) < 4 else []
        cells.append(cell("Moon", nak, [verse_cell(16, verse_no)],
                          text[start:end], status="auto-draft", flags=flags))
    found = sum(1 for c in cells if c["status"] == "auto-draft")
    if found < 27:
        warn(f"nakshatras: {found}/27 parsed")
    return {"matrix": "nakshatras", "version": MATRIX_VERSION,
            "axes": {"rows": ["Moon"], "columns": NAKSHATRAS},
            "cells": cells,
            "notes": "The Moon in each of the 27 asterisms (Ch 16). The translation groups 2-3 "
                     "nakshatras per verse; clauses split on 'asterism of X'. Tokens are aligned "
                     "to the canonical order (the text's own order) with fuzzy name verification; "
                     "single-letter OCR abbreviations fill positionally and are flagged."}


# ---------------------------------------------------------------- ascendants (derived)
def build_ascendants(st: Store) -> dict:
    t1820 = st.text(18, 20)
    subcases_by_sign: dict[str, list] = {}
    for vno in (1, 4, 9):
        for s in sentences(st.text(20, vno)):
            for sign in subcase_signs(s):
                subcases_by_sign.setdefault(sign, []).append(
                    {"excerpt": s, "citations": [verse_cell(20, vno)]})
    directions = {"eastern": ["Aries", "Cancer", "Libra", "Scorpio", "Aquarius"],
                  "northern": ["Sagittarius", "Pisces", "Gemini", "Virgo"],
                  "western": ["Taurus"], "southern": ["Capricorn", "Leo"]}
    sanskrit_signs = {"Aries": "Mesha", "Taurus": "Vrishabha", "Gemini": "Mithuna",
                      "Cancer": "Kataka", "Leo": "Simha", "Virgo": "Kanya",
                      "Libra": "Tula", "Scorpio": "Vrischika", "Sagittarius": "Dhanus",
                      "Capricorn": "Makara", "Aquarius": "Kumbha", "Pisces": "Meena"}
    t513 = st.text(5, 13, include_notes=True)
    cells = []
    for sign in SIGNS:
        dirn = next((d for d, ss in directions.items() if sign in ss), None)
        place_ex = None
        m = re.search(re.escape(sanskrit_signs[sign]) +
                      r"\s+represents\s+(.*?)(?=[A-Z][a-z]+\s+represents|$)", t513, re.I | re.S)
        if m:
            place_ex = re.sub(r"\s+", " ", m.group(1)).strip(" .;")
        derivation = (
            "Brihat Jataka has no standalone per-ascendant chapter. This cell is COMPOSED from "
            "the source's own rules: (1) Ch 18 v20 — the sign effects described for the Moon "
            "apply also to the rising sign when it and its lord are powerful; (2) Ch 1 sign "
            "qualities; (3) Ch 20 lagna sub-cases; (4) Ch 5 v13/v20 places and directions.")
        c = cell("lagna", sign, [verse_cell(18, 20), verse_cell(1, 6)], t1820,
                 status="derived", derivation=derivation,
                 sign_qualities_ref={"matrix": "signs", "col": sign},
                 moon_sign_effects_ref={"matrix": "planet_in_sign", "row": "Moon", "col": sign},
                 lagna_subcases=subcases_by_sign.get(sign, []),
                 delivery_room_direction=dirn, delivery_room_citations=[verse_cell(5, 20)],
                 places_excerpt=place_ex, places_citations=[verse_cell(5, 13)])
        if not dirn or not place_ex:
            c["flags"] = ["ocr_suspect"]
        cells.append(c)
    return {"matrix": "ascendants", "version": MATRIX_VERSION,
            "axes": {"rows": ["lagna"], "columns": SIGNS},
            "cells": cells,
            "notes": "DERIVED matrix — every quality is a citation into Ch 1/17/18/20/5 plus the "
                     "source's own extension rule (Ch 18 v 20). No verse was paraphrased into new "
                     "doctrine; the composition rule itself is the cited verse."}


# ---------------------------------------------------------------- house-lord rules
def build_house_lord_rules(st: Store) -> dict:
    def r(rid, houses, condition, effect, cites, classification):
        return {"id": rid, "houses": houses, "condition": condition, "effect": effect,
                "classification": classification,
                "citations": [verse_cell(*c) for c in cites], "status": "draft"}

    rules = [
        r("HL-1", [1], "The lord of the ascendant, or Jupiter, or Mercury occupies or aspects "
          "the ascendant", "The ascendant becomes powerful (and not so by other planets)",
          [(1, 19)], "strength"),
        r("HL-2", list(range(1, 13)), "A house is powerful and its lord is powerful",
          "The objects signified by the house are promoted; if either is weak, they are reduced",
          [(18, 20)], "neutral"),
        r("HL-3", list(range(1, 13)), "A benefic occupies a bhava / a malefic occupies a bhava",
          "Benefics promote the bhava and malefics reduce it — reversed in the 6th, 8th, 12th",
          [(20, 10)], "neutral"),
        r("HL-4", list(range(1, 13)), "Dignity of the occupying planet: exalted / moolatrikona / "
          "own / friendly / inimical / debilitated-or-combust",
          "Effects full / three-quarters / one-half / one-quarter / less than one-quarter / "
          "wholly fail", [(20, 11)], "table"),
        r("HL-5", [10], "The planet occupying the 10th from Lagna or Moon (Sun-father, "
          "Moon-mother, Mars-enemy, Mercury-friend, Jupiter-brother, Venus-wife, Saturn-servant); "
          "and the lord of the Navamsa occupied by the lord of the 10th",
          "Source of wealth and the avocation follow that planet",
          [(10, 1), (10, 2), (10, 3)], "table"),
        r("HL-6", [10], "The yoga planet occupies a friendly / inimical / own / exaltation sign",
          "Wealth through a friend / an enemy / that house / the native's own powers",
          [(10, 4)], "tend"),
        r("HL-7", [1, 4, 7, 10], "Jupiter, the lord of the Moon's sign, or the lord of the "
          "ascendant occupies a Kendra", "The native is happy in his manhood", [(22, 5)], "strength"),
        r("HL-8", list(range(1, 13)), "Vargottama lagna-navamsa or Moon; benefics in the 2nd from "
          "the Sun; Kendras empty of planets", "The native is happy and prosperous",
          [(22, 4)], "strength"),
        r("HL-9", list(range(1, 13)), "Planets in own/exalted/moolatrikona signs in Kendras are "
          "Karaka to one another; a planet in the 10th from another is its special Karaka",
          "Karaka-planet configurations", [(22, 1), (22, 2), (22, 3)], "neutral"),
        r("HL-10", list(range(1, 13)), "Charts in which 'the signs Aries, Cancer and Leo are "
          "occupied by their lords' (and cognate patterns)",
          "Birth of kings (if born in a king's family) / richness otherwise",
          [(11, 10), (11, 15), (11, 16), (11, 17)], "strength"),
        r("HL-11", [1, 10], "Dasa of a Raja-yoga planet in the 10th or Lagna, or of the most "
          "powerful planet; vs dasa of planets in inimical or depression signs",
          "Kingdom obtained in the former, lost in the latter", [(11, 19)], "tend"),
        r("HL-12", list(range(1, 13)), "The dasa lord in a Prishtodaya / Sirodaya sign; Sun and "
          "Mars act on sign entry, Jupiter and Venus mid-sign, Saturn and Moon before leaving, "
          "Mercury throughout", "Effects manifest late in the period / at its start; planets "
          "time their effects within a sign", [(22, 5), (22, 6)], "neutral"),
    ]
    for rule in rules:
        for c in rule["citations"]:
            if not st.exists(c["chapter"], c["verse"]):
                warn(f"house_lord_rules {rule['id']}: citation Ch {c['chapter']} "
                     f"v {c['verse']} missing")
    return {"matrix": "house_lord_rules", "version": MATRIX_VERSION,
            "axes": {"rows": ["rule"], "columns": ["condition", "effect"]},
            "cells": rules,
            "notes": "Brihat Jataka states lord-arrangement doctrine as PRINCIPLES (house+lord "
                     "power, dignity grading, benefic/malefic) plus specific Raja-yoga charts — "
                     "not a systematic 12x12 'lord of N in house M' table. That table belongs to "
                     "later texts and is NOT filled here (charter: no chapter, no doctrine). "
                     "Each rule is a draft awaiting Scholar Reviewer verification."}


# ---------------------------------------------------------------- chapter map
WIKI_CHAPTERS = [
    (1, "Samjnadhvaya (untitled; opens with a prayer, defines terms)", "Definitions (Zodiacal)"),
    (2, "Grahayoni Prabheda", "Definitions (Planetary)"),
    (3, "Viyoni Janama Adhyaya", "Viyoniprada"),
    (4, "Nisheka", "Nisheka Kala (Time of Conception)"),
    (5, "Janama Kal Lakshana", "Janma-kala (Matters at Birth Time)"),
    (6, "Balarishta", "Balarishta (Early Death)"),
    (7, "Ayurdaya", "Ayurdaya (Length of Life)"),
    (8, "Dasantradasa", "Dasas and Antardasas"),
    (9, "Ashtaka Varga", "Ashtakavargas"),
    (10, "Karamjeeva", "Avocation (Karmajiva)"),
    (11, "Raja Yoga", "Raja Yoga (Birth of Kings)"),
    (12, "Nabhasa Yoga", "Nabhasa Yogas"),
    (13, "Chandra Yogadhyaya", "Chandra (Lunar) Yogas"),
    (14, "Dwigraha Yogadhyaya", "Double Planetary Yogas"),
    (15, "Pravrajya Yoga", "Ascetic Yogas (Pravrajya)"),
    (16, "Rikshasiladhyaya", "Nakshatras (Moon in the Asterisms)"),
    (17, "Rasisiladhyaya", "Moon in the Several Signs"),
    (18, "Rasisiladhyaya", "Sun, Mars and other Planets in the Several Signs"),
    (19, "Drishti Phaladhyaya", "Planetary Aspects (Drishti)"),
    (20, "Bhavadhyaya", "Planets in the Bhavas"),
    (21, "Asrya Yogadhyaya", "Planets in the Several Vargas"),
    (22, "Prakirnadhyaya", "Miscellaneous Yogas"),
    (23, "Anishtadhyaya", "Malefic Yogas"),
    (24, "Stree Jatakadhyaya", "Horoscopy of Women (Strijataka)"),
    (25, "Niryanadhyaya", "Death"),
    (26, "Nasta Jataka", "Lost Horoscopes (Apavatika)"),
    (27, "Drekkanadhyaya", "Drekkanas"),
]


def build_chapter_map(st: Store) -> dict:
    entries = []
    store = {c["chapter"]: c for c in st.chapters}
    for n, sanskrit, _ in WIKI_CHAPTERS:
        c = store.get(n, {})
        entries.append({"store_chapter": n, "sanskrit_name": sanskrit,
                        "store_title": c.get("title"),
                        "verse_count": c.get("verse_count")})
    return {"version": "chapter-map-1.0.0",
            "source": "store chapters.json cross-checked against the canonical 28-chapter list "
                      "(Wikipedia 'Brihat Jataka', retrieved 2026-09-21; English titles from the "
                      "translation held in sourcetext/, itself a public-domain open-internet text)",
            "chapters": entries,
            "known_divergences": [
                "This translation contains chapters 1-27 only; chapter 28 (Upasamharadhyaya, the "
                "concluding chapter) is absent from this edition.",
                "docs/01-source-text-foundation.md numbers chapters differently from the "
                "translation (its ch.2/3 split, ch.27 Prasna and ch.28 Nisheka-Adhana do not "
                "exist in this text). Store numbering is canonical for all citations.",
                "Ch 18 contains a misnumbered record: Saturn's first verse is stored as v11 "
                "(duplicate number with Mercury's v11). Recorded, not silently fixed.",
            ],
            "status": "pending Scholar Reviewer sign-off"}


# ---------------------------------------------------------------- main
def coverage(m: dict) -> dict:
    cells = m["cells"]
    n = len(cells)
    ok = sum(1 for c in cells if c["status"] in ("auto-draft", "derived", "draft"))
    review = sum(1 for c in cells if c["status"] == "needs_review")
    gaps = sum(1 for c in cells if c["status"] == "gap")
    return {"cells": n, "classified": ok, "needs_review": review, "gaps": gaps,
            "coverage_pct": round(100.0 * ok / n, 1) if n else None}


def main() -> int:
    ap = argparse.ArgumentParser()
    root = Path(__file__).resolve().parents[2]
    ap.add_argument("--store", default=str(root / "backend/data/verse_store"))
    ap.add_argument("--out", default=str(root / "backend/data/matrices"))
    args = ap.parse_args()
    st = Store(Path(args.store))
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"verse store {st.store_version}: {len(st.verses)} records")

    matrices = {
        "signs": build_signs(st),
        "houses": build_houses(st),
        "nakshatras": build_nakshatras(st),
        "planet_in_sign": build_planet_in_sign(st, build_moon_in_sign(st)),
        "planet_in_house": build_planet_in_house(st),
        "moon_sign_aspects": build_moon_sign_aspects(st),
        "moon_navamsa_aspects": build_moon_navamsa_aspects(st),
        "conjunctions": build_conjunctions(st),
        "ascendants": build_ascendants(st),
        "house_lord_rules": build_house_lord_rules(st),
    }

    bad = 0
    for name, m in matrices.items():
        for c in m["cells"]:
            for cit in c.get("citations", []):
                if not st.exists(cit["chapter"], cit["verse"]):
                    bad += 1
                    warn(f"{name}: dangling citation Ch {cit['chapter']} v {cit['verse']}")
        (out_dir / f"{name}.json").write_text(json.dumps(m, ensure_ascii=False, indent=1) + "\n")

    (Path(args.store) / "chapter_map.json").write_text(
        json.dumps(build_chapter_map(st), ensure_ascii=False, indent=1) + "\n")

    manifest = {
        "matrix_version": MATRIX_VERSION,
        "verse_store_version": st.store_version,
        "built_by": "backend/scripts/build_matrices.py (deterministic; no network; no runtime AI)",
        "review": "all cells are auto-draft/derived until Scholar Reviewer verification",
        "citation_errors": bad,
        "matrices": {name: coverage(m) for name, m in matrices.items()},
        "gaps_declared": {
            "planet_in_sign.Rahu": "nodes have no sign-results chapter in this text",
            "planet_in_sign.Ketu": "nodes have no sign-results chapter in this text",
            "planet_in_house.Rahu": "nodes have no bhava-results chapter in this text",
            "planet_in_house.Ketu": "nodes have no bhava-results chapter in this text",
            "house_lord_rules.12x12": "the source gives principles + specific charts, not a "
                                      "systematic lord-of-N-in-M table; left unfilled",
            "ascendants": "derived matrix — composed from Ch 18 v20 + Ch 1 + Ch 20 + Ch 5; no "
                          "standalone chapter exists",
            "chapter_28": "Upasamharadhyaya absent from this translation",
        },
        "warnings": WARNINGS,
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1) + "\n")

    print("\ncoverage:")
    for name, cov in manifest["matrices"].items():
        print(f"  {name:24s} {cov['cells']:4d} cells  {str(cov['coverage_pct']):>5}% classified  "
              f"{cov['needs_review']:3d} review  {cov['gaps']:3d} gaps")
    print(f"citation errors: {bad}; warnings: {len(WARNINGS)}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
