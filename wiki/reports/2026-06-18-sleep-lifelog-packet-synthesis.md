# 2026-06-18 Sleep Lifelog Packet Synthesis Report

이 보고서는 2026-06-18 Wave41 LGB/CB Foldsafe Synthesis smoke local OOF diagnostic packet의 ingest 결과를 요약한다.

## 주요 내용
- Foldsafe Synthesis smoke local OOF diagnostic 결과는 기존 reproduction 결과와 거의 동일한 grouped_macro_log_loss(0.6198365213240887)를 기록.
- split policy 및 leakage policy는 canonical-split-and-leakage-policy를 준수함.
- DACON leaderboard에는 제출되지 않았으며, local OOF evidence만으로 claim status는 supported로 유지됨.

## claim registry
- 기존 local OOF claim이 supported로 유지됨 ([Current Supported Claims](../claims/current-supported-claims.md)).

## open questions
- 해당 모델이 DACON leaderboard에 제출되어 private score가 확인될 때까지 검증 필요 ([sleep-lifelog-open-issues](../targets/sleep-lifelog-open-issues.md)).

## cross-link
- [Canonical Split And Leakage Policy](../preprocessing/canonical-split-and-leakage-policy.md)
- [DACON Leaderboard History](../performance/dacon-leaderboard-history.md)
- [Current Supported Claims](../claims/current-supported-claims.md)

## next actions
- leaderboard 제출 evidence 확보 시 claim status update 필요.

---

본 synthesis report는 smoke local OOF diagnostic 결과를 기록하며, 추가 evidence가 확보될 때 claim boundary 및 registry를 업데이트한다.

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
