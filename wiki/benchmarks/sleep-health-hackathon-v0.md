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
summary: First-class definition of the sleep-health-hackathon-v0 benchmark on sleep-lifelog-2024. Locks the seven prediction targets (Q1-Q3 subjective, S1-S4 objective), the primary local metric (grouped macro log-loss under GroupKFold by subject_id with 3 folds), and the allowed claim boundaries for downstream results.
raw_paths:
- benchmark.yaml
raw_evidence:
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/manifest.yaml
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/benchmark.yaml
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/packet.md
intended_wiki_targets:
- wiki/benchmarks/2026-05-29-sleep-health-hackathon-v0.md
metrics_to_verify: []
claims:
- status: tentative
  text: sleep-health-hackathon-v0 evaluates seven sleep-health prediction targets (Q1, Q2, Q3, S1, S2, S3, S4) on sleep-lifelog-2024 under a locally locked GroupKFold-by-subject-id sprint-1 policy with 3 folds, and reports a grouped macro log-loss aggregated as a macro mean across targets.
- status: tentative
  text: Allowed claim boundaries against this benchmark are local_oof_diagnostic_only, same_split_baseline_comparison, and public_lb_observation_only. Public leaderboard scores require a DACON submission and are reported separately from local OOF diagnostic scores.
- status: tentative
  text: An unseen-subject generalization track (Track A) is the recommended main track; a same-subject temporal forecasting track (Track B) is recorded as a separate candidate and must not be conflated with Track A, especially for Q-family targets that are participant-relative averages.
publish_action: bot_pr
risk_tier: tier2-interpretation
---

# Sleep Health Hackathon Benchmark v0 Definition

## Page Status

- packet_id: `2026-05-29-sleep-health-hackathon-v0`
- generated_by_run: `26628582638-1`
- publish_action: `bot_pr`
- risk_tier: `tier2-interpretation`
- review_required: `true`
- owner: `chunryongoh`
- status: `submitted`
- task: `benchmark-definition`
- dataset: `sleep-lifelog-2024` (`v0`)
- split: `groupkfold-subject-3fold-oof`
- model: `not-applicable`
- claim_boundary: `benchmark_definition_not_metric_claim`
- claim_status: `tentative`
- date: `2026-05-29`
- compiled_packet: [automation/.cache/compiled/2026-05-29-sleep-health-hackathon-v0.json](../../automation/.cache/compiled/2026-05-29-sleep-health-hackathon-v0.json)

## Synthesis

`sleep-health-hackathon-v0` is the stable benchmark entity for sleep-health prediction on `sleep-lifelog-2024`. It defines the target taxonomy, local primary metric, evaluation split, track semantics, and allowed result-claim boundaries. It does not claim any model score, baseline win, leaderboard rank, or production performance.

한국어 메모: 이 벤치마크의 핵심은 로컬 OOF 진단, 동일 split 비교, DACON public LB 관찰을 서로 분리해 기록하는 것이다. 특히 Q 계열 라벨은 참가자 상대값이므로 Track A와 Track B 결과를 섞어 해석하면 안 된다.

## Stable Entity Fields

- name: `sleep-health-hackathon-v0`
- dataset_ref: `sleep-lifelog-2024`
- task_family: `sleep-health-prediction`
- primary_metric: `grouped_macro_logloss`
- canonical_local_split: `groupkfold-subject-3fold-oof`
- group_key: `subject_id`
- n_folds: `3`
- claim_status: `tentative`
- metrics_to_verify: `[]`

## Dataset Anchor

This benchmark evaluates the stable dataset entity `[[datasets/sleep-lifelog-2024]]`. The benchmark inherits the dataset packet's local sprint-1 grouped-subject split policy and leakage cautions. Any later packet that changes the dataset target set, split policy, or organizer-official evaluation protocol should explicitly supersede this benchmark page or create a new benchmark version.

## Target Taxonomy

The benchmark scores seven binary targets from `ch2026_metrics_train.csv`:

| target | kind | label source | interpretation |
| --- | --- | --- | --- |
| `Q1` | `subjective-binary` | `ch2026_metrics_train.csv` column `Q1` | perceived sleep quality, participant-relative |
| `Q2` | `subjective-binary` | `ch2026_metrics_train.csv` column `Q2` | bedtime physical fatigue, participant-relative |
| `Q3` | `subjective-binary` | `ch2026_metrics_train.csv` column `Q3` | bedtime stress level, participant-relative |
| `S1` | `objective-binary` | `ch2026_metrics_train.csv` column `S1` | total sleep time guideline compliance |
| `S2` | `objective-binary` | `ch2026_metrics_train.csv` column `S2` | sleep efficiency compliance |
| `S3` | `objective-binary` | `ch2026_metrics_train.csv` column `S3` | sleep onset latency compliance |
| `S4` | `objective-binary` | `ch2026_metrics_train.csv` column `S4` | wakefulness after sleep onset compliance |

