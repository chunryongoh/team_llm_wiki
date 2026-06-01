---
id: sleep-lifelog-evaluation-protocol
type: decision
title: Sleep Lifelog Evaluation Protocol
status: provisional
claim_status: tentative
review_required: true
summary: organizer-official rule이 확인되기 전까지 Sleep Lifelog/DACON reporting에서 local OOF, DACON public leaderboard, DACON private leaderboard를 별도 evidence class로 기록한다는 provisional decision이다.
date: '2026-06-01'
related_sources:
  - wiki/sources/2026-06-01-dacon-leaderboard-claim-boundary.md
related_dataset: wiki/datasets/sleep-lifelog-2024.md
related_benchmark: wiki/benchmarks/sleep-health-hackathon-v0.md
related_features: wiki/features/sleep-lifelog-feature-landscape.md
related_questions: wiki/questions/sleep-lifelog-open-questions.md
raw_evidence:
- raw/users/chunryongoh/references/2026-06-01-dacon-leaderboard-claim-boundary/manifest.yaml
- raw/users/chunryongoh/references/2026-06-01-dacon-leaderboard-claim-boundary/notes.md
- raw/users/chunryongoh/references/2026-06-01-dacon-leaderboard-claim-boundary/packet.md
---

# Sleep Lifelog Evaluation Protocol

## Decision

Sleep Lifelog 2024 / DACON-ETRI sleep-health hackathon 결과를 보고할 때, organizer-official split 또는 private leaderboard interpretation rule이 확인되기 전까지 다음 세 evidence class를 분리한다.

- `Local GroupKFold OOF metrics`
- `DACON public leaderboard results`
- `DACON private leaderboard results`

이 결정은 [DACON Leaderboard and Local OOF Claim Boundary](../sources/2026-06-01-dacon-leaderboard-claim-boundary.md)의 `tentative` claim을 운영 규칙으로 정리한 것이다. supported performance claim이 아니며, raw metric 또는 official split evidence를 새로 만들지 않는다.

## Protocol Table

| evidence class | 허용되는 보고 | 필요한 raw evidence | 금지되는 보고 |
|---|---|---|---|
| `Local GroupKFold OOF metrics` | local validation evidence로 보고한다. `group_key: subject_id`, fold count, fold file, seed, metric script를 함께 보존한다. | local run config, fold assignment, metric output, dataset version, model/feature config | matching submission record 없이 DACON leaderboard claim으로 승격하지 않는다. |
| `DACON public leaderboard results` | submission feedback으로 보고한다. `submission_id`, timestamp, target configuration, preprocessing, `feature_set_id`, `model_family`를 함께 기록한다. | DACON submission log, public score row, submission metadata | private evidence 없이 local conclusion을 자동 supersede했다고 쓰지 않는다. |
| `DACON private leaderboard results` | private leaderboard가 공개되면 final leaderboard evidence로 별도 기록한다. | official/private leaderboard row, matching submission metadata | local OOF row와 한 row로 병합하거나 local metric처럼 해석하지 않는다. |

## Decision Status

- decision status: `provisional`
- claim_status: `tentative`
- metrics_to_verify: 현재 source 기준 `[]`
- model_family: 현재 source 기준 `not-applicable`

이 protocol은 팀 reporting convention이다. DACON 또는 ETRI organizer가 official split protocol, public/private leaderboard semantics, private leaderboard finality를 명시하면 해당 근거가 이 decision을 supersede할 수 있다.

## Implications for Feature Work

feature 또는 preprocessing 변경을 leaderboard feedback과 연결하려면 [Sleep Lifelog Feature Landscape](../features/sleep-lifelog-feature-landscape.md)의 provenance field를 채워야 한다. 특히 `feature_set_id`, `preprocessing_version`, `target_configuration`, `submission_id`, `timestamp`가 없으면 public leaderboard feedback은 directional note로만 남긴다.

## Related Open Questions

공식 split rule, submission metadata schema, local fold provenance, feature provenance template은 [Sleep Lifelog Open Questions](../questions/sleep-lifelog-open-questions.md)에 backlog로 남아 있다.
