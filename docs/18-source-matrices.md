# 18 — Source Matrices: The Classified Brihat Jataka

### Every placement, aspect, conjunction and lord-arrangement the Brihat Jataka actually states — extracted verbatim, cited, and honestly gapped. Built from the open public-domain translation held in `sourcetext/`, cross-checked against the canonical chapter list.

This delivers the structural half of [doc 17](./17-laya-verse-classification.md)'s programme: where doc 17 classifies verses into *topics* for the King's Daily Brief, this doc classifies the source into *matrices* — the lookup grids a deterministic runtime needs before any topic card can name a data point. The build is done **true to the source texts**: every cell is a verbatim clause with its `(Ch, verse)` citation; what the source does not say is an explicit gap, never filled.

---

## 1. What was built

`backend/scripts/build_matrices.py` (build-time only, deterministic, no network) reads the Verse Store (`verse_store 2026.08.29`, 483 verses of the public-domain English translation of the Brihat Jataka) and emits ten matrices + a manifest into `backend/data/matrices/`, plus the canonical chapter map into the store:

| Matrix | Axes | Source chapters | Cells | State |
|----|----|----|----|----|
| `signs` | sign | 1 | 12 | 100% (colours OCR-flagged) |
| `houses` | house | 1, 18, 20 | 12 | 100% |
| `ascendants` | lagna sign | 1, 5, 17, 18, 20 | 12 | 100% **derived** |
| `nakshatras` | Moon × 27 asterisms | 16 | 27 | 24 classified, 3 `needs_review` |
| `planet_in_sign` | 9 grahas × 12 signs | 17, 18 | 108 | 84 classified; 24 node-row **gaps** |
| `planet_in_house` | 7 grahas × 12 bhavas | 20 | 84 | 100% (partly by the source's own reference rule) |
| `moon_sign_aspects` | Moon's sign × 6 aspecting planets | 19 | 72 | 100% |
| `moon_navamsa_aspects` | 7 navamsa lords × 6 aspecting planets | 19 | 42 | 41 classified, 1 `needs_review` |
| `conjunctions` | 21 unordered pairs | 14 | 21 | 100% |
| `house_lord_rules` | 12 lord-arrangement rules | 1, 10, 11, 18, 20, 22 | 12 | 100% draft |

**365 cells, 0 dangling citations, every excerpt verified verbatim against its verse by test.**

## 2. Method — curation verified by machine, not trusted

The classifier is a **hybrid**: hand-curated verse→cell maps (from a close reading of the OCR), each *programmatically verified* — a cell is only emitted when its clause actually contains the planet/sign/house tokens it claims. Failures downgrade to `needs_review` or explicit gaps, never silently accepted. Three source behaviours required special machinery:

1. **Shared clauses.** The translation often gives one clause for two signs ("Mars in Aries or Scorpio"). Both cells reference the same clause with `shared`/`shared_with`.
2. **Composition by reference.** For planets in houses, the source itself says "in the remaining houses he produces the same effects as the Sun [Jupiter] in those places" (Ch 20 v6/v8/v9). Those cells are materialised with `via_reference` and cite **both** the composing verse and the referenced cell's verse — the grid is complete *because the source composes it*, not because we did.
3. **Derived ascendants.** Brihat Jataka has no per-lagna chapter. The ascendants matrix is composed from the source's own extension rule — Ch 18 v 20: "effects described for the several signs … are mentioned also for the rising sign" — plus Ch 1 sign qualities, Ch 20 lagna-specific sub-cases (Sun/Moon/Saturn in specific rising signs), and Ch 5 places/directions. Every cell carries its `derivation` chain. Nothing is paraphrased into new doctrine.

OCR handling is variant-based and evidence-driven: every variant token in the script (`'VentlS'`, `'SUD'`, `'Man'`, `'M.:rcury'`, `'t Hh'` for 11th, `'ta:urus'`…) was observed in the scan. Nakshatra names OCR-shortened to single letters are aligned by the text's own canonical order — confirmed where the source itself abbreviates ("P. Phalguni" = Pubba).

## 3. The canonical chapter map (store-numbering reconciliation)

`backend/data/verse_store/chapter_map.json` records store chapter ↔ Sanskrit adhyāya name ↔ English title, cross-checked against the canonical 28-chapter list (retrieved from the public chapter list, 2026-09-21). Recorded divergences:

- The translation holds **chapters 1–27 only**; Ch 28 (*Upasamharadhyaya*, concluding) is absent from this edition.
- **docs/01's map does not match the translation** (its ch 2/3 split, ch 27 Prasna and ch 28 Nisheka-Adhana do not exist in this text). **Store numbering is canonical for every citation in the matrices, rules, and briefs.** docs/01 requires a correcting pass.
- **Ch 18 contains a misnumbered record**: Saturn's first verse is stored as v 11 (duplicate number with Mercury's v 11). The builder selects records by content and the defect is recorded in the map.