`S4` is part of the current benchmark definition. Older six-target descriptions should not be used for new benchmark or feature claims unless a later packet adjudicates the difference.

## Metric Policy

Primary metric:

- name: `grouped_macro_logloss`
- definition: mean across the seven targets of subject-grouped log-loss computed on out-of-fold validation predictions.
- averaging_policy: `macro-mean over targets`
- loss_basis: `log-loss per target`
- aggregation_order: `subject-grouped fold predictions -> concatenated OOF predictions -> per-target log-loss -> macro mean across targets`

Secondary diagnostic metrics may be reported alongside the primary metric when raw evidence is supplied by a result packet:

- `macro_f1`
- `macro_roc_auc`
- `macro_brier`

This benchmark definition includes no numeric metric values. Any future result packet must provide raw YAML or JSON evidence through `metrics_to_verify` before a score can be treated as checked.

## Evaluation Tracks

| track | name | status | interpretation |
| --- | --- | --- | --- |
| `A` | `unseen-subject-generalization` | recommended main track | Uses grouped-subject validation to reduce person-identity leakage, especially for Q-family participant-relative labels. |
| `B` | `same-subject-temporal-forecasting` | candidate alternative | May answer a temporal forecasting question, but must not be conflated with Track A or used alone to imply unseen-subject generalization. |

Canonical sprint-1 local comparisons should use Track A with 3-fold `GroupKFold` by `subject_id`. Track B can be useful for a separate product or forecasting question, but it has different leakage semantics and needs its own claim boundary.

## Public Leaderboard Semantics

The benchmark YAML records DACON public and private leaderboards, with the public leaderboard using 44 percent of the test set. Public and private aggregations are described as average log-loss.

A public leaderboard score is only a `public_lb_observation_only` claim unless the specific DACON submission, timestamp or submission id, and score evidence are recorded in a downstream packet. Public leaderboard movement should not promote a local OOF diagnostic result into a model-ranking claim.

## Allowed Claim Boundaries

Downstream packets that reference this benchmark should declare one of these boundaries:

- `local_oof_diagnostic_only`: a local canonical `GroupKFold` OOF result with raw metric evidence.
- `same_split_baseline_comparison`: a comparison where baseline and candidate use the same dataset, target set, split, folds, and metric implementation.
- `public_lb_observation_only`: a recorded DACON public leaderboard observation, kept separate from local OOF diagnostics.

Any benchmark result that changes split policy, excludes targets, uses Track B, or reports only public LB movement should say so directly rather than inheriting the main Track A interpretation.

## Interpretation Rules

- Do not compare Track A and Track B scores as if they measure the same generalization problem.
- Interpret Q-family and S-family improvements separately; subjective participant-relative labels and objective guideline-compliance labels have different leakage and error-analysis risks.
- Strong local performance is not a public leaderboard claim without submission evidence.
- A same-split comparison is valid only when the baseline and candidate share the canonical `GroupKFold` by `subject_id` 3-fold policy and the same target set.
- This page defines evaluation semantics only; it does not establish that any model is good, best, or production-ready.

## Claim Register

All current benchmark claims remain `tentative`:

- `tentative`: the benchmark evaluates seven targets on `sleep-lifelog-2024` under the local 3-fold `GroupKFold` by `subject_id` policy and uses grouped macro log-loss as the primary local metric.
- `tentative`: allowed claim boundaries are `local_oof_diagnostic_only`, `same_split_baseline_comparison`, and `public_lb_observation_only`; DACON public leaderboard observations are separate from local OOF diagnostics.
- `tentative`: Track A is the recommended unseen-subject generalization track, while Track B is a same-subject temporal forecasting candidate that must not be conflated with Track A.

## Provenance

- packet_id: `2026-05-29-sleep-health-hackathon-v0`
- raw_packet_root: `raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/`
- raw_packet_files:
  - `raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/manifest.yaml`
  - `raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/benchmark.yaml`
  - `raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/packet.md`
- dataset_page: `[[datasets/sleep-lifelog-2024]]`
- generated_by_run: `26628582638-1`

## Open Questions, Conflicts, and Supersession Notes

- Six-target versus seven-target framing: current benchmark work should include `S4`; older six-target notes are superseded unless later packet evidence disputes this.
- Official organizer protocol: this page records the local sprint-1 split policy. If DACON or the organizer publishes a more specific official validation protocol, a new packet should supersede or version this benchmark.
- Metric implementation details: future result packets should record the exact log-loss implementation details they used, including probability clipping or library defaults, before metric values are compared.
- Public LB evidence: a public leaderboard observation requires downstream raw evidence for the specific submission. This benchmark definition itself has no public score.
- Stable path: the manifest's `intended_wiki_targets` contains a dated path, but repository policy renders benchmark entities to stable paths such as `wiki/benchmarks/sleep-health-hackathon-v0.md`; the packet id remains in provenance.
