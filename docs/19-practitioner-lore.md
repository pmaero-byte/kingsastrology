# 19 — Practitioner Lore: The Living Tradition, Harvested and Classified

### What astrologers on open forums and remedy portals actually suggest — harvested from the open web, classified under the docs/17 Laya protocol, cross-checked against the court's classical layer, and FIREWALLED from doctrine.

---

## 0. Why this exists, and its one hard boundary

The Brihat Jataka is the throne; the verse store and matrices (docs/18) are its doctrine. But the *living tradition* — what a practicing astrologer on r/vedicastrology, Quora, or a remedy portal tells someone with a weak Saturn today — is a different species of knowledge: unrevised, unversed, often Lal Kitab-derived, sometimes commercial. The court does not serve it as doctrine. It **observes** it, classified and organised, so that:

1. the ministries can see what the tradition currently says, per graha;
2. every claim can be cross-checked against the classical layer (does the forum's day/gem/colour/metal match Varāhamihira's own assignments?);
3. the boundary between *classical* and *customary* never blurs in anything we render.

**The firewall (binding):** the lore corpus (`backend/data/practitioner_lore/`) never enters the verse store, never carries verse citations, never renders in a reading or a Daily Brief. Every entry is a draft awaiting Scholar Reviewer triage; ethics-flagged entries can never be auto-drafted (enforced by test).

## 1. The harvest (2026-09-22)

Open web search over practitioner sources: **r/vedicastrology** consensus (thread URLs not retained by the engine — flagged `source_confidence: low`), practicing-astrologer sites (Komilla Sutton, Shilaavinyaas, Astro Nupur, Aditya Kundli, Indastro, Boloji), remedy portals (AstroSage), media astrology (Times of India), and Lal Kitab compilations. Reddit and Quora block direct crawling from this environment (HTTP 403), so forum content enters as search-summarised consensus with explicit low-confidence marking rather than unverifiable pseudo-quotes. **60 sourced entries**; each records site, URL, source kind, and confidence.

## 2. The classification (Laya protocol, docs/17)

`backend/scripts/classify_lore_laya.py` runs the typed-question battery over every entry:

- **Q1 `noul` × 9** — which graha the advice concerns (word-boundary token match; multi-label).
- **Q2 `choice`** — kind of advice: mantra | charity | gemstone | behavioral | ritual | worship | technique | caution.
- **Q3 `noul` (ethics)** — outcome/health/wealth guarantee language; any p ≥ 0.30 forces human review.
- **Q4 (rule)** — **classical-agreement check**: deterministic cross-check of the entry's day/gem/colour/metal mentions against the court's verified conventions (Brihat Jataka Ch 2 v 5 colour verse, Āśvalāyanagṛhyapariśiṣṭa 2.3 materials, the god-planet mapping). Verdicts: consistent / partial / contradicts / no-basis.

Status ladder as in doc 17: `auto-draft` (p ≥ 0.85 + margin) → `scholar-assist` (≥ 0.50) → `escalated`; nothing is ever auto-verified.

**Engine honestly recorded:** the manifest says `fallback-lexicon-v1`. The real `convaiinnovations/laya` checkpoint was designed in doc 17 and is wired behind `--laya`, but the model card itself warns it is near-chance zero-shot on typed decisions until fine-tuned, and the 421M weights are not provisioned on this build host. The lexicon engine implements the *identical* battery, thresholds, and output contract, so swapping in a fine-tuned Laya later changes nothing downstream.

## 3. What the tradition says, organised

**Result: 60/60 classified, 0 escalated, 2 ethics-flagged, 0 contradictions with the classical layer.**

### By graha (entries may touch several)

