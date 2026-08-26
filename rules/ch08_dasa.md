# Chapter 4 — Dasa & Antardasa — Planetary divisions and sub-divisions of life

- **Source:** Brihat Jataka, Chapter 4 (running header "Ch. VIII"; chapter divider "CHAPTER IX")
- **Source text:** sourcetext/pdfcoffee.com_brihat-jataka-of-varahamihira-pdf-free.pdf
- **Runtime use:** deterministic, one-way; no AI at runtime
- **Authoring:** drafted (AI-assisted) → human scholar review → frozen
- **Status legend:** see §5 of README.md

> Framing note for this chapter: a Dasa is *the season of life you are in* — its lord sets the pace and colour of that stretch of years, not a fixed fate. Strength/tend rules below describe the texture of that season; the technical-name `table` rules (R-4.5 to R-4.8) decide whether a given period reads as Sampurna/Poorna (prosperous), Rikta/Adhama (lean), or Misraphala (mixed), and the effect rules (R-4.12 to R-4.18) then shade in the season accordingly. Where a planet is well-placed, the gift-side of its season leads; where it is ill-placed, the same season is named as a tendency to tend, paired with its offsetting strength.

---

## R-4.1 — Dasa order: Kendra, Panaphara, Apoklima groups

- **Cites:** Ch 4, v 1
- **Classification:** table
- **Condition:** Determine which of {Lagna, Sun, Moon} is most powerful (by the sthana/dik/chesta/kala/graha-darsana balas of Ch 2 st. 19–21). Its period comes first and heads its sign-quality group. Then come the periods of planets occupying Kendra houses (1, 4, 7, 10) from that most powerful of {Lagna/Sun/Moon}; then those in Panaphara houses (2, 5, 8, 11); then those in Apoklima houses (3, 6, 9, 12). If no planets occupy a given group, the periods of the other planets come in the order stated. The sign-quality (Movable / Fixed / Common) of the powerful Lagna/Sun/Moon decides the group order: Movable-sign group first → Fixed → Common; if Fixed, Fixed → Common → Movable; if Common, Common → Movable → Fixed.
- **Effect (one-way, dignity-closing):** The order of your life-seasons is set by whichever of the rising sign, the Sun, or the Moon is strongest at birth: its group leads, and the planets standing in the angular (Kendra) houses follow first, then those in the succedent (Panaphara) houses, then those in the cadent (Apoklima) houses. Empty groups are simply skipped, and the remaining seasons follow in the stated order.
- **Verse (source):** "Determine first which of the following three is powerful—(a) the Rising Sign, the Sun and the Moon. His period comes first. Then follow the periods of the planets occupying the Kendra houses, from such powerful rising sign or the Sun or the Moon. Then come the periods of the planets occupying the Panaphara houses from the same; and lastly come the periods of planets occupying the Apoklima houses (b). If there be no planets in the Kendra or Panaphara or Apoklima houses, then the periods of the other planets come in the order stated (c)."
- **Status:** draft
- **Notes:** Translator notes (a) "in more ways than one in comparison with the other two according to Yavaneswara (vide Stanzas 19 to 21 of Ch. II, and Stanza 19 of Ch. I)"; (b) the within-group order is given in stanza 2; (c) the 8 Dasa periods split into three groups by sign-quality (Movable / Fixed / Common); the leading group is always headed by the powerful Lagna/Sun/Moon. Testable from ChartFactBundle once "most powerful of {Lagna, Sun, Moon}" and house-group occupancy are computed.

## R-4.2 — Within-group order: power, then period-length, then rising order

- **Cites:** Ch 4, v 2
- **Classification:** table
- **Condition:** Among planets occupying the same house-group (Kendra / Panaphara / Apoklima) from the leading Lagna/Sun/Moon, order their Dasa periods by: (1) greatest strength first; (2) if equal strength, the planet whose Dasa period (per Ch 4 years) is longest first; (3) if equal in both, the planet that rises first (reappears after conjunction with the Sun) first. Dasa lengths are those "found in the last Chapter" (Ch 4).
- **Effect (one-way, dignity-closing):** Within each group, the strongest planet's season opens; ties break toward the longer natural period, and further ties break toward the planet that rises first. This gives a determinate sequence for every season of the chart.
- **Verse (source):** "The lengths of the several planetary periods known as Dasas are the same as those of the planets, as found in the last Chapter. Again, of the several planets occupying the Kendra or Panaphara or Apoklima houses, the Dasa period of the most powerful planet comes first, then comes that of the planet next in power and so on; but if the planets be of equal power (a), the Dasa period of the planet whose period is the longest comes first; and if the planets be of equal power and period, then, the period of the planet which rises first (b) comes first."
- **Status:** draft
- **Notes:** Translator note (a) gives the equal-power rule: e.g. if Saturn is strong in 3 of the five bala-ways and Mars in 2, but Mars has Naisargika strength over Saturn, the two are counted equal. Note (b): "rises first" = reappears after conjunction with the Sun, per Garga. The "last Chapter" years are the planetary Ayur-dasa years of Ch 4 (not the Vimshottari years of R-4.24); scholar review should confirm which year-table the runtime should attach to this rule.

## R-4.3 — Antardasa fractions by house from the Dasa lord

