# 16 — The Tafhīm Protocol: Implementation Ledger

*Response to "The Tafhim Protocol — How al-Bīrūnī would build the mundane instrument." This page maps each demand of that report to what now exists in this repository, and states plainly what is still not built. Nothing here claims more than it has proven.*

---

## I. The six layers, as built

| Layer | Demand | Built | Where |
|----|----|----|----|
| **0 — Zīj** | Ephemeris rows as sacred text: versioned, hash-pinned, reproducible | ✅ `services/sky_engine.py` + `services/zij.py`: SHA-256-pinned element constants, per-row tier stamp, pinned sample + manifest, `GET /api/v1/zij/manifest` | Rows reproducible from constants alone; Python↔JS agree to 5×10⁻⁷°; PyEphem-validated (VER-001, VER-002) |
| **1 — Qānūn** | Pure functions; every factor cites its rule; three epistemic tiers | ✅ `services/qanun.py`: paksha, kāla-bāla (sect + paksha), dignity, natural nature, naisargika rank, drishti, sun-separation, dispositor — every factor carries `tier` ∈ {measured, doctrine, hypothesis} and a rule citation (R-1.6, R-1.13, R-2.1 canon, R-2.5, R-2.13, R-2.21) | Verse citations verified against the rule files themselves; a test bans verdict-language from the engine |
| **2 — Tribunal** | Falsification ledger as a loud surface, a tab not a footnote | ✅ `/tribunal` page + `GET /api/v1/tribunal`; seeded with 2 verifications, 6 limitations, and **empty** retraction & pre-registration schemas | `data/tribunal/ledger.json` — append-only policy stated in the file |
| **3 — Astrolabe** | Dial as interface; works offline in spirit | ✅ Spacetime Clock (`/clock`): drishti chords (R-2.13) drawn as strength-coded sight-lines, ± error bars per graha | True offline (service worker) not yet built |
| **4 — Madrasa** | Long-press any element → the lesson, Q&A form | ✅ Tafhīm mode: tap any legend row (or concept) → lesson panel in EN/हिंदी/العربية, each lesson tier-stamped | Lessons cover the 9 grahas + retrograde, nakshatra, sidereal-vs-tropical, drishti |
| **5 — Caravanserai** | Open, documented endpoints | ✅ `/api/v1/{sky,zij/manifest,zij/row,calendars,crescent,tribunal}` — auto-documented at `/docs` (OpenAPI) | No auth, no keys: scholars can replicate |

## II. The amendments, as built

| Amendment | Built | Honesty note |
|----|----|----|
| **Multi-calendar** (one timestamp, many eras) | ✅ Hijrī (tabular), Solar Hijrī/Jalālī (Birashk) **+ Yazdgirdī year**, Vikram Saṃvat, Śaka (official), Kali ahargaṇa, Julian & Gregorian — live on the clock and at `/api/v1/calendars` | Each converter prints its algorithm and error; anchors unit-tested (Hijrī epoch, Kali epoch, Śaka new year, Julian 1582) |
| **Restore the crescent** | ✅ `services/crescent.py` + `/api/v1/crescent` + hilal panel on the clock: sunset (refraction + horizon dip from elevation), topocentric Moon (parallax), ARCL/ARCV/ΔA, illumination, Moon age (negative before conjunction), moonset lag, Yallop q-band | **Raw observables are [measured]; the A–F class is [hypothesis]** — the implementation is unverified against Yallop's original tables (Tribunal LIM-004). Never a religious ruling; the disclaimer ships on screen and in the API |
| **Topocentric pride** | ✅ lat/lon/**elevation** entry (persisted); horizon dip 1.76·√h; Bennett refraction; lunar parallax throughout the crescent path; sect (day/night) computed from the true solar altitude at the observer | Full observatory-grade corrections (geodetic datum, pressure/temperature) not yet |
| **Error bars visible** | ✅ ±arcmin column in the clock legend (from the published validation constants); `err_arcmin` on every zīj body; `ayanamsa_err_arcmin` on rows | Percentile bands behind gauges: not yet (no gauge UI yet) |
| **Languages** | ✅ i18n scaffold: English, हिंदी, العربية with RTL layout flip, persisted per visitor; lessons trilingual | 8 languages + bilingual technical glossary: scaffold exists, corpus not yet |
| **Outcome ledger** (harvest outcomes nightly) | ⚠️ Structure only: the Tribunal accepts verification entries with evidence hashes; no nightly ingestion job exists in this repo | This repo computes no weather/treaty claims to harvest; the loop belongs with the mundane-weather engine's own repo |
| **Hallway of thirty** | ❌ Not built | Usability testing is a human-ministry task (docs/08) |
| **Persistent identifiers** | ⚠️ Zīj constants hash + pinned sample exist; no DOI/ARK minting | |
| **The 2028 wager governance** | ➖ Out of scope for this repository | The frozen-scores corpus lives in the sibling predictions repo; the Tribunal here carries the schema this pattern would demand (pre-registration with script hash + adjudicator) |

## III. Where this build deliberately diverges

1. **Doctrine source.** The protocol's studio engine is Hellenistic (Chaldean hour-lords, receptions, VOC). This repository's source of truth is the **Brihat Jataka**. The Qānūn therefore implements the canon of *this* court — kāla-bāla sect instead of Chaldean lords, R-2.13 drishti instead of applying/separating arcs — rather than importing a foreign doctrine under a borrowed name. Where a concept has no rule here (combustion), the engine publishes the **raw geometry** and asserts nothing.
2. **Rahu/Ketu drishti.** R-2.13's table covers the seven grahas. The engine draws no chords for the nodes rather than inventing one (Tribunal DIS-002).
3. **The zīj window.** The protocol asks 1600–2126. The JPL approximate elements are fitted 1800–2050; rows outside are computed but stamped `tier: extrapolated`. We will not print an extrapolated number wearing a measured badge — extend the window only by upgrading the element set (Swiss Ephemeris, Phase-0 A1).

## IV. Verification summary (what we measured before asserting)

- **PyEphem cross-check** (2026-08-26 10:57 UT): Sun 0.01°, five planets ≤ 0.10°, Moon 0.36°.
- **Cross-language**: Python `sky_engine` vs browser `ephemeris.js` — worst Δ 4.6×10⁻⁷° over three epochs (2000, 2026, 2030).
- **46 backend tests** green: zīj tiering & manifest, factor tiers/citations, drishti geometry (incl. Mars special sight, orb, node exclusion), calendar anchors, crescent behaviour across a real lunation (Sep 2026: q rises −0.82 → 0.51 → 1.81; pre-conjunction age negative), API contract, OpenAPI documentation.
- **Visual**: clock verified in-browser — bezel, calendars strip, hilal panel, drishti chords, lessons, Arabic RTL.

## V. The next honest steps (in the protocol's own order)

1. **Crescent verification** — check the Yallop implementation against HMNAO tables with a scholar; move LIM-004 from hypothesis to measured or engrave its retraction.
2. **Swiss-Ephemeris engine (A1)** behind `/api/v1/zij` — retires the approximation caveats LIM-002/LIM-003 and widens the window honestly.
3. **Offline clock** — nightly cache of the zīj rows (the protocol's "brass needed no network").
4. **Outcome ledger loop** — nightly ingestion + auto-scoring, once this court renders claims worth scoring.
5. **More languages** — the scaffold takes a new tongue as one dict + one lesson set.
6. **The hallway of thirty** — Karachi, São Paulo, Lagos.

---

*Built 2026-08-26. Every number on these screens carries its lineage; every limitation is published at* `/tribunal`.
