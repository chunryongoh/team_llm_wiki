---
id: sleep-lifelog-evaluation-protocol
type: decision
title: Sleep Lifelog Evaluation Protocol
status: active-review-required
date: 2026-06-01
dataset: sleep-lifelog-2024
benchmark: sleep-health-hackathon-v0
summary: >-
  sleep-lifelog 평가는 local OOF diagnostic, DACON leaderboard, organizer-official validation claim을 분리하며, leakage risk가 문서화된 packet은 `local_oof_diagnostic_only` boundary를 넘지 않는다.
review_required: true
raw_evidence:
- raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/manifest.yaml
- raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/blend_weights.json
- raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/final_reblend_summary.json
- raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/leakage_audit.json
- raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/metrics.json
- raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/packet.md
- raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/performance.yaml
---

# Sleep Lifelog Evaluation Protocol

## 결정

Sleep-lifelog 작업에서는 성능 claim을 세 등급으로 분리한다.

1. `local_oof_diagnostic_only`: 팀 내부 split과 metric으로 계산한 diagnostic claim이다. 현재 [LGB CB Reproduction Local OOF Diagnostic](../performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic.md)이 여기에 속한다.
2. DACON public/private leaderboard claim: 제출 id, public/private score, 제출 파일 lineage가 raw provenance로 있어야 한다. 관련 boundary source는 [DACON Leaderboard and Local OOF Claim Boundary](../sources/2026-06-01-dacon-leaderboard-claim-boundary.md)를 따른다.
3. organizer-official validation claim: 주최 측 공식 split 또는 공식 평가 결과가 raw evidence로 있어야 한다.

`local_oof_diagnostic_only` claim은 raw metric과 split이 검증되어도 leaderboard 또는 official validation claim으로 자동 승격하지 않는다.

## 현재 적용 사례

`2026-06-01-lgb-cb-reproduction-local-oof-diagnostic` packet은 다음 조건 때문에 local diagnostic으로 유지된다.

- split: `local-groupkfold-subject-5fold-oof`
- group key: `subject_id`
- primary metric: `grouped_macro_log_loss`, lower is better
- supported metric: `targetwise_reblend_macro_log_loss` `0.6198365213240887`
- baseline: `baseline_wave41_macro_log_loss` `0.6198684545582471`
- delta: `delta_vs_wave41` `-3.19332341584e-05`
- claim boundary: `local_oof_diagnostic_only`
- leakage audit status: `completed_with_known_risks`

따라서 지원되는 결론은 Q2에 LGB/CB fixed blend `0.1`을 섞은 targetwise reblend가 Wave41 maintained local OOF line을 아주 작게 개선했다는 것이다. standalone LGB/CB 우위, 모든 target 개선, leaderboard 우위는 현재 결정 범위 밖이다.

## Metric and split rules

- Local OOF 성능은 split name, group key, fold count, metric definition을 함께 기록해야 한다.
- `grouped_macro_log_loss`는 `Q1`, `Q2`, `Q3`, `S1`, `S2`, `S3`, `S4` target log-loss 평균으로 기록한다.
- log-loss 계열은 lower is better를 명시한다.
- 보조 metric인 `macro_f1`, `macro_roc_auc`, `macro_brier_score`는 primary claim을 대체하지 않는다.
- seed/fold uncertainty가 없으면 작은 delta의 안정성을 claim하지 않는다.

## Leakage and feature-scope rules

다음이 남아 있으면 claim boundary를 좁힌다.

- train+test transductive feature statistics
- grouped OOF 전에 fit된 global train median imputer
- subject identity 또는 subject target encoding feature
- date/rolling alignment manual review 미완료
- default에서 제외된 variant를 근거 없이 포함하는 것

Feature risk와 후속 검증은 [Sleep Lifelog Feature Landscape](../features/sleep-lifelog-feature-landscape.md)와 [Sleep Lifelog Open Questions](../questions/sleep-lifelog-open-questions.md)에 연결한다.

## Promotion gate

Local diagnostic을 더 강한 claim으로 승격하려면 다음 raw evidence가 필요하다.

- leaderboard claim: DACON submission id, public/private score, 제출 파일 lineage, local run id mapping
- official validation claim: organizer-official split 또는 result artifact
- fold-safe claim: fold별 preprocessing fit, target encoding policy, feature alignment audit, raw metrics
- robust small-delta claim: multi-seed 또는 repeated split stability와 uncertainty interval

## Review checklist

- claim_status가 raw packet의 status와 일치하는가?
- metric value가 raw `metrics.json` 또는 packet-specific YAML과 일치하는가?
- split과 group key가 성능 claim 옆에 있는가?
- leakage audit의 known risks가 숨겨지지 않았는가?
- leaderboard나 official validation으로 암묵 승격하지 않았는가?

## Provenance

- dataset: [Sleep Lifelog 2024 Dataset](../datasets/sleep-lifelog-2024.md)
- benchmark: [Sleep Health Hackathon Benchmark v0](../benchmarks/sleep-health-hackathon-v0.md)
- performance packet: [LGB CB Reproduction Local OOF Diagnostic](../performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic.md)
- synthesis report: [2026-06-01 Sleep Lifelog Packet Synthesis](../reports/2026-06-01-sleep-lifelog-packet-synthesis.md)