- **Cites:** Ch 4, v 3
- **Classification:** table
- **Condition:** For a given Dasa lord L, the Antardasa (sub-period) length of a planet P occupying a house counted from L is a fraction of L's Antardasa period: P in the same house as L → 1/2; P in the 5th or 9th from L → 1/3 each; P in the 7th from L → 1/7; P in the 4th or 8th from L → 1/4. The Antardasa periods of the Lagna-dasa are determined the same way. If several planets share a house, the most powerful among them is the Antardasa lord and takes that house's fraction; if no planet occupies a place, that fraction is simply omitted. Within-group order of sub-periods: the lord itself first, then the same-house planet, then 5th/9th, then 7th, then 4th/8th.
- **Effect (one-way, dignity-closing):** Each main season is divided into sub-seasons. The lord of the season takes the largest share; planets sharing its house take half each; those a trine away (5th/9th) take a third; the opposite-seat (7th) takes a seventh; and those on the 4th/8th axis take a quarter. Empty seats contribute no sub-season.
- **Verse (source):** "The period of the Antardasa (a) (sub-division of planetary period) of the planet (b) occupying the same house as the lord of the Dasa period, is one-half of the Antardasa period of such lord. The Antardasa periods of the planets occupying the 5th and the 9th houses from the lord of the Dasa period, are, each, one-third; those of the planets occupying the 7th house from the lord are, each, one-seventh; and those of the planets occupying the 4th and the 8th houses from the lord, are, each, one-fourth of the Antardasa period of the lord. The Antardasa periods of the Lagna-dasa shall be determined in the same way."
- **Status:** draft
- **Notes:** Translator note (a): Dasa = planetary division of life; Antardasa = sub-division. Note (b) spells out the within-period order and the "most powerful planet in a shared house becomes Antardasa lord" rule; also that if several planets occupy the 5th/9th the fraction for the powerful one of each is 1/3, and similarly 1/4 for the 4th/8th. Fractions are testable given ChartFactBundle house positions and a "most powerful in house" selector.

## R-4.4 — Antardasa fractions reduced to a common denominator

- **Cites:** Ch 4, v 4
- **Classification:** table
- **Condition:** Take the set of fractions {1/2, 1/3, 1/7, 1/4} that actually apply in a given Dasa (only those houses that are occupied). Reduce them to a common denominator with different numerators; sum the numerators; divide the Dasa period by that sum to get a unit; multiply the unit by each numerator to obtain each Antardasa length.
- **Effect (one-way, dignity-closing):** The sub-season lengths are kept in exact proportion to one another. Reduce the applicable fractions to one denominator, add the numerators, and the Dasa length divided by that sum gives the base unit; each numerator times the unit is that sub-season's length.
- **Verse (source):** "The fractions (a) should all be made to have a common denominator with different numerators. The Dasa period should be divided by the sum of the numerators and the quotient when multiplied by the several numerators will give the periods of the several Antardasas."
- **Status:** draft
- **Notes:** Translator note (a): the possible fractions are 1/2, 1/3, 1/7, 1/4. Worked example in the footnote: if planets occupy the same house, 5th/9th, and 4th/8th (but not 7th) from the lord, the fractions 1/2 : 1/3 : 1/4 reduce to 12/84 : 6/84 : 4/84 wait — the footnote's arithmetic reads "12 : 6 : 4 : 3" with sum 25 (the 3 appears to be the lord's own share or a misprint; the running text gives 12, 6, 4, 3 summing to 25). Scholar review should verify the footnote numerators against a critical edition; the algorithm itself is testable.

## R-4.5 — Sampurna, Rikta, and Ashta — period names by dignity

- **Cites:** Ch 4, v 5
- **Classification:** table
- **Condition:** For the most powerful planet at birth: (a) if it occupies the exaltation degree of its exaltation sign → its Dasa (and Antardasa) is **Sampurna** (also Poorna if it occupies the exaltation sign but is not otherwise powerful, per the commentator); (b) if a weak planet occupies the depression degree of its depression sign → **Rikta** (also Rikta if a weak planet occupies simply its depression sign); (c) if a planet occupies an inimical Navamsa AND the depression degree of its depression sign → **Ashta**.
- **Effect (one-way, dignity-closing):** A season whose lord stands at its exaltation degree is named Sampurna — full, vast in prosperity. A season whose lord is weak at its depression degree is named Rikta — lean, a season of restraint. A season whose lord is both in an inimical Navamsa and at its depression degree is named Ashta — the leanest naming, to be tended with care.
- **Verse (source):** "The Dasa period (a) of the most powerful (b) planet occupying at the time of birth the exaltation degree of its exaltation sign, (c) is known as Sampurna (a). The dasa period of a weak planet occupying the depression degree of its depression sign is known as Rikta (e). The dasa period of a planet occupying an inimical Navamsa and also the depression degree of its depression sign is known as Ashta."
- **Status:** draft
- **Notes:** Translator note (a): the naming applies to the Antardasa period as well in all three cases. (b) "powerful in every way" per Ch 2 st. 19–21. (c) the commentator extends Sampurna/Poorna naming to a planet that is not powerful but occupies its exaltation sign. (e) the commentator extends Rikta to a weak planet occupying simply its depression sign. OCR: the source prints "Allisllta" for the third name — this is an obvious scan error for "Ashta"; flagged for scholar confirmation (the Sanskrit may be *Aṣṭa* / "burnt"). The naming feeds R-4.19 (benefic/malefic/mixed).

## R-4.6 — Avarohini, Madhyama, Arohini, Adhama — period names by motion and Navamsa

- **Cites:** Ch 4, v 6
- **Classification:** table
- **Condition:** For a Dasa lord: (a) if it is quitting the exaltation degree and moving toward the depression sign → **Avarohini** (descending); while so moving, if it occupies a friendly or exaltation Navamsa (or its own Navamsa per the commentator) → **Madhyama**; (b) if it is quitting the depression degree and moving toward the exaltation sign → **Arohini** (ascending); while so moving, if it occupies an inimical or depression Navamsa → **Adhama**. Per the commentator, Arohini and Madhyama dasas produce prosperity; Avarohini and Adhama dasas produce difficulty; a planet in a neutral sign or Navamsa produces neither.
- **Effect (one-way, dignity-closing):** A season whose lord is climbing from depression toward exaltation — Arohini — is a rising season, and if it passes through friendly or exaltation Navamsas it is Madhyama, a season of measured good. A season whose lord is descending from exaltation toward depression — Avarohini — is a waning season, and if it passes through inimical or depression Navamsas it is Adhama, a season to be tended. A lord in a neutral seat gives a season of neither peak nor trough.
- **Verse (source):** "The dasa period (a) of a planet which quitting the exaltation degree moves towards the depression sign is known as Avarohini (b); while so moving, if the planet occupy a friendly or an exaltation Navamsa (c), his dasa period is known as Madhyama. Again, the dasa period of a planet which quitting the depression degree moves towards its exaltation sign is known as Arohini (d); while so moving, if the planet occupy an inimical or a depression Navamsa, his dasa period is known as Adhama (e)."
- **Status:** draft
- **Notes:** Translator note (a): applies to Antardasa also. (b) "such dasa periods produce evil." (c) the commentator reads "or his own Navamsa"; an exaltation Navamsa is one bearing the name of the exaltation sign. (d) "such dasa periods produce prosperity." (e) the commentator summarises: Arohini and Madhyama → prosperity; Avarohini and Adhama → evil; neutral sign/Navamsa → neither. "Motion toward" requires ephemeris state at the commencement of the Dasa — testable if the runtime computes the lord's directional motion at that epoch.

