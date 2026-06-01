# Team LLM Wiki Overview

이 wiki는 team LLM experiments, sources, model notes, feature work, benchmark outcomes를 위한 유지보수형 synthesis layer이다. raw evidence는 `raw/` 아래에 append-only로 남기고, `wiki/`는 review-aware automation과 LLM-assisted synthesis를 통해 팀이 다시 사용할 수 있는 stable memory로 정리한다.

## 현재 Sleep Lifelog / DACON-ETRI 작업 축

- dataset: [Sleep Lifelog 2024 Dataset Definition](datasets/sleep-lifelog-2024.md)
- benchmark: [Sleep Health Hackathon Benchmark v0 Definition](benchmarks/sleep-health-hackathon-v0.md)
- source boundary: [DACON Leaderboard and Local OOF Claim Boundary](sources/2026-06-01-dacon-leaderboard-claim-boundary.md)
- feature synthesis: [Sleep Lifelog Feature Landscape](features/sleep-lifelog-feature-landscape.md)
- evaluation decision: [Sleep Lifelog Evaluation Protocol](decisions/sleep-lifelog-evaluation-protocol.md)
- open questions: [Sleep Lifelog Open Questions](questions/sleep-lifelog-open-questions.md)
- synthesis report: [2026-06-01 Sleep Lifelog Packet Synthesis](reports/2026-06-01-sleep-lifelog-packet-synthesis.md)

## Claim Policy Reminder

local OOF metric, DACON public leaderboard feedback, DACON private leaderboard result는 서로 다른 evidence class로 기록한다. raw metric, split, submission metadata, private leaderboard evidence가 명시되지 않은 상태에서는 성능 claim이나 leaderboard claim을 supported로 승격하지 않는다.

## Raw Evidence

raw_evidence:
- raw/users/chunryongoh/references/2026-06-01-dacon-leaderboard-claim-boundary/manifest.yaml
- raw/users/chunryongoh/references/2026-06-01-dacon-leaderboard-claim-boundary/notes.md
- raw/users/chunryongoh/references/2026-06-01-dacon-leaderboard-claim-boundary/packet.md
