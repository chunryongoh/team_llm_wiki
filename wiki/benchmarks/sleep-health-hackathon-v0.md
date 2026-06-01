---
type: benchmark
entity_id: sleep-health-hackathon-v0
title: Sleep Health Hackathon Benchmark v0
dataset: sleep-lifelog-2024
task_family: sleep-health-prediction
claim_status: tentative
claim_boundary: benchmark_definition_not_metric_claim
review_required: true
packet_ids:
  - 2026-05-29-sleep-health-hackathon-v0
source_paths:
  - raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/manifest.yaml
  - raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/benchmark.yaml
  - raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/packet.md
related_pages:
  - wiki/datasets/sleep-lifelog-2024.md
  - wiki/features/sleep-lifelog-feature-landscape.md
  - wiki/decisions/sleep-lifelog-evaluation-protocol.md
  - wiki/questions/sleep-lifelog-open-questions.md
  - wiki/reports/2026-05-29-sleep-lifelog-benchmark-synthesis.md
raw_evidence:
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/manifest.yaml
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/benchmark.yaml
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/packet.md
---

# Sleep Health Hackathon Benchmark v0

This is the stable benchmark entity page for `sleep-health-hackathon-v0`. It defines the local evaluation target for the [Sleep Lifelog 2024 dataset](../datasets/sleep-lifelog-2024.md). It is not a result page and does not claim any model metric, leaderboard rank, or baseline improvement.

## Provenance

| field | value |
| --- | --- |
| packet id | `2026-05-29-sleep-health-hackathon-v0` |
| owner | `chunryongoh` |
| packet type | `benchmark` |
| packet status | `submitted` |
| deterministic ingest run | `26628582638-1` |
| claim status | `tentative` |
| claim boundary | `benchmark_definition_not_metric_claim` |
| raw sources | `manifest.yaml`, `benchmark.yaml`, `packet.md` under `raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/` |

## Benchmark definition

- Dataset: [Sleep Lifelog 2024](../datasets/sleep-lifelog-2024.md)
- Task family: `sleep-health-prediction`
- Label file: `ch2026_metrics_train.csv`
- Canonical local split: `GroupKFold` by `subject_id`, 3 folds
- Main local track: Track A, unseen-subject generalization
- Candidate separate track: Track B, same-subject temporal forecasting

## Targets

| id | family | kind | label source | description |
| --- | --- | --- | --- | --- |
| Q1 | subjective | binary | `ch2026_metrics_train.csv` column `Q1` | Perceived sleep quality, participant-relative |
| Q2 | subjective | binary | `ch2026_metrics_train.csv` column `Q2` | Bedtime physical fatigue, participant-relative |
| Q3 | subjective | binary | `ch2026_metrics_train.csv` column `Q3` | Bedtime stress level, participant-relative |
| S1 | objective | binary | `ch2026_metrics_train.csv` column `S1` | Total sleep time guideline compliance |
| S2 | objective | binary | `ch2026_metrics_train.csv` column `S2` | Sleep efficiency compliance |
| S3 | objective | binary | `ch2026_metrics_train.csv` column `S3` | Sleep onset latency compliance |
| S4 | objective | binary | `ch2026_metrics_train.csv` column `S4` | Wakefulness after sleep onset compliance |

Supersession note: the packet records older six-target summaries as superseded by the released package and metric description that include `S4`. This remains a tentative packet claim pending review of the released raw package.

## Metric policy

Primary metric: `grouped_macro_logloss`.

Definition from the benchmark packet: mean across the seven targets of subject-grouped log-loss computed on out-of-fold validation predictions.

Aggregation order:

1. Generate fold-level predictions under the canonical subject-grouped split.
2. Concatenate out-of-fold predictions into one OOF table.
3. Compute log-loss per target.
4. Macro-average the seven target losses.

Secondary metrics recorded for reporting context only:

- `macro_f1`
- `macro_roc_auc`
- `macro_brier`

No numeric metric values are present in the source packet.

## Evaluation tracks

### Track A: unseen-subject generalization

- Status: recommended main local track in the packet.
- Split: `GroupKFold` by `subject_id`.
- Folds: 3.
- Rationale: protects against person-identity leakage, especially for participant-relative Q-family labels.

### Track B: same-subject temporal forecasting

- Status: candidate alternative track, not the main benchmark track.
- Requirement: must not be conflated with Track A.
- Risk: Q-family labels are especially dangerous to evaluate under Track B alone because participant-relative averages can encode subject identity and reporting style.

## Public leaderboard policy

The packet records DACON public and private leaderboard semantics as separate from local OOF diagnostics:

- Public leaderboard share of test: `0.44`.
- Public and private aggregation: average log-loss.
- Public leaderboard movement is noisy directional feedback, not the final truth signal.
- A public leaderboard observation requires a recorded DACON submission and must use the `public_lb_observation_only` claim boundary.

## Allowed downstream claim boundaries

Downstream result-bearing packets that reference this benchmark must declare one of the following boundaries and carry their own raw evidence:

- `local_oof_diagnostic_only`: local result under the canonical GroupKFold OOF policy.
- `same_split_baseline_comparison`: baseline and candidate compared under the identical split policy.
- `public_lb_observation_only`: public DACON leaderboard observation for a specific submission.

## Interpretation guardrails

- Do not compare Track A and Track B as if they were the same benchmark.
- Do not promote local OOF diagnostics into public or private leaderboard claims.
- Interpret Q-family and S-family target results separately when experiments arrive.
- Do not claim organizer-official validation semantics unless an organizer-published split protocol appears.
- See the [evaluation protocol decision](../decisions/sleep-lifelog-evaluation-protocol.md) and [open questions](../questions/sleep-lifelog-open-questions.md).

## Claims preserved from source

- tentative: sleep-health-hackathon-v0 evaluates seven sleep-health prediction targets (Q1, Q2, Q3, S1, S2, S3, S4) on sleep-lifelog-2024 under a locally locked GroupKFold-by-subject-id sprint-1 policy with 3 folds, and reports a grouped macro log-loss aggregated as a macro mean across targets.
- tentative: Allowed claim boundaries against this benchmark are local_oof_diagnostic_only, same_split_baseline_comparison, and public_lb_observation_only. Public leaderboard scores require a DACON submission and are reported separately from local OOF diagnostic scores.
- tentative: An unseen-subject generalization track (Track A) is the recommended main track; a same-subject temporal forecasting track (Track B) is recorded as a separate candidate and must not be conflated with Track A, especially for Q-family targets that are participant-relative averages.