## R-4.7 — Misraphala — mixed period names

- **Cites:** Ch 4, v 7
- **Classification:** table
- **Condition:** A Dasa lord that occupies a depression or inimical Navamsa while in a good position (own house, friendly house, Moolatrikona, or exaltation house) is named **Misraphala** (mixed). The commentator extends the same name to: a lord in an inimical or depression sign while in its own / friendly / Moolatrikona / exaltation Navamsa, or in a Vargottama place. The several names indicate by their meaning the nature of the dasa: Sampurna → vast prosperity; Poorna → prosperity; Adhama → misery, little prosperity; Rikta → misery and poverty; Misraphala → a mixture of good and evil.
- **Effect (one-way, dignity-closing):** A season whose lord is dignified in one Varga but weakened in another is Misraphala — a mixed season, some gifts and some strains interwoven, neither wholly bright nor wholly lean. The name itself tells you the texture: Sampurna and Poorna bring prosperity, Adhama and Rikta bring restraint, and Misraphala brings both in turn.
- **Verse (source):** "The dasa period (a) of a planet, which occupies a depression or an inimical Navamsa, when in a good position (b), is known as Misraphala (c). The several names of the dasas indicate by their meaning the nature of the dasa periods (d). We shall describe (in the course of this Chapter) (e) the effects of the several planetary dasas."
- **Status:** draft
- **Notes:** (a) applies to Antardasa also. (b) "good position" = own house, friendly house, Moolatrikona, or exaltation house. (c) the commentator's extensions as above. (d) the name→meaning map (Sampurna, Poorna, Adhama, Rikta, Misraphala) is the runtime lookup. (e) forward reference to stanza 12 onward.

## R-4.8 — Lagna-dasa naming by rising Drekkana and sign-quality

- **Cites:** Ch 4, v 8
- **Classification:** table
- **Condition:** Classify the rising sign by quality (Movable = Aries/Cancer/Libra/Capricorn; Fixed = Taurus/Leo/Scorpio/Aquarius; Common = Gemini/Virgo/Sagittarius/Pisces) and note the rising Drekkana (1st, 2nd, or 3rd). The Lagna-dasa name is:
  - Common rising sign: 1st Drekkana → Adhama; 2nd → Madhyama; 3rd → Uttama (Subha).
  - Movable rising sign: 1st → Uttama; 2nd → Madhyama; 3rd → Adhama (Asubha).
  - Fixed rising sign: 1st → Adhama (Asubha); 2nd → Uttama (Subha); 3rd → Madhyama (Sama).
  The names indicate the nature of the Lagna-dasa period: Adhama → misery; Madhyama → mixed; Uttama → prosperity.
- **Effect (one-way, dignity-closing):** The opening season of life — the Lagna-dasa — is graded by the quality of the rising sign and which third of it is rising. An Uttama (Subha) opening is prosperous; a Madhyama (Sama) opening is mixed; an Adhama (Asubha) opening is lean and asks for tending. Whichever you find, the grade names the season's texture, not its verdict.
- **Verse (source):** "According as the rising Drekkana is the first, second or third, the Lagna dasa is known as Adhama, Madhyama or Uttama if the rising sign be a common sign; Uttama, Madhyama or Adhama if the rising sign be a movable sign; and Adhama, Uttama or Madhyama if the rising sign be a fixed sign."
- **Status:** draft
- **Notes:** Translator's prose expansion in the footnote lays out all nine combinations and the alternate names (Subha/Asubha/Sama). Testable from ChartFactBundle once rising sign, its quality, and the rising Drekkana index are known.

## R-4.9 — Naisargika (natural) Dasa order and years

- **Cites:** Ch 4, v 9
- **Classification:** table
- **Condition:** The Naisargika (natural) Dasa applies to all creatures. The order and years are: Moon 1, Mars 2, Mercury 9, Venus 20, Jupiter 18, Sun 20, Saturn 50 — totalling 120 years. If the Naisargika Dasa period and the ordinary planetary Dasa (or Antardasa) period run together, that period is prosperous. Per Yavaneswara, the closing period (after 120 years) is the Naisargika Lagna-dasa and produces prosperity (some object to this). The lord of a Naisargika Dasa, if powerful and in an Upachaya place, produces prosperity; if weak and in an Apachaya place, produces evil.
- **Effect (one-way, dignity-closing):** Alongside the birth-chart Dasas runs a natural sequence shared by all living beings — Moon, Mars, Mercury, Venus, Jupiter, Sun, Saturn — covering 120 years. When a natural season and a chart season coincide, the overlap is prosperous. A natural-season lord who is strong and in an Upachaya seat gives prosperity; one who is weak and in an Apachaya seat asks for tending.
- **Verse (source):** "The Naisargika (natural) dasas in the case of all creatures are those of the Moon, Mars, Mercury, Venus, Jupiter, the Sun and Saturn in the order stated, and their periods are respectively 1, 2, 9, 20, 18, 20 and 50 years (a). If the Naisargika Dasa period and the ordinary planetary dasa (b) period happen to run together, such period (c) will be a prosperous one. According to Yavaneswara, the closing period (d) is the Naisargika Lagna dasa and produces prosperity. This is objected to by some."
- **Status:** draft
- **Notes:** (a) total 120 years. (b) or Antardasa per the commentator. (c) a similar remark applies to the Antardasa periods. (d) the period of life after 120 years. This is the *Naisargika* Dasa — distinct from the Vimshottari/Udu Dasa of R-4.24; scholar review should confirm both are surfaced in the runtime and not conflated.

