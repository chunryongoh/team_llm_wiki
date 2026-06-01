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

# Sleep Health Hackathon Benchmark v0

## Page Status

- stable_page: `wiki/benchmarks/sleep-health-hackathon-v0.md`
- packet_id: `2026-05-29-sleep-health-hackathon-v0`
- generated_by_run: `26628582638-1`
- publish_action: `bot_pr`
- risk_tier: `tier2-interpretation`
- review_required: `true`
- owner: `chunryongoh`
- source_status: `submitted`
- task: `benchmark-definition`
- claim_boundary: `benchmark_definition_not_metric_claim`
- claim_status: `tentative`
- metrics_to_verify: `[]`

## What This Page Is

`sleep-health-hackathon-v0` is the stable benchmark entity for sleep-health prediction on `[[datasets/sleep-lifelog-2024]]`. It records the target set, local primary metric, local split policy, track semantics, public leaderboard interpretation, and allowed result-claim boundaries.

This page is a benchmark definition, not a result page. It makes no claim about any model score, baseline win, leaderboard rank, or production readiness. Downstream experiment or performance packets must carry their own raw evidence and metric verification before any numeric score can be treated as checked.

## Stable Entity Fields

| field | value |
| --- | --- |
| benchmark_name | `sleep-health-hackathon-v0` |
| dataset_ref | `sleep-lifelog-2024` |
| task_family | `sleep-health-prediction` |
| primary_metric | `grouped_macro_logloss` |
| canonical_local_split | `groupkfold-subject-3fold-oof` |
| split_policy | `GroupKFold` by `subject_id` |
| n_folds | `3` |
| main_track | Track A, `unseen-subject-generalization` |
| alternative_track | Track B, `same-subject-temporal-forecasting` |
| claim_status | `tentative` |

## Dataset Anchor

The benchmark evaluates models on the stable dataset entity `[[datasets/sleep-lifelog-2024]]` with dataset version `v0`. The benchmark inherits the dataset packet's local sprint-1 grouped-subject split policy and leakage cautions.

If a later packet changes the dataset target set, split policy, released package interpretation, or organizer-official evaluation protocol, that packet should explicitly supersede this benchmark page or create a new benchmark version. The current page should not be silently overwritten with incompatible evaluation semantics.

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

`S4` is part of the current benchmark definition. Older six-target summaries are treated as superseded for current team work unless later raw evidence adjudicates the target-count conflict differently.

## Metric Policy

Primary metric:

- name: `grouped_macro_logloss`
- definition: mean across the seven targets of subject-grouped log-loss computed on out-of-fold validation predictions
- averaging_policy: `macro-mean over targets`
- loss_basis: `log-loss per target`
- aggregation_order: `subject-grouped fold-level predictions -> concatenate OOF predictions -> compute log-loss per target -> macro mean across targets`

Secondary diagnostic metrics may be reported alongside the primary metric when a result packet supplies raw evidence:

- `macro_f1`: macro F1 across the seven targets
- `macro_roc_auc`: macro ROC-AUC across the seven targets
- `macro_brier`: macro Brier score across the seven targets

This benchmark packet includes no numeric metric values. Any future result packet should record enough raw evidence to verify the split, target set, prediction rows, and metric implementation before a score is used for comparison.

## Evaluation Tracks

| track | name | status | interpretation |
| --- | --- | --- | --- |
| `A` | `unseen-subject-generalization` | recommended main track | Uses grouped-subject validation to reduce person-identity leakage, especially for Q-family participant-relative labels. |
| `B` | `same-subject-temporal-forecasting` | candidate alternative | May answer a same-subject temporal forecasting question, but must not be conflated with Track A or used alone to imply unseen-subject generalization. |

Canonical sprint-1 local comparisons should use Track A with 3-fold `GroupKFold` by `subject_id`. Track B has different leakage semantics and requires explicit labeling in downstream claims.

## Public Leaderboard Semantics

