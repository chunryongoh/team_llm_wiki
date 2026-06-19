# 2026-06-18 Sleep Lifelog Packet Synthesis

2026-06-18 Wave41 LGB/CB Foldsafe Synthesis smoke local OOF diagnostic 결과를 기반으로 최신 packet ingest 및 synthesis를 기록한다.

## 주요 내용
- Wave41 LGB/CB Foldsafe Synthesis smoke local OOF diagnostic 결과: grouped_macro_log_loss 0.6198365213240887
- 기존 local_oof_diagnostic_only claim을 미세하게 개선
- DACON leaderboard, organizer validation, local OOF, notebook output은 분리 관리

## 증거 및 claim 경계
- [Performance leaf](../performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic.md)에서 상세 metric 및 claim 경계 확인 가능
- [Claim registry](../claims/current-supported-claims.md)에서 supported claim 상태 유지

## 관련 페이지
- [DACON Leaderboard History](../performance/dacon-leaderboard-history.md)
- [Canonical Split And Leakage Policy](../preprocessing/canonical-split-and-leakage-policy.md)
- [Sleep Lifelog Feature Landscape](../features/sleep-lifelog-feature-landscape.md)
- [Sleep Lifelog Evaluation Protocol](../decisions/sleep-lifelog-evaluation-protocol.md)
- [Sleep Lifelog Open Questions](../targets/sleep-lifelog-open-issues.md)

## 다음 액션
- DACON leaderboard 및 organizer validation raw evidence 확보 필요
- open questions backlog 관리

---
- packet id: 2026-06-19-packet-scan
- schema version: packet-graph-v1.0

## Raw Evidence

raw_evidence:
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/manifest.yaml
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/artifact_summary.json
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/metrics.json
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/packet.md
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/packet_entity_graph.json
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/performance.yaml
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/question_queue.yaml
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/semantic_lint.json
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/wiki_plan.yaml
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/source_note.md
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/source_artifacts/suite_summary.json
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/source_artifacts/suite_metrics.json
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/source_artifacts/decision_matrix.csv
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/source_artifacts/candidate_status.csv
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/source_artifacts/fold_subjects.json
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/source_artifacts/suite_plan.json
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/source_artifacts/optuna_trials.csv
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/source_artifacts/targetwise_reblend_summary.json
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/source_artifacts/blend_weights.json
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/source_artifacts/target_deltas.json
