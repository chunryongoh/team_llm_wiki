---
id: sleep-lifelog-feature-landscape
type: feature-landscape
title: Sleep Lifelog Feature Landscape
status: draft
summary: Sleep Lifelog 2024 및 DACON/ETRI sleep-health hackathon에서 feature, preprocessing, target configuration을 submission metadata와 함께 추적해야 한다는 현재 reporting landscape를 정리한다.
claim_status: tentative
primary_dataset: wiki/datasets/sleep-lifelog-2024.md
primary_benchmark: wiki/benchmarks/sleep-health-hackathon-v0.md
related_sources:
  - wiki/sources/2026-06-01-dacon-leaderboard-claim-boundary.md
related_decisions:
  - wiki/decisions/sleep-lifelog-evaluation-protocol.md
related_questions:
  - wiki/questions/sleep-lifelog-open-questions.md
raw_evidence:
- raw/users/chunryongoh/references/2026-06-01-dacon-leaderboard-claim-boundary/manifest.yaml
- raw/users/chunryongoh/references/2026-06-01-dacon-leaderboard-claim-boundary/notes.md
- raw/users/chunryongoh/references/2026-06-01-dacon-leaderboard-claim-boundary/packet.md
---

# Sleep Lifelog Feature Landscape

이 page는 [Sleep Lifelog 2024 Dataset Definition](../datasets/sleep-lifelog-2024.md)과 [Sleep Health Hackathon Benchmark v0 Definition](../benchmarks/sleep-health-hackathon-v0.md)를 사용하는 작업에서 feature provenance를 어떻게 기록할지 정리한다. 현재 직접 근거는 [DACON Leaderboard and Local OOF Claim Boundary](../sources/2026-06-01-dacon-leaderboard-claim-boundary.md) packet이며, raw feature list, feature importance, ablation metric, leaderboard score는 제공되지 않았다.

## 현재 확정된 범위

`2026-06-01-dacon-leaderboard-claim-boundary` source가 제공하는 feature 관련 지식은 성능 claim이 아니라 reporting requirement이다. DACON public leaderboard feedback은 `target configuration`, `preprocessing`, `feature set`, `model family`, `timestamp`와 함께 기록될 때만 local OOF run 또는 private leaderboard result와 비교할 수 있다.

따라서 이 page는 어떤 feature가 더 좋다는 주장을 하지 않는다. 대신 feature가 validation evidence와 leaderboard evidence를 연결하는 metadata 축임을 기록한다.

## Feature Provenance Fields

| field | 기록 이유 | evidence class |
|---|---|---|
| `dataset.name` / `dataset.version` | Sleep Lifelog 2024 released package 기준을 고정한다. | dataset provenance |
| `split.name` / `group_key` | local OOF가 어떤 subject-level split에서 나왔는지 구분한다. | local validation evidence |
| `fold_file` / `seed` | local GroupKFold OOF 재현성을 확인한다. 현재 packet에는 `fold_file: null`이다. | local validation evidence |
| `target_configuration` | DACON submission target이 local metric과 같은지 확인한다. | submission metadata |
| `preprocessing_version` | public leaderboard feedback이 어떤 preprocessing의 결과인지 추적한다. | submission metadata |
| `feature_set_id` | feature 변경과 score 변경을 연결하기 위한 최소 단위다. | submission metadata |
| `model_family` | feature effect와 model effect를 분리하기 위한 최소 단위다. 현재 source의 model은 `not-applicable`이다. | model provenance |
| `submission_id` / `timestamp` | DACON public/private leaderboard row와 local run을 연결한다. | leaderboard evidence |
| `leaderboard_phase` | `public` feedback과 `private` final evidence를 분리한다. | leaderboard evidence |

## Reporting Boundary

feature set이 바뀌어 DACON public leaderboard score가 변했다는 설명은 matching submission metadata가 없으면 tentative interpretation으로만 남겨야 한다. public leaderboard feedback은 directional and potentially noisy로 취급하며, private leaderboard evidence나 organizer-official rule 없이 local OOF conclusion을 자동으로 supersede하지 않는다. 이 결정은 [Sleep Lifelog Evaluation Protocol](../decisions/sleep-lifelog-evaluation-protocol.md)에 정리되어 있다.

## 현재 없는 근거

- raw feature matrix schema
- feature engineering code 또는 preprocessing config hash
- feature ablation metric
- local OOF metric row
- DACON public/private leaderboard score row
- submission_id와 local run id의 매핑

이 누락 항목은 [Sleep Lifelog Open Questions](../questions/sleep-lifelog-open-questions.md)의 `sleep-lifelog-oq-002`, `sleep-lifelog-oq-003`, `sleep-lifelog-oq-004`와 연결된다.