## R-4.10 — Prosperity conditions for a Dasa period

- **Cites:** Ch 4, v 10
- **Classification:** strength
- **Condition:** A Dasa (or Antardasa) period is prosperous when, at its commencement, any of the following holds: (i) the Dasa lord or one of its friendly planets occupies the Lagna; (ii) the Lagna belongs to a Varga (Sign/Hora/Drekkana/Navamsa/Dvadasamsa/Trimsamsa) of the Dasa lord; (iii) a benefic planet occupies the Lagna; (iv) the Dasa lord occupies the 3rd, 6th, 10th, or 11th house from the Lagna. Additionally, the Moon brings prosperity while she transits a sign friendly to the Dasa lord, or the Dasa lord's exaltation sign, or the 3rd, 6th, 10th, 11th, 5th, 9th, or 7th house from the sign occupied by the Dasa lord; in other places she produces misery. If the Lagna-occupying friendly/benefic planet is an Atimitra (very friendly) to the Dasa lord, the period is very prosperous; if an Atisatru (bitter enemy), not prosperous; if neutral, just the effects of the Dasa period occur.
- **Effect (one-way, dignity-closing):** A season is prosperous when the Dasa lord or a friendly planet rises at its opening, or the rising sign carries the lord's own division, or a benefic graces the ascendant, or the lord stands in an Upachaya seat (3, 6, 10, 11) from the Lagna. The Moon transiting a friendly or exaltation sign of the lord, or one of the 3/6/10/11/5/9/7 seats from him, sweetens the days within that season; elsewhere she marks harder days. Where the friendly planet is a very-friend, the prosperity deepens; where it is a bitter enemy, the season's good is withheld.
- **Verse (source):** "If the lord of the Dasa period or one of his friendly planets occupy the Lagna (a), or if the Lagna belong to the Varga (division) (b) of the lord of the Dasa period, or if a benefic planet occupy the Lagna, or if the lord of the Dasa period occupy the 3rd, 6th, 10th or the 11th house from the Lagna, such Dasa period (c) will be a prosperous one (d). Again, when the Moon occupies (e) a sign friendly (f) to the lord of the Dasa (g) or the exaltation sign of the lord of the Dasa or the 3rd, 6th, 10th, 11th, 5th, 9th or the 7th house (h) from the sign occupied by the lord of the Dasa period, she will bring on prosperity: otherwise (i), she will produce misery."
- **Status:** draft
- **Notes:** (a) "Lagna" is interpreted as the rising sign at the moment of commencement of the Dasa — the translator remarks that determining the Lagna at a Dasa's commencement (let alone its Varga) is "absolutely impossible" without recomputing the heavens for that hour; scholar review should decide whether the runtime uses the birth Larga or a recomputed commencement Lagna. (b) Varga examples: Sign, Hora, Drekkana, Navamsa, Dvadasamsa, Trimsamsa of the Dasa lord. (c) or Antardasa per the commentator. (d) Atimitra / Atisatru / neutral refinements as above. (e)–(i) the Moon's transit seats are reckoned from the sign occupied by the Dasa lord (or Antardasa lord) in the course of motion. The good/bad effects affect, by Varga, the objects signified by the several Bhavas (cf. Ch 1 st. 15). Some sub-conditions depend on transit ephemeris at runtime — testable if the engine computes the Moon's place at the relevant time.

## R-4.11 — Moon's sign at a Dasa's commencement — flavour of the season

- **Cites:** Ch 4, v 11
- **Classification:** neutral
- **Condition:** At the commencement of a Dasa period, note the sign the Moon occupies. By that sign: Cancer → rich, comfortable, respected; Aries or Scorpio → wife unchaste; Gemini or Virgo → learned, gains friends, becomes rich; Leo → works in forests, on roads, near houses; Taurus or Libra → eats sumptuous meals; Capricorn or Aquarius → gets a bad woman; Sagittarius or Pisces → rich, happy, respected.
- **Effect (one-way, dignity-closing):** The Moon's sign at the opening of a season colours its texture: Cancer steadies you in comfort and respect; Gemini or Virgo turns the season toward learning, friendship, and wealth; Taurus or Libra toward generous meals; Sagittarius or Pisces toward happiness and regard; Leo toward work in forests, roads, and homesteads; Aries or Scorpio toward strain in partnership; Capricorn or Aquarius toward difficult companions. Each is a seasonal colour, not a verdict on the whole life.
- **Verse (source):** "If, at the time of commencement of the Dasa period of a planet, the Moon occupy sign Cancer, the native will become rich, will live in comfort and will be respected; if, at the time, the Moon occupy sign Aries or sign Scorpio, his wife will become unchaste; if the Moon occupy either sign Gemini or sign Virgo, the person will become learned, get friends and become rich; if the Moon occupy sign Leo, the person will work in forests, on roads and near houses; if the Moon occupy sign Taurus or sign Libra, he will eat sumptuous meals; if she occupy sign Capricorn or sign Aquarius, he will get a bad woman: and if the Moon occupy sign Sagittari or sign Pisces, the person will become rich, happy and respected."
- **Status:** draft
- **Notes:** Requires the Moon's sign at the Dasa's commencement (recomputed epoch). The "wife unchaste" / "bad woman" phrases are stark in the source; the runtime should render them as seasonal strain in partnership/companionship rather than as a verdict on a person. Paired with R-4.10's prosperity conditions where applicable. Testable given the commencement Moon sign.

## R-4.12 — Dasa of the Sun

