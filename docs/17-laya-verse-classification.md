# 17 — Laya: Verse Classification & the King's Daily Brief

### Classify every verse of the Brihat Jataka into topics and rules at build time; serve each king a topic-driven daily brief at runtime. The no-AI-at-runtime law (doc 13) is unchanged.

---

## 0. What this document decides

1. **Adopts Laya** (`convaiinnovations/laya`, Apache 2.0) as the **build-time** classification engine for the Verse Store.
2. **Defines the topic taxonomy** — the first formal taxonomy over the 483 stored verses (today they carry only frequency keywords).
3. **Defines the question battery** — the exact typed questions Laya answers per verse, with accept/assist/escalate thresholds.
4. **Designs the King's Daily Brief v2** — how classified topics + computed data points are presented to the king each morning.
5. **Adds nothing to runtime.** Laya never runs in production; its frozen, human-verified output does. `runtime_ai: false` remains true in every served provenance block.

The standing assumption, per the court metaphor of doc 07: **the users are the kings.** The product does not chat with them; it holds a daily audience with them.

---

## 1. The model: what Laya is, and why it may serve at court

### 1.1 Findings from the model card (investigated 2026-09-21)

| Property | Finding |
|----|----|
| Kind | Non-autoregressive **decision model** — answers typed questions about a state; **never generates text** |
| Backbone | ModernBERT-large + decision head (option scorer, act/escalate head), ~421M params, 512-token context |
| Answer types | `choice` (pick from supplied options), `score` (ordinal), `noul` (yes/no probability) — **options are supplied per question; there is no built-in label set** |
| Safety valve | Built-in **escalation head**: the model can abstain and route to a human |
| License / hosting | Apache 2.0, open weights, free self-host (~33 ms/forward) |
| Stated limits | Near-chance **zero-shot** on typed decisions (capability comes from fine-tuning); struggles with 50+ options; weakest at ordinal scoring; **ships over-confident — calibrate on your own data** |
| Sibling checkpoint | `laya-multilingual` (mmBERT-base, 100+ languages incl. Hindi) — not needed now (see §9) |

### 1.2 Fit to the charter

Four properties make Laya admissible where a generative model would not be:

1. **It cannot hallucinate doctrine.** It outputs probabilities over labels *we* supply. Invented yogas are structurally impossible — the option list is the Brihat Jataka's own topic set. This serves Pillar 1 (source fidelity) directly.
2. **Its escalation head matches our honest-uncertainty rule.** The `rules/README.md` philosophy — `blocked_ocr` rather than guessing — has a machine counterpart: Laya abstains, the verse goes to the human Scholar Reviewer queue. 334 verses already sit in `uncertain.json`; Laya's first productive job is triaging that queue.
3. **It decides labels, never prose.** The AGENTS.md determinism boundary ("yoga/condition detection is performed by the deterministic rule-base — agents render, they do not decide presence") is preserved: Laya classifies *source verses* at build time; presence in a chart is still decided only by the frozen rule-base at runtime.
4. **Self-hosted and offline.** Verse text never leaves the court's build machine. Pillar 4 (the person owns their chart) is untouched — Laya never sees chart data at all, only public source text.

### 1.3 Constraints → mitigations

| Constraint (from the card) | Mitigation in this design |
|----|----|
| Near-chance zero-shot on typed decisions | Fine-tune on the scholar-labeled seed before any production use (§4). Zero-shot numbers are recorded but never trusted. |
| Ships over-confident | Temperature calibration on held-out scholar labels; decisions use **calibrated probability + margin**, never raw argmax (§3.3). |
| Weak with 50+ options | Every option list ≤ 20; the topic axis uses a two-stage split (domain group → topic) so no question ever offers more than 14 options. |
| Ordinal scoring weakest | `score` questions are **forbidden** in v1 of the battery. Confidence comes from calibrated `noul`/`choice` probabilities, not ordinal ratings. |
| 512-token context | Verses are short OCR paragraphs; the longest is truncated at sentence boundaries with a flag, never silently. |
| English base checkpoint | Our stored `translation_text` is English — correct checkpoint. Hindi/Arabic are rendered at runtime by fixed templates (verse preserved verbatim); there is no multilingual classification to do. |

