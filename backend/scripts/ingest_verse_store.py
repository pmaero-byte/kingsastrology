#!/usr/bin/env python3
"""M1 — Verse Store ingestion (build-time tool, run by the verse-indexer).

Extracts the Brihat Jataka translation PDF (Sagar Publications) into a
structured, verse-indexed Verse Store. This is the source-of-truth layer the
whole product cites from (AGENTS.md, docs/01, .claude/agents/verse-indexer.md).

Faithfulness contract (verse-indexer guardrails):
  - Text is extracted AS IS. Only mechanical line-noise is removed (page
    numbers, running headers, book titles, printer hyphens at line breaks).
  - Damaged/ambiguous verses are flagged in `uncertain`, never silently fixed.
  - Chapter and verse numbering follow this translation's own numbering.

Output (backend/data/verse_store/):
  manifest.json   — version, source, counts, generation time
  chapters.json   — chapter index: title, page range, verse count
  verses.json     — [{chapter, verse, sanskrit_ref, translation_text,
                      keywords[], pages, notes?, flags[]}]
  uncertain.json  — [{chapter, verse, issue, excerpt, suggested_review}]
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pymupdf

STORE_VERSION = "2026.08.29"
SOURCE_PDF = "sourcetext/pdfcoffee.com_brihat-jataka-of-varahamihira-pdf-free.pdf"

# Chapter -> (first page, last page), 1-indexed PDF pages, per this translation.
# Verified against running headers ("CH. IV" etc.) and chapter title pages.
CHAPTER_PAGES: dict[int, tuple[int, int]] = {
    1: (38, 53),    # Definitions & Elementary Principles (Zodiacal)
    2: (54, 64),    # Definitions & Elementary Principles (Planetary)
    3: (65, 69),    # Animal & Vegetable Horoscopy (Viyoniprada)
    4: (70, 82),    # Nisheka Kala (time of conception)
    5: (83, 99),    # Matters connected with birth time
    6: (100, 106),  # Balarishta (early death)
    7: (107, 127),  # Ayurdaya (length of life)
    8: (128, 147),  # Dasas and Antardasas
    9: (148, 167),  # Ashtakavargas
    10: (168, 171), # Avocation
    11: (172, 182), # Raja Yoga
    12: (183, 200), # Nabhasa Yogas
    13: (201, 208), # Chandra (Lunar) Yogas
    14: (209, 222), # Double Planetary Yogas
    15: (223, 226), # Ascetic Yogas
    16: (227, 230), # Nakshatras (Moon in the asterisms)
    17: (231, 235), # Moon in the several signs
    18: (236, 248), # Sun, Mars and other planets in the several signs
    19: (249, 255), # Planetary Aspects
    20: (256, 261), # Planets in the Bhavas
    21: (262, 267), # Planets in the several Vargas
    22: (268, 271), # Miscellaneous Yogas
    23: (272, 280), # Malefic Yogas
    24: (281, 289), # Horoscopy of Women
    25: (290, 297), # Death
    26: (298, 312), # Lost Horoscopes
    27: (313, 323), # Drekkanas
}
CHAPTER_TITLES = {
    1: "Definitions and Elementary Principles (Zodiacal)",
    2: "Definitions and Elementary Principles (Planetary)",
    3: "Viyoniprada (Animal and Vegetable Horoscopy)",
    4: "Nisheka Kala (Time of Conception)",
    5: "Janma-kala (Matters Connected with Birth Time)",
    6: "Balarishta (Early Death)",
    7: "Ayurdaya (Determination of the Length of Life)",
    8: "Dasas and Antardasas (Planetary Divisions of Life)",
    9: "Ashtakavargas",
    10: "Avocation (Karmajiva)",
    11: "Raja Yoga (Birth of Kings)",
    12: "Nabhasa Yogas",
    13: "Chandra (Lunar) Yogas",
    14: "Double Planetary Yogas",
    15: "Ascetic Yogas (Pravrajya)",
    16: "Nakshatras (Moon in the Asterisms)",
    17: "Moon in the Several Signs",
    18: "Sun, Mars and other Planets in the Several Signs",
    19: "Planetary Aspects (Drishti)",
    20: "Planets in the Bhavas",
    21: "Planets in the Several Vargas",
    22: "Miscellaneous Yogas",
    23: "Malefic Yogas",
    24: "Horoscopy of Women (Strijataka)",
    25: "Death",
    26: "Lost Horoscopes (Apavatika)",
    27: "Drekkanas",
}

# Marker: verse number at line start. Arabic ("1.", "15."), OCR-damaged
# variants ("2,0." for 20., "S." for 5., "G." for 6., "B." for 8.,
# "It." for 11., "I I." for 11., "6;" / "7\"" / "10 . ." for period-less
# terminators, "\ 6." for a stray leading backslash), or Roman ("I.",
# "II.", "IV."). Case-sensitive: "If." must never parse as a marker, and
# ambiguous forms ("II." = 2 or 11) are resolved by the expected verse
# sequence (see _parse_marker).
_MARKER_RE = re.compile(
    r"^\s*[-–—.·'\"`\\~]*\s*([0-9]{1,3}(?:,[0-9])?|[IVXlSGtBfioO][\sIVXlSGtBfioO]{0,4})"
    r"\s*[.;,\"']+\s*(.*)$",
)
# NOTES section header (OCR-damaged: "l"'OTES", "NOTI';S", "N OTES",
# "NOTI::S", "NUTFS", "NOTF..S", "Notes.-", "Noles :-" ...).
_NOTES_RE = re.compile(r"^\s*[NlI][\s.'’`\"]*[OU0][\s.'’`\"]*[TLl][E'I;lF:U0.]*[S5]", re.IGNORECASE)

_ROMAN = {"I": 1, "V": 5, "X": 10, "L": 50}
# OCR letter-for-digit substitutions seen in this scan: S=5, G=6, B=8,
# F/f=1 (the "fl." ligature for "11."), t=1 ("It."/"to." for 11/10),
# o/O=0 ("to." for 10.), i=1, l=1. Multi-letter forms must fit the expected
# verse sequence, so "If." never parses as a marker (its digit reading 11
# would not match the expected number).
_DIGIT_LETTERS = {"I": 1, "i": 1, "l": 1, "t": 1, "T": 1, "S": 5, "G": 6,
                  "B": 8, "F": 1, "f": 1, "o": 0, "O": 0}


def _roman_to_int(s: str) -> int:
    s = s.replace("l", "I").upper()  # lowercase "l" is OCR for "I", not "L"
    total, prev = 0, 0
    for ch in reversed(s):
        val = _ROMAN.get(ch, 1)
        total += -val if val < prev else val
        prev = val
    return total


def _digit_concat(num: str) -> int:
    return int("".join(str(_DIGIT_LETTERS.get(ch, 0)) for ch in num if not ch.isspace()))


def _parse_marker(num: str, expected: int | None) -> int | None:
    """Resolve a marker to a verse number, or None if it is not plausibly a
    verse marker. OCR letter-substitutions ("S."=5, "B."=8, "It."=11,
    "I I."=11) and ambiguous roman forms ("II." = 2 or 11) are resolved by
    the expected next verse number; a multi-letter form that fits neither is
    rejected so prose like "If. when ..." never becomes a verse."""
    s = num.strip()
    if s.isdigit():
        return int(s)
    if all(ch.isdigit() or ch == "," for ch in s):   # "2,0." for 20.
        return int(s.replace(",", ""))
    has_special = any(ch in s for ch in "SGtBfF")  # unambiguous OCR digits
    cands: set[int] = set()
    if has_special:
        cands.add(_digit_concat(s))
    else:
        cands.add(_roman_to_int(s))
        if len(s) > 1:
            cands.add(_digit_concat(s))              # "II."/"It." as 11
    if expected is not None and expected in cands:
        return expected
    if has_special and expected is not None and len(s) > 1:
        return None                                  # must fit the sequence
    if len(cands) == 1:
        return cands.pop()
    return _roman_to_int(s)


# ---------------------------------------------------------------- page noise
# Applied to the top-4 / bottom-4 lines of each page only (running headers,
# page numbers, chapter titles). Body text is never touched.
_ZONE = 4

_NOISE_PUNCT_RE = re.compile(r"^[\d•,.!\[\]()'\"*—_–·\s]+$")
_NOISE_DIGITS_RE = re.compile(r"^\d{1,3}$")
# Book-title running headers: "The Brihat Jataka" and OCR manglings thereof.
_NOISE_BOOK_RE = re.compile(
    r"[Bb]r[il1j!;,']{1,3}?[a-z0-9!;,']*|[Jj][a-z0-9!;,']*[kK][a-z0-9!;,']{0,2}"
)
# Chapter running heads: "CHAPTER XV", "CH. VII]", "eH. VII]", "H. XXVUJ" ...
_NOISE_CH_RE = re.compile(
    r"^\s*[A-Za-z']{1,9}\.?[ \[(]*[IVXLCDM0-9UJru]{1,8}[\])]?\s*$"
)
# Margin running heads embedded mid-page in the OCR stream ("[CH. I",
# "CH. v]", "(CH. II", "[eH. I"). Bracketed so body references like
# "vide stanza 21, Ch. V" are never touched.
_HEADER_TOKEN_RE = re.compile(
    r"[\[(]\s*[A-Za-z]{1,4}[.'’]?\s*[IVXLCDMivxlcdmnTt0-9]{1,7}[\])]?"
    r"|[A-Za-z]{1,4}[.'’]?\s*[IVXLCDMivxlcdmnTt0-9]{1,7}[\])]"
)


def _is_page_noise(line: str) -> bool:
    return bool(
        _NOISE_PUNCT_RE.match(line)
        or _NOISE_DIGITS_RE.match(line)
        or _NOISE_BOOK_RE.search(line)
        or _NOISE_CH_RE.match(line)
    )


# -------------------------------------------------------------- verse split

def _join_lines(lines: list[str]) -> str:
    """Join wrapped lines; drop printer hyphens at line breaks, keep '·'."""
    out = ""
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if out and out.endswith("-"):
            out = out[:-1] + line
        elif out and out.endswith("·"):
            out += line
        else:
            out = (out + " " + line) if out else line
    return re.sub(r"\s+", " ", out).strip()


def extract_chapter(doc, chapter: int) -> tuple[list[dict], list[dict]]:
    """Return (verses, uncertain) for one chapter."""
    first_page, last_page = CHAPTER_PAGES[chapter]
    verses: list[dict] = []
    uncertain: list[dict] = []
    seen_numbers: set[int] = set()

    current: dict | None = None          # verse under construction
    in_notes = False
    note_lines: list[str] = []
    in_table_run = False                 # consecutive non-sequential markers
    expected_next = 1                    # next verse number in the sequence

    def flush_notes() -> None:
        nonlocal note_lines
        if current is not None and note_lines:
            current["notes"] = _join_lines(note_lines)
            note_lines = []

    def flush_verse() -> None:
        nonlocal current
        if current is not None:
            verses.append(current)
            current = None

    def start_verse(number: int, first_line: str, page: int) -> None:
        nonlocal current, in_notes
        flush_notes()
        flush_verse()
        in_notes = False
        current = {
            "chapter": chapter,
            "verse": number,
            "text_lines": [first_line] if first_line else [],
            "start_page": page,
            "flags": [],
        }

    def append_text(line: str) -> None:
        """Attach a line to the verse under construction; create a flagged
        'table' verse if no verse is open (content is never dropped)."""
        nonlocal current
        if current is None:
            current = {
                "chapter": chapter,
                "verse": 0,
                "text_lines": [line],
                "start_page": None,
                "flags": ["table"],
            }
        else:
            current["text_lines"].append(line)

    for page_idx in range(first_page - 1, last_page):
        page_no = page_idx + 1
        text = doc[page_idx].get_text()
        lines = [l.rstrip() for l in text.split("\n")]
        n = len(lines)
        seen: list[tuple[str, int]] = []  # (line, page), noise stripped
        for idx, raw in enumerate(lines):
            line = raw.strip()
            if not line:
                continue
            if _NOTES_RE.match(line):     # notes headers first: "l"'OTES" is
                seen.append((line, page_no))  # not a verse marker
                continue
            if _MARKER_RE.match(line):    # markers are never page noise
                seen.append((line, page_no))
                continue
            line = _HEADER_TOKEN_RE.sub("", line).strip()
            if not line:
                continue
            if (idx < _ZONE or idx >= n - _ZONE) and _is_page_noise(line):
                continue
            if _NOISE_PUNCT_RE.match(line):
                continue
            seen.append((line, page_no))

        for i, (line, page_no) in enumerate(seen):
            notes_header = _NOTES_RE.match(line)
            if notes_header:
                flush_notes()
                in_notes = True
                trailing = line[notes_header.end():].strip()
                if trailing:
                    note_lines.append(trailing)
                continue
            marker = _MARKER_RE.match(line)
            if marker:
                number = _parse_marker(marker.group(1), expected_next)
                rest = marker.group(2).strip()
                if number is None:
                    # Not plausibly a verse marker (e.g. "If. ...") — prose.
                    if current is not None:
                        current["text_lines"].append(line)
                    continue
                # A quote/apostrophe terminator with no text is table OCR
                # garbage ("15\"" from a table row), never a verse marker.
                if not rest and line.endswith(('"', "'")):
                    if current is not None:
                        current["text_lines"].append(line)
                    continue
                # A plain digit marker whose text starts with another digit is
                # note/table prose ("3. 0,2. ..."), not a verse.
                if rest and rest[0].isdigit() and "," not in marker.group(1):
                    if current is not None:
                        current["text_lines"].append(line)
                    continue
                # Table/list rows run as consecutive markers; the row text is
                # short and the numbers are NOT sequential (e.g. the 60-amsa
                # list "1. Ghora / 10. Agoi / 19. Mridu ..."). A real stanza
                # advances the sequence by one, so a sequential marker never
                # enters a table run.
                next_is_marker = i + 1 < len(seen) and bool(_MARKER_RE.match(seen[i + 1][0]))
                if in_table_run:
                    if next_is_marker or (rest and len(rest) < 30):
                        append_text(line)
                        continue
                    in_table_run = False      # run ends: this marker is a verse
                elif next_is_marker and number != expected_next and (not rest or len(rest) < 30):
                    in_table_run = True
                    append_text(line)
                    continue
                if number in seen_numbers:
                    # The translation restarts numbering for later sections and
                    # reuses numbers inside NOTES/example blocks. If we are
                    # inside a NOTES block the item stays in the notes of the
                    # current stanza; otherwise it starts a new verse (new
                    # numbered series). Both are flagged for Scholar Review.
                    if in_notes:
                        note_lines.append(line)
                    else:
                        start_verse(number, rest, page_no)
                    uncertain.append({
                        "chapter": chapter,
                        "verse": number,
                        "issue": "ambiguous",
                        "excerpt": rest[:160] or line,
                        "suggested_review": "This number duplicates an earlier "
                                            "verse in the same chapter (the "
                                            "translation restarts numbering "
                                            "for new sections). Confirm the "
                                            "verse number or renumber.",
                    })
                    continue
                if in_notes:
                    flush_notes()
                    in_notes = False
                seen_numbers.add(number)
                expected_next = number + 1
                start_verse(number, rest, page_no)
                continue

            if in_notes:
                note_lines.append(line)
                continue

            if current is not None:
                current["text_lines"].append(line)

    flush_notes()
    flush_verse()

    # --- assemble records + uncertainty flags -------------------------------
    out_verses: list[dict] = []
    for v in verses:
        text = _join_lines(v["text_lines"])
        flags = _quality_flags(chapter, v["verse"], text)
        record = {
            "chapter": chapter,
            "verse": v["verse"],
            "sanskrit_ref": f"Brihat Jataka {chapter}.{v['verse']}",
            "translation_text": text,
            "keywords": _keywords(text),
            "pages": [v["start_page"]] if v["start_page"] else [],
        }
        if v.get("notes"):
            record["notes"] = v["notes"]
        combined = list(dict.fromkeys([*v.get("flags", []), *[f["issue"] for f in flags]]))
        if combined:
            record["flags"] = combined
        out_verses.append(record)
        for flag in flags:
            uncertain.append({
                "chapter": chapter,
                "verse": v["verse"],
                "issue": flag["issue"],
                "excerpt": flag["excerpt"],
                "suggested_review": flag["suggested_review"],
            })
    return out_verses, uncertain


# ----------------------------------------------------------- quality checks

_OCR_GARBAGE_RE = re.compile(r"[~|§£¦½¼¾ºª¤]|:::|\.\.\.\.+")
_TERMINAL_RE = re.compile(r"[.?!:;\"”]$")


def _quality_flags(chapter: int, verse: int, text: str) -> list[dict]:
    flags: list[dict] = []
    if not text:
        flags.append({
            "issue": "broken",
            "excerpt": "",
            "suggested_review": "Verse extracted empty; check the PDF page by hand.",
        })
        return flags
    if _OCR_GARBAGE_RE.search(text):
        flags.append({
            "issue": "ocr",
            "excerpt": text[:160],
            "suggested_review": "OCR artifacts visible (garbled characters); "
                                "compare against the PDF page and correct.",
        })
    if len(text) < 60:
        flags.append({
            "issue": "fragment",
            "excerpt": text[:160],
            "suggested_review": "Verse is short for a Jataka stanza; verify it "
                                "was not truncated or merged with its neighbour.",
        })
    if not _TERMINAL_RE.search(text):
        flags.append({
            "issue": "truncated",
            "excerpt": text[-120:],
            "suggested_review": "Verse does not end with terminal punctuation; "
                                "verify the tail was captured.",
        })
    return flags


# ---------------------------------------------------------------- keywords

_STOPWORDS = {
    "the", "and", "of", "to", "a", "is", "in", "be", "are", "his", "her",
    "with", "for", "will", "or", "as", "at", "by", "from", "he", "she",
    "them", "their", "that", "this", "these", "those", "which", "when",
    "who", "whose", "whom", "if", "not", "no", "one", "two", "may", "shall",
    "would", "should", "can", "could", "into", "upon", "than", "then",
    "there", "also", "such", "so", "all", "any", "more", "most", "some",
    "other", "others", "its", "it", "has", "have", "had", "been",
    "being", "but", "because", "between", "over", "under", "through",
    "during", "about", "after", "before", "born", "birth", "person",
}


def _keywords(text: str, limit: int = 8) -> list[str]:
    words = re.findall(r"[A-Za-z]{4,}", text.lower())
    counts = Counter(w for w in words if w not in _STOPWORDS)
    return [w for w, _ in counts.most_common(limit)]


# ------------------------------------------------------------------- main

def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    pdf_path = repo_root / SOURCE_PDF
    if not pdf_path.exists():
        print(f"source PDF not found: {pdf_path}", file=sys.stderr)
        return 1

    doc = pymupdf.open(str(pdf_path))
    all_verses: list[dict] = []
    all_uncertain: list[dict] = []
    chapter_index: list[dict] = []

    for chapter in sorted(CHAPTER_PAGES):
        verses, uncertain = extract_chapter(doc, chapter)
        all_verses.extend(verses)
        all_uncertain.extend(uncertain)
        chapter_index.append({
            "chapter": chapter,
            "title": CHAPTER_TITLES[chapter],
            "source_pages": list(CHAPTER_PAGES[chapter]),
            "verse_count": len(verses),
        })
        print(f"ch{chapter:02d}: {len(verses):3d} verses, "
              f"{len(uncertain):2d} flagged")

    out_dir = repo_root / "backend" / "data" / "verse_store"
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "verse_store_version": STORE_VERSION,
        "source_pdf": str(pdf_path.relative_to(repo_root)),
        "source_pdf_pages": len(doc),
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "chapter_count": len(chapter_index),
        "verse_count": len(all_verses),
        "uncertain_count": len(all_uncertain),
        "policy": "Extracted faithfully from the OCR layer of the source PDF. "
                  "OCR-damaged verses are flagged uncertain and await Scholar "
                  "Reviewer clearance; nothing here is silently corrected.",
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "chapters.json").write_text(
        json.dumps(chapter_index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "verses.json").write_text(
        json.dumps(all_verses, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "uncertain.json").write_text(
        json.dumps(all_uncertain, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"\nwrote {len(all_verses)} verses, {len(all_uncertain)} uncertain "
          f"flags -> {out_dir.relative_to(repo_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
