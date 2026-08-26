# 07 — Organisation Structure
### The Court of Kingsastrology

Varahamihira does not build alone, and neither do we. The work is organized as a royal court: a sovereign (product authority), a privy council (the charter's pillars), ministries (functions), and a bench of AI ministers (agents) that serve the human court. Humans hold final authority; agents serve, verify, and never override a human ruling on doctrine.

## 1. The court at a glance

```
                    ┌─────────────────────────────┐
                    │  The Sovereign (Product Owner)│
                    │  "Varahamihira's voice" —     │
                    │  final say on scope & doctrine│
                    └──────────────┬──────────────┘
                                   │
            ┌──────────────────────┼──────────────────────┐
            ▼                      ▼                      ▼
   ┌─────────────────┐  ┌──────────────────┐  ┌───────────────────┐
   │ Privy Council    │  │ Ministry of the  │  │ Ministry of the   │
   │ (Charter Pillars)│  │ Source (Jataka)  │  │ Engine (Compute)  │
   │ - Fidelity       │  │ - Verse Store    │  │ - Ephemeris       │
   │ - Round-Earth    │  │ - Rule-Base      │  │ - Dasa/Ashtaka.   │
   │ - Strength-first │  │ - Scholar Review │  │ - Bhava/Varga     │
   │ - User owns data │  └──────────────────┘  └───────────────────┘
   └─────────────────┘
                                   │
   ┌───────────────┬───────────────┼───────────────┬───────────────┐
   ▼               ▼               ▼               ▼               ▼
 Ministry of     Ministry of     Ministry of     Ministry of     Ministry of
 Counsel (AI)    Platforms       Tongue          Trust & Ethics   Stewardship
 - Mirror        - Web           - Translation   - Privacy        - QA/SLOs
 - Prasna        - Android       - Re-leveling   - Tone-Gate      - Observability
 - Vocation      - iOS           - Voice         - Ethics agent   - Faithfulness
 - Rectification - macOS         - Accessibility - Legal/health   - sweeps
 └───────────────┴───────────────┴───────────────┴───────────────┴───────────────┘
                  served by the AI Agent Court (see 09-agent-roster.md)
```

## 2. Roles & headcount (target, lean)

| Ministry | Human lead | Other humans | AI agents serving |
|----|----|----|----|
| Sovereign / Product | Product Owner (1) | — | — |
| Source (Jataka) | Source Steward (1) | Scholar Reviewer(s) (1–2, Indic+Sanskrit) | rule-compiler, verification |
| Engine (Compute) | Engine Lead (1) | Astronomical/ephemeris engineer (1) | (deterministic; agents for QA) |
| Counsel (AI) | AI Lead (1) | Prompt/agent engineer (1) | counselors (Mirror, Prasna, Karmijiva, etc.), citation, tone-gate, ethics |
| Platforms | Platform Lead (1) | Web (1), Android (1), iOS/macOS (1–2) | per-platform QA agents |
| Tongue | Localization Lead (1) | Translators per language (contract) | verse-translator, re-leveler |
| Trust & Ethics | Ethics Officer (1) | Privacy/legal (contract) | ethics agent, tone-gate, privacy audit |
| Stewardship | Reliability Lead (1) | QA/SRE (1) | faithfulness-sweep, observability |

A faithful small court outranks a large careless one. The team scales with verified demand, never ahead of faithfulness.

## 3. Governance cadence

- **Daily (agents):** every generated reading passes Tone-Gate + Citation + Ethics automatically.
- **Weekly:** ministry leads review faithfulness-sweep results, tone-gate rejection trends, ethics blocks.
- **Per-release:** Scholar Reviewer signs off that the rule-base additions for that release are verse-faithful before ship.
- **Quarterly:** full ethics + privacy audit; charter-pillar review; the Sovereign reaffirms or revises scope (charter prevails on conflict).

## 4. Authority & escalation

- **Doctrine disputes** → Source Steward + Scholar Reviewer; if unresolved → Sovereign; charter is the tiebreaker.
- **Tone/ethics failures in production** → withhold the reading, alert Ethics Officer, fix before re-serving.
- **Compute accuracy doubts** → Engine Lead reproduces against test charts (mine included); never papered over.
- **Agents never override a human ruling on doctrine.** An agent may *refuse* to render (tone-gate/ethics), but it may not *decide* new doctrine.

## 5. How agents fit into the human court

Agents are **staff**, not ministers-with-vote. The human ministry lead is accountable for the agent's domain. Every agent has a defined bounded scope (see `09-agent-roster.md` and `.claude/agents/*.md`) and a human owner who reviews its behavior and gates its outputs into production.

---

*Next: [08 — Responsibilities](./08-responsibilities.md)*