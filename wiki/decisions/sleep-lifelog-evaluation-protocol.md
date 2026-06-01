---
id: sleep-lifelog-evaluation-protocol
type: decision
title: Sleep Lifelog Evaluation Protocol
status: provisional-active
source_packets:
  - 2026-05-29-sleep-lifelog-2024
  - 2026-05-29-sleep-health-hackathon-v0
claim_status: tentative
review_required: true
related_dataset: sleep-lifelog-2024
related_benchmark: sleep-health-hackathon-v0
summary: "Sprint-1 local evaluation은 `GroupKFold` by `subject_id` 3 folds와 `grouped_macro_logloss`를 canonical policy로 사용합니다. 이 결정은 organizer-official split이 아니라 review-required local protocol입니다."
raw_evidence:
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/manifest.yaml
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/benchmark.yaml
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/packet.md
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/manifest.yaml
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/dataset.yaml
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/packet.md
---

# Sleep Lifelog Evaluation Protocol

이 decision page는 [sleep-lifelog-2024](../datasets/sleep-lifelog-2024.md)와 [sleep-health-hackathon-v0](../benchmarks/sleep-health-hackathon-v0.md)에 대한 sprint-1 local evaluation policy를 기록합니다.

## Decision

현재 local canonical evaluation은 다음으로 고정합니다.

- split: `GroupKFold`
- group_key: `subject_id`
- n_folds: `3`
- split name: `groupkfold-subject-3fold-oof`
- primary metric: `grouped_macro_logloss`
- aggregation: `OOF-concat per target -> log-loss per target -> macro mean across targets`
- main track: Track A `unseen-subject-generalization`

이 결정은 organizer-official validation protocol이 아니라 local sprint-1 policy입니다. `claim_status`는 raw packets와 동일하게 `tentative`입니다.

## Rationale

Q-family targets (`Q1`, `Q2`, `Q3`)는 participant-relative subjective labels입니다. Same-subject split에서는 participant identity 또는 reporting style이 validation rows에 누수될 수 있습니다. `GroupKFold` by `subject_id`는 unseen-subject generalization을 더 직접적으로 테스트하므로 benchmark packet은 Track A를 recommended main track으로 둡니다.

## Track Separation

| track | name | decision |
| --- | --- | --- |
| Track A | `unseen-subject-generalization` | local canonical main track입니다. 결과 packet은 이 track을 기본으로 보고해야 합니다. |
| Track B | `same-subject-temporal-forecasting` | candidate alternative입니다. Track A와 혼동하거나 같은 leaderboard처럼 합치지 않습니다. |

Track B를 쓰는 packet은 split semantics, leakage controls, Q-family interpretation limits를 별도로 설명해야 합니다.

## Consequences for Claims

- `local_oof_diagnostic_only`: Track A canonical OOF 결과를 local diagnostic으로만 기록합니다.
- `same_split_baseline_comparison`: baseline과 candidate가 동일한 split file/policy를 공유할 때만 비교합니다.
- `public_lb_observation_only`: DACON public leaderboard observation은 submission evidence와 함께 별도로 기록합니다.

Metric value가 있어도 split policy와 target aggregation이 검증되지 않으면 claim을 승격하지 않습니다.

## Supersession Triggers

다음 raw evidence가 들어오면 이 decision은 업데이트 또는 supersede되어야 합니다.

- organizer-official split protocol
- DACON private leaderboard interpretation rule
- canonical fold file or seed policy
- Track B를 formal alternative로 채택하는 팀 결정
- target count 또는 label definition에 대한 released package update

## Open Questions

남은 질문은 [Sleep Lifelog Open Questions](../questions/sleep-lifelog-open-questions.md)에 유지합니다. 특히 official split 부재, aggregation window, DACON submission 기록 양식은 downstream result review 전에 닫히거나 명시적으로 제한되어야 합니다.
