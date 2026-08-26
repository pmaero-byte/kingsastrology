# Chapter 4 — Ayurdaya — Determination of the Length of Life / Life-Stage

- **Source:** Brihat Jataka, Chapter 4 (numbered "CH. VII" in the translator's pagination; the chapter heading prints "CHAPTER VIII" at the close)
- **Source text:** sourcetext/pdfcoffee.com_brihat-jataka-of-varahamihira-pdf-free.pdf
- **Runtime use:** deterministic, one-way; no AI at runtime
- **Authoring:** drafted (AI-assisted) → human scholar review → frozen
- **Status legend:** see §5

> **LIFE-STAGE NOTE (binding on this whole chapter).** In this product, Ayurdaya is delivered as **life-stage pacing only**. No precise death date is ever produced. Life-span figures, if shown, are a **wide band** framed as context for pacing one's efforts — never a countdown. The stages this chapter feeds are: childhood, youth, building, mastery, withdrawal. Every effect below is framed constructively as a stage-and-effort map; nothing here is a death clock. Computational figures (Pindayurdaya, Amsayurdaya, reductions) are preserved as table rules so the engine can compute a band, but the user-facing text always closes on dignity and what to do with the season at hand.

---

## R-4.1 — Maximum planetary years (Pindayurdaya base)

- **Cites:** Ch 4, v 1
- **Classification:** table
- **Condition:** For each graha g in {Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn}, when g occupies its exact exaltation degree (Ch 1, v 13), its base contribution (in Savana years) is the fixed value in the table below. Savana year = 360 Savana days; a Savana day runs sunrise-to-sunrise.
- **Effect (one-way, dignity-closing):** The luminaries and planets each carry a maximum life-stage allotment when perfectly placed. These figures are the *scale factors* for the life-season map; they are gifts read as the span a fully dignified planet can pace, not a fixed allotment to the person.
- **Verse (source):** "According to Maya, Yavanacharya, Manittha and Parasara, the maximum number of the years of the Sun, the Moon and other planets are respectively 19, 25, 15, 12, 15, 21 and 20 when the planets are in their exaltation degrees."
- **Status:** draft
- **Notes:** Translator footnote (a): the years are Savana years (360 Savana days; a Soura/solar year = 365.242264 days). Footnote (b): this chapter states several methods; the Author begins with Pindayurdaya. The exaltation signs/degrees are given in Ch 1, v 13. Table — Sun 19, Moon 25, Mars 15, Mercury 12, Jupiter 15, Venus 21, Saturn 20. OCR: "Manfttha" corrected to "Manittha"; "arc" corrected to "are".

## R-4.2 — Reductions for debility, inimical sign, and Astangata (combustion)

- **Cites:** Ch 4, v 2
- **Classification:** table
- **Condition:** Apply reductions to a graha's base years (R-4.1) as follows:
  - (a) **Neechardhaharana:** if g is in its depression (debilitation) degree → take one-half of R-4.1. If between exaltation and depression, scale linearly by arc-distance from exaltation toward depression (proportional reduction).
  - (b) **Lagnayurdaya (Lagna contribution):** years from Lagna = number of Navamsas of the rising sign already risen above the horizon.
  - (c) Alternate (Manittha): Lagna years = number of signs from the first point of Aries to the Lagna.
  - (d) **Satru-Kshetraharana:** if g occupies an inimical sign → lose one-half of its years.
  - (e) **Astangata-harana:** if g is combust (Astangata — disappeared within the combustion limits listed) → lose one-half; where both Satru-Kshetra and Astangata apply, take the **greater** reduction only.
  - (f) Exception: no Satru-Kshetra reduction for Mars occupying an inimical sign (text word "Vakra" — read by some as Mars, by others as a retrograde planet; Varahamihira concurs with the retrograde reading; Badarayana and Garga support the Mars reading).
  - (g) Exception: no Astangata reduction for Venus and Saturn.
  - Combustion limits (degrees from the Sun): Mars 17; Mercury 14 (12 if retrograde); Jupiter 11; Venus 10 (8 if retrograde); Saturn 15; Moon 12.
- **Effect (one-way, dignity-closing):** When a planet is placed in debility or under solar glare, its life-stage contribution is softened but not removed — the season it paces is shorter and asks more care; the exceptions for Mars, Venus and Saturn remind us that some placements keep their stride even in difficulty. These are calibration steps, not verdicts.
- **Verse (source):** "If the planets are in their depression degrees, their years will be one-half of those stated above; if in any other places, the years shall be obtained by proportion. The number of years given by Lagna is the same as the number of Navamsas of the rising sign that may have risen above the horizon. According to some, the number of years given by Lagna is the number of signs between the first point of Aries and the Lagna. Again, if a planet be in an inimical sign, he loses one-half; if he be an Astangata planet, he loses one-half; but no reduction need be made in the case of Mars occupying an inimical sign, or in the case of Saturn and Venus being Astangata planets."
- **Status:** draft
- **Notes:** Footnotes (a)–(h) preserved above. Footnote (c): "some" = Manittha and his school; the Commentator concurs. Footnote (d): Saravali rules that if the lord of the rising Navamsa is powerful, follow (b); if the lord of the rising sign is powerful, follow the signs-from-Aries rule. Footnote (f): Astangata = a planet disappeared within a combustion limit, its light obscured by the Sun; direct-course limits and retrograde limits are listed. Footnote (h): "Vakra" — Varahamihira reads it as "retrograde planet"; Badarayana and Garga read it as "Mars." Flag for scholar review: which reading to freeze. OCR fixes: "depression degro" → "depression degree"; "propoc­tion" → "proportion"; "I~~aili~~his_~~ir~~m" reconstructed as the inimical-sign half-loss clause (source line is garbled; meaning recovered from translator notes — flag for scholar review).

## R-4.3 — Chakrapataharana: house reductions from the rising sign

- **Cites:** Ch 4, v 3
- **Classification:** table
- **Condition:** For each planet p occupying the n-th house from the rising sign (n ∈ {12, 11, 10, 9, 8, 7}), reduce p's years:
  - Malefic in 12th → full reduction (keep 0 of that planet's years).
  - Malefic in 11th → keep 1/2.
  - Malefic in 10th → keep 1/3.
  - Malefic in 9th → keep 1/4.
  - Malefic in 8th → keep 1/5.
  - Malefic in 7th → keep 1/6.
  - If the occupant is **benefic** instead, keep one-half more than the malefic case at that house (i.e. keep 1/2, 3/4, 2/3, 5/8, 11/20, 7/12 respectively — "one-half of the stated reduction" applied to the kept fraction). Flag for scholar review: exact benefic fractions per the translator's note.
  - If several planets occupy one sign, reduce for the **most powerful** one only (Satyacharya; Varahamihira concurs).
  - Reductions are applied to the post-R-4.2 years; order of applying multiple reductions does not affect the final result.
- **Effect (one-way, dignity-closing):** Planets placed in the waning houses (12th through 7th) trim the life-stage budget — malefics more, benefics gently. Where several share a house, the strongest sets the trim. This calibrates the season-map so the building stages are paced realistically; it never cancels a life.
- **Verse (source):** "If malefic planets occupy the 12th, 11th, 10th, 9th, 8th, or the 7th house from the rising sign, a reduction in full, one of one-half, one-third, one-fourth, one-fifth and one-sixth shall be made respectively in the years obtained. If the planets occupying the said houses be benefic ones, the reduction will only be one-half of what was stated for each. But if several planets occupy a single sign, the reduction shall be made for the most powerful one. This is according to Satyacharya."
- **Status:** draft
- **Notes:** Translator note: this reduction (Chakrapataharana) must always be made; where two reductions apply, either order gives the same result. Footnote (a): for malefics keep 0, 1/2, 1/3, 1/4, 1/5, 1/6. Footnote (b): for benefics the kept fraction is half-reduction-on-the-reduction — i.e. the reduction amount is halved, so kept = 1 − (reduction/2). Scholar review needed to confirm the exact six benefic fractions. Footnote (c): Varahamihira concurs with Satyacharya's "most powerful one" rule.

## R-4.4 — Krurodayaharana: malefic in the rising sign

- **Cites:** Ch 4, v 4
- **Classification:** table
- **Condition:** If a malefic planet (Sun, Mars, Saturn — and not the waning Moon, per Badarayana) occupies the rising sign:
  - Let T = total years obtained after R-4.1 through R-4.3.
  - Let N = number of Navamsas from the first point of Aries to the rising Navamsa (counting the fraction of the rising Navamsa already risen).
  - Reduction = T × N / 108. Subtract this from T.
  - If the malefic is aspected by a benefic, the reduction is halved.
  - If both a benefic and a malefic occupy the rising sign, the reduction is taken for the planet nearest the rising point (Badarayana).
  - Alternate (Saravali, Commentator concurs): N = number of Navamsas of the rising sign that have risen above the horizon (not from Aries). The text admits both readings.
- **Effect (one-way, dignity-closing):** A malefic on the ascendant refines the life-season map by how far the sky has turned since Aries; a benefic aspect softens this. The result is a tighter band for the early stages, framing where care and building matter most — not a verdict on life's end.
- **Verse (source):** "If a malefic planet occupy the rising sign, then multiply the total number of years already obtained by the number of Navamsas between the first point of Aries and the Lagna of the rising Navamsa and divide the product by 108. The quotient will be the number of years to be subtracted from the total number of years already obtained. But, if the malefic planet be aspected by a benefic one, the amount of reduction will only be one-half of what was stated above."
- **Status:** draft
- **Notes:** Footnote (a): malefic = Sun, Mars, Saturn, and not the waning Moon (Badarayana). Footnote (b): take the fraction of the rising Navamsa also into account. Footnote (c): this reduction is called Krurodayaharana. Footnote (d): Saravali's reading uses Navamsas of the rising sign already risen; the Commentator concurs — the text supports both. Flag for scholar review: which reading to freeze.

## R-4.5 — Maximum life-span by species

- **Cites:** Ch 4, v 5
- **Classification:** table
- **Condition:** Fixed maximum life-spans: man and elephant 120 years 5 days; horse 32; ass and camel 25; buffalo and ox 24; dog (and clawed animals — cat, tiger, lion, etc.) 12; goat and deer-like 16. To scale for an animal: compute as for a human, then multiply by the species maximum and divide by (120 years 5 days).
- **Effect (one-way, dignity-closing):** This is a species-scaling table; in the product it is used only to frame the upper bound of the human band (120y 5d) as the reference arc for the life-stage map. Animal figures are noted as doctrine but not rendered for human users.
- **Verse (source):** "The maximum length of life of man and the elephant is 120 years and 5 days, that of the horse is 32 years, that of the ass and the camel is 25 years, that of the buffalo and the ox is 24 years, that of the dog is 12 years, and that of the goat and the like is 16 years."
- **Status:** draft
- **Notes:** Footnote (a): "dog and animals with claws, such as the cat, the tiger, the lion, and the like." Footnote (b): "Goat, the deer and the like." Translator note gives the scaling rule. OCR fix: "Dog (a) is 12" → "dog is 12".

## R-4.6 — Reference yoga attaining the maximum human span

- **Cites:** Ch 4, v 6
- **Classification:** table
- **Condition:** Reference configuration (worked example, not a runtime rule): last Navamsa of Pisces rising; Mercury past 25 minutes into Taurus; all other planets in their exaltation signs (and, per Commentators, exaltation degrees). The verse asserts the resulting total is the maximum 120 years 5 days.
- **Effect (one-way, dignity-closing):** This is the calibration yoga that ties R-4.1's per-planet maxima to the 120y5d human ceiling. It is preserved as a self-check for the engine; it is not a user-facing prediction.
- **Verse (source):** "The length of life of a person born when the last Navamsa of Pisces is rising, when Mercury has just passed 25 minutes in sign Taurus and when all the other planets occupy their exaltation signs is the maximum period of 120 years and 5 days."
- **Status:** draft
- **Notes:** The translator prints the worked Rasi Chakra and the full reduction walkthrough (Chakrapataharana on Mars in 11th and Saturn in 8th; no Satrukshetra, Astangata, or Krurodaya reductions apply). Totals: Sun 19, Moon 25, Mars 7y6m5d, Mercury 7y6m, Jupiter 15, Venus 21, Saturn 16, Lagna 9 → 120y5d. Kept as a test fixture for the engine. OCR fixes: "aDd" → "and"; "2S" → "25"; "IS" → "15".

## R-4.7 — Pindayurdaya critique (commentarial, flagged non-Author)

- **Cites:** Ch 4, v 7
- **Classification:** neutral
- **Condition:** Doctrine statement (not chart-testable). The verse reports that Pindayurdaya was also treated by Vishnugupta, Devaswami and Siddhasena; it objects that, rejecting the Balarishta (early-death) period of 8 years, Pindayurdaya never yields under 20 years.
- **Effect (one-way, dignity-closing):** Pindayurdaya is one of three methods; it is sound for the building-and-mastery stages but is known to be weak at the very early season. The product treats its output as a mid-life pacing band, not an early-life verdict.
- **Verse (source):** "This Pindayurdaya method has also been treated of by Vishnugupta, Devaswami and Siddhasena. Rejecting the age of 8, the period of Balarishta or early death, the main fault in this Pindayurdaya is, that, in no case, it gives us years less than 20."
- **Status:** draft
- **Notes:** Footnote (a): Vishnugupta = Chanakya. Footnote (b): the period of Balarishta, to which none of the Ayurdaya rules apply. Footnote (c): the Commentator considers this stanza **not the Author's**; he meets the objection by a worked horoscope (Lagna = first Navamsa of Aquarius; Sun/Moon/Venus exalted; Mercury/Jupiter/Saturn debilitated; Mars at 28° Aquarius) yielding 16y5m — under 20. Flag for scholar review: whether to carry this stanza as doctrine.

## R-4.8 — Raja-Yoga / long-life yoga overlap objection (commentarial, flagged non-Author)

- **Cites:** Ch 4, v 8
- **Classification:** neutral
- **Condition:** Doctrine statement (not chart-testable). The verse objects that certain astrologers (Badarayana, Yavaneswara) ascribe royal life to the very yoga that gives maximum life-span, and that this is evidently erroneous; and that persons born under a sovereign's yoga are often found to live long and poor.
- **Effect (one-way, dignity-closing):** A long-life configuration and a sovereign-role configuration may coexist — length of season and station in life are separate gifts. The product keeps them separate: the life-stage band never claims a throne, and a station reading never claims a span.
- **Verse (source):** "To the very yoga to which the maximum length of life has been assigned, certain Astrologers have ascribed the life of a king. There is an evident error in this. Another error is, that persons born under the yoga of a sovereign are found to live long and poor."
- **Status:** draft
- **Notes:** Footnote (a): "such as Badarayana and Yavaneswara." Footnote (b): the Commentator considers this stanza too **not the Author's**, the objection being absurd — a yoga can be both long-life and sovereign; the second objection is frivolous. OCR fixes: "acc of len" → "are found"; "Jive long and poor" → "live long and poor".

## R-4.9 — Jeevasarma's equal-sevenths and Satyacharya's Navamsa years

- **Cites:** Ch 4, v 9
- **Classification:** table
- **Condition:** Two alternate per-planet year schemes:
  - (Jeevasarma, standing alone, unsupported) each planet's maximum at exaltation = 1/7 of 120y5d = 17 years 1 month 22 days 8 ghatikas 34.3 vighatikas ≈ 17.14484 years, nothing omitted.
  - (Satyacharya, widely supported) each planet's years = the number of Navamsas passed over by that planet (counting from the Navamsa of Aries immediately preceding). No planet can give more than 12 years under this rule.
- **Effect (one-way, dignity-closing):** Satyacharya's Navamsa-count method is the supported alternative to the fixed maxima of R-4.1. It paces each planet's season by how far it has travelled through the zodiac — a finer, more individualised map. Jeevasarma's equal-sevenths is noted but not adopted.
- **Verse (source):** "According to Jeevasarma, the maximum number of years for each planet when in his exaltation sign and degree is one-seventh of the maximum length of human life — 120 years and 5 days — which is, 17 years, 1 month, 22 days, 8 ghatikas, 34.3 vighatikas — 17.14484 years, nothing omitted. In this view, Jeevasarma stands alone and is not supported by other authorities. According to Satyacharya, the planetary years are the same as the number of Navamsas passed over by each planet. This view has the support of many authorities."
- **Status:** draft
- **Notes:** Footnote (a): the several reductions are still to be made, as in Pindayurdaya, before the resulting length is read. Footnote (b): counting from the Navamsa of Aries immediately preceding — so no planet gives more than 12 years. OCR fixes: "buman" → "human"; "hothing" → "nothing"; "Navafn'as" → "Navamsas".

## R-4.10 — Satyacharya Navamsa-from-minutes computation

- **Cites:** Ch 4, v 10
- **Classification:** table
- **Condition:** For each planet p with longitude L (in degrees+minutes): convert L to minutes M; quotient Q = floor(M / 200) = number of Navamsas passed from the first point of Aries (one Navamsa = 200′). Divide Q by 12; the remainder R = Navamsas from the next preceding Navamsa of Aries, and R is also the years (and fraction of a year) for p. (Worked example: Sun at 115°13′ → M = 6913′ → Q = 34 Navamsas → 34 mod 12 = 10 remainder → 10 Navamsas from the preceding Aries Navamsa → 10y 6m 23d 24 ghatikas.)
- **Effect (one-way, dignity-closing):** This is the deterministic procedure that turns each planet's longitude into its Satyacharya year-contribution. It is a computation step feeding the life-stage band, not a user-facing verdict.
- **Verse (source):** "According to Satyacharya, convert the Sphuta or longitude of the planet into minutes; divide the number of minutes by 200; the quotient will represent the number of Navamsas passed over by the planet from the first point of Aries. Divide this by 12, the remainder will give the number of Navamsas from the Navamsa of Aries and the number is also the number of years and fraction of a year for the planet."
- **Status:** draft
- **Notes:** Worked example in source: Sun 115°13′ → 6913′ → 34 Navamsas passed → remainder 10+ (translator prints "lOH ~" / "10½" — OCR garbled) → 10y 6m 23d 24 ghatikas. Flag for scholar review: the exact remainder fraction in the example.

## R-4.11 — Treble for exaltation/retrograde, double for Vargottama/Navamsa/Swakshetra/Drekkana (Satyacharya)

- **Cites:** Ch 4, v 11
- **Classification:** table
- **Condition:** In Satyacharya's Amsayurdaya, for each planet p:
  - If p is in its exaltation sign **or** retrograde → multiply its years by 3.
  - If p is in its Vargottama, or its Navamsa, or Swakshetra, or Drekkana → multiply its years by 2.
  - Same reductions as Pindayurdaya apply (Satru-Kshetra except for Mars; Astangata except for Venus and Saturn; Chakrapata); Krurodayaharana does **not** apply to Satyacharya's method (see R-4.12).
  - Per Garga: a planet in its Neecharasi loses one-half, excepting Chakrapataharana which must always be done; where several reductions apply to one planet, the **biggest** one alone suffices (Bhattotpala, uncontradicted).
  - Order invariance: double/treble first then reduce, or reduce first then double/treble — same result.
- **Effect (one-way, dignity-closing):** Dignified and spirited placements (exalted, retrograde, in own Navamsa or Drekkan or Vargottama) amplify a planet's pacing contribution — a wider season for that planet's gifts. Reductions still apply, but where several would stack, the largest single one is taken; this is kinder, not harsher.
- **Verse (source):** "Again, if any planet occupies its exaltation sign or is retrograde in its motion, the years assigned to it shall be trebled; and if the planet be in its Vargottama or Navamsa or Swakshetra or Drekkana, its years shall be doubled. The above is a special feature in Satyacharya's Ayurdaya. In other respects, it resembles the Pindayurdaya — the several reductions already referred to apply to the present case."
- **Status:** draft
- **Notes:** Footnote (a): reductions applying to Satyacharya = Satru-Kshetra (except Mars), Astangata (except Venus and Saturn), and Chakrapata; Krurodayaharana does **not** apply (see R-4.12). Garga's Neecha-half rule and Bhattotpala's "biggest single reduction" rule quoted in the same footnote. OCR fixes: "retrogradt" → "retrograde"; "Satya­cbaryar" → "Satyacharya's"; "Drekkanna" → "Drekkana" (kept as printed where it appears as a proper term).

## R-4.12 — Satyacharya Lagna years; Krurodayaharana excluded

- **Cites:** Ch 4, v 12
- **Classification:** table
- **Condition:** In Satyacharya's method:
  - Lagna years = number of Navamsas passed over (counted from the next preceding Navamsa of Aries), as for the planets (R-4.10).
  - If the rising sign is powerful (per Ch 1, v 19), then Lagna years = number of signs passed over from Aries (the alternate of R-4.2).
  - **Krurodayaharana does not apply** to Satyacharya's method.
  - The R-4.1 fixed maxima are **not** used here; the Satyacharya per-planet years (R-4.10/R-4.11) are the ones subjected to the reductions.
- **Effect (one-way, dignity-closing):** The ascendant's contribution follows the same Navamsa logic as the planets; if the rising sign is strong, the coarser sign-count is used instead. Krurodayaharana — the early-life trim — is set aside in this method, which is one reason Amsayurdaya is preferred for the full life-season map.
- **Verse (source):** "According to Satyacharya, the years, months, etc. for the Lagna, the rising degree, are the same as the number of Navamsas passed over (as in the case of planets); but if the rising sign be powerful, then, the number of signs passed over represents the years, months, etc. The reduction known as Krurodayaharana does not apply to Satyacharya's method. In the case of the other reductions, the years given in the first stanza ought not to be employed."
- **Status:** draft
- **Notes:** Footnote (a): counting from the next preceding Navamsa of Aries. Footnote (b): "as stated in Stanza 19, Ch. I." Footnote (c): as in Note (d) to Stanza 2. Footnote (d): the special Satyacharya years (not R-4.1 maxima) are the ones reduced.

## R-4.13 — Amsayurdaya is the best method; single-largest multiplier suffices

- **Cites:** Ch 4, v 13
- **Classification:** strength
- **Condition:** Doctrine (method-choice). Satyacharya's Amsayurdaya is declared the best of the three Ayurdaya methods. Objection: planetary years get multiplied several times. Resolution: where a period must be multiplied by several numbers, multiply **once by the largest**. Specifically: if it must be doubled twice or thrice, double once; if trebled twice or thrice, treble once; if it must be both doubled and trebled, treble only.
- **Effect (one-way, dignity-closing):** Amsayurdaya is the master method for the life-stage map. Its multiplications are gentle: a planet never gets amplified more than its largest single warrant. Where the rising-sign lord is powerful, follow Amsayurdaya; where the Sun is powerful, Pindayurdaya; where the Moon is powerful, the Naisargika method (Manittha, Saravali). Bhattotpala favours Amsayurdaya.
- **Verse (source):** "In the matter of Ayurdaya, the method of Satyacharya (known as Amsayurdaya) is the best (of the three methods of Ayurdaya). Objection is made to it, on the ground, that the planetary years have to be multiplied several times. This is not so; where any period has to be multiplied by several numbers, it will be sufficient if the period is multiplied once and by the largest number."
- **Status:** draft
- **Notes:** Footnote (a) gives the cases (Mercury in Virgo exalted + own house + last Navamsa Vargottama + retrograde — would seem to double twice and treble twice; the rule says: double once, treble once, and where both, treble only). Footnote (b): if doubled twice/thrice → double once; if trebled twice/thrice → treble once; if both double and treble → treble only. Manittha/Saravali method-choice by strongest of {rising-sign lord, Sun, Moon} → {Amsayurdaya, Pindayurdaya, Naisargika}. Per others, both Pindayurdaya and Amsakayurdaya should be used to divide life into Dasas/Antardasas and events predicted by both. Bhattotpala favours Amsakayurdaya. OCR fix: "IIny" → "any".

## R-4.14 — Exceptional-life yoga (ordinary rules do not apply)

- **Cites:** Ch 4, v 14
- **Classification:** neutral
- **Condition:** Configuration: Cancer rising; Jupiter and the Moon in the rising sign; Mercury and Venus in Kendras (1st/4th/7th/10th from Lagna); the other planets in the 11th, 6th and 3rd houses. For such a chart, ordinary Ayurdaya calculation does not apply; the verse states the life "far exceeds the maximum period of normal human existence."
- **Effect (one-way, dignity-closing):** Rare, highly dignified configurations exceed the normal life-stage band. In the product this is rendered as "an unusually long mastery-and-withdrawal season; pace your efforts accordingly" — never as a fixed death date. The Commentator's 27 additional example horoscopes (sages living centuries; "by the power of drugs and mantras") are noted as doctrine but are **not** rendered as user-facing predictions; they are flagged for scholar review.
- **Verse (source):** "The life of a person born when sign Cancer is rising, when Jupiter and the Moon occupy such rising sign, when Mercury and Venus occupy the Kendras and the other planets occupy the 11th, 6th and the 3rd houses is not subject to ordinary calculation, but far exceeds the maximum period of the normal human existence."
- **Status:** draft
- **Notes:** Footnote (a): ordinary Ayurdaya rules do not apply; "for further particulars, vide Notes at the end of Chapter IX." The translator then appends 27 example horoscopes of sages (Leo rising with Jupiter in it, etc., living 1,000 / 2,000 / 10,000 / 60,000 years, "a yuga," "a Kalpa," "countless," attaining Deva/Brahma/Muni/Rishi status, often "by the power of drugs and mantras"). These are commentarial exempla, not the Author's verses. Flag for scholar review: whether to carry any of the 27 as separate draft rules. OCR fixes: "perioo" → "period"; "eminel1t" → "eminent"; "penon" → "person"; "Navam sa" → "Navamsa"; "Jupit er" → "Jupiter"; "Simbasa­Darosa" left as printed (an Amsa name, unclear — flag).

## R-4.15 — Shadvarga / Dasavarga Amsa dignities (table for R-4.11 amplifications)

- **Cites:** Ch 4, Amsas Explained (notes at end of chapter)
- **Classification:** table
- **Condition:** A planet occupying its own particular house / Navamsa / Dwadasamsa / Trimsamsa etc. is in its **Varga**. Counting the number of its own Vargas occupied:
  - 2 Vargas → Parijatamsa
  - 3 Vargas → Uttamamsa
  - 4 Vargas → Gopuramsa
  - 5 Vargas → Simhasanamsa
  - 6 Vargas → Paravatamsa
  - 7 or 8 Vargas → Devalokamsa
  - 9 Vargas → Airavatamsa
  - 10 Vargas → Vaiseshikamsa
  - Additional divisions: Saptamamsa (7 parts), Dasamsa (10), Shodasamsa (16), Shashtyamsa (60). Shashtyamsa names for odd signs run Ghora, Rakshasa, Deva, Kubera, … Indurekha (60 names); even signs run the same list in inverse order. A planet in its own Varga within these divisions qualifies for the R-4.11 doubling.
- **Effect (one-way, dignity-closing):** The Amsa dignities name how thoroughly a planet occupies its own territory — the deeper the occupancy, the wider the planet's season in the life-stage map. These are gifts to highlight; they amplify the planet's contribution constructively.
- **Verse (source):** "Now, a planet which occupies his particular house, Navamsa, Dwadasamsa, Trimsamsa, etc., is said to be in his Varga. A planet occupying two Vargas is said to be in Parijatamsa; if he occupies three Vargas, he is said to be in Uttamamsa; if four vargas, in Gopuramsa; if five vargas, in Simhasanamsa; if six, in Paravatamsa; if seven or eight, in Devalokamsa; if nine, in Airavatamsa; and if ten, in Vaiseshikamsa."
- **Status:** draft
- **Notes:** The Amsas-Explained section also defines Saptamamsa, Dasamsa, Shodasamsa and the 60 Shashtyamsa names (preserved in the source). This table supports R-4.11's doubling rule (Vargottama / Navamsa / Swakshetra / Drekkana). Shodasamsa lords add Brahma, Vishnu, Rudra, Surya (odd signs, in that order; even signs in reverse). Flag for scholar review: confirm the canonical list of Shashtyamsa names and their ordering before freezing. OCR fixes: "Sltasfdyamsa" → "Shashtyamsa"; "Dosavarga" → "Dasavarga"; "IJosavarga" → "Dasavarga".