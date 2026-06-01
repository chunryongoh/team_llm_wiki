---
id: sleep-lifelog-open-questions
type: open-questions
title: Sleep Lifelog Open Questions
source_packets:
  - 2026-05-29-sleep-lifelog-2024
  - 2026-05-29-sleep-health-hackathon-v0
claim_status: tentative
review_required: true
summary: "sleep-lifelog-2024와 sleep-health-hackathon-v0 통합 후 남은 unresolved questions, supersession watch items, review blockers를 추적합니다."
raw_evidence:
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/manifest.yaml
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/benchmark.yaml
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/packet.md
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/manifest.yaml
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/dataset.yaml
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/packet.md
---

# Sleep Lifelog Open Questions

이 페이지는 [dataset](../datasets/sleep-lifelog-2024.md), [benchmark](../benchmarks/sleep-health-hackathon-v0.md), [feature landscape](../features/sleep-lifelog-feature-landscape.md), [evaluation protocol](../decisions/sleep-lifelog-evaluation-protocol.md)에 걸친 미해결 질문을 추적합니다.

## Active Questions

| id | status | question | why it matters |
| --- | --- | --- | --- |
| `Q-SL-001` | open | Organizer-official split protocol이 존재하거나 공개될 예정인가? | 현재 `groupkfold-subject-3fold-oof`는 local canonical sprint-1 policy일 뿐 official validation semantics가 아닙니다. |
| `Q-SL-002` | open | `sleep-sensor:placeholder`의 실제 schema와 feature extraction 범위는 무엇인가? | dataset packet은 sleep sensor를 참조하지만 exhaustive schema mapping을 제공하지 않습니다. |
| `Q-SL-003` | open | `self-report:bedtime-questionnaire`에서 labels와 구분되는 covariates가 무엇이며 leakage risk는 어떻게 관리하는가? | self-report covariates는 Q-family labels와 가까워 leakage boundary가 중요합니다. |
| `Q-SL-004` | open | `sleep_date`와 `lifelog_date` 기준 modality별 aggregation window를 어떻게 표준화할 것인가? | minute-level streams와 nested payloads를 tabular modeling table로 만들 때 재현성과 leakage control이 필요합니다. |
| `Q-SL-005` | open | `about 700 days` dataset description과 `450` modeling rows 사이의 filtering/join lineage는 무엇인가? | dataset scale claim과 modeling table claim의 provenance를 더 세밀하게 검증해야 합니다. |
| `Q-SL-006` | open | Track B `same-subject-temporal-forecasting`을 실제로 사용할 경우 Q-family participant-relative leakage를 어떻게 제한할 것인가? | Track B 결과는 Track A와 혼동하면 안 되며 별도 claim boundary가 필요합니다. |
| `Q-SL-007` | open | DACON public/private leaderboard submission evidence를 어떤 packet schema로 기록할 것인가? | `public_lb_observation_only` claim은 submission id, timestamp, score, public/private distinction이 필요합니다. |
| `Q-SL-008` | open | Q-family와 S-family metric diagnostics를 어떻게 함께 보고할 것인가? | benchmark primary metric은 macro mean이지만 interpretation은 target family별로 분리해야 합니다. |

## Supersession Watchlist

- six-target older summaries는 current wiki에서 superseded로 취급하지만, 새로운 upstream document가 나타나면 `S4` 포함 여부를 재확인해야 합니다.
- organizer-official split이 나오면 [evaluation protocol](../decisions/sleep-lifelog-evaluation-protocol.md)의 `provisional-active` status를 재검토해야 합니다.
- canonical fold file, seed, or OOF artifact가 들어오면 benchmark page의 split description을 더 재현 가능하게 바꿔야 합니다.

## Review Blockers for Result Claims

Result-bearing PR은 최소한 다음을 만족해야 합니다.

- `sleep-lifelog-2024`와 `sleep-health-hackathon-v0`를 명시적으로 참조합니다.
- `Q1`-`Q3`, `S1`-`S4` target coverage를 누락하지 않습니다.
- split이 `GroupKFold` by `subject_id` 3 folds인지, 아니면 Track B인지 명확히 밝힙니다.
- `grouped_macro_logloss` 계산 순서를 재현 가능한 evidence로 제공합니다.
- `metrics_to_verify`가 비어 있지 않은 성능 claim은 raw metric/split evidence를 포함합니다.
