---
id: sleep-health-hackathon-v0
type: benchmark
packet_type: benchmark
title: Sleep Health Hackathon Benchmark v0
source_packets:
  - 2026-05-29-sleep-health-hackathon-v0
owner: chunryongoh
claim_status: tentative
claim_boundary: benchmark_definition_not_metric_claim
review_required: true
related_dataset: sleep-lifelog-2024
primary_metric: grouped_macro_logloss
canonical_split: groupkfold-subject-3fold-oof
summary: "sleep-lifelog-2024의 Q1-Q3 subjective targets와 S1-S4 objective targets를 `GroupKFold` by `subject_id` 3 folds와 `grouped_macro_logloss`로 평가하는 local benchmark 정의입니다. 성능 claim은 포함하지 않습니다."
raw_evidence:
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/manifest.yaml
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/benchmark.yaml
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/packet.md
---

# Sleep Health Hackathon Benchmark v0

이 문서는 `sleep-health-hackathon-v0`의 안정 benchmark entity 페이지입니다. 날짜별 packet mirror가 아니라, downstream experiment, feature, decision, report가 참조할 공통 정의를 유지합니다.

관련 페이지: [Sleep Lifelog 2024 Dataset](../datasets/sleep-lifelog-2024.md), [Sleep Lifelog Feature Landscape](../features/sleep-lifelog-feature-landscape.md), [Sleep Lifelog Evaluation Protocol](../decisions/sleep-lifelog-evaluation-protocol.md), [Sleep Lifelog Open Questions](../questions/sleep-lifelog-open-questions.md), [2026-05-29 synthesis report](../reports/2026-05-29-sleep-lifelog-benchmark-synthesis.md).

## Provenance

- packet id: `2026-05-29-sleep-health-hackathon-v0`
- packet_type: `benchmark`
- owner: `chunryongoh`
- deterministic ingest run: `26628582638-1`
- raw packet root: `raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/`
- raw files: `manifest.yaml`, `benchmark.yaml`, `packet.md`
- claim_boundary: `benchmark_definition_not_metric_claim`
- claim_status: `tentative`
- review-required: true

## Benchmark Scope

`benchmark.yaml`는 이 benchmark가 [sleep-lifelog-2024](../datasets/sleep-lifelog-2024.md)를 사용하며 task family가 `sleep-health-prediction`이라고 정의합니다. 이 페이지는 benchmark definition만 다루며, 특정 model run, metric value, leaderboard rank, baseline superiority는 주장하지 않습니다.

## Targets

모든 target은 `ch2026_metrics_train.csv`의 label columns에서 옵니다.

| id | kind | label_source | description |
| --- | --- | --- | --- |
| `Q1` | `subjective-binary` | `ch2026_metrics_train.csv` column `Q1` | Perceived sleep quality, participant-relative. |
| `Q2` | `subjective-binary` | `ch2026_metrics_train.csv` column `Q2` | Bedtime physical fatigue, participant-relative. |
| `Q3` | `subjective-binary` | `ch2026_metrics_train.csv` column `Q3` | Bedtime stress level, participant-relative. |
| `S1` | `objective-binary` | `ch2026_metrics_train.csv` column `S1` | Total sleep time guideline compliance. |
| `S2` | `objective-binary` | `ch2026_metrics_train.csv` column `S2` | Sleep efficiency compliance. |
| `S3` | `objective-binary` | `ch2026_metrics_train.csv` column `S3` | Sleep onset latency compliance. |
| `S4` | `objective-binary` | `ch2026_metrics_train.csv` column `S4` | Wakefulness after sleep onset compliance. |

`S4`는 released package에 포함된 target입니다. older dataset paper summaries의 six-target framing은 현재 benchmark 정의에서는 superseded note로만 남깁니다.

## Metrics

Primary metric은 `grouped_macro_logloss`입니다.

- definition: `Mean across the seven targets of subject-grouped log-loss computed on out-of-fold validation predictions.`
- averaging_policy: `macro-mean over targets`
- loss_basis: `log-loss per target`
- aggregation_basis: `subject-grouped fold-level predictions concatenated into an OOF dataset before per-target log-loss`
- aggregation order: `OOF-concat per target -> log-loss per target -> macro mean across targets`

Secondary metrics는 benchmark packet에 `macro_f1`, `macro_roc_auc`, `macro_brier`로 기록되어 있습니다. 현재 raw evidence는 metric definitions만 제공하므로 numeric score claim은 없습니다.

## Evaluation Policy

Sprint-1 local canonical policy는 [Sleep Lifelog Evaluation Protocol](../decisions/sleep-lifelog-evaluation-protocol.md)에 decision record로 분리되어 있습니다.

- split: `groupkfold-subject`
- group_key: `subject_id`
- n_folds: `3`
- aggregation: `macro-mean over targets`
- canonical local split name: `groupkfold-subject-3fold-oof`

Tracks:

| track | name | status | interpretation |
| --- | --- | --- | --- |
| `A` | `unseen-subject-generalization` | recommended main track | Q-family participant-relative labels의 person-identity leakage를 줄이기 위한 main local track입니다. |
| `B` | `same-subject-temporal-forecasting` | candidate alternative | 별도 candidate track이며 Track A 결과와 혼동하거나 직접 대체하면 안 됩니다. |

## Public Leaderboard Boundary

DACON public leaderboard는 test set의 `0.44` share에 대한 feedback으로 기록되어 있고, public/private aggregations는 average log-loss입니다. Public leaderboard movement는 noisy directional feedback으로만 취급합니다. DACON submission evidence가 없는 local OOF result는 public claim이 아닙니다.

## Allowed Claim Boundaries

Downstream result-bearing packets는 아래 boundary 중 하나를 명시해야 합니다.

- `local_oof_diagnostic_only`: canonical `GroupKFold` OOF local diagnostic만 실행한 결과입니다.
- `same_split_baseline_comparison`: baseline과 candidate가 같은 split policy를 공유할 때만 허용되는 비교입니다.
- `public_lb_observation_only`: 특정 DACON submission의 public leaderboard observation입니다.

## Interpretation Rules

- Strong local performance는 split policy가 identity leakage를 허용하면 의미가 약해집니다.
- Q-family subjective targets와 S-family objective targets는 관련은 있지만 별도 진단 단위로 해석해야 합니다.
- Same-split comparison은 baseline과 candidate가 모두 canonical `GroupKFold` by `subject_id` 3-fold policy를 공유할 때만 유효합니다.
- Public leaderboard movement는 local claim boundary를 자동으로 승격하지 않습니다.

## Preserved Claims

- tentative: `sleep-health-hackathon-v0`는 `sleep-lifelog-2024` 위에서 `Q1`, `Q2`, `Q3`, `S1`, `S2`, `S3`, `S4`를 평가하고 `GroupKFold` by `subject_id` 3 folds 및 `grouped_macro_logloss` macro mean을 사용합니다.
- tentative: 허용 claim boundaries는 `local_oof_diagnostic_only`, `same_split_baseline_comparison`, `public_lb_observation_only`이며 public leaderboard score는 DACON submission과 함께 local OOF와 분리해 보고해야 합니다.
- tentative: Track A `unseen-subject-generalization`이 recommended main track이고 Track B `same-subject-temporal-forecasting`은 별도 candidate track입니다.