| Graha | Mentions | The tradition's emphasis |
|----|----|----|
| **Shani** | 12 | the most remediated graha: Saturday practices, black-item donation (til, urad, oil, iron), crow/peepal lamp, feeding the poor, seva to laborers and the elderly — and *gemstone caution* (neelam "can backfire") |
| **Surya** | 7 | arghya to the rising sun, Aditya Hridaya, ruby in gold, wheat/jaggery/copper donation, respect for the father |
| **Budha** | 8 | Wednesday green donation, emerald (after consultation), Saraswati worship, Gayatri 45 days, honesty/cleanliness (Lal Kitab) |
| **Guru** | 6 | Thursday fast, yellow donation (turmeric, chana dal, books), yellow sapphire, Vishnu/Brihaspati worship |
| **Chandra** | 5 | Om Chandraya 108×, milk/rice/white donation, pearl, silver glass, mother's blessings, gentle routines |
| **Rahu** | 6 | Saturday blanket/oil/black-sesame donation, hessonite, elephant idol (Lal Kitab), avoid speculation, *remedy the planet whose house Rahu occupies* |
| **Mangala** | 4 | Mangal beej 11,000×, masoor dal/red cloth/copper donation, red coral, anger discipline |
| **Shukra** | 4 | Friday white donation, diamond/opal, respect for women, cleanliness |
| **Ketu** | 4 | Ganesha worship with durva/modak, blanket donation, cat's eye |
| *(general)* | 8 | cross-cutting: gemstone caution and consult-before-wearing, daan as the default remedy, behaviour over ritual |

### By kind

charity 18 · gemstone 13 · mantra 11 · behavioral 10 · ritual 5 · caution 1 · technique 1 · worship 1 — **the tradition's center of gravity is charity and conduct, not gemstones**, exactly as the r/vedicastrology consensus put it ("consistent effort, honesty and humility matter more than gemstones").

### Classical agreement (21 consistent · 0 contradicts · 39 no-basis)

Every entry that names a day, gem, colour, or metal agrees with the classical layer — Saturday-black-iron-iron for Shani, Wednesday-green-emerald for Budha, Friday-white-silver-diamond for Shukra, and so on. The living tradition has *added* a remedial apparatus the Brihat Jataka never states (donations, fasts, idols, Lal Kitab precautions); it has not *contradicted* the classical assignments. The 39 "no-basis" entries are behavioural and Lal Kitab advice that simply makes no classical-axis claim — recorded as such, never as agreement.

### Ethics flags (2)

"Daan is the best way…" (absolutist) and "a weak Mercury can cause job losses…" (harm-language causation) — both forced to `scholar-assist`; neither can render anywhere without human review.

## 4. Files

| Path | What |
|----|----|
| `backend/data/practitioner_lore/corpus.jsonl` | 60 sourced entries (text, site, URL, kind, confidence) |
| `backend/data/practitioner_lore/classified.json` | per-entry classification (grahas, kind, ethics, agreement, status) |
| `backend/data/practitioner_lore/manifest.json` | engine, counts, firewall statement |
| `backend/scripts/classify_lore_laya.py` | the battery (Laya behind `--laya`; deterministic fallback default) |
| `backend/tests/test_practitioner_lore.py` | 8 tests: sourcing, firewall, statuses, determinism |

## 5. Standing cautions

1. Forum consensus entries carry `source_confidence: low` — the search engine summarised r/vedicastrology consensus without retaining thread URLs. Before any ministry use, those need re-harvesting with URLs retained.
2. The lexicon engine is transparent but shallow: probabilities are normalised keyword scores, not learned calibration. Fine-tuning the real Laya on scholar-triaged lore (doc 17 §4) replaces it without touching the contract.
3. Remedies involving expenditure (gemstones, pujas, homas) are commercial territory; any future rendering of lore must pass the ethics gate that already blocks verdict language — and today, no rendering path exists at all, by design.

---

*See also: [17 — Laya Verse Classification](./17-laya-verse-classification.md) (the protocol), [18 — Source Matrices](./18-source-matrices.md) (the classical layer the lore is checked against), `docs/11-ethics-and-risks.md`.*