- **Cites:** Ch 4, v 12
- **Classification:** tend
- **Condition:** The current Dasa (or Antardasa) lord is the Sun. Apply the good-side effects when the Sun's period is benefic by R-4.5 to R-4.8 (Sampurna/Poorna/Arohini/Madhyama/Misraphala-good); apply the strain-side when malefic (Rikta/Ashta/Avarohini/Adhama/Misraphala-evil); both when mixed.
- **Effect (one-way, dignity-closing):** The Sun's season gains wealth through perfumes, nails, elephant-tusk and the like, tiger-skin and the like, gold, through acts of boldness, through roads, through the king, and through battle. It makes one cruel, courageous, persevering, renowned, and valorous; one gives liberally. The season also tends to bring trouble through wife, son, money, enemy, weapons, fire, or the king; quarrels with servants; and chest- and belly-aches and the like — these are tendencies to tend, offset by the courage and renown the same season gives, and by the liberal hand it opens.
- **Verse (source):** "In the Dasa period (a) of the Sun, a person will acquire wealth by dealing in perfumes or nails, tush of elephants and the like animals, in tiger skin and the like, in gold, by acts of cruelty, by means of roads, by the king and by battle. He will become cruel, courageous, persevering, renowned and valorous, will get into trouble through his wife, son, money, enemy, weapons, fire or the king; and he will become liberal in gifts and addicted to sinful deeds; he will quarrel with his servants and will become afflicted with pain in his chest and belly and the like diseases."
- **Status:** draft
- **Notes:** (a) or Antardasa per the commentator. The technical name (Sampurna etc.) decides which side of the effect comes to pass (cf. R-4.19). "Acts of cruelty" / "sinful deeds" are rendered in the source; the runtime should frame them as the harsh-bold texture of a Sun season, paired with the courage and liberality the same season brings.

## R-4.13 — Dasa of the Moon

- **Cites:** Ch 4, v 13
- **Classification:** strength
- **Condition:** The current Dasa (or Antardasa) lord is the Moon. Benefic side applies when the period is Sampurna/Poorna/Arohini/Madhyama; the strain-side (sleep, idleness, loss of wisdom/wealth/renown, quarrels with powerful men and kinsmen) applies when malefic.
- **Effect (one-way, dignity-closing):** The Moon's season brings benefit through mantras, Brahmins, sugarcane products, milk, ghee and the like, cloth, flowers, play, sesame seeds, and food. One grows patient, honours virtuous Brahmins and the Devas, gains daughters, and increases in wisdom, wealth, and renown. The same season can lean toward sleep and idleness and quarrels with the powerful and with kin — tended by the patience and devotion it also opens.
- **Verse (source):** "In the Dasa period of the Moon, the person will derive benefits from dealing in or by means of the mantras, the Brahmins, the productions of sugar-cane, milk, ghee, and the like, cloth, flower, play, sesamum seeds and food; he will be of patient nature; he will respect virtuous Brahmins and the Devas; he will get daughters and will acquire an increase of wisdom, wealth and renown. The person will indulge in sleep and idleness, will lose his wisdom, wealth and renown and will quarrel with powerful men and with kinsmen."
- **Status:** draft
- **Notes:** No translator footnote. The closing strain-clause is paired with the patience/devotion/wisdom strength above so the season is not doom-leading.

## R-4.14 — Dasa of Mars

- **Cites:** Ch 4, v 14
- **Classification:** tend
- **Condition:** The current Dasa (or Antardasa) lord is Mars. Benefic side applies when Mars's period is Sampurna/Poorna/Arohini/Madhyama; the strain-side when malefic.
- **Effect (one-way, dignity-closing):** Mars's season gains wealth through fighting one's enemies, through one's brother, the king, lands, woollen goods, and goats. The season also tends toward hatred of sons, friends, wife, and brothers, distaste for the learned and the eminent, diseases of thirst, blood, fever, bile, loss of limbs, or association with other women, and harsh, cruel speech — these are tendencies to tend, offset by the courage and the brother-/king-/land-backed wealth the same season can bring.
- **Verse (source):** "In the Dasa period of Mars, the person will acquire wealth, by fighting with his enemies, through his brother, the king, lands, woollen goods and goats. He will hate his sons, friends, wife, and brothers and will dislike learned men and men of importance; he will suffer from diseases caused by or connected with thirst, blood, fever, bile, loss of limbs or sexual intercourse with other women. He will associate with men doing wicked deeds; he will become vicious, harsh in speech and cruel."
- **Status:** draft
- **Notes:** No translator footnote. The strain-side is heavy in the source; the runtime should pair every strain with Mars's gift-side (courage, wealth through brothers/king/lands) so the season reads as demanding, not damning.

## R-4.15 — Dasa of Mercury

- **Cites:** Ch 4, v 15
- **Classification:** strength
- **Condition:** The current Dasa (or Antardasa) lord is Mercury. Benefic side applies when the period is Sampurna/Poorna/Arohini/Madhyama; the strain-side (harsh words, grief, imprisonment, pain, and diseases from vitiated vata-pitta-sleshma) when malefic.
- **Effect (one-way, dignity-closing):** Mercury's season gains wealth through acts of message, through friends, preceptors, and Brahmins; one is praised by the learned, becomes famous, and gets brass and the like, mixed metals, gold, horses, lands, popularity, comfort, and ease. One grows skilled in gentle ridicule and in service, increases in wisdom, and does deeds of virtue successfully. The same season can bring harsh words, grief, imprisonment, bodily pain, and disorders of wind, bile, and phlegm — tended by the wisdom, learning, and virtuous conduct it also opens.
- **Verse (source):** "In the Dasa period of Mercury, the person will acquire wealth by doing acts of message and through friends, preceptors and Brahmins. His praises will be sung by learned men. He will become famous and will get brass and the like, mixed metals, gold, horses, lands, popularity, comfort and ease. He will be skilled in the art of ridiculing others and serving under other men. He will get an increase of wisdom and successfully do deeds of virtue. He will suffer from harsh words, will suffer from grief, imprisonment, pain of mind and diseases arising from an aggravation of the three dhatus—vata (the air), pitta (bile), and sleshma (phlegm)."
- **Status:** draft
- **Notes:** No translator footnote. OCR-corrected "Ris praises .viII" → "His praises will"; "ao;.~tion" → "aggravation"; "main" → "mind".

## R-4.16 — Dasa of Jupiter

