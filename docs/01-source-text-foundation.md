# 01 — Source-Text Foundation Map

### The Brihat Jataka is the throne; this map shows which chapter authorizes which feature.

Every product capability below is bound to a chapter (*adhyaya*) of the **Brihat Jataka of Varahamihira**. The chapter numbering follows the translation held in `sourcetext/`. Where the OCR renders a Roman numeral imperfectly, the Sanskrit chapter name is given as the canonical reference.

> **Rule:** A feature may be built only if at least one chapter is named as its authority. Features with no chapter are out of scope until a verse is found for them.

---

## A. Foundations of the chart (must exist before any reading)

| Ch. | Adhyaya (Sanskrit) | Subject | Authorizes feature |
|----|----|----|----|
| 1 | Unmadagati / Introduction | Nature of the science, time measures, planetary years | `core.time-measures`, `core.planetary-years` |
| 2 | Mesadi | The twelve signs of the zodiac, their natures, lords, castes, directions | `core.rasi-model`, `core.sign-qualities` |
| 3 | Grahagana | The seven planets + Rahu/Ketu, natures, exaltation, debility, moolatrikona, friendships | `core.graha-model`, `core.dignity-table`, `core.planetary-relations` |

These three chapters are the **engine bed**. No reading is possible without them. They produce: sign set, planet set, dignity lookups, friendship/enmity tables used by every later chapter.

## B. Origin of a life (conception → birth)

| Ch. | Adhyaya | Subject | Authorizes feature |
|----|----|----|----|
| 4 | Viyoniprada | Non-uterine / unusual births | `feature.unusual-birth-context` (edge-case handling) |
| 5 | Nisheka | Time of conception, menstrual & fertility timing | `feature.nisheka-fertility` — conception/fertility timing advisor |
| 6 | Janma-kala (matters at birth) | Conditions at the moment of birth, the rising sign | `feature.birth-time-engine`, `feature.lagna-analysis` |

## C. The length and seasons of a life

| Ch. | Adhyaya | Subject | Authorizes feature |
|----|----|----|----|
| 7 | Balarishta | Early death / dangers in childhood | `feature.balarishta-screen` — early-life risk screening (delivered gently, as a "tend carefully" notice) |
| 8 | Ayurdaya | Determination of the length of life | `feature.ayurdaya-estimator` — life-span / life-stage estimate with confidence band |
| 9 | Dasa & Antardasa | Planetary periods and sub-periods of life | `feature.dasa-timeline` — the life timeline (the flagship "seasons of your life" view) |
| 10 | Ashtakavarga | Benefic/malefic point scores per house per planet | `feature.ashtakavarga-score` — transit & house-strength scoring model |

## D. Vocation and station (the strength side of the mirror)

| Ch. | Adhyawa | Subject | Authorizes feature |
|----|----|----|----|
| 11 | Karmajiva (Avocation) | Wealth from father, mother, friend, brother, wife, servant; profession | `feature.karmajiva-advisor` — vocation/career recommender |
| 12 | Raja Yoga | The birth of kings; combinations for sovereignty & leadership | `feature.raja-yoga-detector`, `feature.leadership-profile` |
| 13 | Nabhasa Yogas | The 32 Nabhasa yogas — overall life-pattern archetypes | `feature.nabhasa-archetype` — life-pattern archetype classifier |
| 14 | Chandra (Lunar) Yogas | Sun-Moon based yogas (Adhi etc.) — conduct, wealth, intelligence | `feature.lunar-yoga-detector` |
| 15 | Double planetary yogas | Yogas from pairs of planets together in a sign | `feature.pair-yoga-detector` |

## E. The inner character and the ascetic path

| Ch. | Adhyaya | Subject | Authorizes feature |
|----|----|----|----|
| 16 | Pravrajya (Ascetic Yogas) | When four+ planets occupy one sign → renunciation / focused vocation | `feature.pravrajya-detector` — single-minded-vocation / ascetic tendency reading |
| 17 | Nakshatra (Moon in asterisms) | Moon in each of the 27 nakshatras → conduct & temperament | `feature.nakshatra-temperament` — nakshatra personality model |
| 18 | Rasi-Chandra (Moon in signs) | Moon in each zodiac sign | `feature.moon-in-sign-profile` |
| 19 | Graha-in-Rasi (Sun, Mars & others in signs) | Each planet in each sign | `feature.planet-in-sign-profile` — the core "strengths/weaknesses per planet" engine |
| 20 | Drishti (Planetary aspects) | Effects of planets aspecting each other and the Moon | `feature.aspect-effects` |

## F. Houses, divisional charts, and the synthesis

| Ch. | Adhyaya | Subject | Authorizes feature |
|----|----|----|----|
| 21 | Bhava (Planets in houses) | Each planet in each of the 12 bhavas | `feature.bhava-profile` — life-area readings (1st=body/self, 2nd=wealth, … 12th=loss/ liberation) |
| 22 | Varga (Planets in divisional charts) | Each planet in its own house in the several vargas | `feature.varga-engine` — divisional charts (D1, D9, D10, etc.) for depth |
| 23 | Mishra (Miscellaneous yogas) | Planets in own/exalted/moolatrikona signs | `feature.misc-yoga-detector` |
| 24 | Arishta (Malefic yogas) | Afflictions from 5th/7th etc. | `feature.arishta-detector` — risk indicators (delivered constructively, per Pillar 3) |

## G. Special readings

| Ch. | Adhyaya | Subject | Authorizes feature |
|----|----|----|----|
| 25 | Strijataka | Horoscopy of women | `feature.strijataka` — women-specific readings (with appropriate framing) |
| 26 | Apavatika (Lost horoscopes) | Recovering an unknown birth time | `feature.birth-rectification` — AI birth-time rectification engine |
| 27 | Prasna | Queries / horary — answering a question from the moment asked | `feature.prasna` — "Ask the King" decision/query engine |
| 28 | Nisheka-Adhana (closing) | Conception & prenatal recap | `feature.prenatal-summary` |

---

## The verse-citation contract

Every reading rendered to a user is built from one or more of the features above. Each feature, in turn, resolves every one of its outputs to a **(chapter, verse)** pair in the source text. The UI exposes this as a footnoted citation; tapping it opens the verse with the surrounding translation text.

This is what makes us *Kingsastrology* and not a generic horoscope app: **the source text is always one tap away from any claim.**

## Priority tiers for the roadmap

- **Tier 1 — The mirror (MVP):** chapters 2, 3, 9, 17, 18, 19, 21, 13, 12, 24. These together produce a complete *strengths-and-weaknesses self-portrait* with a life timeline. Nothing else ships until these are faithful.
- **Tier 2 — The counselor:** chapters 11, 8, 10, 20, 14, 15, 16, 25, 27. Vocation, longevity stage, ashtakavarga scoring, aspects, lunar & ascetic yogas, women's readings, the query engine.
- **Tier 3 — The full court:** chapters 1, 4, 5, 6, 7, 22, 23, 26, 28. Conception, unusual births, birth-time matters, divisional charts, rectification, prenatal summary.

The roadmap phases (see `02-product-roadmap.md`) are built on exactly these tiers.

---

*Next: [02 — Product Roadmap](./02-product-roadmap.md)*