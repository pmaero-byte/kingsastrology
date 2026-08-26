# 06a — Platform Plan: Web App (PWA)

## Role in the kingdom
The **Web app is the proving ground and the public gate**. The Mirror launches here first (Phase 1) because iteration is fastest and faithfulness can be verified quickly. It also hosts the public **Verse Explorer** — so anyone, even without a chart, can read the source.

## Stack
- **Next.js (React) + PWA** (service worker for offline cached reports).
- TypeScript; Tailwind or equivalent; accessibility-first (WCAG AA).
- API client to the shared Core (see `05-architecture.md`); no doctrine in the client.

## Screens / routes
1. `/` — the gate: a single clear purpose ("Know yourself, by the source"), privacy promise up front.
2. `/chart/new` — birth-data entry with privacy UX (why we ask, how it's stored, deletable).
3. `/reading/mirror` — the flagship self-portrait (B1); sectioned; tap-to-verse.
4. `/reading/prasna` — Ask the King (Phase 2).
5. `/reading/karmajiva` — vocation (Phase 2).
6. `/rectify` — birth-time rectification interview (Phase 3).
7. `/verse/{ch}/{v}` — verse page (Sanskrit ref + translation + which features cite it).
8. `/explore` — public Verse Explorer & yoga catalog (scholar mode); no login required to read the source.
9. `/account` — birth-data vault management, language, altitude (child/scholar), delete.

## Distinctive responsibilities
- **Fastest iteration** — new verse-cited features land here first, prove faithfulness, then go native.
- **Verse Explorer** — the source reaches the public; the only place where reading the Jataka needs no birth data.
- **Scholar mode** — side-by-side verse + chart + rule inspector (richer on macOS, present here too).
- **Web Speech** for voice counsel (C3) where the browser supports it.

## Offline behavior
- Service worker caches already-generated cited reports for re-reading without connectivity.
- New readings require connectivity (compute + grounded generation happen server-side).

## Faithfulness & guardrails
- Every rendered claim is a link to `/verse/{ch}/{v}`.
- `provenance` block visible in a collapsible "How this was made" panel (engine/rulebase/versestore versions, verification_passed).
- Tone-Gate/Ethics enforced server-side; client never relaxes them.

## Launch criteria (Phase 1)
- MVP success criteria from `03-project-scope.md` met on Web.
- Verse Explorer live and searchable.
- Tap-to-verse works from every claim in the Mirror.

## Risks
- Browser TTS/STT variance → graceful fallback to text.
- SEO of verse pages must be careful: we expose the source, not individuals' charts.