- **Cites:** Ch 4, v 16
- **Classification:** strength
- **Condition:** The current Dasa (or Antardasa) lord is Jupiter. Benefic side applies when the period is Sampurna/Poorna/Arohini/Madhyama; the minor strain-side (foot-journey, ear pain, quarrels with the wicked) when malefic.
- **Effect (one-way, dignity-closing):** Jupiter's season gains wealth through acts of worship, through learning, valour, ingenuity, bright personal appearance, military fame, generosity, mantras, diplomacy, the king, and the Vedas. One increases in gold, horses, sons, elephants, and clothes, and wins the friendship of good kings. One learns things needing great ingenuity. The season can also bring foot-journey, ear pain, and quarrels with wicked men — light tendencies, tended by the worship, learning, and generosity at the season's centre.
- **Verse (source):** "In the Dasa period of Jupiter, the person will acquire wealth by acts of worship, by his learning, valour, ingenuity, bright personal appearance, military fame, by acts of generosity, mantras, diplomacy, the king and the Vedas. He will have an increase of gold, horses, sons, elephants and clothes, and will acquire the friendship of good kings. He will learn things requiring much ingenuity, will suffer from foot journey and pain in the ear and will quarrel with wicked men."
- **Status:** draft
- **Notes:** No translator footnote. OCR-corrected "acq "lirc" → "acquire"; "50115" → "sons"; "clotbs" → "clothes".

## R-4.17 — Dasa of Venus

