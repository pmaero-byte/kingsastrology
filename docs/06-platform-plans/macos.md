# 06d — Platform Plan: macOS

## Role in the kingdom
The **macOS app is the scholar's desk**. Where the mobile apps are the king's instruction to the people, the macOS app is where a serious reader — a student, a jyotishi, a researcher — can sit with the source, the chart, and the rules side by side and verify the work themselves.

## Stack
- **Swift + SwiftUI (native macOS)**; share as much as possible with the iOS codebase (shared SwiftUI views + shared Core Data cache layer).
- Keychain auth; on-device encrypted cache.
- API client to the Core; **scholar tooling** is the differentiator.

## Screens / layout
1. **Three-pane scholar view** (default): left = chart + divisional charts; center = reading; right = verse pane (the cited verse in full, with surrounding context). All linked: click a claim → the verse pane scrolls to it.
2. Birth-data entry & account.
3. Mirror, Prasna, Karmijiva, Ayurdaya life-stage, Strijataka.
4. Rectification workspace (Phase 3): event-anchor timeline, candidate times, confidence band.
5. **Rule Inspector** — browse the compiled yoga rule-base, see each rule's source verse, its verification status, and version history.
6. **Verse Explorer** — full 28-chapter browsing with search and keyword index.
7. Divisional charts deep view (D1/D9/D10/…) with cited readings (Phase 3).

## Distinctive responsibilities
- **Verifiability** — the scholar can inspect *how* any conclusion was reached: compute version, rule version, verse text. This is the platform where the "source of truth" promise is most fully expressed.
- **Rule Inspector** — transparency into the compiled rule-base (subject to human-review gating).
- **Reproducibility** — export a reading with full provenance (engine/rulebase/versestore versions) for study.

## Offline behavior
- Cached readings + cached verse text available offline.
- Scholar browsing of the verse store works offline (it's the source).

## Faithfulness & guardrails
- Same server-side guardrails; plus the scholar view *surfaces* them (verification status visible per rule).

## Launch criteria (Phase 2)
- Three-pane view with click-claim→-verse linking working.
- Verse Explorer + Rule Inspector usable.
- Parity with iOS/Web on the Mirror.

## Risks
- Scope creep into "astrology software for professionals" → stay grounded: this is still the king's instruction, made inspectable — not a professional forecasting toolset.