The benchmark YAML records a DACON public/private leaderboard policy:

- public leaderboard share of test: `0.44`
- public and private aggregation: average log-loss
- interpretation: public leaderboard movement is noisy directional feedback, not the final truth signal

A public leaderboard score is only a `public_lb_observation_only` claim unless a downstream packet records the specific submission evidence, such as the submission identifier or timestamp and the observed score. Public leaderboard movement must not promote a local OOF diagnostic result into a supported model-ranking claim.

## Allowed Downstream Claim Boundaries

Downstream packets that reference this benchmark should use one of these boundaries:

- `local_oof_diagnostic_only`: a local canonical `GroupKFold` OOF result with raw metric evidence.
- `same_split_baseline_comparison`: a comparison where baseline and candidate share the same dataset, target set, split policy, folds, and metric implementation.
- `public_lb_observation_only`: a recorded DACON public leaderboard observation, kept separate from local OOF diagnostics.

Any result that changes split policy, excludes targets, uses Track B, or reports only public leaderboard movement should state that directly instead of inheriting the main Track A interpretation.

## Interpretation Rules

- Do not compare Track A and Track B scores as if they measure the same generalization problem.
- Interpret Q-family and S-family changes separately; subjective participant-relative labels and objective guideline-compliance labels have different leakage and error-analysis risks.
- Strong local performance is not a public leaderboard claim without DACON submission evidence.
- Same-split comparisons are valid only when baseline and candidate use the same canonical `GroupKFold` by `subject_id` 3-fold policy and the same seven-target set.
- This page defines evaluation semantics only; it does not establish that any model is good, best, or production-ready.

## Claim Register

All current benchmark claims remain `tentative`:

- `tentative`: `sleep-health-hackathon-v0` evaluates seven targets (`Q1`, `Q2`, `Q3`, `S1`, `S2`, `S3`, `S4`) on `sleep-lifelog-2024` under a locally locked 3-fold `GroupKFold` by `subject_id` sprint-1 policy, and reports grouped macro log-loss as a macro mean across targets.
- `tentative`: allowed claim boundaries are `local_oof_diagnostic_only`, `same_split_baseline_comparison`, and `public_lb_observation_only`; DACON public leaderboard observations are separate from local OOF diagnostics.
- `tentative`: Track A is the recommended unseen-subject generalization track, while Track B is a same-subject temporal forecasting candidate that must not be conflated with Track A, especially for Q-family participant-relative labels.

## Provenance

- packet_id: `2026-05-29-sleep-health-hackathon-v0`
- raw_packet_root: `raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/`
- raw_packet_files:
  - `raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/manifest.yaml`
  - `raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/benchmark.yaml`
  - `raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/packet.md`
- packet_raw_paths:
  - `benchmark.yaml`
- related_dataset: `[[datasets/sleep-lifelog-2024]]`
- latest_context_run: `26628582638-1`

## Open Questions and Supersession Notes

- Official organizer protocol: this page records the local sprint-1 split policy. If DACON or the organizer publishes a more specific official validation protocol, a new packet should supersede or version this benchmark.
- Six-target versus seven-target framing: current benchmark work includes `S4`; older six-target notes are treated as superseded unless later packet evidence disputes this.
- Metric implementation details: future result packets should record exact log-loss implementation details, including probability clipping or library defaults, before metric values are compared.
- Public leaderboard evidence: this benchmark definition has no public score. Public leaderboard claims require downstream raw evidence for a specific DACON submission.
- Stable path note: the packet manifest lists a dated intended wiki target, but repository policy renders benchmark entities to stable paths. The packet id remains in provenance.

## Reviewer Checklist

- Confirm that no numeric performance claim was added to this benchmark definition.
- Confirm that future result pages using this benchmark cite one of the allowed claim boundaries.
- Confirm that Track B results, if any, are not summarized as Track A unseen-subject generalization results.
- Confirm that downstream comparisons include all seven targets unless a later packet explicitly supersedes the target set.
