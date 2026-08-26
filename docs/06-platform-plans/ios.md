# 06c — Platform Plan: iOS

## Role in the kingdom
The **iOS app is polish and privacy**. Apple's platform lets us express the king's "the person owns their chart" pillar with strong on-device protections. The experience is calmer, more private, and accessibly refined.

## Stack
- **Swift + SwiftUI**; iOS 16+ target; universal design.
- **Keychain** auth (OIDC); on-device **Core Data** encrypted cache for reports.
- API client to the Core; no doctrine in-app.

## Screens
1. Gate / onboarding (privacy-first framing; Apple-style clarity).
2. Birth-data entry (place search → lat/long; "stored encrypted, yours, deletable").
3. Mirror reading (offline-readable once generated).
4. Prasna, Karmijiva (Phase 2).
5. Voice Court (Phase 2): iOS Speech framework; spoken cited answers.
6. Rectification interview (Phase 3).
7. Verse page + Verse Explorer (light).
8. Account: vault, delete, language, altitude.

## Distinctive responsibilities
- **Privacy polish** — make the user's ownership of their birth data visible and credible (what's stored, where, how to delete, that it's never sold).
- **Accessibility excellence** — VoiceOver, Dynamic Type, full voice path.
- **Calm tone** — typography and motion that support dignity, not spectacle.

## Offline behavior
- Cached cited reports readable offline.
- Generate/refresh requires connectivity; honest state.

## Faithfulness & guardrails
- Server-side Tone-Gate/Ethics; client shows `verification_passed`.
- Tap-to-verse native sheet; "where is this written?" one tap away.

## Launch criteria (Phase 2)
- Mirror parity with Web (citations + tone).
- VoiceOver pass on the Mirror.
- Privacy copy reviewed; deletion verified end-to-end (server + on-device cache).

## Risks
- App Store review of astrology/health-adjacent framing → keep copy firmly in "self-knowledge / reflection" territory; avoid any medical/health claims.