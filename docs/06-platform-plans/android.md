# 06b — Platform Plan: Android

## Role in the kingdom
The **Android app is reach**. India and much of the round Earth runs on Android across wildly varying devices and connectivity. This app must be **offline-first for reading** and forgiving on low-end hardware. The king instructs *all* his people, not only those with flagship phones.

## Stack
- **Kotlin + Jetpack Compose**; Min SDK chosen for broad Indian device coverage; lean APK/AAB.
- On-device **Room** encrypted cache for generated reports; API client to the Core.
- Keystore-backed auth (OIDC); encrypted birth-data handling.

## Screens
1. Gate / onboarding (privacy promise, language choice, altitude choice).
2. Birth-data entry (with place search; lat/long captured for round-Earth compute).
3. Mirror reading (offline-readable once generated).
4. Prasna, Karmajiva (Phase 2).
5. Voice Court (Phase 2): ASR question → spoken cited answer; large-button elder mode.
6. Rectification interview (Phase 3).
7. Verse page + light Verse Explorer.
8. Account: birth-data vault, delete, language, altitude.

## Distinctive responsibilities
- **Offline-first read** — cached cited reports open without connectivity; clear "needs connection to refresh/generate" state.
- **Low-bandwidth** — compress responses; cache verse text; avoid large assets.
- **Voice + elder accessibility** — large-text mode, voice-in/voice-out, minimal jargon default.
- **Localization** — strong Indic-language support (Devanagari, Tamil, etc. per translation capacity).

## Offline behavior
- Read cached reports fully offline.
- Generate/refresh requires connectivity; show honest state.
- Verse text cached per the readings that cite them.

## Faithfulness & guardrails
- Same citation contract, Tone-Gate, Ethics — all server-side; client reflects `verification_passed`.
- No doctrine in the app; if it shows a claim, it came from the API.

## Launch criteria (Phase 2)
- Mirror consistent with Web (same citations, same tone).
- Offline read verified on a low-end device with airplane mode.
- Voice path works end-to-end on at least one common device.

## Risks
- Device/OS fragmentation → test matrix prioritized to the devices the target users actually own.
- TTS quality per language → pick best-available engine, allow text fallback.