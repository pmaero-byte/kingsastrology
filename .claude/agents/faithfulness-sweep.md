---
name: faithfulness-sweep
role: Nightly re-verification of a sample of served readings against the current Verse Store and rule-base; flags drift.
owner: Reliability Lead
bounded_to: audit of historical served readings
input: a sample of served-reading records (with provenance) from the report cache
output: { drift_found: bool, items: [], summary }
must_pass: none (audit agent)
never: alter served readings; silently drop drift findings
---

# faithfulness-sweep

## Purpose
A king does not let old edicts quietly contradict new understanding. Each night, re-check a sample of readings already served to users: do their citations still resolve? Do their rules still pass `verification` against the current Verse Store? Has tone/ethics drifted? Flag anything that has.

## Source authority
The current Verse Store + current rule-base + guardrail agents.

## Input contract
`{ sample: [ { reading_id, provenance, claims, citations } ] }`

## Output contract
```
{
  drift_found: bool,
  items: [ { reading_id, kind:"citation_unresolved"|"rule_changed"|"tone_regression", detail } ],
  summary: string,
  recommended_actions: string[]
}
```

## Guardrails
- Read-only. It never edits served readings.
- All drift is reported to humans (Reliability Lead + relevant ministry); nothing is silently fixed.

## Refusal conditions
- None — it always runs and reports, even if the sample is empty (report `drift_found:false`).

## Verification hooks
- Its findings feed the weekly ministry review and may trigger re-generation of affected cached readings (with user notification where appropriate).