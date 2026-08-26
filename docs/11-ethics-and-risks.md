# 11 — Ethics & Risks

The charter sets the moral floor; this document makes it operational and lists the risks a faithful product must defend against.

## 1. Ethical principles (binding)

1. **Astrology counsels self-knowledge; it is not licensed advice.** No medical, legal, or financial verdicts. The `ethics` agent enforces this on every render; out-of-scope questions are redirected to professionals.
2. **No precise death-date prediction.** Ayurdaya is delivered as life-stage pacing only. This is a hard rule regardless of what the verse math suggests.
3. **Strength before doom (Pillar 3).** The `tone-gate` agent rejects doom-leading drafts; every "what to tend" is paired with an offsetting strength. A reading that ends in fear has failed.
4. **The person owns their chart.** Birth data is encrypted, portable, deletable, never sold, never used for model training. Deletion propagates to all caches.
5. **Dignity for all.** Sensitive readings (women's, early-life, fertility) are reviewed by the `sensitivity` agent and a human; framed with contemporary dignity while honoring the source.
6. **Transparency.** Every reading carries provenance (engine/rulebase/versestore versions, verification_passed). The user can always ask "where is this written?" and reach the verse.
7. **Honesty about uncertainty.** Rectification shows a confidence band; life-stage shows a wide band; no soft estimate is presented as a hard fact.

## 2. Risk register

| # | Risk | Impact | Mitigation | Owner |
|----|----|----|----|----|
| R1 | LLM hallucinates a yoga/verse not in the source | Faithfulness destroyed | Deterministic rule-base at runtime; `citation` + `verification` agents; LLM only renders | AI Lead |
| R2 | Doom-leading/fatalistic output harms a user | Psychological harm; charter failure | `tone-gate` on every render; offsetting-strength rule; dignity close | Ethics Officer |
| R3 | Medical/legal/financial verdict causes real-world harm | Safety + liability | `ethics` agent; redirect to professionals; copy review | Ethics Officer |
| R4 | Precise death date scares a user (esp. a child's chart) | Severe harm | Hard ban in `ethics`; Ayurdaya = life-stage; Balarishta = gentle "tend" notice | Ethics Officer |
| R5 | Birth data leak / sale | Privacy catastrophe | Envelope encryption; never sold; never trained on; deletion honored + audited | Ethics Officer |
| R6 | Compute inaccuracy (wrong ephemeris/ayanamsa) | Every reading wrong | Swiss Ephemeris; test-chart regression (incl. Varahamihira's); per-change QA | Engine Lead |
| R7 | OCR errors in verse store corrupt doctrine | False citations | `verse-indexer` flags uncertain; human Scholar Reviewer clears; `verification` checks | Source Steward |
| R8 | Tone parity drift across platforms | Inconsistent king's voice | `parity-check` agent per release; shared Core (no doctrine in shells) | Platform Lead |
| R9 | Over-claiming accessibility while excluding users | Charter failure (reach all people) | Voice path, large-text, plain-language modes tracked as launch criteria | Platform Lead |
| R10 | Cultural insensitivity in translation/framing | Harm + loss of trust | Human translator review per language; `sensitivity` agent | Localization Lead |
| R11 | Algorithmic determinism disguised as fate | Disempowerment | Always frame as tendency, not verdict; "planets indicate, they do not decree" in copy | Ethics Officer |
| R12 | Children's charts used to forecast their fate | Ethical red line | For minors: readings limited to constructive/developmental framing; no Balarishta death language; guardian-gated | Ethics Officer |

## 3. Hard no-go list (never, regardless of demand)

- Death-date prediction.
- Medical/legal/financial verdicts.
- Selling birth data or ad-targeting from chart contents.
- Sun-sign daily newspaper columns as "your reading."
- Matchmaking pass/fail verdicts on people or relationships.
- "Lucky number" / gambling features.

## 4. Audit cadence

- **Every render:** tone-gate, citation, ethics (automated).
- **Nightly:** faithfulness-sweep on served readings.
- **Per-release:** Scholar Reviewer (doctrine), Ethics Officer (safety), Platform parity.
- **Quarterly:** full privacy + ethics audit; charter-pillar review.

## 5. User-facing ethics commitments (published)

A short, plain-language promise shown at the gate:
> *We read the Brihat Jataka to help you know your strengths and tend your weaknesses — never to frighten you. Every claim cites its verse, which you can read yourself. Your birth data is yours: encrypted, never sold, deletable. This is self-knowledge, not a substitute for doctors, lawyers, or financial advisors.*

---

*See also: [00 — Vision Charter](./00-vision-charter.md), [03 — Project Scope](./03-project-scope.md), [09 — Agent Roster](./09-agent-roster.md)*