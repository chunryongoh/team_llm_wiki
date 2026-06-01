---
id: sleep-health-hackathon-v0
type: benchmark
title: Sleep Health Hackathon v0
entity_name: sleep-health-hackathon-v0
dataset:
  name: sleep-lifelog-2024
  version: v0
task_family: sleep-health-prediction
owner: chunryongoh
status: submitted
claim_boundary: benchmark_definition_not_metric_claim
claim_status: tentative
review_required: true
publish_action: bot_pr
risk_tier: tier2-interpretation
latest_packet_id: 2026-05-29-sleep-health-hackathon-v0
latest_packet_date: '2026-05-29'
source_packets:
  - id: 2026-05-29-sleep-health-hackathon-v0
    packet_type: benchmark
    title: Sleep Health Hackathon Benchmark v0 Definition
    date: '2026-05-29'
    owner: chunryongoh
    status: submitted
    claim_boundary: benchmark_definition_not_metric_claim
    claim_status: tentative
    raw_paths:
      - raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/manifest.yaml
      - raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/benchmark.yaml
      - raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/packet.md
metrics_to_verify: []
claims:
  - status: tentative
    text: sleep-health-hackathon-v0 evaluates seven sleep-health prediction targets (Q1, Q2, Q3, S1, S2, S3, S4) on sleep-lifelog-2024 under a locally locked GroupKFold-by-subject-id sprint-1 policy with 3 folds, and reports a grouped macro log-loss aggregated as a macro mean across targets.
  - status: tentative
    text: Allowed claim boundaries against this benchmark are local_oof_diagnostic_only, same_split_baseline_comparison, and public_lb_observation_only. Public leaderboard scores require a DACON submission and are reported separately from local OOF diagnostic scores.
  - status: tentative
    text: An unseen-subject generalization track (Track A) is the recommended main track; a same-subject temporal forecasting track (Track B) is recorded as a separate candidate and must not be conflated with Track A, especially for Q-family targets that are participant-relative averages.
raw_evidence:
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/manifest.yaml
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/benchmark.yaml
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/packet.md
---

# Sleep Health Hackathon v0

This page is the stable team-memory page for the `sleep-health-hackathon-v0` benchmark. It synthesizes the submitted benchmark packet rather than mirroring packet files directly.

**Current status:** review-required, `tentative`. This page defines a benchmark entity and its evaluation policy. It does **not** claim any model score, leaderboard rank, or baseline result.

## Entity Summary

`sleep-health-hackathon-v0` is the team benchmark for seven binary sleep-health prediction targets on [[datasets/sleep-lifelog-2024]]. Its sprint-1 local evaluation policy is GroupKFold by `subject_id` with 3 folds, and its primary local diagnostic metric is grouped macro log-loss over the seven targets.

Downstream experiment or performance packets that cite this benchmark must provide their own raw evidence and split-aware metric verification. Strong local results remain local diagnostic claims unless a DACON submission is recorded and explicitly scoped as a public leaderboard observation.

## Provenance

| field | value |
| --- | --- |
| latest packet id | `2026-05-29-sleep-health-hackathon-v0` |
| packet type | `benchmark` |
| owner | `chunryongoh` |
| packet date | `2026-05-29` |
| packet status | `submitted` |
| claim boundary | `benchmark_definition_not_metric_claim` |
| claim status | `tentative` |

Raw evidence paths:

- `raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/manifest.yaml`
- `raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/benchmark.yaml`
- `raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/packet.md`

## Dataset Anchor

- dataset: [[datasets/sleep-lifelog-2024]]
- dataset version in packet: `v0`
- task family: `sleep-health-prediction`
- label source: `ch2026_metrics_train.csv`

## Prediction Targets

The benchmark scores seven binary targets. The source packet separates subjective Q-family targets from objective S-family targets because their interpretation and leakage risks differ.

| target | kind | label source | description |
| --- | --- | --- | --- |
| `Q1` | subjective-binary | `ch2026_metrics_train.csv` column `Q1` | Perceived sleep quality, participant-relative. |
| `Q2` | subjective-binary | `ch2026_metrics_train.csv` column `Q2` | Bedtime physical fatigue, participant-relative. |
| `Q3` | subjective-binary | `ch2026_metrics_train.csv` column `Q3` | Bedtime stress level, participant-relative. |
| `S1` | objective-binary | `ch2026_metrics_train.csv` column `S1` | Total sleep time guideline compliance. |
| `S2` | objective-binary | `ch2026_metrics_train.csv` column `S2` | Sleep efficiency compliance. |
| `S3` | objective-binary | `ch2026_metrics_train.csv` column `S3` | Sleep onset latency compliance. |
| `S4` | objective-binary | `ch2026_metrics_train.csv` column `S4` | Wakefulness after sleep onset compliance. |

