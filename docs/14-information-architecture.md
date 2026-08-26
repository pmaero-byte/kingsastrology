# 14 — Information Architecture: One-Way Flow

### The user receives. The user does not query. Feedback flows back separately.

This document defines how a person moves through Kingsastrology to find what they are looking for, and the strict one-way shape of every reading. It overrides the interactive/chat and Prasna-query designs in earlier docs.

## 1. The one-way principle

- The product **presents**; the user **reads**. There is no chat, no question-and-answer dialogue, no conversational agent.
- The user's inputs are **facts** (birth data; optionally event anchors for rectification; language & altitude preferences). They are not prompts.
- Given those facts, the engine deterministically produces a **complete, static, verse-cited reading**. The user reads it top to bottom.
- **Feedback** is a separate, one-way channel: user → the team (see §6). It is not a conversation with the product.

## 2. Why one-way

1. **Faithfulness over flattery.** A dialogue tempts a system to say what the user wants to hear; a fixed reading holds to the source.
2. **Determinism.** One-way + no runtime AI (per `13-build-philosophy.md`) means the reading is reproducible and auditable.
3. **Clarity of purpose.** The user came to understand their strengths and weaknesses from the Brihat Jataka — not to debate a chatbot. A structured reading serves that directly.
4. **Reach.** A static reading works offline, on low-end devices, in any language, with voice read-aloud — no inference dependency.

## 3. The logical structure (so the user finds what they seek)

The reading is organized in a **fixed, predictable order** so a returning user always knows where a thing lives. Each section is composed from the matching `rules/` chapters.

```
1. The Gate              — what this is, the source, the privacy promise, the dignity pledge
2. Your Chart at a Glance — lagna, Moon nakshatra, Sun sign, the planets & their dignity (Ch I–III)
3. Who You Are           — temperament from Moon-nakshatra (Ch XVI), Moon-in-sign (Ch XVII),
                           Sun & planets in their signs (Ch XVIII), planetary significations (Ch II)
4. Your Strengths        — exalted/own/Moolatrikona planets (Ch I, II), Raja yogas (Ch XI),
                           Nabhasa archetypes of strength (Ch XII), Lunar yogas (Ch XIII),
                           favorable Double yogas (Ch XIV), strong Kendras & bhavas (Ch XX),
                           strong Ashtakavarga houses (Ch IX)
5. What to Tend          — debilitated/afflicted placements, malefic yogas, difficult aspects
                           (Ch XVIII, XIX, XIV) — EACH paired with its offsetting strength
6. Your Vocation         — Karmajiva: sources of wealth & suited fields (Ch X)
7. The Season You Are In — current Dasa & Antardasa as life-pacing (Ch VIII)
8. Your Life-Stage       — Ayurdaya as pacing context, wide band, no death date (Ch VII)
9. Early-Life Note       — Balarishta, a gentle "tend carefully" notice only (Ch VI)
10. The Closing Charge   — a king's instruction: how to live well with this knowledge,
                           ending on dignity; the planets indicate tendency, not verdict
```

- **Strengths before what-to-tend** (Pillar 3) is enforced by the fixed order, not by an AI at runtime.
- **Every claim in every section is footnoted to its verse**; "where is this written?" is one tap away and opens the verse in the Verse Explorer.

## 4. Navigation model (finding what they seek)

- **Primary path:** Gate → enter birth data → the full reading (§3), scrollable, section-anchored.
- **Section jump-rail:** a persistent, labeled index (the 10 sections) so a user can jump straight to "Your Vocation" or "The Season You Are In." This is how a user *finds what they are looking for* without a search/chat crutch.
- **Verse Explorer (no birth data needed):** browse all 20 chapters' verses and the compiled yoga catalog. A reader who wants the source itself, or who wants to look up a specific yoga/term, goes here. Public on Web; present on all platforms.
- **Term glossary:** Kalapurusha, Kendra, Upachaya, Dasa, Ashtakavarga, Nabhasa, etc. — defined from Ch I–III, linked from any reading.
- **"Where is this written?"** from any claim → the exact verse, in context.
- **Altitude toggle:** child mode / scholar mode on the same frozen content (per `13-build-philosophy.md` §3 `re-leveler`). Verse always preserved.

## 5. Inputs (facts, not prompts)

| Input | Purpose | Required |
|----|----|----|
 Birth date, time, place (→ lat/long on the round Earth) | Compute the chart | Required |
 Event anchors (dates + nature) | Rectification, if birth time unknown | Optional |
 Language | Render frozen text + preserved verse | Optional (default) |
 Altitude (child / scholar) | Re-level frozen text | Optional |
 Voice read-aloud on/off | Accessibility | Optional |

No free-text question field exists in the natal product. (Prasna / horary, which is inherently a question→answer dialogue, is **out of scope** for the one-way product and is not built.)

## 6. Feedback channel (user → team, one-way)

- A dedicated, simple **Feedback** affordance on every reading and in the Verse Explorer: the user can send a comment (e.g., "this verse seems mis-translated," "this reading helped," "a citation looks wrong").
- Feedback flows to the **team** (Reliability + Source stewards), not back into the user's reading. It feeds the build-time loop: a flagged verse → `verse-indexer`/Scholar Reviewer; a flagged rule → `verification`/Scholar Reviewer; a tone concern → Ethics Officer.
- The user is told their feedback improves the source-fidelity of the product for everyone. No realtime reply is implied.
- Feedback never attaches to or alters a person's chart record.

## 7. Cross-platform consistency

The same 10-section structure, jump-rail, Verse Explorer, and feedback channel render on Web, Android, iOS, and macOS. The macOS "scholar desk" adds the side-by-side verse/rule inspector on top of the same structure (`06-platform-plans/macos.md`). One-way shape is identical everywhere.

## 8. What is explicitly removed vs. earlier docs

- No "Ask the King / Prasna" query interface (was `counselor-prasna`).
- No conversational Mirror agent (the Mirror is now a deterministic composed reading, §3).
- No chat input field. No runtime generation of any kind.
- Rectification, when added, is input-data-driven and deterministic (`13-build-philosophy.md` §7).

---

*See also: `13-build-philosophy.md` (no AI in production), `rules/README.md` (the rule-base that feeds §3).*