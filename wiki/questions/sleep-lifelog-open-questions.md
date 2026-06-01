---
id: sleep-lifelog-open-questions
type: questions
status: open
summary: Sleep Lifelog 2024 및 DACON/ETRI reporting에서 claim promotion을 막고 있는 official rule, submission metadata, local split provenance, feature provenance 질문을 추적한다.
related_dataset: wiki/datasets/sleep-lifelog-2024.md
related_benchmark: wiki/benchmarks/sleep-health-hackathon-v0.md
related_source: wiki/sources/2026-06-01-dacon-leaderboard-claim-boundary.md
related_decision: wiki/decisions/sleep-lifelog-evaluation-protocol.md
related_features: wiki/features/sleep-lifelog-feature-landscape.md
raw_evidence:
- raw/users/chunryongoh/references/2026-06-01-dacon-leaderboard-claim-boundary/manifest.yaml
- raw/users/chunryongoh/references/2026-06-01-dacon-leaderboard-claim-boundary/notes.md
- raw/users/chunryongoh/references/2026-06-01-dacon-leaderboard-claim-boundary/packet.md
---

# Sleep Lifelog Open Questions

이 page는 [DACON Leaderboard and Local OOF Claim Boundary](../sources/2026-06-01-dacon-leaderboard-claim-boundary.md)에서 나온 unresolved question을 actionable backlog로 관리한다. 현재 모든 관련 claim은 `tentative`이며, 아래 질문들은 [Sleep Lifelog Evaluation Protocol](../decisions/sleep-lifelog-evaluation-protocol.md)과 [Sleep Lifelog Feature Landscape](../features/sleep-lifelog-feature-landscape.md)의 claim promotion 조건이다.

## Backlog

### sleep-lifelog-oq-001

- question: DACON/ETRI organizer-official split protocol과 public/private leaderboard 해석 규칙은 무엇이며, 현재 팀 reporting convention을 supersede해야 하는가?
- priority: `high`
- owner_role: `competition-lead`
- merge_blocker: `false`
- needed_evidence: DACON/ETRI 공식 규칙 문서, private leaderboard 공지, organizer가 명시한 validation/leaderboard interpretation 문장, 해당 원문 링크 또는 raw packet.
- close_condition: 공식 근거가 wiki source로 등록되고 `wiki/decisions/sleep-lifelog-evaluation-protocol.md`의 supersession 문구와 claim_status가 재검토되면 종료한다.

### sleep-lifelog-oq-002

- question: DACON public/private submission row를 local OOF run과 연결하기 위한 최소 submission metadata schema는 무엇인가?
- priority: `high`
- owner_role: `mlops-engineer`
- merge_blocker: `false`
- needed_evidence: `submission_id`, timestamp, target configuration, preprocessing version, `feature_set_id`, `model_family`, local run id, fold/seed, public/private score를 포함한 원시 submission log 또는 schema packet.
- close_condition: 필수 metadata 필드가 decision page와 feature landscape에 반영되고, 누락 시 leaderboard claim을 금지하는 검증 기준이 정리되면 종료한다.

### sleep-lifelog-oq-003

- question: `local-groupkfold-subject-3fold-oof-vs-dacon-public-private`에서 사용한 `subject_id` group key, fold file, seed, metric 계산 방식은 raw evidence로 고정되어 있는가?
- priority: `high`
- owner_role: `data-scientist`
- merge_blocker: `false`
- needed_evidence: fold assignment file, split generation code/config, group key 정의, metric 계산 script 또는 raw packet, OOF row와 run id 매핑.
- close_condition: local OOF evidence가 재현 가능한 split/metric provenance를 갖추고, local claim과 DACON leaderboard claim의 경계가 검증 가능해지면 종료한다.

### sleep-lifelog-oq-004

- question: feature set, preprocessing, target configuration 변경이 DACON public leaderboard feedback 해석에 미치는 영향을 어떻게 기록할 것인가?
- priority: `medium`
- owner_role: `feature-engineer`
- merge_blocker: `false`
- needed_evidence: `feature_set_id`/version, preprocessing config hash, target column/config, `model_family`, submission timestamp를 포함한 feature provenance template 또는 실제 submission example.
- close_condition: `wiki/features/sleep-lifelog-feature-landscape.md`에 feature provenance template이 확정되고, 이후 submission packet이 같은 필드를 채우면 종료한다.

## Review Note

`merge_blocker: false`는 이 tentative wiki integration PR을 막지 않는다는 뜻이다. 다만 위 질문들이 닫히기 전에는 local OOF, DACON public leaderboard, DACON private leaderboard 사이의 claim promotion은 하면 안 된다.
