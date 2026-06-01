---
id: 2026-06-01-dacon-leaderboard-claim-boundary
packet_type: reference
type: reference
title: DACON Leaderboard and Local OOF Claim Boundary
date: '2026-06-01'
owner: chunryongoh
status: submitted
task: dacon-sleep-health-reporting-policy
dataset:
  name: sleep-lifelog-2024
  version: released-package
  hash: null
split:
  name: local-groupkfold-subject-3fold-oof-vs-dacon-public-private
  group_key: subject_id
  fold_file: null
model:
  family: not-applicable
  weights_in_repo: false
claim_boundary: Team reporting convention for the DACON/ETRI sleep-health hackathon; not organizer-official split evidence.
claim_status: tentative
summary: DACON/ETRI sleep-health hackathon 결과 보고에서 local GroupKFold OOF, DACON public leaderboard, DACON private leaderboard를 분리해 기록해야 한다는 팀 reporting boundary를 정리한다.
raw_provenance:
  packet_id: 2026-06-01-dacon-leaderboard-claim-boundary
  packet_dir: raw/users/chunryongoh/references/2026-06-01-dacon-leaderboard-claim-boundary
  manifest: raw/users/chunryongoh/references/2026-06-01-dacon-leaderboard-claim-boundary/manifest.yaml
  notes: raw/users/chunryongoh/references/2026-06-01-dacon-leaderboard-claim-boundary/notes.md
  packet: raw/users/chunryongoh/references/2026-06-01-dacon-leaderboard-claim-boundary/packet.md
raw_paths:
  - notes.md
intended_wiki_targets:
  - wiki/sources/2026-06-01-dacon-leaderboard-claim-boundary.md
metrics_to_verify: []
claims:
  - status: tentative
    text: Local GroupKFold OOF metrics and DACON public/private leaderboard results should be recorded as separate evidence classes.
  - status: tentative
    text: DACON public leaderboard feedback should not automatically supersede local validation conclusions without matching submission metadata and private leaderboard evidence.
publish_action: direct_commit
risk_tier: tier0-catalog
generated_by_run: 26740055632-1
related_pages:
  - wiki/datasets/sleep-lifelog-2024.md
  - wiki/benchmarks/sleep-health-hackathon-v0.md
  - wiki/features/sleep-lifelog-feature-landscape.md
  - wiki/decisions/sleep-lifelog-evaluation-protocol.md
  - wiki/questions/sleep-lifelog-open-questions.md
  - wiki/reports/2026-06-01-sleep-lifelog-packet-synthesis.md
raw_evidence:
- raw/users/chunryongoh/references/2026-06-01-dacon-leaderboard-claim-boundary/manifest.yaml
- raw/users/chunryongoh/references/2026-06-01-dacon-leaderboard-claim-boundary/notes.md
- raw/users/chunryongoh/references/2026-06-01-dacon-leaderboard-claim-boundary/packet.md
---

# DACON Leaderboard and Local OOF Claim Boundary

이 page는 `2026-06-01-dacon-leaderboard-claim-boundary` packet의 source-level provenance와 claim boundary를 보존한다. 관련 dataset은 [Sleep Lifelog 2024 Dataset Definition](../datasets/sleep-lifelog-2024.md), 관련 benchmark는 [Sleep Health Hackathon Benchmark v0 Definition](../benchmarks/sleep-health-hackathon-v0.md)이다. 이 source에서 파생된 통합 page는 [Sleep Lifelog Feature Landscape](../features/sleep-lifelog-feature-landscape.md), [Sleep Lifelog Evaluation Protocol](../decisions/sleep-lifelog-evaluation-protocol.md), [Sleep Lifelog Open Questions](../questions/sleep-lifelog-open-questions.md), [2026-06-01 Sleep Lifelog Packet Synthesis](../reports/2026-06-01-sleep-lifelog-packet-synthesis.md)이다.

## Provenance

- packet_id: `2026-06-01-dacon-leaderboard-claim-boundary`
- generated_by_run: `26740055632-1`
- owner: `chunryongoh`
- status: `submitted`
- packet_type: `reference`
- publish_action: `direct_commit`
- risk_tier: `tier0-catalog`
- task: `dacon-sleep-health-reporting-policy`
- dataset: `sleep-lifelog-2024` / `released-package`
- split: `local-groupkfold-subject-3fold-oof-vs-dacon-public-private`
- group_key: `subject_id`
- model.family: `not-applicable`
- model.weights_in_repo: `false`
- metrics_to_verify: `[]`
- raw manifest: `raw/users/chunryongoh/references/2026-06-01-dacon-leaderboard-claim-boundary/manifest.yaml`
- raw notes: `raw/users/chunryongoh/references/2026-06-01-dacon-leaderboard-claim-boundary/notes.md`
- raw packet: `raw/users/chunryongoh/references/2026-06-01-dacon-leaderboard-claim-boundary/packet.md`

## Claim Boundary

원문 `claim_boundary`는 다음과 같다.

> Team reporting convention for the DACON/ETRI sleep-health hackathon; not organizer-official split evidence.

따라서 이 page는 organizer-official validation split, official leaderboard scoring rule, private leaderboard interpretation rule을 증명하지 않는다. 현재 값은 팀 내부 reporting convention이며 `claim_status: tentative`로 유지한다.

## Evidence Classes

이 packet이 구분하는 evidence class는 세 가지다.

1. `Local GroupKFold OOF metrics`: local validation evidence이다. raw split, fold file, group key, seed, metric script가 함께 있어야 재현 가능한 local claim이 된다.
2. `DACON public leaderboard results`: submission feedback이다. submission metadata, target configuration, preprocessing, feature set, model family, timestamp와 함께 기록해야 한다.
3. `DACON private leaderboard results`: private leaderboard가 공개되었을 때 final leaderboard evidence로 기록한다. local OOF row와 같은 row로 병합하지 않는다.

## Claims

| status | raw claim | Korean review note |
|---|---|---|
| `tentative` | Local GroupKFold OOF metrics and DACON public/private leaderboard results should be recorded as separate evidence classes. | local validation과 DACON leaderboard 결과를 같은 성능 claim으로 합치지 말아야 한다는 reporting rule이다. |
| `tentative` | DACON public leaderboard feedback should not automatically supersede local validation conclusions without matching submission metadata and private leaderboard evidence. | public leaderboard feedback만으로 local validation conclusion을 대체했다는 claim을 만들 수 없다. |

## Supersession Note

raw `notes.md`와 `packet.md`는 이 convention이 organizer-official rule이 아니라는 점을 명시한다. DACON 또는 ETRI organizer가 official split protocol, public/private leaderboard interpretation rule, private leaderboard evidence를 명시하면 그 근거가 이 page의 convention보다 우선한다. 그 경우 [Sleep Lifelog Evaluation Protocol](../decisions/sleep-lifelog-evaluation-protocol.md)과 [Sleep Lifelog Open Questions](../questions/sleep-lifelog-open-questions.md)를 함께 갱신해야 한다.
