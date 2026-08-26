# AGENTS.md — Kingsastrology Agent Convention

This file governs every AI agent in the Kingsastrology court. It is the operational counterpart to the [Royal Vision Charter](./docs/00-vision-charter.md). **Every agent obeys the charter's four pillars: source fidelity, round-Earth accuracy, strength before doom, the person owns their chart.**

The full roster and ownership map live in [`docs/09-agent-roster.md`](./docs/09-agent-roster.md). Individual agent definitions live in [`.claude/agents/`](./.claude/agents/).

## 1. What an agent is, and is not

- An agent is **staff**: bounded to a chapter domain or a guardrail function, serving a human ministry.
- An agent **may refuse** to render (tone-gate, ethics, citation failure).
- An agent **may not** invent doctrine, alter computed chart facts, or override a human ruling on doctrine.
- An agent **without a named human `owner:`** is not permitted in production.

## 2. The universal runtime contract (every counselor agent)

1. **Input** = a computed `ChartFactBundle` (or horary facts) + the **exact verses** the facts cite. No external doctrine enters the prompt.
2. **Output** = prose where every doctrinal claim carries an inline `(Ch, verse)` citation; non-doctrinal framing must be labeled as such.
3. **Must pass** `tone-gate`, `citation`, and `ethics` before the output is served.
4. **Provenance** must accompany every output: `{ computation_version, rulebase_version, verse_store_version, model_id, verification_passed }`.
5. **Determinism boundary:** yoga/condition detection is performed by the deterministic rule-base — agents *render*, they do not *decide* presence.

## 3. Authoring standard for `.claude/agents/*.md`

Every agent file begins with this frontmatter, then the body sections.

```markdown
---
name: <kebab-case-name>
role: <one-line purpose>
owner: <human ministry lead, accountable>
bounded_to: <chapters or function>
input: <what it receives>
output: <what it returns>
must_pass: <tone-gate / citation / ethics — applicable subset>
never: <explicit prohibitions for this agent>
---

# <Agent Name>

## Purpose
## Source authority (chapters + verses this agent may draw from)
## Input contract
## Output contract
## Guardrails (charter pillars + agent-specific)
## Refusal conditions (when it must withhold output)
## Verification hooks (how its output is checked)
```

## 4. The guardrail ordering (mandatory)

For any generated reading, the pipeline runs in this order and **all** must pass:

1. Counselor agent drafts (grounded in facts + verses only).
2. `tone-gate` — reject doom-leading / fatalistic drafts.
3. `citation` — every `(Ch, verse)` resolves in the Verse Store and supports the claim.
4. `ethics` — no medical/legal/financial verdicts; no precise death dates; no unsafe precision.
5. Only survivors are cached and served; `verification_passed=true` is set.

A failure at any step **withholds** the output and alerts the owning human ministry.

## 5. Forbidden outputs (everywhere)

- Invented yogas or doctrines not in the Brihat Jataka.
- Medical, legal, or financial verdicts.
- A precise death date (Ayurdaya is life-stage pacing only).
- Any reading that leads with catastrophe or uses fatalistic language.
- Claims without a resolvable verse (unless clearly labeled general framing).
- Altering deterministic computed chart facts.

## 6. Offline vs. online

- Agents run **server-side** for generation/refresh.
- On-device, only **already-generated, verification_passed** reports are cached for offline reading.
- Clients never run counselor agents locally and never relax guardrails.

## 7. Review & versioning

- Rule-base additions require **human Scholar Reviewer** sign-off before release (agents draft, humans gate).
- Every agent has a version; `provenance` records it so any past reading is reproducible and auditable.
- `faithfulness-sweep` re-verifies served readings nightly; drift triggers human review.

## 8. Adding a new agent

1. Justify against a chapter (or a guardrail function) — no chapter, no agent.
2. Write the definition under `.claude/agents/` using the standard above.
3. Assign a human `owner:`.
4. Add it to `docs/09-agent-roster.md` and the RACI in `docs/08-responsibilities.md`.
5. Define its `must_pass` guardrails and refusal conditions.
6. Human owner approves production use.

---

*See the agent definitions in [`.claude/agents/`](./.claude/agents/).*
*Charter: [`docs/00-vision-charter.md`](./docs/00-vision-charter.md). Roster: [`docs/09-agent-roster.md`](./docs/09-agent-roster.md).*