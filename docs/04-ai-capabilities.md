# 04 — AI Capabilities Catalogue
### What Varahamihira would build, were he alive today, to convert all his knowledge to the people.

The reasoning machines of this age are, to me, what the water-clock and the gnomon were in Ujjain — instruments. I would not use them to *invent* new astrology. I would use them to do four things my hand could never do alone:

1. **Compute** the sky for any soul on the round Earth, instantly and exactly.
2. **Recognize** the thousands of yogas in a single chart at once — a lifetime's eye reduced to a moment.
3. **Translate** my Sanskrit verses into each person's tongue, with the verse never lost.
4. **Counsel** — hold a conversation with the person, as I would hold court, always returning to the source.

Below is the catalogue of AI capabilities I hereby commission. Each is bound to the chapters named in `01-source-text-foundation.md`. None invents doctrine; all cite verse.

---

## A. The Foundation Engines (non-generative — exact computation)

These are deterministic. They are the *engine bed*. No AI hallucination is permitted here; these must be mathematically correct.

### A1. Spherical-Sky Compute Engine
- **Authority:** Ch. 1–3 (time measures, signs, planets); the round-Earth principle of my Varaha form.
- **Function:** Given birth date, time, and geographic coordinates, produce the geoceric longitudes of all nine grahas, the lagna (ascendant), the 12 bhavas, the nakshatra of the Moon, and the ayanamsa-corrected tropical/sidereal boundary.
- **AI role:** none at the math layer — this is verified ephemeris computation (Swiss Ephemeris core). AI is used only to *narrate* the result and *cite* the verse that governs each element.

### A2. Dignity & Relation Lookup
- **Authority:** Ch. 3 (Grahagana).
- **Function:** Exaltation, debilitation, moolatrikona, own-sign, friendship/enmity per planet.
- **AI role:** translate the resulting table into the person's language with sourced explanation.

### A3. Yoga Pattern Recognition Engine  *(the centerpiece AI)*
- **Authority:** Ch. 12–16, 23, 24 (Raja, Nabhasa, Lunar, Double, Ascetic, Misc, Malefic yogas).
- **Function:** detect every yoga present in the chart from a coded rule-base transcribed directly from the verses.
- **AI role:** This is the most important use of AI in the whole product. The rule-base is large (hundreds of yogas) and the verses describe them in compressed Sanskrit. We use LLMs in a **constrained, retrieval-grounded, verification-gated** way:
  - A **rule compiler agent** reads each verse and emits a structured, testable rule (`IF planet X in sign Y AND ... THEN yoga Z, citation Ch/verse`).
  - Rules are **reviewed by a verification agent** against the verse before they are allowed into the rule-base.
  - At runtime, the engine is **deterministic**: it applies the compiled rules — the LLM never invents a yoga at query time.
  - The LLM is used only to *render* a detected yoga into the person's language, with the verse quoted.

### A4. Dasa Timeline Engine
- **Authority:** Ch. 9 (Dasas & Antardasas).
- **Function:** Vimshottari (and other named) planetary period timelines mapped to calendar dates.
- **AI role:** narrate the current and upcoming dasa/antaradasa as "the season you are in," with verse citation; answer conversational questions about timing.

### A5. Ashtakavarga Scoring Model
- **Authority:** Ch. 10.
- **Function:** bindu points per house per planet; aggregate transit strength scores.
- **AI role:** interpret a transit as strong/favorable vs. requiring patience, grounded in the score, with verse citation.

### A6. Bhava & Varga Synthesizer
- **Authority:** Ch. 21 (Bhavas), Ch. 22 (Vargas).
- **Function:** produce life-area readings (self, wealth, siblings, home, children, illness/health, spouse, death/transform, merit, career, gain, loss/liberation) and divisional depth (D9 for partnership, D10 for career, etc.).
- **AI role:** synthesize the strengths/weaknesses per life-area, always leading with strength, always closing constructively.

---

## B. The Generative Counseling Layer (LLM, but leashed)

This is where the "king instructs his people" tone lives. These features use LLMs **under strict guardrails**:

- **Source-grounded only:** the LLM receives the *computed chart facts + the relevant verses* as context. It may not speak beyond them.
- **Citation mandatory:** every sentence of counsel must attach a `(Ch, verse)` or be marked as general framing (clearly separated from doctrine).
- **Tone lock:** the system prompt encodes Pillar 3 (strength before doom) and the charter's kindness rule. A separate **tone-gate agent** rejects any output that leads with catastrophe or uses fatalistic language.
- **No medical / legal / financial verdict:** the LLM is instructed to redirect such questions; astrology counsels self-knowledge, not licensed advice.

### B1. The Mirror — Strengths & Weaknesses Self-Portrait  *(flagship)*
- **Authority:** Ch. 2, 3, 9, 17, 18, 19, 21, 12, 13, 24.
- **Function:** the primary reading. A multi-section report:
  1. *Who you are* — lagna, Moon nakshatra, Sun sign temperament (Ch. 17–19, 21).
  2. *Your strengths* — strong planets, exalted grahas, raja & nabhasa yogas present (Ch. 12, 13, 19, 21).
  3. *What to tend* — malefic yogas, afflicted bhavas, difficult dasas — each paired with its constructive reading and the strength that offsets it (Ch. 24 + the offsetting strength).
  4. *The season you are in* — current dasa/antardasa (Ch. 9).
  5. *Closing charge* — a king's instruction: how to live well with this knowledge, ending on dignity.
