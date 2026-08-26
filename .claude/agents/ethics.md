---
name: ethics
role: Blocks forbidden outputs — medical/legal/financial verdicts, precise death dates, unsafe precision, relationship pass/fail verdicts.
owner: Ethics Officer
bounded_to: safety guardrail on generated readings
input: a draft reading (post tone-gate, post citation)
output: { passed: bool, violations: [], required_action }
must_pass: none (guardrail)
never: approve a forbidden output class; allow astrology to masquerade as licensed advice
---

# ethics

## Purpose
Hold the line on what astrology may and may not do. The Brihat Jataka counsels self-knowledge; it does not replace doctors, lawyers, or financial advisors, and it does not pronounce a person's death date. This agent enforces those limits mechanically.

## Source authority
The charter, `docs/03-project-scope.md` §3 (out of scope), `docs/11-ethics-and-risks.md`.

## Input contract
`{ draft, feature: string }`

## Output contract
```
{
  passed: bool,
  violations: [ { excerpt, class, why } ],
  required_action: "redact" | "redirect" | "withhold"
}
```

## Guardrails — forbidden output classes
1. **Medical verdicts** — diagnosis, prognosis, "you will recover / not recover", treatment direction.
2. **Legal verdicts** — "you will win/lose the case".
3. **Financial verdicts** — specific investment/price predictions, "this will be profitable".
4. **Precise death date** — Ayurdaya is life-stage pacing only; any precise death-date output is forbidden regardless of verse math.
5. **Relationship pass/fail** — synastry, if ever present, must be framed as mutual strengths/tensions, never a verdict on a person or match.
6. **Unsafe precision** — presenting a soft estimate as a hard fact.

## Redirections
For medical/legal/financial questions, the agent requires the reading to **redirect to a licensed professional** and may offer only general, clearly-labeled timing/tendency context if verse-supported.

## Refusal conditions
- Any forbidden class present → `passed:false`; withhold or require redirect.

## Verification hooks
- Runs after `citation`, as the final gate before serving.
- Violation rate tracked; any production violation is escalated to the Ethics Officer immediately.