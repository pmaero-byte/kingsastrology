# 05 — Cross-Platform Architecture

## 1. Principle: one throne, four faces

The doctrinal and computational core is built **once** and shared by all four platforms. Only the shells differ. This guarantees the verse-citation contract and the tone are identical everywhere — a person reading on a phone in a village sees the same faithful text as a scholar on a Mac.

```
┌──────────────────────────────────────────────────────────────┐
│  PLATFORM SHELLS  (UI only — no doctrine lives here)          │
│  Web (PWA) │ Android (Kotlin) │ iOS (Swift) │ macOS (Swift)   │
└───────────────┬──────────────────────────────────────────────┘
                │  REST/JSON + GraphQL over HTTPS; offline cache
┌───────────────▼──────────────────────────────────────────────┐
│  API GATEWAY  (auth, rate-limit, request provenance)          │
└───────────────┬──────────────────────────────────────────────┘
                │
┌───────────────▼──────────────────────────────────────────────┐
│  KINGSASTROLOGY CORE  (the throne — built once)               │
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐  │
│  │ Compute     │  │ Yoga Rule-   │  │ Verse Store         │  │
│  │ Engine (A1- │  │ Base + Rule  │  │ (28 ch, indexed,    │  │
│  │ A6, Swiss   │  │ Compiler     │  │  cited)             │  │
│  │ Ephemeris)  │  │ (verified)   │  │                     │  │
│  └─────────────┘  └──────────────┘  └─────────────────────┘  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  COUNSELING PIPELINE  (grounded LLM, leashed)         │    │
│  │  facts+verses → Counselor agent → Tone-Gate →         │    │
│  │  Citation check → Ethics check → rendered report       │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  AGENT COURT  (see 09-agent-roster.md, .claude/agents)│    │
│  └──────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────┘
                │
┌───────────────▼──────────────────────────────────────────────┐
│  DATA  (user-owned, encrypted)                                 │
│  Birth-data vault │ Report cache │ Event-anchors (rectif.)     │
└───────────────────────────────────────────────────────────────┘
```

## 2. The Core (shared, platform-agnostic)

### 2.1 Compute Engine
- Language: a portable core (Rust or Go recommended for determinism + cross-platform FFI; Python acceptable for the server build with a compiled ephemeris binding).
- Ephemeris: **Swiss Ephemeris** for geocentric positions; ayanamsa selectable (Lahiri default, configurable).
- Outputs a canonical `ChartFactBundle` (JSON) where **every field carries its governing `(chapter, verse)` citation**.

### 2.2 Yoga Rule-Base
- Stored as machine-readable rules compiled **offline** by the Rule-Compiler agent from verses, then **human-reviewed** and versioned.
- Runtime detection is **deterministic** — the LLM never decides whether a yoga is present.
- Each rule: `{ id, chapter, verse, condition, yoga_name, classification(strength|tend), citation }`.

### 2.3 Verse Store
- Source: the translation in `sourcetext/`, verse-indexed.
- Schema: `{ chapter, verse, sanskrit_ref, translation_text, keywords[] }`.
- The citation-check agent verifies every rendered citation resolves to a real verse whose text supports the claim.

### 2.4 Counseling Pipeline (the leashed LLM)
Strict order, every render:
1. Gather computed facts + the exact verses the facts cite.
2. Counselor agent drafts prose from **only** the provided facts + verses (retrieval-grounded; no external doctrine).
3. **Tone-Gate agent** rejects doom-leading/fatalistic drafts.
4. **Citation agent** verifies every claim's `(Ch, verse)` resolves in the Verse Store.
5. **Ethics agent** blocks forbidden outputs (medical/legal/financial verdicts, precise death dates).
6. Only surviving drafts are cached and served.

### 2.5 Agent Court
See `09-agent-roster.md` and `.claude/agents/*.md`. Agents are bounded to chapter domains and never override the deterministic engine.

## 3. API surface (shared by all four shells)

| Endpoint | Purpose |
|----|----|
| `POST /chart/compute` | Birth data → `ChartFactBundle` (compute only; no prose) |
| `POST /reading/mirror` | Facts → Mirror self-portrait (cited, tone-gated) |
| `POST /reading/prasna` | Question + time → horary answer (cited) |
| `POST /reading/karmajiva` | Facts → vocation reading |
| `POST /rectify/start`, `/rectify/anchor` | Birth-time rectification interview |
| `GET /verse/{ch}/{v}` | Fetch verse text (powers tap-to-verse) |
| `GET /yogas?chapter=` | Yoga catalog (scholar / verse explorer) |
| `POST /account/birthdata` | Encrypted birth-data vault (user-owned) |
| `DELETE /account/birthdata` | Honored deletion |

- All responses include a `provenance` block: `{ computation_version, rulebase_version, verse_store_version, model_id, verification_passed: bool }`.
- **Offline rule:** a report, once generated, is cached on-device and readable without connectivity (critical for Android reach). Recomputation/regeneration requires connectivity.

## 4. Platform shells (distinctive responsibilities only)

| Concern | Web (PWA) | Android | iOS | macOS |
|----|----|----|----|----|
| UI framework | React/Next + PWA | Kotlin + Jetpack Compose | Swift + SwiftUI | Swift + SwiftUI (native) |
| Engine access | API over HTTPS | API + on-device cache | API + on-device cache | API + on-device cache (richer scholar view) |
| Voice | Web Speech API | Android Speech | iOS Speech | macOS Speech |
| Offline | service-worker cached reports | Room cache | Core Data cache | Core Data cache |
| Distinctive | Public verse explorer; fastest iteration | Reach; offline-first | Privacy polish | Scholar desk: side-by-side verse/chart/rules |
| Auth | OIDC | OIDC + Keystore | OIDC + Keychain | OIDC + Keychain |

Shells contain **no doctrine logic**. If a platform "knows" something, it learned it from the Core API. This is what keeps parity enforceable.

## 5. Data & privacy architecture

- **Birth data vault:** encrypted at rest (envelope encryption); keys per-user; never used for training; never sold; deletable on demand and propagated to all caches.
- **Report cache:** stores generated cited reports for offline read; cleared on birth-data deletion.
- **No analytics on chart contents.** Product analytics may record *usage* (features touched, taps-to-verse) but never the substance of a person's chart.
- **Provenance logging:** every served reading records the engine/rulebase/versestore versions so any past reading is reproducible and auditable.

## 6. Observability & verification (built in)

- Every reading's `verification_passed` must be `true` before serving; false → withheld + alert.
- Tone-Gate rejection rate and Ethics-block rate tracked as **quality SLOs**, not just bugs.
- A nightly **faithfulness sweep**: re-verify a sample of served readings against the current verse store; flag drift.

## 7. Technology choices (recommended, subject to team confirmation)

- Core compute: Rust (or Go) + Swiss Ephemeris FFI; JSON-over-HTTP/GraphQL.
- Counseling LLM: a frontier reasoning model accessed via API; **deterministic rule application at runtime**.
- Agent runtime: Claude-style agents per `.claude/agents/*.md`, with structured outputs and verification tools.
- Web: Next.js (React) PWA.
- Android: Kotlin + Jetpack Compose, Min SDK targeting broad Indian device base.
- iOS/macOS: Swift + SwiftUI, universal macOS where sensible.
- Storage: Postgres for accounts/report metadata; encrypted object store for birth-data vault; on-device encrypted caches.

---

*Next: [06 — Platform Plans](./06-platform-plans/)*
*See also: [09 — Agent Roster](./09-agent-roster.md), [10 — Data Models](./10-data-models.md)*