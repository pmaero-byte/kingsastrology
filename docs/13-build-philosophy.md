# 13 — Build Philosophy: No AI in Production

### AI builds the product. The product itself is deterministic.

This is a hard constraint set by the project owner and it overrides the earlier runtime-AI design in `04-ai-capabilities.md` and `05-architecture.md`. Read this document as the current truth where those conflict.

## 1. The rule

- **AI is used only to BUILD Kingsastrology** — authoring rule files, verifying them against the source, correcting OCR, translating verse + content into other languages, and linting tone/ethics on the frozen content.
- **No AI runs at runtime.** When a user opens the app and reads their chart, no LLM is queried. The reading is produced **deterministically**: a compute engine + a frozen, human-reviewed rule-base + pre-authored text.
- The shipped product contains **frozen artifacts only**: the verse store, the rule-base, the pre-authored effect text (per language), and the compute engine. Nothing generates at request time.

## 2. Why

1. **Faithfulness is reproducible.** A deterministic engine + frozen rules means the same birth data always yields the same reading, traceable to the same verses. No model drift, no hallucination, no "the AI said something different today."
2. **The source stays sovereign.** With no runtime generation, there is no path by which a model can invent a yoga or soften a verse into something the source didn't say. The verse-citation contract is mechanically guaranteed.
3. **Offline, low-cost, private.** No inference calls means the app can run offline (critical for Android reach), costs nothing per reading, and never sends a person's chart to a server for "generation."
4. **Trust.** A person can audit exactly what produced their reading: engine version + rule-base version + verse-store version + the frozen text. That auditability is impossible with runtime generation.

## 3. What gets built by AI (build-time only) — and the gate

| Build-time AI agent | What it does | Human gate before freeze |
|----|----|----|
| `verse-indexer` | Ingest the source PDF → verse store; flag OCR damage | Scholar Reviewer clears every `uncertain` verse |
| `rule-compiler` | Draft a rule from a verse (this produced the `draft` files in `rules/`) | Scholar Reviewer moves `draft`→`verified` |
| `verification` | Adversarially check a rule/claim against its verse | Scholar Reviewer confirms; rejects route back |
| `verse-translator` | Translate verse + effect text to a language (verse preserved verbatim) | Human translator review per language |
| `tone-gate` (build-time lint) | Scan frozen effect text for doom-leading/fatalistic language | Ethics Officer signs off the content set |
| `ethics` (build-time lint) | Scan frozen text for forbidden outputs (death dates, medical/legal/financial verdicts) | Ethics Officer signs off |
| `re-leveler` | Produce child-mode & scholar-mode variants of frozen text | AI Lead review |
| `faithfulness-sweep` | Nightly: re-verify frozen rules/text against the verse store; flag drift | Reliability Lead triages |

**Every AI-produced artifact is `draft` until a human moves it to `verified`.** Only `verified` artifacts are frozen and shipped. The agents never auto-promote.

## 4. The frozen artifacts (what ships)

1. **Verse store** — verse-indexed source text (`sourcetext/` → structured, OCR-cleared, scholar-reviewed).
2. **Rule-base** — `rules/ch01..ch20.md` rules with `Status: verified`, compiled into a deterministic machine-readable form (the `.md` is the source of truth; code is generated from it).
3. **Pre-authored effect text** — the `Effect (one-way…)` fields, frozen per language, including child/scholar altitudes.
4. **Compute engine** — deterministic ephemeris math (Swiss Ephemeris), dasa/ashtakavarga/bhava/varga computation.
5. **Reading composer** — deterministic assembly: evaluate rules against the `ChartFactBundle` → order the matched rules into the fixed section structure (`14-information-architecture.md`) → render from frozen text + verse quotes.

## 5. The runtime pipeline (deterministic, no AI)

```
birth data (+ optional event anchors)
        │
        ▼
 [Compute engine]  ── ephemeris, dasa, ashtakavarga, dignity ──→  ChartFactBundle (with citations)
        │
        ▼
 [Rule evaluator]  ── apply frozen, verified rules ──→  matched rules (each with verse)
        │
        ▼
 [Reading composer]  ── fixed section order, frozen text + verse quotes ──→  one-way reading
        │
        ▼
 rendered (web / android / ios / macos)  ── cached for offline re-read
```

No node in this pipeline calls a model. The "tone" and "ethics" guarantees were enforced **at build time** on the frozen text, not at request time.

## 6. What this means for the earlier design docs

- `04-ai-capabilities.md` §B (the generative counseling layer) and §D (runtime agent court) are **withdrawn from runtime**. Those agents become **build-time tools** (§3 above).
- `05-architecture.md` "Counseling Pipeline (the leashed LLM)" is replaced by the deterministic composer in §5 above. The API endpoints that implied generation (`/reading/prasna` conversational) are removed; Prasna (horary) is **out of scope** for the one-way product (see `14-information-architecture.md`).
- `09-agent-roster.md` counselor agents (`counselor-mirror`, `counselor-prasna`, etc.) are reclassified as build-time authoring/lint tools, not runtime services. The `Mirror` is no longer an agent — it is a **deterministic reading** composed from `rules/`.

## 7. Birth-time rectification under this model

Rectification (Chapter XXVI — out of the first-20 scope for now) is still possible deterministically: the user supplies event anchors as **input data**; the engine searches the time interval and presents the best-fit time with a confidence band. No dialogue, no LLM. When it enters scope it follows the same deterministic pattern.

## 8. Versioning & audit

Every shipped reading carries provenance: `{ computation_version, rulebase_version, verse_store_version, language_pack_version }`. Because everything is frozen and versioned, any past reading is bit-reproducible. This is the strongest possible faithfulness guarantee and is only achievable because there is no runtime AI.

---

*See also: `rules/README.md` (the rule lifecycle), `14-information-architecture.md` (the one-way reading structure).*
*Supersedes the runtime-AI portions of `04`, `05`, `09`.*