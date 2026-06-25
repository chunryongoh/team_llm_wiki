---
id: wave43-open-validation-gaps
type: open-issues
page_role: registry
title: Wave43 Open Validation Gaps
status: active
date: 2026-06-25
claim_status: tentative
raw_evidence:
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/question_queue.yaml
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/semantic_lint.json
---

# Wave43 Open Validation Gaps

These questions block promotion from strong local OOF evidence to leaderboard or final team policy.

| question | priority | close condition |
|---|---|---|
| Attach official leaderboard export or submission hash for public `0.60761` and final stack submission | high | raw evidence links candidate, submission file, timestamp, and DACON row |
| Decide whether OOF prediction arrays should be copied into packets | medium | reproducibility policy balances packet size and privacy/security |
| Supersede same-subject-hole if organizer split semantics are released | high | official split note is linked from split policy and claim registry |
| Select next S4 strategy | medium | same-split S4 ablation beats final stack or is logged as negative |

## Immediate Next Actions

1. Add leaderboard evidence for the best actual submission.
2. Attach fold assignment or row membership artifacts for same-subject-hole.
3. Run target-level ablations for S4 fragmentation/WASO proxies.
4. Keep projected public score out of supported claims.

## Related Pages

- [Wave43 Claude Campaign Stack](../performance/wave43-claude-campaign-stack.md)
- [DACON Leaderboard History](../performance/dacon-leaderboard-history.md)
- [Current Supported Claims](../claims/current-supported-claims.md)