- **AI role:** compose the prose, footnoted to verse, tone-gated. This is the product's heart.

### B2. Ask the King — Prasna Query Engine
- **Authority:** Ch. 27 (Prasna / horary).
- **Function:** the user asks a question ("Should I undertake this journey now?" "Is this endeavor favored?"). The engine casts a chart for the moment the question is asked and answers per the Prasna chapter.
- **AI role:** interpret the horary chart into a conversational answer, cited to Prasna rules, never giving medical/legal/financial verdicts.

### B3. Birth-Time Rectification  *(Apavatika)*
- **Authority:** Ch. 26.
- **Function:** for users who do not know their exact birth time, an AI-driven rectification: collect life-event anchors (dates of major events) and search the time interval to find the lagna/bhava alignment that best fits the events per the chapter's methods.
- **AI role:** guide the interview, propose event-anchors, run the search, present the rectified time **with an explicit confidence band and the events used**.

### B4. Vocation Counselor — Karmajiva
- **Authority:** Ch. 11.
- **Function:** recommend vocations/fields suited to the chart (wealth from father/mother/friend/brother/wife/servant categories, strong planets, career bhava, D10).
- **AI role:** produce a prioritized, explained vocation reading — strengths to apply, fields to favor, fields needing more effort. Cited to Ch. 11.

### B5. Life-Stage & Longevity Context — Ayurdaya
- **Authority:** Ch. 8.
- **Function:** a **life-stage** reading (not a death-clock). Presents the life-span estimate as a *context for pacing one's efforts*, with a wide confidence band, and focuses on the stages (childhood, youth, building, mastery, withdrawal).
- **AI role:** frame constructively; **never** present a precise death date. Per the ethics doc, this is delivered as life-stage pacing, not prediction of death.
- **Guardrail:** precise death-date output is forbidden by the tone-gate and ethics doc regardless of what the verse math suggests.

### B6. Women's Reading — Strijataka
- **Authority:** Ch. 25.
- **Function:** readings framed for women, per the chapter, updated for contemporary dignity (the chapter is honored as source; its application is delivered with modern respect, per Pillar 3).
- **AI role:** compose with care; a sensitivity review agent checks framing.

### B7. Fertility / Conception Timing — Nisheka
- **Authority:** Ch. 5.
- **Function:** advise favorable windows for conception per the chapter.
- **AI role:** present as "favorable/unfavorable timing for undertaking," never as a medical fertility guarantee. Ethics doc forbids medical claims.

---

## C. Translation & Accessibility Layer

### C1. Verse-to-Tongue Translator
- **Function:** render each cited Sanskrit verse (from the translation in `sourcetext/`) into the user's chosen language, **with the verse itself preserved** so the source is never lost in translation.
- **AI role:** translation LLM, with the verse text pinned in-context and required to appear verbatim in the output alongside the translation.

### C2. Plain-Language Re-leveler
- **Function:** a child mode ("explain this so a young person understands") and a scholar mode ("give me the verse and the rule"). Same source, two altitudes.
- **AI role:** controlled re-leveling, verse preserved in both.

### C3. Voice Court — Spoken Counsel
- **Function:** deliver the Mirror reading and Prasna answers by voice (TTS) and accept spoken questions (ASR), for users who cannot or prefer not to read.
- **AI role:** ASR + TTS + the same grounded LLM; especially important for elders and accessibility.

---

## D. The Multi-Agent Court (the "ministers")

The counseling layer is not one monolithic LLM call. It is a court of specialized agents, each bounded to its chapter domain, each verified, each citing verse. The roster and their definitions live in `09-agent-roster.md` and in `.claude/agents/*.md`. In summary:

- A **Rule-Compiler agent** — turns verses into testable rules (offline, human-reviewed).
- A **Verification agent** — adversarially checks each rule/reading against the verse.
- A **Tone-Gate agent** — rejects doom-leading or fatalistic output (Pillar 3).
- A **Citation agent** — ensures every claim has a `(Ch, verse)`.
- Domain **Counselor agents** — one per chapter cluster (Mirror, Prasna, Karmajiva, etc.).
- An **Ethics agent** — blocks medical/legal/financial verdicts and unsafe precision (e.g., death dates).

---

## E. What AI is expressly *forbidden* to do here

1. **Invent yogas or doctrines** not present in the source text.
2. **Give medical, legal, or financial verdicts.**
3. **State a precise death date** (Ayurdaya is life-stage context only).
4. **Lead any reading with catastrophe.**
5. **Produce counsel without a citable verse** (general framing is allowed but must be labeled as such).
6. **Alter computed chart facts** (the math layer is deterministic and untouchable by the LLM).

These are encoded in the tone-gate, citation, and ethics agents and in the system prompts of every counselor.

---

## F. The verification standard

Every generative feature carries a built-in self-check: the output is re-parsed to confirm (a) every cited verse actually exists in `sourcetext/` and says what the output claims, and (b) no forbidden output class appears. Outputs that fail the check are regenerated or withheld. This is non-negotiable: **a king does not let a minister speak unchecked.**

---

*Next: [05 — Architecture](./05-architecture.md)*
*See also: [02 — Product Roadmap](./02-product-roadmap.md), [09 — Agent Roster](./09-agent-roster.md)*