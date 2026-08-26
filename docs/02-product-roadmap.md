# 02 — Product Roadmap
### The King's Plan, in four phases and four platforms.

This roadmap executes the tier order from `01-source-text-foundation.md` (Tier 1 mirror → Tier 2 counselor → Tier 3 full court) across four platforms: **Web, Android, iOS, macOS**. It is sequenced so that faithfulness arrives before breadth — the mirror must be true before the court is large.

---

## Guiding sequence

1. **Build the engine bed once** (core compute + rule-base + verse store) — shared across all four platforms.
2. **Prove the mirror on one platform first** (Web) — because it is the fastest to iterate and the easiest to verify.
3. **Then carry the same faithful mirror to the native apps** (Android, iOS, macOS) — same engine, native shells.
4. **Then expand the court** (Tier 2, Tier 3) on all platforms in lockstep.

The engine is built once; the platforms differ only in shell, offline behavior, and affordances.

---

## Phase 0 — Foundation & Source Ingestion  *(weeks 1–4)*

**Goal:** a clean, machine-readable *Brihat Jataka* and a deterministic compute core.

- Digitize and verse-index the source PDF → `sourcetext/` → structured `verse-store` (chapter, verse, Sanskrit, translation).
- Stand up the **Spherical-Sky Compute Engine** (A1) with Swiss Ephemeris; verify against known charts (mine included, as recorded).
- Implement **Dignity & Relation Lookup** (A2), **Dasa Timeline** (A4), **Ashtakavarga** (A5), **Bhava/Varga** (A6).
- Establish the **verse-citation contract** in the data layer: every computed fact carries its `(Ch, verse)`.
- Stand up the agent court scaffolding (`.claude/agents/`) and the **Rule-Compiler** + **Verification** pipeline.

**Exit criteria:** a headless API that, given birth data, returns a fully verse-cited chart JSON. All compute verified against test charts. No UI yet.

## Phase 1 — The Mirror (Tier 1)  *(weeks 5–12)*

**Goal:** the flagship **Strengths & Weaknesses Self-Portrait** (B1), live on Web.

- Compile rules for Ch. 2, 3, 9, 17, 18, 19, 21, 12, 13, 24 via the Rule-Compiler agent; each verified.
- Build the **Mirror report** pipeline: computed facts + verses → tone-gated, cited prose, leading with strength, closing on dignity.
- Web app: birth-data entry (with privacy UX), the Mirror report, tap-to-verse citations, "where is this written?" pane.
- **Tone-Gate**, **Citation**, and **Ethics** agents enforced on every render.
- Plain-language re-leveler (C2): child mode + scholar mode.

**Exit criteria:** a real user can enter birth data on the web and receive a faithful, verse-cited, dignity-closing self-portrait. ≥95% of citations auto-verified to the verse store. Tone-gate blocks 100% of doom-leading drafts in QA.

## Phase 2 — The Counselor (Tier 2), all platforms  *(weeks 13–24)*

**Goal:** carry the mirror to Android/iOS/macOS and add the conversational court.

- Native shells: Android (Kotlin/Jetpack), iOS (Swift/SwiftUI), macOS (Swift/SwiftUI, possibly Catalyst/macOS-native).
  - Shared engine via the API; **on-device cache** of the user's chart; **offline read** of already-generated reports.
  - macOS: a richer scholar-grade view (side-by-side verse + chart + divisional).
- Add features: **Ask the King / Prasna** (B2), **Vocation Counselor / Karmajiva** (B4), **Ashtakavarga transit** (A5 UI), **Aspect effects** (Ch. 20), **Lunar & Ascetic yogas** (Ch. 14, 16), **Women's reading** (B6).
- **Voice Court** (C3): spoken counsel on mobile (ASR/TTS) for accessibility.
- Multi-language (C1): launch with [English + 2 Indic languages; expand after].

**Exit criteria:** the Mirror is consistent across all four platforms (same citations, same tone). Prasna answers are verse-cited and ethics-gated. Voice path works on Android & iOS.

## Phase 3 — The Full Court (Tier 3)  *(weeks 25–40)*

**Goal:** the complete chapter coverage, the difficult features done responsibly.

- **Birth-Time Rectification** (B3) with confidence band and event-anchor interview.
- **Ayurdaya life-stage** (B5) — life-stage pacing only; precise-death-date forbidden by ethics.
- **Nisheka fertility timing** (B7) — framed as favorable timing, not medical guarantee.
- **Divisional charts UI** (D9, D10, etc.) with verse-cited readings (Ch. 22).
- **Balarishta early-life screen** (Ch. 7) — delivered as a gentle "tend carefully in early years" notice, never as a death forecast for a child. **Hard ethics review.**
- **Misc & unusual-birth context** (Ch. 1, 4, 6, 23, 28).
- Scholar tooling on macOS/Web: rule-base inspector, verse explorer, yoga catalog.

**Exit criteria:** all 28 chapters represented and verse-cited; rectification ships with confidence band; ethics agent passes full audit.

## Phase 4 — Stewardship & Scale  *(ongoing)*

- Rule-base hardening, more languages, accessibility, localization for the round Earth (any lat/long).
- Public "verse explorer" so anyone can read the source without a chart.
- Community verification: scholars can flag a verse interpretation; flagged items route to the Verification agent + human review.
- Platform parity SLAs, observability, and the never-ending tone-gate QA.

---

## Platform delivery summary

| Platform | Phase 1 | Phase 2 | Phase 3 | Distinctive role |
|----|----|----|----|----|
| **Web** | ✅ Mirror launches here | + Prasna, vocation, voice (Web Speech) | + Rectification, scholar tools | Fastest iteration, public verse explorer, scholar mode |
| **Android** | — | ✅ Mirror + offline cache | + Voice court, rectification | Reach across India; offline-first for low-connectivity |
| **iOS** | — | ✅ Mirror + offline cache | + Voice court, rectification | Privacy-first polish; Apple-native UX |
| **macOS** | — | ✅ Mirror, scholar view | + Divisional deep view, rule inspector | The scholar's desk: side-by-side verse/chart/rules |

## What "done" means for a feature

A feature is done only when **all** hold:
1. Its rule(s) are compiled from a named verse and verified.
2. Its output cites `(Ch, verse)` and the citation is auto-verified.
3. It passes the Tone-Gate (no doom-leading) and Ethics (no forbidden verdicts).
4. It is consistent across every platform that has shipped it.
5. A real user can tap any claim and reach the source verse.

---

*Next: [03 — Project Scope](./03-project-scope.md)*