### 1.4 The boundary line

```
BUILD TIME (may use Laya)                    RUNTIME (deterministic only)
─────────────────────────────                ──────────────────────────────
backend/scripts/classify_verses_laya.py      backend/app/services/brief.py
backend/scripts/laya_questions.json          backend/app/services/chart_engine.py
        │                                           │
        ▼                                           ▼
draft topics/kinds on verse records           frozen topics + verified rules
        │                                           │
        ▼                                           ▼
HUMAN Scholar Reviewer confirms               topic_index.json → Brief v2
        │                                           │
        ▼                                           ▼
verse_store + topic_index (frozen,            GET /api/v1/brief  (runtime_ai: false)
  versioned, provenance-stamped)
```

`requirements.txt` (runtime) never gains `laya`; it lives in a build-only extra (`pyproject.toml [project.optional-dependencies] build-ai]`). CI fails if `app/` imports it.

---

## 2. The topic taxonomy

Today the store has no taxonomy — `keywords[]` are frequency tokens. This section defines one. **Axis T topics are the only thing the Daily Brief selects on** (§6), so the taxonomy is designed for the king's morning, not for librarians.

### 2.1 Four axes per verse

Every verse receives one record on each axis, each with a calibrated probability:

| Axis | Question it answers | Cardinality |
|----|----|----|
| **T — Topic** | Which domain of the king's life does this verse speak to? | one primary + 0–3 secondary |
| **E — Entity** | Which chart object does it speak about? | multi |
| **K — Kind** | What kind of rule material is it? | one |
| **G — Guardrail flags** | What special handling does it need? | multi |

### 2.2 Axis T — the fourteen domains of the court

