---
id: sleep-lifelog-open-questions
type: open-questions
title: Sleep Lifelog Open Questions
status: active
last_updated: 2026-06-01
summary: >-
  sleep-lifelog 후속 backlog는 local OOF claim을 유지한 채 fold-safe ablation, Q2 blend 검증, leaderboard 매핑, date/rolling alignment audit, uncertainty 추정을 요구한다.
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

# Sleep Lifelog Open Questions

이 페이지는 [Sleep Lifelog 2024 Dataset](../datasets/sleep-lifelog-2024.md), [Sleep Health Hackathon Benchmark v0](../benchmarks/sleep-health-hackathon-v0.md), [LGB CB Reproduction Local OOF Diagnostic](../performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic.md), [Sleep Lifelog Feature Landscape](../features/sleep-lifelog-feature-landscape.md), [Sleep Lifelog Evaluation Protocol](../decisions/sleep-lifelog-evaluation-protocol.md)에 연결된 실행 가능한 backlog다.

## Backlog

| id | priority | owner_role | merge_blocker | question | needed_evidence | close_condition |
|---|---|---|---|---|---|---|
| `sleep-lifelog-oq-001` | `P0` | modeling lead | false | `train_test_transductive_notebook_reproduction`, `global_train_median_imputer_before_cv`, subject identity, subject target encoding feature를 fold-safe하게 바꾸거나 제거했을 때 `grouped_macro_log_loss`와 target별 metric이 어떻게 변하는가? | fold-safe ablation run id, split definition, per-target OOF predictions or metric summary, raw `metrics.json`, leakage audit update | 동일 `local-groupkfold-subject-5fold-oof` 또는 명시적으로 비교 가능한 split에서 ablation별 `grouped_macro_log_loss`와 target별 deltas가 raw packet으로 제출된다. |
| `sleep-lifelog-oq-002` | `P1` | modeling lead | false | Q2에서만 관측된 LGB/CB source-diversity 이득이 별도 weight search 또는 nested/fold-safe 절차에서도 유지되는가? | Q2 per-target blend-weight search log, candidate ids, validation protocol, OOF metric table, overfit 방지 설명 | Q2 weight 선택 절차와 metric이 raw evidence로 제출되고 현재 `0.1` weight 결과와 비교된다. |
| `sleep-lifelog-oq-003` | `P1` | benchmark owner | false | local OOF line과 DACON public/private leaderboard 제출 사이의 submission id, score, cutoff, model lineage가 어떻게 매핑되는가? | DACON submission ids, public/private scores, 제출 파일 lineage, local run ids, leaderboard claim boundary packet | leaderboard claim이 local OOF와 분리된 source 또는 benchmark page에 raw provenance와 함께 기록된다. |
| `sleep-lifelog-oq-004` | `P0` | feature owner | false | date/rolling alignment feature가 target leakage 없이 fold boundary와 subject boundary를 지키는가? | feature generation code review note, fold-aware alignment audit, target별 leakage check, 재현 가능한 raw audit artifact | date/rolling alignment audit이 통과 또는 제외 결정으로 문서화되고 feature landscape의 risk status가 갱신된다. |
| `sleep-lifelog-oq-005` | `P2` | evaluation owner | false | 현재 local OOF delta `-3.19332341584e-05`가 seed/fold 변동 대비 의미 있는가? | multi-seed 또는 repeated split 결과, confidence interval 또는 rank stability table, 동일 metric 정의 | seed/fold uncertainty interval이 raw packet으로 제출되어 현재 delta의 안정성이 판단된다. |
| `sleep-lifelog-oq-006` | `P2` | feature owner | false | `timing_entropy`가 default에서 제외된 이유와 안전한 variant 조건은 무엇인가? | `source_with_timing_entropy` variant metric, leakage audit, feature definition, inclusion/exclusion rationale | `timing_entropy` variant가 fold-safe audit과 metric evidence로 유지 또는 제외 결정된다. |

## 현재 merge와의 관계

위 질문들은 현재 synthesis PR의 merge blocker가 아니다. 이유는 이번 PR이 claim을 승격하지 않고, raw evidence가 지원하는 `local_oof_diagnostic_only` boundary를 보존하기 때문이다. 단, 위 질문들이 닫히기 전에는 [Sleep Lifelog Evaluation Protocol](../decisions/sleep-lifelog-evaluation-protocol.md)에 따라 leaderboard, official validation, robust small-delta claim으로 승격할 수 없다.

## Provenance

- packet id: `2026-06-01-lgb-cb-reproduction-local-oof-diagnostic`
- raw evidence: `packet.md`, `performance.yaml`, `metrics.json`, `final_reblend_summary.json`, `blend_weights.json`, `leakage_audit.json`
- synthesis report: [2026-06-01 Sleep Lifelog Packet Synthesis](../reports/2026-06-01-sleep-lifelog-packet-synthesis.md)
