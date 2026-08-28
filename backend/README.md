# Kingsastrology Backend

Deterministic backend scaffold for the one-way Kingsastrology product.

## Scope

- Loads only `rules/ch08_*.md` through `rules/ch20_*.md`.
- Ignores Chapters 1-7 by design.
- Treats the filename chapter as canonical for backend scope.
- Surfaces mismatches in legacy rule headers/citations as warnings.
- Does not run AI at runtime.

## Verse Store (M1)

The verse-indexed Brihat Jataka source text — the layer every citation
resolves against.

- **Source:** `sourcetext/pdfcoffee.com_brihat-jataka-of-varahamihira-pdf-free.pdf` (Sagar Publications translation).
- **Ingestion (build-time, verse-indexer):** `scripts/ingest_verse_store.py` — run it to rebuild:

  ```bash
  python3 scripts/ingest_verse_store.py
  ```

  The script extracts all 27 chapters faithfully from the PDF's OCR layer,
  strips mechanical page noise, recovers OCR-damaged verse markers
  ("S." for 5, "B." for 8, "It." for 11, "2,0." for 20 …), and flags every
  damaged/ambiguous verse in `data/verse_store/uncertain.json` for Scholar
  Reviewer clearance. Nothing is silently corrected.
- **Artifacts:** `backend/data/verse_store/{manifest,chapters,verses,uncertain}.json`.
- **API:**
  - `GET /api/v1/verse/{chapter}` — all verses of a chapter
  - `GET /api/v1/verse/{chapter}/{verse}` — one verse, a range ("1-3"), or a list ("1, 4") — powers tap-to-verse
  - `GET /api/v1/verse-store/manifest`
  - `GET /api/v1/verse-store/uncertain`
  - `GET /api/v1/citation-check` — every rule citation resolved against the store (the build-time citation gate)

## Chart engine (A1-A6)

Birth data → `ChartFactBundle` (docs/10 §7): geocentric positions, lagna,
whole-sign bhavas, nakshatra, Vimshottari dasa timeline, ashtakavarga,
navamsa, dignity. Deterministic; no AI; every doctrinal field cites
(chapter, verse).

- **Swiss Ephemeris (A1)** — `app/services/swe_engine.py`. Optional at
  runtime; install project-locally where pip is PEP-668-blocked:

  ```bash
  python3 -m pip install --target ./vendor pyswisseph
  ```

  When unavailable the engine falls back to the validated approximation
  (`sky_engine`) with a provenance note (Tribunal LIM-002/LIM-003/LIM-006).
- **Endpoints:**
  - `POST /api/v1/chart/compute` — birth data → ChartFactBundle
  - `POST /api/v1/reading/mirror` — birth data → chart + deterministic rule
    match + composed reading. Readings are served with
    `verification_passed=true` when every matched rule is `verified`;
    otherwise the reading is **withheld** at the M3 scholar-review gate
    (AGENTS.md §4) with the reason and the blocking rule ids.
  - `GET /mirror` — the Mirror page (birth-data form → chart → tap-to-verse).

## Scholar review status (M3, as of 2026-08-29)

- **19 rules frozen** (`Status: verified` in `rules/`): R-12.1, R-16.12,
  R-18.{Jupiter.Gemini, Mars.Capricorn, Mercury.Aquarius,
  Saturn.Sagittarius, Sun.Aquarius, Venus.Capricorn}, R-19.6, R-19.23,
  R-20.1–R-20.9. Each was cross-checked against its cited verse in the
  verse store (fuzzy text match ≥0.6 / exact for recovered stanzas) and its
  condition was confirmed machine-testable. Decisions are logged through
  the review workbench (`/review/api/rules/.../review`).
- **Citation correction:** the rules in `ch08`–`ch11`, `ch13`–`ch19` cited
  "Ch 4" for every verse (a drafting mislabel of the translation's chapter
  numbering). Corrected to each file's own chapter; the citation gate now
  shows 313/318 resolving, with the 5 remaining gaps enumerated as
  verse-store re-extraction TODOs (Ch 8 v 18; Ch 18 v 17).
- **Rejected:** R-20.10 (its bad-effect scaling is not in Ch 20 v 11,
  which scales only good effects; its condition is also not
  machine-testable — the evaluator now reports it as unsupported).
- **Remaining:** 271 rules still `draft`, awaiting the same review.

## Run

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```

Useful endpoints:

- `GET /` — redirects to the frontend
- `GET /app` — polished rule review frontend
- `GET /health`
- `GET /rules/scope`
- `GET /rules/chapters`
- `GET /rules/chapters/12`
- `GET /rules?status=draft&classification=strength`
- `GET /rules/by-id/R-12.3`
- `POST /reading/compose`
- `POST /chart/evaluate`
- `POST /reading/from-chart`
- `GET /review` — manual rule review workbench
- `GET /review/rules?chapter=12` — filtered review workbench

The backend currently accepts chart facts that have already been computed by an ephemeris/chart engine. It does not calculate planetary positions yet. Given those facts, `/chart/evaluate` deterministically matches supported rule conditions and `/reading/from-chart` composes a one-way draft reading from the matched rules.

## Manual Rule Review Frontend

Open:

```text
http://127.0.0.1:8000/app
```

Each rule has fields for:

- decision: `Unreviewed`, `Approved`, or `Needs Improvement`
- reviewer
- comments
- improvements

Saved reviews are written to:

```text
backend/data/rule_reviews.json
```

The classic server-rendered fallback remains available at:

```text
http://127.0.0.1:8000/review/rules
```

Example:

```bash
curl -s http://127.0.0.1:8000/chart/evaluate \
  -H 'content-type: application/json' \
  -d '{
    "planets": [
      {"name":"Sun","sign":"Aries","house":1},
      {"name":"Jupiter","sign":"Cancer","house":10}
    ],
    "allow_draft": true,
    "compose": true
  }'
```
