# Kingsastrology

### *A faithful, verse-cited, dignity-closing reading of the Brihat Jataka of Varahamihira — for every person, on every device.*

> *I am Varahamihira. I wrote the Brihat Jataka so a person might know their strength and their weakness, and so conduct themselves as a good and capable person. A horoscope is not a prison; it is a mirror held by a king to the face of his people. This product holds my text as the source of truth, and uses today's machines only to compute, recognize, translate, and counsel — never to invent.* — the Royal Vision Charter

---

## What this is

Kingsastrology turns the **Brihat Jataka** (28 chapters) into a digital product that delivers **strengths-and-weaknesses self-knowledge** to people — always verse-cited, always dignity-closing, never doom-leading. It ships across **Web, Android, iOS, and macOS**, all sharing one faithful Core engine and one agent court.

We are in the **planning stage**. This repository currently holds the full planning dossier. No product code is written yet — by intent.

## The four pillars (non-negotiable)

1. **Source fidelity** — every claim cites chapter & verse of the Brihat Jataka; "where is this written?" is always one tap away.
2. **Round-Earth accuracy** — true geocentric ephemeris on a spherical Earth; no flat approximations, no borrowed columns.
3. **Strength before doom** — strengths lead; weaknesses are paired with offsetting strengths; readings end on dignity.
4. **The person owns their chart** — birth data encrypted, deletable, never sold.

## Source of truth

- `sourcetext/pdfcoffee.com_brihat-jataka-of-varahamihira-pdf-free.pdf` — the Brihat Jataka translation. The throne. Everything derives from here.

## Planning dossier (`docs/`)

Read in order:

| # | Document | What it holds |
|----|----|----|
| 00 | [Vision Charter](docs/00-vision-charter.md) | The king's intent, voice, mission, four pillars, builders' oath |
| 01 | [Source-Text Foundation](docs/01-source-text-foundation.md) | All 28 chapters mapped to features + priority tiers |
| 02 | [Product Roadmap](docs/02-product-roadmap.md) | Phases 0–4 across all four platforms |
| 03 | [Project Scope](docs/03-project-scope.md) | In/out of scope, MVP, success criteria |
| 04 | [AI Capabilities](docs/04-ai-capabilities.md) | The AI features Varahamihira would build, grounded in chapters |
| 05 | [Architecture](docs/05-architecture.md) | One Core, four shells; API; data; guardrails |
| 06 | [Platform Plans](docs/06-platform-plans/) | [Web](docs/06-platform-plans/webapp.md) · [Android](docs/06-platform-plans/android.md) · [iOS](docs/06-platform-plans/ios.md) · [macOS](docs/06-platform-plans/macos.md) |
| 07 | [Organisation Structure](docs/07-organisation-structure.md) | The court: sovereign, privy council, ministries, agent staff |
| 08 | [Responsibilities](docs/08-responsibilities.md) | RACI by deliverable & duty; non-delegable human accountabilities |
| 09 | [Agent Roster](docs/09-agent-roster.md) | All AI ministers, their bounds, owners, runtime contract |
| 10 | [Data Models](docs/10-data-models.md) | Canonical shapes with the citation contract embedded |
| 11 | [Ethics & Risks](docs/11-ethics-and-risks.md) | Binding ethics, risk register, hard no-go list |
| 12 | [Milestones & Timeline](docs/12-milestones-timeline.md) | M0–M13, faithfulness-gated |

## Agent court

- [AGENTS.md](AGENTS.md) — the agent convention governing all ministers.
- [.claude/agents/](.claude/agents/) — individual agent definitions (rule-compiler, verification, verse-indexer, counselor-mirror, counselor-prasna, counselor-ayurdaya, counselor-rectify, tone-gate, citation, ethics, verse-translator, faithfulness-sweep, …).

## The flagship

**The Mirror** (`counselor-mirror`) — a five-section self-portrait:
1. *Who you are* → 2. *Your strengths* → 3. *What to tend* (paired with offsetting strength) → 4. *The season you are in* → 5. *A king's closing charge* (dignity).

Every claim footnoted to a verse; tone-gated; ethics-gated; citation-verified.

## Status

**Planning.** Charter, scope, roadmap, architecture, org, responsibilities, agent definitions, data models, ethics, and milestones are drafted. Next: convene the human court, ingest the verse store, and stand up the headless compute core (Phase 0).

## The builders' oath

> *I will hold the Brihat Jataka as the source of truth. I will compute the sky as upon a round Earth. I will deliver each person's strengths before their weaknesses, and their weaknesses only so they may grow. I will let no reading end in fear. I will guard the birth data of every soul as the king guards his people.*

---

*Sealed in the court of the present age, by the hand of Varahamihira.*