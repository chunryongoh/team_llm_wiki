---
id: 2026-06-25-sleep-lifelog-packet-synthesis
type: synthesis-report
page_role: report
title: Sleep Lifelog Packet Synthesis 2026-06-25
status: active
date: 2026-06-25
claim_status: supported
raw_evidence:
- raw/results/llm-synthesis/28153765973-2/report.json
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/manifest.yaml
---

# Sleep Lifelog Packet Synthesis 2026-06-25

This report integrates the wave43 Claude campaign packet. GitHub Actions primary OpenAI synthesis hit HTTP 429 and fell back to GitHub Models; this branch was then manually refined in Codex to replace deterministic scaffolds with stable wiki entities.

## Main Result

Wave43 `stack-v2` is the current best local OOF evidence: calibrated macro log-loss `0.5897217743642561` under same-subject-hole five-fold validation. The supported claim is local OOF only.

## Entity Updates

- [Wave43 Claude Campaign Stack](../performance/wave43-claude-campaign-stack.md) records the current best local result and claim boundaries.
- [Wave43 Feature Families](../features/wave43-feature-families.md) separates target-specific feature hypotheses.
- [Wave43 Stacked Ensemble](../models/wave43-stacked-ensemble.md) documents the targetwise candidate stack.
- [Same Subject Hole CV](../preprocessing/same-subject-hole-cv.md) records the validation surface and its non-official status.
- [S1 Total Sleep Time](../targets/s1-total-sleep-time.md) and [S3 Sleep Onset Latency](../targets/s3-sleep-onset-latency.md) capture target insights.
- [Wave43 Open Validation Gaps](../targets/wave43-open-validation-gaps.md) tracks promotion blockers.

## Boundary Decisions

- `0.58972` local OOF is supported.
- `0.59272` projected public is tentative.
- `0.60761` public observation is tentative until leaderboard export or submission hash is attached.
- Q-family impossibility is superseded; Q3 remains hard.
- S4 remains an unresolved target despite WASO/transfer attempts.
