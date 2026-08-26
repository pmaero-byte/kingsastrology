# Rules — Authoring Format & Lifecycle

### The deterministic rule-base for Kingsastrology, written as markdown **before any code.**

> **Production rule:** There is **no AI at runtime** in this product. AI is used **only to build** these rule files (drafting, verifying, translating). Every rule below is a *planning artifact* that must pass **human scholar review** before it is frozen into code. Once frozen, the runtime applies these rules **deterministically** — no LLM, no generation, no chat. The user receives a one-way, verse-cited reading computed from these rules.

## 1. Scope

Rules are authored for **Chapters 1–20** of the Brihat Jataka only (through *Planetary Aspects*). Chapters 21–28 are out of scope for now.

## 2. File layout

```
rules/
  README.md            <- this file (format + lifecycle)
  ch01_<name>.md       <- one file per chapter, 1..20
  ...
  ch20_<name>.md
```

## 3. Per-chapter file header

```markdown
# Chapter N — <Sanskrit name> — <English subject>

- **Source:** Brihat Jataka, Chapter N
- **Source text:** sourcetext/pdfcoffee.com_brihat-jataka-of-varahamihira-pdf-free.pdf
- **Runtime use:** deterministic, one-way; no AI at runtime
- **Authoring:** drafted (AI-assisted) → human scholar review → frozen
- **Status legend:** see §5
```

## 4. Rule entry format

Each rule is one block:

```markdown
## R-<ch>.<n> — <short name>

- **Cites:** Ch N, verse V  (e.g. Ch 17, v 1)
- **Classification:** strength | tend | neutral | table
- **Condition:** <a precise, machine-testable statement over:
    graha, rasi, nakshatra, bhava? (n/a for ch1-20 except dignity), aspect,
    dignity, dasa, ashtakavarga, conjunction>
- **Effect (one-way, dignity-closing):** <plain-language outcome the user reads;
    strengths stated as gifts; "tend" items paired with their offsetting strength
    or constructive framing — never doom-leading>
- **Verse (source):** "<quote the translation text verbatim, OCR-corrected only
    for obvious scanning errors; if unreadable, write [OCR UNREADABLE]>
- **Status:** verified | draft | blocked_ocr
- **Notes:** <OCR issues, alternate readings from the translator's notes,
    dependencies on other rules, flags for scholar review>
```

### Field rules

- **Cites** must point to a real verse in the chapter. Number verses by the translator's numbering shown in the source (the "1.", "2.", … markers).
- **Condition** must be testable from the computed `ChartFactBundle` (see `docs/10-data-models.md`). No prose-only conditions. If a condition cannot be made testable, mark `Status: draft` and explain in Notes.
- **Classification:**
  - `strength` — a favorable indication / gift to highlight first.
  - `tend` — an unfavorable or delicate indication, always paired with an offsetting strength or constructive framing (Pillar 3).
  - `neutral` — descriptive (e.g. temperament), neither good nor bad.
  - `table` — a fixed lookup (dignity table, sign lords, nakshatra lords) used by other rules.
- **Effect** is the **one-way text the user reads**. Write it as the king instructs: clear, sourced, kind, actionable. No questions to the user. No "you may…" hedging that hides the source. No fatalistic language.
- **Verse (source)** is quoted **verbatim** from the translation. Correct only obvious scan errors (e.g. "trutifuJ" → "truthful"). Do **not** paraphrase. If a verse is unreadable, set `blocked_ocr` and quote `[OCR UNREADABLE]`.
- **Status** lifecycle in §5.

## 5. Status lifecycle

| Status | Meaning | May enter code? |
|----|----|----|
| `blocked_ocr` | Source verse unreadable; needs `verse-indexer` + human to recover | No |
| `draft` | Authored from source but not yet human-reviewed | No |
| `verified` | Human scholar reviewer has confirmed the rule matches the verse and the condition is testable | **Yes (frozen)** |

**All rules start as `draft` or `blocked_ocr`.** A human Scholar Reviewer (see `docs/07-organisation-structure.md`, `docs/08-responsibilities.md`) moves a rule to `verified`. Only `verified` rules are frozen into the runtime.

## 6. Authoring guardrails (binding)

1. **Source fidelity.** Every rule's condition and effect must be traceable to the quoted verse. Do not invent doctrine, yogas, or effects.
2. **No AI at runtime.** These files are the *substitute* for runtime AI. They must be complete enough that a deterministic engine can render the whole reading from them alone.
3. **One-way.** Effects are statements, not questions. The product presents; the user reads. (User feedback flows separately to the team — see `docs/14-information-architecture.md`.)
4. **Strength before doom.** `tend` rules must carry their offsetting strength / constructive framing inline in the Effect.
5. **Testable conditions.** If you cannot state a testable condition, say so in Notes and leave `draft`.
6. **Honest uncertainty.** Use `blocked_ocr` rather than guessing. The translator's footnotes (alternate readings) go in Notes.

## 7. How rules combine into a reading (information flow)

At runtime (deterministic):
1. Compute the `ChartFactBundle` (ch 1–3 tables + ephemeris).
2. Evaluate every rule in `rules/` against the bundle → a list of matched rules, each with its verse.
3. Compose the one-way reading in a fixed section order (see `docs/14-information-architecture.md`): strengths first, then "what to tend" (paired), then life-season (dasas), then a dignity-closing charge.
4. Render from **pre-authored effect text** (these files) + verse quotes — no generation.

## 8. Build-time AI usage (allowed, bounded)

AI may be used **while building** to:
- draft rule files from the source text (this is what produced the `draft` files),
- propose OCR corrections (flagged for human review),
- translate verse + effect text into other languages (verse preserved verbatim; human translator review),
- adversarially verify a rule against its verse (the `verification` agent — build-time lint),
- run a `tone-gate` lint on authored effect text (build-time, on the frozen content).

None of these run at runtime. The shipped product contains only frozen, `verified`, human-reviewed rules and pre-authored text.

---

*See `docs/13-build-philosophy.md` for the full no-AI-in-production architecture, and `docs/14-information-architecture.md` for the one-way reading structure.*