The source packet records that `S4` is included in the released package and that older six-target summaries are superseded by the released metric description. This remains part of the tentative dataset/benchmark definition, not a performance claim.

## Evaluation Policy

### Canonical sprint-1 local policy

| field | value |
| --- | --- |
| split | `groupkfold-subject` |
| group key | `subject_id` |
| folds | `3` |
| aggregation | macro mean over targets |
| primary local result form | out-of-fold validation predictions |

The canonical local policy is designed to evaluate unseen-subject generalization and to reduce person-identity leakage risk, especially for participant-relative Q-family labels.

### Tracks

| track | name | recommended | interpretation |
| --- | --- | --- | --- |
| `A` | `unseen-subject-generalization` | yes | Main track. Uses subject grouping to protect against person-identity leakage for Q-family labels. |
| `B` | `same-subject-temporal-forecasting` | no | Candidate alternative track. Must be reported separately and must not be conflated with Track A. Q-family targets are especially risky under this track alone. |

## Metrics

### Primary metric: `grouped_macro_logloss`

Definition from the benchmark packet: mean across the seven targets of subject-grouped log-loss computed on out-of-fold validation predictions.

Aggregation order:

1. Generate fold-level validation predictions under GroupKFold by `subject_id`.
2. Concatenate the fold-level validation predictions into one out-of-fold prediction table.
3. Compute log-loss separately for each target.
4. Report the macro mean across the seven target log-loss values.

### Secondary metrics

The packet also records these secondary metrics for reporting alongside the primary metric:

- `macro_f1`: macro F1 across the seven prediction targets.
- `macro_roc_auc`: macro ROC-AUC across the seven prediction targets.
- `macro_brier`: macro Brier score across the seven prediction targets.

No numeric metric value is claimed on this page.

## Public Leaderboard Scope

The benchmark packet records a DACON public/private leaderboard policy:

- public leaderboard share of test set: `0.44`
- public and private aggregation: average log-loss
- interpretation: public leaderboard movement is noisy directional feedback, not the final truth signal

A public leaderboard score is only a `public_lb_observation_only` claim when a specific DACON submission is recorded. It must not be merged into, or used to promote, local OOF diagnostic claims.

## Allowed Claim Boundaries for Downstream Results

Downstream result packets referencing this benchmark must stay inside one of these boundaries unless new raw evidence justifies a different reviewed boundary:

- `local_oof_diagnostic_only`: result only ran the canonical local GroupKFold OOF evaluation.
- `same_split_baseline_comparison`: baseline and candidate use the same canonical GroupKFold-by-subject 3-fold split policy.
- `public_lb_observation_only`: result records a DACON public leaderboard score for a specific submission.

Same-split comparisons are valid only when the compared runs share the same split policy and metric computation. Track A and Track B results must be kept separate.

## Working Interpretation Rules

- Interpret subjective Q-family targets and objective S-family targets separately; a change that helps one family may not carry the same meaning for the other.
- Strong local performance is not a public leaderboard claim unless a DACON submission and score are recorded in a result-bearing packet.
- Public leaderboard movement must not promote a local result above its declared claim boundary.
- Any model, feature, or performance page citing this benchmark needs raw evidence and numeric metric verification in its own packet root.

## Preserved Source Claims

All source claims remain `tentative`:

- **tentative:** sleep-health-hackathon-v0 evaluates seven sleep-health prediction targets (Q1, Q2, Q3, S1, S2, S3, S4) on sleep-lifelog-2024 under a locally locked GroupKFold-by-subject-id sprint-1 policy with 3 folds, and reports a grouped macro log-loss aggregated as a macro mean across targets.
- **tentative:** Allowed claim boundaries against this benchmark are local_oof_diagnostic_only, same_split_baseline_comparison, and public_lb_observation_only. Public leaderboard scores require a DACON submission and are reported separately from local OOF diagnostic scores.
- **tentative:** An unseen-subject generalization track (Track A) is the recommended main track; a same-subject temporal forecasting track (Track B) is recorded as a separate candidate and must not be conflated with Track A, especially for Q-family targets that are participant-relative averages.

## Reviewer Checklist

- Confirm any future result packet uses the same `subject_id` GroupKFold 3-fold policy before accepting `same_split_baseline_comparison` claims.
- Require explicit raw metric tables or predictions before recording any numeric score.
- Keep DACON public leaderboard observations separate from local OOF diagnostics.
- Revisit this benchmark page if an organizer-official split protocol supersedes the local sprint-1 policy.
