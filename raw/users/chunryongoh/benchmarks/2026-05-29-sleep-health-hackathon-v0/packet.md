---
id: 2026-05-29-sleep-health-hackathon-v0
packet_type: benchmark
title: Sleep Health Hackathon Benchmark v0 Definition
date: "2026-05-29"
owner: chunryongoh
claim_boundary: benchmark_definition_not_metric_claim
claim_status: tentative
route: wiki/benchmarks
---

# Sleep Health Hackathon Benchmark v0 Definition

This packet locks the benchmark entity that downstream experiment, performance, and decision packets reference when reporting sleep-health prediction results. It defines the seven targets, the primary metric and its definition, the canonical evaluation split, the alternative track, and the allowed claim boundaries.

## Dataset Anchor

This benchmark evaluates models on the [[datasets/2026-05-29-sleep-lifelog-2024]] dataset under its locally locked GroupKFold-by-subject sprint-1 split policy.

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
