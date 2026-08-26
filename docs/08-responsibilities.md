# 08 — Responsibilities (RACI)

R = Responsible (does the work) · A = Accountable (owns the outcome, one per row) · C = Consulted · I = Informed

## 1. By deliverable

| Deliverable | Product Owner | Source Steward | Scholar Reviewer | Engine Lead | AI Lead | Platform Lead | Localization Lead | Ethics Officer | Reliability Lead |
|----|----|----|----|----|----|----|----|----|----|
| Charter & scope decisions | A/R | C | C | C | C | C | I | C | I |
| Verse Store (digitize, index, cite) | I | A/R | R | C | C | I | C | I | I |
| Yoga rule compilation from verses | I | A | R | C | C | I | I | C | I |
| Rule verification vs verse | I | A | R | C | R | I | I | C | I |
| Compute engine (ephemeris, dasa, ashtakavarga, bhava, varga) | I | C | C | A/R | C | I | I | I | C |
| Counselor agents (Mirror, Prasna, etc.) | C | C | C | C | A/R | I | I | C | I |
| Tone-Gate / Citation / Ethics agents | I | C | C | C | R | I | I | A | C |
| Cross-platform parity | C | I | I | C | C | A/R | I | I | R |
| Web app | C | I | I | C | C | A/R | C | C | R |
| Android app | C | I | I | C | C | A/R | C | C | R |
| iOS app | C | I | I | C | C | A/R | C | C | R |
| macOS app | C | I | I | C | C | A/R | C | C | R |
| Translation (verse-to-tongue, re-leveling) | I | C | C | I | C | I | A/R | C | I |
| Privacy / birth-data vault / deletion | I | I | I | C | C | R | I | A | R |
| Faithfulness sweep & SLOs | I | C | C | C | C | I | I | C | A/R |
| Release sign-off (doctrine) | A | R | R | I | I | I | I | C | I |
| Release sign-off (safety/ethics) | A | I | I | I | I | I | I | R | C |

## 2. By recurring duty

| Duty | Owner | Cadence |
|----|----|----|
| Tone-Gate/Ethics/Citation enforcement on every render | AI Lead (system) | every request |
| Faithfulness sweep (re-verify served readings vs verse store) | Reliability Lead | nightly |
| Scholar review of new rules | Scholar Reviewer | per-release |
| Privacy/deletion audit | Ethics Officer | quarterly |
| Cross-platform parity check | Platform Lead | per-release |
| Charter-pillar review | Product Owner | quarterly |
| Compute accuracy regression (test charts) | Engine Lead | per engine change |

## 3. The non-delegable accountabilities (humans only)

These may **never** be delegated to an agent:

1. **Approving a new rule into the rule-base** — a human Scholar Reviewer must sign off, even though the Rule-Compiler agent drafts it.
2. **Authorizing scope/charter change** — the Product Owner.
3. **Deciding a doctrine dispute** — humans; charter prevails.
4. **Authorizing release** — Product Owner, with Scholar Reviewer (doctrine) and Ethics Officer (safety) sign-off.
5. **Handling a real user's complaint about a reading's accuracy** — a human reviews, the Verification agent assists, a human decides the remedy.

## 4. Agent ownership map

Every agent file in `.claude/agents/` has a `owner:` field naming the human ministry lead accountable for it (see `09-agent-roster.md`). An agent with no human owner is not allowed in production.

---

*Next: [09 — Agent Roster](./09-agent-roster.md)*