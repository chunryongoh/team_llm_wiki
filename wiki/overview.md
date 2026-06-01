# Team LLM Wiki Overview

이 위키는 팀의 LLM-assisted 연구 기억, raw packet ingest 결과, 모델 실험, feature landscape, benchmark outcome을 사람이 리뷰할 수 있는 안정 synthesis layer로 유지한다. Raw evidence는 `raw/` 아래에 있고, `wiki/`는 review-aware automation과 LLM-assisted synthesis가 만든 팀 memory다.

## 현재 sleep-lifelog 작업 맥락

Sleep-lifelog 작업의 안정 entrypoint는 다음과 같다.

- Dataset: [Sleep Lifelog 2024 Dataset](datasets/sleep-lifelog-2024.md)
- Benchmark: [Sleep Health Hackathon Benchmark v0](benchmarks/sleep-health-hackathon-v0.md)
- Performance diagnostic: [LGB CB Reproduction Local OOF Diagnostic](performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic.md)
- Feature synthesis: [Sleep Lifelog Feature Landscape](features/sleep-lifelog-feature-landscape.md)
- Evaluation decision: [Sleep Lifelog Evaluation Protocol](decisions/sleep-lifelog-evaluation-protocol.md)
- Open questions: [Sleep Lifelog Open Questions](questions/sleep-lifelog-open-questions.md)
- Packet synthesis report: [2026-06-01 Sleep Lifelog Packet Synthesis](reports/2026-06-01-sleep-lifelog-packet-synthesis.md)

## 최신 지원 claim

`2026-06-01-lgb-cb-reproduction-local-oof-diagnostic` packet은 `local_oof_diagnostic_only` boundary 안에서만 `supported` claim을 가진다. 지원되는 내용은 LGB/CB reproduction이 standalone 우위가 아니라 Q2에 `0.1` 가중치로 들어간 source-diversity 보강이며, Wave41 local OOF line을 `grouped_macro_log_loss` `0.6198684545582471`에서 `0.6198365213240887`로 미세 개선했다는 것이다.

이 claim은 DACON public leaderboard, private leaderboard, organizer-official validation claim으로 승격되지 않는다. 평가 경계는 [Sleep Lifelog Evaluation Protocol](decisions/sleep-lifelog-evaluation-protocol.md)과 [DACON Leaderboard and Local OOF Claim Boundary](sources/2026-06-01-dacon-leaderboard-claim-boundary.md)를 따른다.

## 운영 원칙

- `raw/`는 append-only source evidence다.
- `wiki/`는 packet mirror가 아니라 안정 entity page와 topic page를 중심으로 유지한다.
- 성능, feature, model ranking claim은 raw metric, split, claim boundary가 있어야 한다.
- LLM-assisted synthesis 결과는 review-required로 취급한다.

## Raw Evidence

raw_evidence:
- raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/manifest.yaml
- raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/blend_weights.json
- raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/final_reblend_summary.json
- raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/leakage_audit.json
- raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/metrics.json
- raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/packet.md
- raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/performance.yaml
