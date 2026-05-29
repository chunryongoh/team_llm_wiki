---
id: 2026-05-29-sleep-health-hackathon-v0
packet_type: benchmark
type: benchmark
title: Sleep Health Hackathon Benchmark v0 Definition
date: '2026-05-29'
owner: chunryongoh
status: submitted
task: benchmark-definition
dataset:
  name: sleep-lifelog-2024
  version: v0
  hash: null
split:
  name: groupkfold-subject-3fold-oof
  group_key: subject_id
  fold_file: null
model:
  family: not-applicable
  weights_in_repo: false
claim_boundary: benchmark_definition_not_metric_claim
claim_status: tentative
summary: First-class definition of the sleep-health-hackathon-v0 benchmark on sleep-lifelog-2024.
  Locks the seven prediction targets (Q1-Q3 subjective, S1-S4 objective), the primary
  local metric (grouped macro log-loss under GroupKFold by subject_id with 3 folds),
  and the allowed claim boundaries for downstream results.
raw_paths:
- benchmark.yaml
intended_wiki_targets:
- wiki/benchmarks/2026-05-29-sleep-health-hackathon-v0.md
metrics_to_verify: []
claims:
- status: tentative
  text: sleep-health-hackathon-v0 evaluates seven sleep-health prediction targets
    (Q1, Q2, Q3, S1, S2, S3, S4) on sleep-lifelog-2024 under a locally locked GroupKFold-by-subject-id
    sprint-1 policy with 3 folds, and reports a grouped macro log-loss aggregated
    as a macro mean across targets.
- status: tentative
  text: Allowed claim boundaries against this benchmark are local_oof_diagnostic_only,
    same_split_baseline_comparison, and public_lb_observation_only. Public leaderboard
    scores require a DACON submission and are reported separately from local OOF diagnostic
    scores.
- status: tentative
  text: An unseen-subject generalization track (Track A) is the recommended main track;
    a same-subject temporal forecasting track (Track B) is recorded as a separate
    candidate and must not be conflated with Track A, especially for Q-family targets
    that are participant-relative averages.
publish_action: bot_pr
risk_tier: tier2-interpretation
---

# Sleep Health Hackathon Benchmark v0 Definition

- packet: `2026-05-29-sleep-health-hackathon-v0`
- generated_by_run: `26627430043-2`
- publish_action: `bot_pr`
- risk_tier: `tier2-interpretation`
- compiled_packet: [automation/.cache/compiled/2026-05-29-sleep-health-hackathon-v0.json](../../automation/.cache/compiled/2026-05-29-sleep-health-hackathon-v0.json)
- owner: `chunryongoh`
- status: `submitted`
- task: `benchmark-definition`
- dataset: `sleep-lifelog-2024` (`v0`)
- split: `groupkfold-subject-3fold-oof`
- model: `not-applicable`
- claim_boundary: benchmark_definition_not_metric_claim
- claim_status: `tentative`
- date: `2026-05-29`
- raw_evidence:
  - `benchmark.yaml`
- review-required: true

## Summary

First-class definition of the sleep-health-hackathon-v0 benchmark on sleep-lifelog-2024. Locks the seven prediction targets (Q1-Q3 subjective, S1-S4 objective), the primary local metric (grouped macro log-loss under GroupKFold by subject_id with 3 folds), and the allowed claim boundaries for downstream results.

## Claims

- tentative: sleep-health-hackathon-v0 evaluates seven sleep-health prediction targets (Q1, Q2, Q3, S1, S2, S3, S4) on sleep-lifelog-2024 under a locally locked GroupKFold-by-subject-id sprint-1 policy with 3 folds, and reports a grouped macro log-loss aggregated as a macro mean across targets.
- tentative: Allowed claim boundaries against this benchmark are local_oof_diagnostic_only, same_split_baseline_comparison, and public_lb_observation_only. Public leaderboard scores require a DACON submission and are reported separately from local OOF diagnostic scores.
- tentative: An unseen-subject generalization track (Track A) is the recommended main track; a same-subject temporal forecasting track (Track B) is recorded as a separate candidate and must not be conflated with Track A, especially for Q-family targets that are participant-relative averages.