## 4. Declared gaps (the source's honest edges)

| Gap | Extent | Note |
|----|----|----|
| Rahu/Ketu placements | 24 cells (signs rows) + absent from houses/aspects/conjunctions | the nodes are defined (Ch 2 v 3) but given **no placement-results anywhere** in this text; left unfilled by charter (no chapter, no doctrine) |
| Systematic 12×12 lord table | — | the source states lord doctrine as **principles + specific Raja-yoga charts** (HL-1…HL-12), not a "lord of N in house M" grid; that grid belongs to later texts and is not imported |
| Jyeshta, Uttarashadha, Dhanishta | 3 nakshatra cells | names dropped by OCR; clause boundaries unrecoverable automatically — queued for human recovery |
| Mars-navamsa × Saturn | 1 clause | verse truncated mid-sentence in the translation; kept as `needs_review` with the citation |

## 5. Verification (what the tests enforce)

`backend/tests/test_matrices.py` (15 tests, part of the backend suite — 107 passed total):

- **Verbatim guarantee** — every excerpt is a whitespace-normalised substring of a record behind its citation. Nothing invented survives this test.
- **Citation integrity** — every `(Ch, verse)` resolves in the Verse Store.
- **Grid completeness & uniqueness** — expected cell counts per matrix; duplicates fail.
- **Gap honesty** — gap cells carry no text and no citation, only a note.
- **Known facts** — 21 conjunction pairs, 7 grahas fully placed, 27 nakshatras, derived ascendants carry derivation chains, composed cells cite both verses.
- **Determinism** — rebuilding into a scratch directory is byte-identical (sha256 per file).

## 6. Status and path to the runtime

Per `rules/README.md` §5 and doc 13: everything here is `auto-draft` / `derived` / `draft` — **nothing enters the runtime until the Scholar Reviewer verifies it**. The matrices are *source indexes* (what the verse says, verbatim); converting them into user-facing Effect text remains the rule-base's job, with tone-gate/citation/ethics as always. The review surface is deliberately pleasant: a reviewer sees one clause at a time with its citation, a repair note field, and the OCR flags.

Once verified, these matrices become the data-point layer under doc 17's Daily Brief topic cards: a Livelihood card's "10th house from Lagna: Taurus, occupied by Saturn in its own sign" line reads its placement from `planet_in_house`, its dignity from the `signs`/Ch 2 tables, and its counsel from verified rules citing the same verses.

## 7. Rebuild

```bash
python3 backend/scripts/build_matrices.py          # writes data/matrices/*.json + manifest
python3 -m pytest backend/tests/test_matrices.py   # enforces §5
```

The build reads only `backend/data/verse_store/`; reruns are byte-identical; warnings (5 standing, all OCR-related) print to stderr and land in `manifest.json`.

---

*Built artifacts: `backend/data/matrices/` (10 matrices + `manifest.json`), `backend/data/verse_store/chapter_map.json`. See also [17 — Laya Verse Classification](./17-laya-verse-classification.md) (topics layer), [`rules/README.md`](../rules/README.md) (rule lifecycle), [`docs/14`](./14-information-architecture.md) (one-way presentation).*