Each topic is bound to its authorizing chapter(s) per doc 01 (no chapter, no topic — the charter's scope rule applies to the taxonomy itself):

| ID | Topic (the king hears it as…) | Authorizing chapters | Feeds feature (doc 01) |
|----|----|----|----|
| `topic.foundation` | "the court's reference tables" | 1–3 | `core.*` (tables; never briefed to kings) |
| `topic.temperament` | "who you are" | 2, 17, 18, 19 | `feature.nakshatra-temperament`, `feature.moon-in-sign-profile`, `feature.planet-in-sign-profile` |
| `topic.livelihood` | "your work and its rewards" | 10/11 (Karmajiva), 21 | `feature.karmajiva-advisor`, `feature.bhava-profile` (10th) |
| `topic.wealth` | "your stores and resources" | 10/11, 21 (2nd, 11th) | `feature.karmajiva-advisor`, `feature.bhava-profile` |
| `topic.sovereignty` | "your leadership and standing" | 12/13 (Raja yogas) | `feature.raja-yoga-detector`, `feature.leadership-profile` |
| `topic.life-pattern` | "the shape of your whole reign" | 13/14 (Nabhasa) | `feature.nabhasa-archetype` |
| `topic.conduct` | "your habits of mind and company" | 14, 20 (lunar yogas, aspects to Moon) | `feature.lunar-yoga-detector`, `feature.aspect-effects` |
| `topic.alliances` | "your bonds and partnerships" | 21 (7th), 25 | `feature.bhava-profile`, `feature.strijataka` |
| `topic.lineage` | "family and origins" | 10/11, 21 (4th), 5 | `feature.bhava-profile`, `feature.nisheka-fertility` |
| `topic.vitality` | "your energy and its seasons" | 7, 8 (Balarishta, Ayurdaya) — **pacing framing only** | `feature.ayurdaya-estimator` (life-stage band) |
| `topic.seasons` | "the timing of your life" | 9 (Dasa), 10 (Ashtakavarga) | `feature.dasa-timeline`, `feature.ashtakavarga-score` |
| `topic.focus` | "single-minded calling" | 16 (Pravrajya) | `feature.pravrajya-detector` |
| `topic.counsel` | "what to tend" | 24 (Arishta) + every `tend` verse | `feature.arishta-detector` (constructive delivery, Pillar 3) |
| `topic.method` | "how the science itself works" | 1, 6, 26, 27, 28 | Verse Explorer / scholar material, never briefed |

Notes:

- **`topic.vitality` is ethics-gated** (§2.5, §6.6): its verses classify, but they never render in a Daily Brief and never yield a date. In the full Mirror reading they appear only as the wide life-stage band of doc 14 §3 §8.
- **`topic.foundation` and `topic.method` are engine/explorer material** — classified for completeness and the Verse Explorer, excluded from briefing by construction.
- Secondary topics exist because Brihat Jataka verses are dense: "Moon in Scorpio" verses are `topic.temperament` primary, often `topic.counsel` secondary. The brief's card selection (§6.4) reads both.

### 2.3 Axis E — entities

Free vocabulary drawn from the computed `ChartFactBundle` domain (doc 10), multi-label:

- `graha.Sun … graha.Ketu` (9)
- `rasi.Aries … rasi.Pisces` (12)
- `bhava.1 … bhava.12` (for ch-21-adjacent verses; rules ch 1–20 use sign/house-from-Moon references where the translation does)
- `nakshatra.set` (verse speaks of nakshatras generally or enumerates them)
- `yoga.<name>` for named yogas (Adhi, Nabhasa set, Raja combinations, …)
- `dasa`, `aspect`, `dignity` (exaltation/debility/moolatrikona/own-sign statements)
- `none` (pure definition/time-measure verses)

### 2.4 Axis K — kind

Extends the existing rule `Classification` vocabulary (rules/README §4) with two source-side kinds, so verses that should *not* become rules say so explicitly:

| Kind | Meaning | Rule path |
|----|----|----|
| `table` | fixed lookup (lords, dignities, years, friends/enemies) | becomes a `table` rule |
| `strength` | favorable indication to highlight | becomes a `strength` rule |
| `tend` | delicate indication, must pair with offsetting strength | becomes a `tend` rule |
| `neutral` | descriptive temperament content | becomes a `neutral` rule |
| `context` | narrative/definition with no testable condition (stories of the science, praise of the king, chapter openings) | stays in Verse Explorer only |
| `blocked_ocr` | text too damaged to classify | verse-indexer recovery queue |

### 2.5 Axis G — guardrail flags

- `ethics.longevity` — Ayurdaya/Balarishta/death-adjacent language → may only ever render as life-stage pacing; **no rule derived from these verses may output a date** (doc 11; AGENTS.md §5).
- `ethics.verdict-risk` — medical/legal/financial verdict language in the translation ("will lose wealth", "disease of X") → rendering must convert to tendency framing; flagged for Ethics Officer at authoring time.
- `ocr.suspect` — scan artifacts, garbled spans, suspicious numbering.
- `numbering.ambiguous` — the duplicate/restarted verse numbering already tracked in `uncertain.json`.

### 2.6 Precondition: chapter-numbering reconciliation

The store numbers 27 chapters from a 28-chapter translation (one chapter compressed), and `docs/01`'s map (Karmajaya = Ch 11) is offset by one from the store/rules numbering (Karmajiva = `rules/ch10_karmajiva.md`, and `chart_engine.py` cites dasa as Ch 8 where doc 01 says Ch 9). Before classification output is frozen, the classifier workstream must produce a **canonical chapter map** (`backend/data/verse_store/chapter_map.json`: store_chapter ↔ doc01_chapter ↔ Sanskrit adhyaya name), signed off by the Scholar Reviewer. Every citation in this document uses store numbering from here on.

---

## 3. The question battery (prompts as data)

Questions live in a versioned file — `backend/scripts/laya_questions.json` — never in code, so the Scholar Reviewer reviews them like rules. **No `score` questions (§1.3).**

### 3.1 The battery (v1)

State passed per verse: `{chapter, verse, sanskrit_ref, translation_text, chapter_title}`. Chapter title is included — it is legitimate prior context from the source itself, not external doctrine.

| # | Type | Question | Options / note |
|----|----|----|----|
| Q1 | `choice` | "Which domain of life does this verse primarily speak to?" | 14 topics (§2.2) |
| Q2 | `noul` ×13 | "Does this verse also speak to {topic}?" | for each topic ≠ Q1's answer |
| Q3 | `noul` | "Does this verse state a condition over chart facts (placements, aspects, periods, dignities) that yields a determinate stated effect?" | the is-it-a-rule test |
| Q4 | `choice` | "What kind of rule material is it?" | `table / strength / tend / neutral / context / blocked_ocr` (shown only if Q3 ≥ threshold) |
| Q5 | `choice` | "At what grain is the condition testable?" | `planet-in-sign / planet-in-house / moon-nakshatra / yoga-presence / dignity-state / dasa-period / aspect / time-measure / not-testable` |
| Q6 | `noul` | "Does this verse concern length of life, death, childhood danger, or disease?" | → `ethics.longevity` / verdict-risk review; conservative threshold |
| Q7 | `noul` | "Does the text contain scanning damage or unreadable spans?" | → `ocr.suspect` |
| Q8 | `noul` | "Does the verse number or surrounding text suggest restarted/ambiguous numbering?" | → `numbering.ambiguous` |

Q6 uses a **deliberately low accept threshold** (§3.3): for ethics flags we prefer false alarms to misses — the cost asymmetry is the whole point of the guardrail ordering.

### 3.2 Worked request (Ch 1, v 6 — a foundation verse)

```json
{
  "state": {
    "chapter": 1, "verse": 6,
    "sanskrit_ref": "Brihat Jataka 1.6",
    "chapter_title": "Unmadagati / Introduction",
    "translation_text": "Mars. Venus. Mercury, the Moon, the Sun, Mercury, Venus, Mars, Jupiter, Saturn, Saturn and Jupiter are respectively the lords of the Signs, and of the Navamsas and Dwadasamsas; ..."
  },
  "questions": [
    {"id": "Q1", "type": "choice",
     "text": "Which domain of life does this verse primarily speak to?",
     "options": ["topic.foundation", "topic.temperament", "topic.livelihood", "...", "topic.method"]},
    {"id": "Q3", "type": "noul",
     "text": "Does this verse state a condition over chart facts that yields a determinate stated effect?"},
    {"id": "Q6", "type": "noul",
     "text": "Does this verse concern length of life, death, childhood danger, or disease?"}
  ]
}
```

Expected (post fine-tune): Q1 → `topic.foundation` p≈0.9+; Q3 → yes (it is a lordship table); Q4 → `table`; Q5 → `dignity-state`; Q6 → no. This verse becomes a `table` rule candidate — and never appears in a Daily Brief, because `topic.foundation` is excluded from briefing (§2.2).

### 3.3 Accept / assist / escalate

All probabilities post-calibration. For `choice`: also require **margin ≥ 0.25 over runner-up**.

| Calibrated condition | Outcome | Who acts |
|----|----|----|
| Q1 p ≥ 0.85 **and** margin ≥ 0.25 | **auto-draft** — topic written to verse record with `status: auto-draft` | pipeline |
| 0.50 ≤ p < 0.85 | **scholar-assist** — pre-filled suggestion in the review UI | Scholar Reviewer confirms or corrects |
| p < 0.50, or escalation head fires, or Q7 flags OCR | **escalated** — queued with model's ranking attached | Scholar Reviewer decides from scratch |
| Q6 p ≥ 0.30 (ethics; intentionally low) | **always** human-reviewed regardless of other scores | Ethics Officer + Scholar Reviewer |

**Nothing is ever auto-verified.** The rules/README §5 lifecycle is untouched: only a human moves anything to `verified`, and only `verified` content freezes into the runtime.

---

## 4. Fine-tuning, calibration, evaluation

Laya is near-chance zero-shot on typed decisions — the card says so and we take it at its word. Production use requires:

1. **Seed corpus.** (a) The 19 `verified` rules with their citing verses as gold labels; (b) the 411 `draft` rules as weak labels (weight 0.5 — they are AI-drafted and may embed errors); (c) **~200 fresh hand-labels** by the Scholar Reviewer across all 14 topics, stratified so every topic has ≥ 8 gold verses; (d) 50 verses double-labeled by two humans to measure agreement (report Cohen's κ; if κ < 0.7, fix the taxonomy wording before training — the taxonomy is the thing under test, not just the model).
2. **Fine-tune** the base checkpoint on the seed (RLCD objective per the card; our own run, on our build machine).
3. **Calibrate** temperature on a held-out scholar-labeled split (300 verses held out of training entirely). Calibration version stamped into provenance.
4. **Report honestly** (recorded in `backend/data/laya_eval.json`, reviewed like everything else): macro-F1 per topic on the held-out set, escalation rate, and — the number that matters most — **false-negative rate on Q6 (ethics flags)**, which must be **0 on the eval set** before L2 exit.
5. **Re-train triggers:** verse_store version bump with text changes; Scholar Reviewer overturns > 5% of auto-drafts in a sweep; taxonomy version bump.

**Exit gate for production classification (L2):** macro-F1 ≥ 0.80 on primary topic, escalation rate ≤ 20%, Q6 false-negative = 0.

---

## 5. Data-model changes

All additive; `STORE_VERSION` bumps per existing convention.

### 5.1 Verse record gains a `taxonomy` block

```json
{
  "chapter": 1, "verse": 6, "sanskrit_ref": "Brihat Jataka 1.6",
  "translation_text": "…",
  "keywords": ["mars", "venus", "…"],
  "pages": [42],
  "taxonomy": {
    "primary": {"topic": "topic.foundation", "p": 0.93},
    "secondary": [{"topic": "topic.method", "p": 0.61}],
    "entities": ["dignity", "rasi.Aries"],
    "kind": "table",
    "grain": "dignity-state",
    "flags": [],
    "status": "scholar-confirmed",
    "classified_by": {"model": "convaiinnovations/laya", "fine_tune": "kings-ft-1", "calibration": "temp-1", "questions": "laya_questions@1"},
    "reviewer": "scholar-reviewer",
    "reviewed_at": "2026-10-05"
  }
}
```

`status ∈ {auto-draft, scholar-assist, scholar-confirmed, escalated}` — only `scholar-confirmed` feeds `topic_index.json`.

### 5.2 New file: `backend/data/verse_store/topic_index.json`

The frozen bridge between classification and the runtime, rebuilt only at build time:

```json
{
  "taxonomy_version": "topics-1.0.0",
  "verse_store_version": "2026.10.xx",
  "topics": {
    "topic.livelihood": {
      "feature": "feature.karmajiva-advisor",
      "chapters": [10, 21],
      "verses": [[10, 1], [10, 2], "…"],
      "verified_rules": ["R-10.1", "…"],
      "briefable": true,
      "ethics_gate": false
    },
    "topic.vitality": {"briefable": false, "ethics_gate": true, "…": "…"}
  }
}
```

### 5.3 Rules gain an optional `Topics` line

Additive to the rules/README §4 block: `- **Topics:** topic.livelihood; topic.wealth` — backfilled for verified rules first. The rule loader exposes it; the brief composer (§6) consumes it.

### 5.4 Provenance gains a classifier line

Every brief and reading served after this change records: `"classifier": {"model": "laya+kings-ft-1", "taxonomy_version": "topics-1.0.0", "human_verified": true}` — so any past reading remains auditable (AGENTS.md §2.4, §7).

---

## 6. The King's Daily Brief v2 — presentation design

### 6.1 The audience framing

The Brief v1 (brief.py, `brief-1.0.0`) is the **realm's** almanac: panchanga for a time and place, no birth data. It stays exactly as is — anonymous visitors get v1.

Brief v2 (`brief-2.0.0`) is **the king's own audience**: when birth data is present (BirthDataVault, doc 10), the same morning brief is held *for this king*, organized by topic. The court metaphor carries the UX, but every line obeys v1's laws, now carried forward:

- **Measure before asserting** — every data point is computed by the zīj/chart engines; every doctrinal sentence is frozen, verified rule text.
- **Certain and conjectural never share a voice** — `measured` / `convention` tier stamps on every line and every data point.
- **Translate everything** — en / हिंदी / العربية via fixed templates; verse quotes verbatim.
- **Refuse flattery, refuse doom** — the brief informs; it never promises and never threatens. It predicts nothing.

### 6.2 Brief structure (fixed order, one-way — doc 14 compliant)

```
1. The Proclamation     day + ruling lord                          [realm, measured]      (v1 line 1)
2. The Moon's Court     Moon nakshatra/pada/rasi, tithi + paksha   [realm, measured]      (v1 line 2)
   └ + The Visitor: transit Moon's relation to natal Moon's
     nakshatra-lord sign — "who visits your gate today"            [personal, measured]   (new)
3. The Lights' Timetable  sunrise/sunset, moonrise/moonset         [realm, measured]      (v1 line 3)
4. The Day's Windows    Abhijit + Rahu Kaal, labelled convention   [realm, convention]    (v1 line 4)
5. The Season           current Vimshottari mahadasa + antardasa
                        lord, its dignity in the king's chart,
                        the season's topic domain                  [personal, measured]   (new, Ch 8/9-store)
6. The Counsel          2–4 topic cards (§6.3)                     [personal, mixed]      (new — the core)
7. Tomorrow's Lookout   next nakshatra + tithi                     [realm, measured]      (v1)
8. The Closing Charge   fixed dignity-closing line                 —                      (new)
```

Sections 1–4 and 7 are byte-identical to v1 (same templates, same tests). v2 adds 5, 6, 8 and leaves the rest untouched — v1 remains a strict subset, so existing determinism tests keep passing.

### 6.3 The topic counsel card

One card per selected topic. A card is **data points first, doctrine second, charge last** — the king sees the machinery before the meaning, al-Bīrūnī's order.

```json
{
  "topic": "topic.livelihood",
  "title": {"en": "Your Work", "hi": "आपका कार्य", "ar": "عملك"},
  "data_points": [
    {"tier": "measured", "label": {"en": "10th house from Lagna", "hi": "…", "ar": "…"},
     "value": {"en": "Taurus, occupied by Saturn in its own sign", "hi": "…", "ar": "…"},
     "source": "chart-1.0.0"},
    {"tier": "measured", "label": {"en": "Current antardasa lord", "hi": "…", "ar": "…"},
     "value": {"en": "Mercury", "hi": "…", "ar": "…"}, "source": "chart-1.0.0"},
    {"tier": "convention", "label": {"en": "Moon transits today", "hi": "…", "ar": "…"},
     "value": {"en": "your 10th house (from natal Moon)", "hi": "…", "ar": "…"},
     "source": "zij-1.0.0"}
  ],
  "reading": {
    "en": "The planet holding your 10th house of work is Saturn, seated in his own ground — the verse of Karmajiva names steady, structural livelihood won through the father's line of work (Ch 10, v 1). This is a gift of endurance: what you build slowly, keeps.",
    "hi": "…", "ar": "…"
  },
  "citations": [{"chapter": 10, "verse": "1"}],
  "charge": {
    "en": "Begin the durable thing today; the season favors foundation over speed.",
    "hi": "…", "ar": "…"
  },
  "provenance": {"rules": ["R-10.1"], "rulebase_version": "…", "verse_store_version": "…",
                  "taxonomy_version": "topics-1.0.0", "verification_passed": true}
}
```

**Card design rules (binding):**

1. **Data points are measured facts only** — positions, dignities, dasa lords, transit houses. No adjectives in `value`.
2. **`reading` text comes only from `verified` rules** (pre-authored Effect text, rules/README §4) — the composer selects and orders frozen sentences; it writes none. Unverified topics get no card, even if classified — the card is only as authoritative as its weakest citation.
3. **Strength first, always.** If a card carries a `tend` sentence, its offsetting strength sentence ships in the same card, after the strength. A card may never open with a caution.
4. **Every doctrinal sentence carries (Ch, verse)**, resolvable in the Verse Store (AGENTS.md §2.2). Non-doctrinal framing is labelled.
5. **`charge` is a dignity-closing instruction, not a prediction** — imperative mood, no outcome promised, no licensed-domain directive (no "invest/sue/diagnose").
6. **Tier stamps everywhere** — a `convention` data point (muhurta, transit-house convention) is visually distinct from `measured` ones, exactly as v1 does for lines.

### 6.4 Card selection is deterministic (no runtime AI)

The composer (`backend/app/services/brief.py` v2) picks **2–4 cards** by a fixed priority ladder — a pure function of `(ChartFactBundle, transit facts, topic_index, verified rule-base)`:

1. **The Season's domain** — the current mahadasa lord's signification topic (e.g., Saturn → `topic.livelihood`; Moon → `topic.temperament`; Jupiter → `topic.wealth`/`topic.lineage`), if that topic is briefable and has ≥ 1 verified rule matching the king's chart.
2. **Today's activated house** — the whole-sign house the transit Moon occupies (counted from natal Moon, the Brihat Jataka's own reference), mapped through the bhava→topic table (10th → livelihood, 7th → alliances, 2nd/11th → wealth, …), if briefable + verified.
3. **The king's standing strengths** — strongest natal dignity/Raja-yoga topic (`topic.sovereignty`, `topic.life-pattern`), so the brief always carries at least one strength card (Pillar 3 enforced structurally).
4. Tie-breaks by fixed order: season > house > strength; cap at 4 cards (attention is a court resource).

Same inputs → same cards, same words, same order. Tested like v1's determinism test.

### 6.5 What never appears in a brief

- **`topic.vitality` cards — never.** No longevity content in a daily brief, ever, regardless of verification state (doc 11; AGENTS.md §5). The life-stage band lives only in the full Mirror reading (doc 14 §3 §8).
- **`topic.foundation` / `topic.method` — never** (tables and meta-material).
- **Unverified or `scholar-assist` topics — never.** Absence of a card is the honest output when review lags.
- **Promises, verdicts, precise risks, death dates** — the forbidden list of AGENTS.md §5, enforced by the build-time tone-gate lint on every card template and by the fact that no such sentence exists in verified rule text.

### 6.6 Delivery notes

- Endpoint: `GET /api/v1/brief` gains optional birth-data reference (`vault_id`); without it, response is v1 shape exactly (`brief_1_compatible: true`).
- The generated brief is cached per (king, date, lang) only after the whole pipeline passes; offline clients serve the cached `verification_passed` copy (AGENTS.md §6).
- `today.html` renders cards below the existing four lines under "The Counsel" — same PWA, no new dependency; the jump-rail gains one anchor.
- The closing charge (line 8) is a single frozen sentence per language, identical every day — the king's benediction, never varied, never personalized.

---

## 7. Pipeline & milestones

| ID | Deliverable | Exit gate | Human gate |
|----|----|----||
| **L0** | Chapter-numbering reconciliation map (`chapter_map.json`) | Scholar sign-off | Scholar Reviewer |
| **L1** | Baseline zero-shot eval on 50 gold verses | Report recorded (expected weak; documented, not deployed) | — |
| **L2** | Seed corpus, fine-tune, calibrate; `laya_eval.json` | macro-F1 ≥ 0.80, escalation ≤ 20%, Q6 FN = 0 | Scholar Reviewer + Ethics Officer |
| **L3** | Classify all 483 verses; triage `uncertain.json` (334 verses) | 100% of verses in a terminal state (confirmed or queued) | Scholar Reviewer sweep |
| **L4** | Freeze `topic_index.json` v1; backfill `Topics:` on verified rules | store version bump; tests green | Scholar Reviewer |
| **L5** | Brief v2 composer + cards + tests; `today.html` update | determinism tests (same inputs → byte-identical brief); v1 subset unchanged | Counselor/UX ministry review |

L5 lands only after L4 — **no card ships ahead of its frozen taxonomy.**

---

## 8. Charter & AGENTS.md compliance matrix

| Rule | How this design complies |
|----|----|
| Pillar 1 — source fidelity | Labels are chosen from a taxonomy bound to chapters; verses quote verbatim; Laya sees only source text |
| Pillar 2 — round-Earth accuracy | Cards' data points come from the same Swiss-Ephemeris engines as v1; no new sky math |
| Pillar 3 — strength before doom | Card rule 3 (§6.3) + selection ladder rung 3 guarantee a strength card daily; vitality excluded |
| Pillar 4 — the person owns their chart | Laya never touches chart data; briefs cached on-device are the king's; provenance on every output |
| AGENTS.md §2.5 determinism boundary | Laya classifies verses at build time; runtime presence-detection stays with the frozen rule-base |
| AGENTS.md §4 guardrail ordering | Card templates linted by tone-gate/citation/ethics at build; only survivors cached/served |
| AGENTS.md §5 forbidden outputs | §6.5 exclusion list; Q6 ethics flag with conservative threshold; no date can render |
| AGENTS.md §7 human sign-off | Taxonomy and questions are versioned artifacts under Scholar Reviewer authority; nothing auto-verifies |
| Doc 13 — no AI at runtime | §1.4 boundary; CI import guard; provenance keeps `runtime_ai: false` |
| Doc 14 — one-way flow | Fixed brief order; no queries; feedback channel unchanged |

---

## 9. Risks & honest limitations

1. **Laya may simply not reach the bar.** If L2's gate is missed after reasonable tuning, the fallback is the same pipeline with the Scholar Reviewer labeling unaided (slower, same output shape). The design degrades gracefully — the taxonomy, question battery, and brief v2 are all model-agnostic.
2. **OCR quality bounds classification.** The source is an OCR'd PDF translation. `ocr.suspect` routing plus the existing verse-indexer recovery path is the mitigation; some verses will stay `blocked_ocr`, and that is the honest state.
3. **Taxonomy wording is the real experiment.** κ < 0.7 between two humans means the topics are unclear, and no model fixes that (§4.1d).
4. **Fine-tune data is thin** (19 gold rules + ~200 labels). Scholar labeling continues during L3; the model is retrained at each sweep, and early auto-drafts will carry more escalations — acceptable, by design.
5. **Overconfidence persists after calibration** on rare topics. Hence the margin requirement and the 0.85 bar; rare topics (e.g., `topic.focus`) will lean human until gold volume grows.
6. **Card monotony.** Frozen text means a king with an unchanging chart hears repeated counsel across a dasa season. Mitigation: cards key on the *season* (antardasa changes every few months) and the *transit house* (changes every ~2.5 days), so the composition varies on the measured facts even while every sentence stays frozen. This is a feature — the court's word is steady.
7. **Chapter-numbering debt** (§2.6) must clear first, or every downstream citation inherits the offset.

---

*Bound artifacts defined here: `backend/scripts/laya_questions.json` (question battery), `backend/data/verse_store/chapter_map.json` (numbering), `backend/data/verse_store/topic_index.json` (frozen taxonomy bridge), `backend/scripts/classify_verses_laya.py` (build-time classifier), `brief-2.0.0` (the King's Daily Brief). See also `docs/13-build-philosophy.md`, `docs/14-information-architecture.md`, `rules/README.md`.*
