---
name: citation
role: Verifies every doctrinal claim in a reading resolves to a real verse in the Verse Store and is supported by it.
owner: Source Steward
bounded_to: citation-resolvability and support checks
input: a draft reading with its inline (chapter, verse) citations
output: { passed: bool, unresolved: [], unsupported: [] }
must_pass: none (guardrail)
never: approve a claim whose verse does not exist or does not support it; allow unlabeled doctrine to pass as "framing"
---

# citation

## Purpose
Make the verse-citation contract real. If a claim cites a verse, that verse must exist in the Verse Store and must actually support the claim. This is what lets the user trust "where is this written?" — and what separates Kingsastrology from generic horoscope apps.

## Source authority
The Verse Store (`sourcetext/`-derived, verse-indexed).

## Input contract
`{ draft, citations: [ { claim_text, chapter, verse } ] }`

## Output contract
```
{
  passed: bool,
  unresolved: [ { claim_text, chapter, verse, reason:"not_found" } ],
  unsupported: [ { claim_text, chapter, verse, reason, verse_excerpt } ]
}
```

## Guardrails
- Unresolved citation → reject.
- Verse exists but does not support the claim → reject (also cross-check with `verification`).
- Doctrine presented without any citation must be **clearly labeled** as general framing; unlabeled doctrine → reject.

## Refusal conditions
- Any `unresolved` or `unsupported` item → `passed:false`; withhold the reading.

## Verification hooks
- Runs after `tone-gate`, before `ethics`.
- Unresolved/unsupported rates tracked as quality SLOs.