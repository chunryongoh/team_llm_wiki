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
- generated_by_run: `26628582638-1`
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

## Benchmark Entity

- name: `sleep-health-hackathon-v0`
- dataset_ref: `sleep-lifelog-2024`
- task_family: `sleep-health-prediction`

### Targets

| id | kind | description |
| --- | --- | --- |
| Q1 | subjective-binary | Perceived sleep quality, participant-relative. |
| Q2 | subjective-binary | Bedtime physical fatigue, participant-relative. |
| Q3 | subjective-binary | Bedtime stress level, participant-relative. |
| S1 | objective-binary | Total sleep time guideline compliance. |
| S2 | objective-binary | Sleep efficiency compliance. |
| S3 | objective-binary | Sleep onset latency compliance. |
| S4 | objective-binary | Wakefulness after sleep onset compliance. |

### Primary Metric

- name: `grouped_macro_logloss`
- definition: `Mean across the seven targets of subject-grouped log-loss computed on out-of-fold validation predictions.`
- averaging_policy: `macro-mean over targets`
- loss_basis: `log-loss per target`
- aggregation_basis: `subject-grouped fold-level predictions concatenated into an OOF dataset before per-target log-loss`

### Evaluation Policy

- split: `groupkfold-subject`
- group_key: `subject_id`
- n_folds: `3`
- aggregation: `macro-mean over targets`
- tracks:
  - `{'id': 'A', 'name': 'unseen-subject-generalization', 'recommended': True, 'description': 'Main track. Protects against person-identity leakage for the Q-family participant-relative labels.'}`
  - `{'id': 'B', 'name': 'same-subject-temporal-forecasting', 'recommended': False, 'description': 'Candidate alternative track. Must not be conflated with Track A; Q-family targets are especially dangerous to evaluate under Track B alone.'}`

### Claim Boundaries

- `local_oof_diagnostic_only`
- `same_split_baseline_comparison`
- `public_lb_observation_only`

### Public Leaderboard

- policy: `public-and-private-leaderboard-on-DACON`
- public_share_of_test: `0.44`
- notes: `Public leaderboard movement is noisy directional feedback, not the final truth signal. Public and private aggregations are average log-loss.`

### Working Implications

- `Improvements must be interpreted separately for subjective Q-family and objective S-family targets.`
- `Strong-local performance is not a public claim unless a DACON submission is recorded and compared at the same split policy.`
- `Same-split baseline comparisons stay valid only when the baseline and the candidate share the canonical GroupKFold-by-subject 3-fold policy.`

## Packet Synthesis

This packet locks the benchmark entity that downstream experiment, performance, and decision packets reference when reporting sleep-health prediction results. It defines the seven targets, the primary metric and its definition, the canonical evaluation split, the alternative track, and the allowed claim boundaries.

## Dataset Anchor

This benchmark evaluates models on the [[preprocessing/sleep-lifelog-2024]] dataset under its locally locked GroupKFold-by-subject sprint-1 split policy.

## Targets

The benchmark scores seven binary targets on `ch2026_metrics_train.csv`:

| id | family | description |
| --- | --- | --- |
| Q1 | subjective | perceived sleep quality (participant-relative) |
| Q2 | subjective | bedtime physical fatigue (participant-relative) |
| Q3 | subjective | bedtime stress level (participant-relative) |
| S1 | objective | total sleep time guideline compliance |
| S2 | objective | sleep efficiency compliance |
| S3 | objective | sleep onset latency compliance |
| S4 | objective | wakefulness after sleep onset compliance |

`S4` is included in the released package; older dataset paper summaries with only six targets are superseded by the released metric description.

## Primary Metric

`grouped_macro_logloss`: mean across the seven targets of subject-grouped log-loss computed on out-of-fold validation predictions. Aggregation order is `OOF-concat per target -> log-loss per target -> macro mean across targets`.

Secondary metrics reported alongside the primary:

- `macro_f1` macro F1 across the seven targets
- `macro_roc_auc` macro ROC-AUC across the seven targets
- `macro_brier` macro Brier across the seven targets

## Evaluation Policy

- Split: `GroupKFold` by `subject_id`
- Folds: 3
- Aggregation: macro mean across targets
- Tracks:
  - Track A unseen-subject generalization (recommended main track; protects against person-identity leakage of Q-family participant-relative labels)
  - Track B same-subject temporal forecasting (candidate alternative; must not be conflated with Track A, especially for Q-family targets)

## Public Leaderboard

DACON publishes a public leaderboard on 44 percent of the test set and a private leaderboard on the full test set. Both report average log-loss. Public leaderboard movement is treated as noisy directional feedback, not the final truth signal.

## Allowed Claim Boundaries

Downstream packets that reference this benchmark must declare one of:

- `local_oof_diagnostic_only` for results that only ran the canonical GroupKFold OOF locally
- `same_split_baseline_comparison` for baseline-vs-candidate comparisons under an identical split policy
- `public_lb_observation_only` for results that observed the DACON public leaderboard score for a specific submission

Performance and experiment packets that target this benchmark must carry raw evidence inside their own packet root and verify the primary metric numerically via `metrics_to_verify`.

## Interpretation Rules

- Strong local performance is not meaningful if the split policy permits identity leakage.
- Improvements should be interpreted separately for subjective Q-family and objective S-family targets.
- Public leaderboard movement must not promote a local result above its declared claim boundary.

## Claim Boundary

This packet only defines the benchmark entity. No specific run, metric value, or ranking is claimed here. Result-bearing packets are required to carry their own raw evidence and split-aware metric verification.

## Claims

- tentative: sleep-health-hackathon-v0 evaluates seven sleep-health prediction targets (Q1, Q2, Q3, S1, S2, S3, S4) on sleep-lifelog-2024 under a locally locked GroupKFold-by-subject-id sprint-1 policy with 3 folds, and reports a grouped macro log-loss aggregated as a macro mean across targets.
- tentative: Allowed claim boundaries against this benchmark are local_oof_diagnostic_only, same_split_baseline_comparison, and public_lb_observation_only. Public leaderboard scores require a DACON submission and are reported separately from local OOF diagnostic scores.
- tentative: An unseen-subject generalization track (Track A) is the recommended main track; a same-subject temporal forecasting track (Track B) is recorded as a separate candidate and must not be conflated with Track A, especially for Q-family targets that are participant-relative averages.

<!-- llm-synthesis:github-models-required-page-fill:2026-06-18:wiki-performance-sleep-health-hackathon-evaluation-policy-md -->
## GitHub Models Fallback Synthesis | 2026-06-18

- packet_ids: `2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic`
- packet_summary: 2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic: Wave41 LGB/CB fold-safe synthesis smoke improved the prior LGB/CB reproduction local OOF diagnostic line from 0.6198365213240887 to 0.6195964535023479, but remains local OOF only and short of the 0.61 goal.
- claim_status: preserved_from_raw_packet
- evidence_boundary: local_oof, notebook_output, DACON_public, DACON_private, and organizer_official evidence must stay separate.
- review_note: This page was conservatively filled in GitHub Actions because the compact fallback model omitted a required wiki page.
- synthesis_report: `wiki/reports/2026-06-18-sleep-lifelog-packet-synthesis.md`
