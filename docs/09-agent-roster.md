# 09 — Agent Roster (the AI Ministers)
### The court of agents that serve the human ministries.

Every agent below is bounded to a chapter domain or a guardrail function. **Agents never invent doctrine, never override the deterministic engine, and never ship a reading that fails Tone-Gate/Citation/Ethics.** Each has a human owner (per `08-responsibilities.md`) and a definition file in `.claude/agents/`.

## A. Source & Rule agents (offline, human-gated)

| Agent | File | Purpose | Bounded to | Human owner |
|----|----|----|----|----|
| **rule-compiler** | `.claude/agents/rule-compiler.md` | Read a verse → emit a structured, testable yoga rule (`IF … THEN yoga, citation`). Drafts only; never auto-enters rule-base. | one verse at a time | Source Steward |
| **verification** | `.claude/agents/verification.md` | Adversarially check a compiled rule / a rendered claim against the verse. Reject if unsupported. | verse vs claim | Scholar Reviewer |
| **verse-indexer** | `.claude/agents/verse-indexer.md` | Verse-store ingestion: clean OCR, index, attach chapter/verse/keywords. Flags uncertain text for human review. | `sourcetext/` → verse store | Source Steward |

## B. Compute-QA agents (deterministic engine, agents only assist)

| Agent | File | Purpose | Human owner |
|----|----|----|----|
| **compute-qa** | `.claude/agents/compute-qa.md` | Run the engine against test charts (incl. Varahamihira's recorded chart) and assert positions/dasas. Reports drift. | Engine Lead |

## C. Counselor agents (grounded LLM, leashed) — one per chapter cluster

| Agent | File | Domain | Authority chapters | Human owner |
|----|----|----|----|----|
| **counselor-mirror** | `.claude/agents/counselor-mirror.md` | The flagship self-portrait (strengths → what-to-tend → season → dignity close) | 2,3,9,17,18,19,21,12,13,24 | AI Lead |
| **counselor-prasna** | `.claude/agents/counselor-prasna.md` | Horary query answering | 27 | AI Lead |
| **counselor-karmijiva** | `.claude/agents/counselor-karmijiva.md` | Vocation / career | 11 | AI Lead |
| **counselor-ayurdaya** | `.claude/agents/counselor-ayurdaya.md` | Life-stage pacing (no death date) | 8 | AI Lead + Ethics Officer |
| **counselor-strijataka** | `.claude/agents/counselor-strijataka.md` | Women's reading (contemporary dignity) | 25 | AI Lead + Ethics Officer |
| **counselor-nisheka** | `.claude/agents/counselor-nisheka.md` | Fertility/conception timing (not medical) | 5 | AI Lead + Ethics Officer |
| **counselor-rectify** | `.claude/agents/counselor-rectify.md` | Birth-time rectification with confidence band | 26 | AI Lead |
| **counselor-balarishta** | `.claude/agents/counselor-balarishta.md` | Early-life "tend carefully" notice (no death forecast) | 7 | AI Lead + Ethics Officer |

## D. Guardrail agents (run on every render)

| Agent | File | Purpose | Human owner |
|----|----|----|----|
| **tone-gate** | `.claude/agents/tone-gate.md` | Reject doom-leading / fatalistic drafts; enforce Pillar 3 (strength before doom) and the kindness rule. | Ethics Officer |
| **citation** | `.claude/agents/citation.md` | Verify every claim's `(Ch, verse)` resolves in the Verse Store and supports the claim. | Source Steward |
| **ethics** | `.claude/agents/ethics.md` | Block medical/legal/financial verdicts, precise death dates, unsafe precision. | Ethics Officer |
| **sensitivity** | `.claude/agents/sensitivity.md` | Check framing for women's readings and other sensitive outputs for contemporary dignity. | Ethics Officer |

## E. Translation & accessibility agents

| Agent | File | Purpose | Human owner |
|----|----|----|----|
| **verse-translator** | `.claude/agents/verse-translator.md` | Translate verse + counsel to user language; **verse preserved verbatim**. | Localization Lead |
| **re-leveler** | `.claude/agents/re-leveler.md` | Child mode / scholar mode re-leveling; verse preserved. | AI Lead |

## F. Stewardship agents

| Agent | File | Purpose | Human owner |
|----|----|----|----|
| **faithfulness-sweep** | `.claude/agents/faithfulness-sweep.md` | Nightly: re-verify a sample of served readings vs current verse store; flag drift. | Reliability Lead |
| **parity-check** | `.claude/agents/parity-check.md` | Per-release: assert citation/tone consistency across Web/Android/iOS/macOS. | Platform Lead |

## Runtime contract (all counselor agents)

1. Input = computed `ChartFactBundle` (or horary facts) + the **exact verses** the facts cite. No external doctrine.
2. Output = prose with inline `(Ch, verse)` on every claim; or clearly-labeled general framing.
3. Must pass `tone-gate`, `citation`, `ethics` before serving.
4. Must include `provenance` (engine/rulebase/versestore versions, verification_passed).
5. May **refuse** to render (e.g., ethics); may **not** invent doctrine or alter computed facts.

## Agent authoring standard

Each `.claude/agents/*.md` file uses this header (see AGENTS.md for the full convention):

```markdown
---
name: <agent-name>
role: <one line>
owner: <human ministry lead>
bounded_to: <chapters or function>
input: <what it receives>
output: <what it returns>
must_pass: <tone-gate / citation / ethics — as applicable>
never: <explicit prohibitions>
---

# <Agent Name>

## Purpose
## Source authority
## Input contract
## Output contract
## Guardrails
## Refusal conditions
## Verification hooks
```

Agents without an `owner:` are not permitted in production.

---

*Next: [10 — Data Models](./10-data-models.md)*
*Agent definitions: [`AGENTS.md`](../AGENTS.md) and `.claude/agents/`*