- **Cites:** Ch 4, v 17
- **Classification:** strength
- **Condition:** The current Dasa (or Antardasa) lord is Venus. Benefic side applies when the period is Sampurna/Poorna/Arohini/Madhyama; the strain-side (quarrels with crowds, king, hunters, wicked men; grief from one's own friends) when malefic.
- **Effect (one-way, dignity-closing):** Venus's season brings enjoyment of sweet music, varied pleasures, perfumes, sumptuous meals, alcohol, fine clothes, women, and precious stones. One grows fine in appearance, valorous, learned in the Sastras, obtains the object of desire, gains friends, becomes skilled in trade and agriculture, and finds hidden treasures and wealth. The season can also bring quarrels with crowds, the king, hunters, and wicked men, and grief from one's own friends — tended by the beauty, learning, and treasure the same season opens.
- **Verse (source):** "In the Dasa period of Venus, the person will enjoy sweet music, various pleasures, perfumes, sumptuous meals, alcohol, fine clothes, women, and precious stones. He will be of fine appearance, valorous, and will enjoy every substance provoking sexual passion, will become learned in the Sastras, will obtain the object of his desire, will acquire friends, will become skilled in trade and in agriculture and will get hidden treasures and wealth. He will quarrel with crowds of people, with the king, hunters and wicked men and he will suffer grief from his own friends."
- **Status:** draft
- **Notes:** Translator note (a) (printed under this stanza): "Yoga Sastra according to the Commentator." The strain-side is paired with the beauty, learning, and treasure strengths above.

## R-4.18 — Dasa of Saturn

- **Cites:** Ch 4, v 18
- **Classification:** tend
- **Condition:** The current Dasa (or Antardasa) lord is Saturn. Benefic side (asses, camels, birds, buffaloes, old women; rule over hamlets/villages/towns; renown) applies when the period is Sampurna/Poorna/Arohini/Madhyama; the heavy strain-side when malefic.
- **Effect (one-way, dignity-closing):** Saturn's season brings asses, camels, birds, buffaloes, and old women, and rule over hamlets, villages, or towns, with renown and grain of inferior quality. The season also tends toward phlegmatic and windy complaints, jealousy, anger, distraction of mind, dirty habits, idleness, grief, and heavy trouble; one's servants, sons, daughters, and wife may gain authority over one, and one's organs may become defective. These are tendencies to tend, offset by the steadiness, stewardship, and local renown the same season can bring — Saturn gives the slow grain that lasts.
- **Verse (source):** "In the Dasa period of Saturn, the person will get asses, camels, birds, buffaloes and old women, will rule over hamlets, villages or towns, and will thereby become renowned and will get grain of inferior quality. He will suffer difficulties from phlegmatic and windy complaints; from jealousy, anger, distraction of mind, and dirty habits. He will be idle, suffer from grief and be much troubled. His servants, sons, daughters and wife will exercise authority over him and his organs will become defective."
- **Status:** draft
- **Notes:** No translator footnote. The strain-side is the heaviest in the chapter; the runtime must pair it with Saturn's gift-side (stewardship, local rule, renown, the grain that lasts) so it reads as a demanding season, not a doom. OCR-corrected "ass.cs" → "asses"; "bir~s" → "birds"; "lUuch" → "much".

## R-4.19 — Benefic, malefic, or mixed period — and the Lagna-dasa

- **Cites:** Ch 4, v 19
- **Classification:** neutral
- **Condition:** Determine the character of a Dasa period from the technical name of its lord (R-4.5 to R-4.8): if the name indicates benefic (Sampurna, Poorna, Arohini, Madhyama, Uttama/Subha), the good effects come to pass; if malefic (Rikta, Ashta, Avarohini, Adhama, Asubha), the bad effects; if mixed (Misraphala, Madhyama-as-mixed, Sama), both come to pass. The effects for the Lagna-dasa are the same as the effects for the Dasa period of the lord of the rising sign. Refinement: planets occupying Upachaya houses at birth, with bright disks and distinct motion, give good effects in their Dasas; planets in Apachaya signs, defeated in conjunction, of disagreeable appearance or small disks, give bad effects. Planets that at the commencement of their Antardasa are aspected by benefics or occupy the Vargas of benefic or Atimitra planets are powerful and will not cause death; otherwise situated, they may cause death.
- **Effect (one-way, dignity-closing):** The season's character is read from its lord's name: a Sampurna/Poorna/Arohini/Uttama name lets the good side of the effect come to pass; a Rikta/Ashta/Avarohini/Adhama name lets the strain side; a Misraphala or Sama name lets both in turn. The Lagna-dasa takes its effects from the lord of the rising sign. Planets strong in Upachaya seats with bright disks give good seasons; planets weakened in Apachaya seats give harder seasons. A sub-season lord aspected by benefics or standing in a benefic's Varga is strong and does not bring closure; otherwise it may.
- **Verse (source):** "If the Dasa period be a benefic one, the good effects will come to pass; if it be a malefic one, the bad effects will come to pass. If it be of a mixed nature, both effects will come to pass. The effects for the Lagna Dasa are the same as the effects for the Dasa period of the lord of the rising sign."
- **Status:** draft
- **Notes:** Translator's footnote adds the Upachaya/Apachaya refinement and the death-causing clause. The "will cause death" phrasing is the source's; the runtime should render it as a dignity-closing caution about a sub-season's weight, not a fatalistic prediction. The "will not cause death" / "will cause death" test depends on aspects and Vargas at the Antardasa commencement — testable given the commencement figure.

## R-4.20 — Metals, occupations, and yoga-fruits within a Dasa

- **Cites:** Ch 4, v 20
- **Classification:** neutral
- **Condition:** In a benefic Dasa of a planet, the person acquires the metals assigned to that planet (Ch 2 st. 12); in a malefic Dasa, he loses them. In the Dasa of a planet, the person's occupation is that mentioned for the planet (Ch 4 st. 2–4). The effects described for the 12 houses from the ascendant (Ch 4), for the 12 signs from Aries (Ch 3), for planetary aspects (Ch 4), and for all Yogas except Nabhasa yogas (Ch 4, 13, 14, 15, 21) occur in the Dasa of the planet that is most powerful among the yoga planets.
- **Effect (one-way, dignity-closing):** In a bright season of a planet you gain its metal; in a lean season you lose some of it. Your work in that season follows the planet's occupation, and the house-, sign-, aspect-, and yoga-fruits tied to that planet ripen in its season — except the Nabhasa yogas, which run through the whole of life.
- **Verse (source):** "In the benefic Dasa periods of the planets, a person will acquire the several metals assigned to the planets (vide Chapter II, 12) and in the malefic Dasa periods of the planets, he will lose them. Again, in the Dasa period of a planet, a person's occupation will be that mentioned for the planet (a). The effects described for the 12 houses from the ascendant, (b) for the 12 signs from Aries, (c) for planetary aspects, (d) and for all Yogas, (e) excepting Nabhasa yogas, (f) will occur in the Dasa period of the planet which is most powerful among the yoga planets (g)."
- **Status:** draft
- **Notes:** Cross-chapter references: (a) Ch 4 st. 2–4; (b) Ch 4; (c) Ch 3; (d) Ch 4; (e) Ch 4, 13, 14, 15, 21; (f) Nabhasa effects run throughout life (Ch 22 st. 19); (g) cf. Ch 22 st. 5. Testable once the "most powerful among the yoga planets" selector and the referenced chapter rules are available.

## R-4.21 — Complexion and sense-quality of a Dasa by element

- **Cites:** Ch 4, v 21
- **Classification:** neutral
- **Condition:** In the Dasa of a planet, the person's complexion is that caused by the elementary principle the planet presides over: Mercury → earth (smell, nose); Venus and Moon → water (taste, tongue); Mars and Sun → fire (shape/appearance, eyes); Saturn → air (touch, body); Jupiter → akasa/ether (sound, ears) — per Ch 2 st. 6. The complexion is accompanied by the sense-quality of that element. Element-complexion mappings (from Brihat Samhita Ch 68 st. 90–93, quoted in the footnote): earth → shining teeth/skin/nails/hair, prosperous; water → glossy, white, clear, green, agreeable, brings happiness and wealth; fire → fearful, lotus/gold/fire-coloured, brings success and valour; air → dirty, not glossy, black, ill-scented, brings difficulty; akasa → crystal-coloured, noble, clear, gives all one desires.
- **Effect (one-way, dignity-closing):** Each season colours you by its lord's element. A Mercury season leans to an agreeable body-scent (earth, smell); a Venus or Moon season to juicy meals and taste (water); a Mars or Sun season to an agreeable, striking appearance (fire, shape); a Saturn season to a soft body and touch (air); a Jupiter season to sweet, ear-pleasing speech (ether, sound). The element's complexion accompanies these — prosperous for earth and water, valour-favouring for fire, noble for ether, and for air a season to be tended.
- **Verse (source):** "In the Dasa period of a particular planet, the person's complexion will be that due to the elementary principles presided over by the planet and the complexion will be accompanied by certain other qualities due to the elementary principles of earth, water, fire, air and akas and discernible by their respective organs of sense, viz., the nose, the tongue, the eyes, the body and the ears."
- **Status:** draft
- **Notes:** The planet→element assignment is from Ch 2 st. 6 (Mercury–earth; Venus & Moon–water; Mars & Sun–fire; Saturn–air; Jupiter–akasa). The element→complexion verses are quoted by Varahamihira from his Brihat Samhita Ch 68 st. 90–93 and are reproduced in the translator's footnote; they are included in the Condition above as the runtime lookup. The "air → death/imprisonment/disease/loss of wealth" complexion line is heavy in the source; render it as a season to be tended, paired with the soft-body/soft-touch quality. Testable from the Dasa lord and the element table.

## R-4.22 — The Divine Soul assumes the season's character

- **Cites:** Ch 4, v 22
- **Classification:** neutral
- **Condition:** In a benefic Dasa, the good effects are caused immediately by the Divine Soul living within the body, assuming for the time a benefic character; in a malefic Dasa it assumes a malefic character and produces evil; in a mixed Dasa, a corresponding character producing both. When a person is found to enjoy the good effects described for a planetary Dasa, that Dasa may be concluded to be running. Effects ascribed to powerless planets are experienced in dream or mental reverie.
- **Effect (one-way, dignity-closing):** The texture of a season is felt as the inner Soul taking on, for that while, the character of its lord — benefic in a bright season, exacting in a lean one, both in a mixed one. Where you notice the described good of a planet's season, that season is the one you are in. Effects tied to planets too weak to act at birth show up as dream or reverie rather than outward event.
- **Verse (source):** "In the benefic Dasa period of a planet, the good effects are caused immediately by the Divine Soul living within the body and assuming for the time being a benefic character (a). When a person is found to enjoy the good effects described for a planetary Dasa period, it may be concluded that such Dasa period is going on at the time. As regards the effects described for planets which might be powerless, these are experienced by a person either in his dream or in mental reveries (b)."
- **Status:** draft
- **Notes:** (a) the commentator extends: malefic period → malefic character producing evil; mixed → both. (b) "a wild train of thought in which a person enjoys or suffers according to his hopes or fears." This is the chapter's pacing frame — the season is worn by the inner Soul, not imposed by fate. Testable only as a rendering principle; the powerless-planet clause is testable via the planet's strength state.

## R-4.23 — Conflicting yoga-effects on the same planet

- **Cites:** Ch 4, v 23
- **Classification:** neutral
- **Condition:** If the effects of a planet are benefic under one yoga and malefic on the same point under another yoga, neither effect occurs. If two or more yogas give one character to a planet and a different yoga gives a different character, the former (majority / stronger) takes effect. But if conflicting effects are assigned to two distinct planets, both come to pass in their respective Dasa periods.
- **Effect (one-way, dignity-closing):** When two yogas pull the same planet in opposite directions on the same point, they cancel and neither dominates. When several yogas agree on a character and one differs, the agreeing set carries the season. And when two different planets carry opposing effects, both ripen — each in its own season, in its own turn.
- **Verse (source):** "If the effects of a planet be found to be benefic under one yoga and malefic in respect to the same point under another yoga (a) neither of the effects will occur; if two or more yogas give a character, one a different character to one and the same planet, the former will take effect. But if, to two distinct planets, conflicting effects have been assigned, both will come to pass in their respective Dasa periods."
- **Status:** draft
- **Notes:** (a) e.g. one yoga declaring a planet brings wealth, another declaring it destroys wealth — the two cancel. This is a resolution rule for the composition layer (§7 of README); testable via the yoga-match set per planet.

## R-4.24 — Udu / Nakshatra (Vimshottari) Dasa — lords, order, years

- **Cites:** Ch 4, translator's N.B. appendix (after v 23)
- **Classification:** table
- **Condition:** The maximum period of human life is divided into 9 parts presided over by the seven planets and Rahu and Ketu. The order and years are: (1) Sun 6; (2) Moon 10; (3) Mars 7; (4) Rahu 18; (5) Jupiter 16; (6) Saturn 19; (7) Mercury 17; (8) Ketu 7; (9) Venus 20 — totalling 120 years. The Dasa lord at birth is found from the asterism the Moon occupies at birth, the nine triangular asterism-sets giving the nine lords:
  - Sun — Krittika, U. Phalguni, U. Ashadha
  - Moon — Rohini, Hasta, Sravana
  - Mars — Mrigasirsha, Chitra, Sravishta
  - Rahu — Ardra, Swati, Satabhishak
  - Jupiter — Punarvasu, Visakha, P. Bhadrapada
  - Saturn — Pushya, Anuradha, U. Bhadrapada
  - Mercury — Aslesha, Jyeshta, Revati
  - Ketu — Aswini, Magha, Mula
  - Venus — Bharani, P. Phalguni, P. Ashada
  The elapsed and remaining years of the birth Dasa are reckoned from the portion of the birth asterism already traversed by the Moon vs. the portion remaining. Each Dasa is subdivided into 9 Antardasas whose lords follow the same order beginning with the Dasa lord; each Antardasa length is proportional to its lord's Dasa length relative to 120 years (Antardasa of P in Dasa of L = (L-years × P-years) / 120). Each Antardasa is further subdivided into 9 Sukshma periods in the same proportion.
- **Effect (one-way, dignity-closing):** This is the Nakshatra Dasa the author notes most Indian astrologers actually use. The Moon's birth-asterism fixes the opening lord and the count of years already elapsed and remaining; the nine seasons then run in the fixed order Sun → Moon → Mars → Rahu → Jupiter → Saturn → Mercury → Ketu → Venus, each with its allotted years, and each is divided into nine sub-seasons in the same order and proportion, and again into nine fine periods. The season you are in is thus fixed by the Moon's place at birth and the elapsed time.
- **Verse (source):** "N.B.—The division of life into Dasas as given by the Author is hardly studied by Indian Astrologers, evidently from the difficulties attending its application. These Astrologers, as a class, employ the exceedingly simple division of life into what is known as Udu or Nakshatra Dasas. According to this, the maximum period of human life is divided into 9 parts presided over by the seven planets and by Rahu and Ketu—the two nodes of the Moon. They come in the following order and their years are also given below: (1) The Sun, 6 years (5) Jupiter, 16 years (2) The Moon 10 (6) Saturn, 19 (3) Mars, 7 (7) Mercury, 17 (4) Rahu, 18 (8) Ketu, 7 (9) Venus, 20 years. The lord of the Dasa period, at the time of birth, is ascertained from the asterism which the Moon occupies at the time—the nine triangular asterisms represent the nine Dasas … How much of the period of a particular Dasa has elapsed and how much remains at the time of birth must be ascertained from the portion of the asterism passed over by the Moon and the portion remaining at the time … Again, the nine Dasa periods are each divided into 9 sub-divisions known as Antardasas—the lord of the first Antardasa being the lord of the Dasa period, and those of the Antardasas which follow are the same as the lords of the Dasa periods which follow … The lengths of the Antardasa periods bear the same proportion to each other as the lengths of the Dasa periods … Again, each of the Antardasa period is further sub-divided into 9 parts, in the same proportion, known as Sukshma periods."
- **Status:** draft
- **Notes:** This is the Vimshottari Dasa as presented in the translator's N.B. appendix (the source prints "16 years" for Jupiter, which matches the standard Vimshottari total of 120 and is retained verbatim). The nine triangular asterism-sets are reproduced exactly from the footnote. The worked arithmetic example in the footnote (Krittika, 64 gh 42 vigh whole; 24 gh 16 vigh elapsed; remainder ≈ 3 Savana years 8 months 29 days) is the model for the elapsed/remaining reckoning and is testable. Antardasa formula: Antardasa(P in L) = L-years × P-years / 120. This table is the primary Dasa system in practice and should be the runtime's default life-season skeleton, with R-4.5 to R-4.8 supplying the technical name and R-4.12 to R-4.18 supplying the effect text for each lord's season. Scholar review should confirm whether the runtime also implements the author's own Ch-8-years Dasa (R-4.1 to R-4.4) or relies on this Vimshottari table alone.