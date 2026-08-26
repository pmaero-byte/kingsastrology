# 03 — Project Scope

## 1. The one-line scope

> *Kingsastrology is a faithful, verse-cited, dignity-closing digital reading of the Brihat Jataka, delivered as strengths-and-weaknesses self-knowledge to any person on the round Earth, on web, Android, iOS, and macOS.*

## 2. In scope

**Source & doctrine**
- All 28 chapters of the *Brihat Jataka* as the sole doctrinal source (per `01-source-text-foundation.md`).
- Verse-indexed, machine-readable verse store; every claim cites `(Ch, verse)`.

**Computation (deterministic, exact)**
- Spherical-sky geocentric ephemeris; ayanamsa-corrected; true lat/long on the round Earth.
- Lagna, 9 grahas, 12 bhavas, 27 nakshatras, divisional vargas.
- Dasa/antardasa timelines; Ashtakavarga scores; dignity & relation tables.
- Yoga detection via a verified rule-base compiled from verses.

**AI counseling (grounded, leashed)**
- The Mirror (strengths & weaknesses self-portrait) — flagship.
- Prasna (horary query), Karmajiva (vocation), life-stage (Ayurdaya as pacing), women's reading, fertility timing, birth-time rectification.
- Tone-Gate, Citation, Ethics, Verification guardrail agents.
- Translation to multiple languages with verse preserved; plain-language re-leveling; voice I/O.

**Platforms**
- Web (PWA), Android, iOS, macOS — same engine, native shells, offline read of cached reports.

**User experience**
- Birth-data privacy UX; tap-to-verse; "where is this written?"; child & scholar altitudes; accessibility (voice, large text).

## 3. Out of scope (explicitly)

- **Any doctrine not in the Brihat Jataka.** No Western tropical sun-sign columns, no imported Tamil/New-Age systems, no invented yogas. (Other classical works may be considered in a far future, only after the Jataka is fully served — and only if added as a *named, separate* source layer, never blurred with the Jataka.)
- **Medical, legal, or financial verdicts.** Astrology counsels self-knowledge; it does not replace licensed professionals. The Ethics agent blocks these.
- **Precise death-date prediction.** Ayurdaya is delivered as life-stage pacing only.
- **Fatalistic / doom-leading presentation.** Forbidden by Pillar 3 and the Tone-Gate.
- **Anonymous mass horoscope columns** ("Aries: today you will…"). We read *your* chart, not your sign.
- **Sale of birth data or advertising-driven data brokerage.** Birth data is the user's; never sold.
- **Matchmaking as a verdict.** Synastry, if ever added, is framed as mutual strengths/tensions to navigate — never as a pass/fail verdict on a relationship or a person.
- **Gambling / "lucky number" features.** Not what the king instructed.

## 4. MVP definition (Phase 1)

The Minimum Viable Product is the **Mirror on Web**:

1. Enter birth data (date, time, place) with clear privacy framing.
2. Compute the chart (A1–A6) and detect Tier-1 yogas.
3. Render the **Mirror self-portrait** (B1): who you are → strengths → what to tend (with offsetting strengths) → the season you are in → a dignity-closing charge.
4. Every claim tap-to-verse; "where is this written?" always available.
5. Tone-Gate, Citation, Ethics enforced.

**MVP success criteria**
- ≥95% of rendered citations auto-verified against the verse store.
- 100% of QA doom-leading drafts blocked by Tone-Gate.
- 0 medical/legal/financial verdicts produced (Ethics audit clean).
- A first-time user can complete a reading and reach the source verse in ≤3 taps from any claim.
- Faithfulness review by ≥1 subject-matter reader passes before public launch.

## 5. Phased scope gates

| Phase | Scope gate | Must be true to advance |
|----|----|----|
| 0 → 1 | Engine bed + verse store | Compute verified against test charts; citation contract in data layer |
| 1 → 2 | Mirror on Web | MVP success criteria all met |
| 2 → 3 | Counselor on all platforms | Cross-platform citation & tone parity verified |
| 3 → 4 | Full court | All 28 chapters verse-cited; rectification ships with confidence band; full ethics audit passes |

## 6. Assumptions & dependencies

- The source PDF translation is treated as authoritative for verse text; a scholar review pass refines OCR artifacts before rules are compiled from any affected verse.
- Ephemeris: Swiss Ephemeris (or equivalent) underpins all computation.
- LLM access: a frontier reasoning model for the counselor agents, with deterministic rule application at runtime (the LLM renders, it does not decide yoga presence).
- Languages: launch languages depend on translation review capacity (see `07-organisation-structure.md`).

## 7. Constraints

- **Source fidelity is the hardest constraint** — it outranks speed, feature count, and growth. A faithful small product beats a vast unfaithful one.
- **Privacy by default** — birth data encrypted at rest, user-owned, deletable, never sold.
- **Accessibility** — voice and plain-language paths are not "nice to have"; the king instructs *all* his people.

## 8. Success measures (north stars)

1. **Faithfulness** — % of claims auto-verified to verse; subject-matter review pass rate.
2. **Dignity of outcome** — user research shows readers end on courage/self-knowledge, not fear. (Surveyed explicitly.)
3. **Reach of the source** — % of users who tap through to a verse at least once (the source reaching the people).
4. **Cross-platform parity** — citation/tone consistency across the four platforms.
5. **Trust** — privacy posture independently auditable; user data deletable and honored.

---

*Next: [04 — AI Capabilities](./04-ai-capabilities.md)*