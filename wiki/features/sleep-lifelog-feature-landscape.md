---
id: sleep-lifelog-feature-landscape
type: feature-landscape
title: Sleep Lifelog Feature Landscape
dataset: sleep-lifelog-2024
benchmark: sleep-health-hackathon-v0
status: active-review-required
last_updated: 2026-06-01
summary: >-
  sleep-lifelog feature memory는 feature family를 성능 claim과 분리해 기록하며, 현재 packet이 지원하는 내용은 LGB/CB reproduction의 transductive statistics, global imputer, subject encoding, date/rolling alignment risk, timing_entropy 제외 사실이다.
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

# Sleep Lifelog Feature Landscape

이 페이지는 [Sleep Lifelog 2024 Dataset](../datasets/sleep-lifelog-2024.md)와 [Sleep Health Hackathon Benchmark v0](../benchmarks/sleep-health-hackathon-v0.md)에서 반복해서 등장하는 feature family와 위험을 누적하는 안정 topic page다. 현재 주요 provenance는 [LGB CB Reproduction Local OOF Diagnostic](../performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic.md) packet `2026-06-01-lgb-cb-reproduction-local-oof-diagnostic`이다.

## 현재 evidence boundary

이 페이지는 feature가 유용하다는 leaderboard claim을 만들지 않는다. 현재 raw evidence가 직접 지원하는 것은 다음뿐이다.

- LGB/CB reproduction은 `feature_mode` `saved_output_reproduction`으로 기록되었다.
- `feature_statistics_scope`는 `train_test_transductive_notebook_reproduction`으로 문서화되었다.
- `SimpleImputer(strategy='median')`는 grouped OOF 전에 전체 training rows에 fit되어 `documented_not_fold_safe`로 기록되었다.
- subject target encoding columns `Q1_subj_enc`, `Q2_subj_enc`, `Q3_subj_enc`, `S1_subj_enc`, `S2_subj_enc`, `S3_subj_enc`, `S4_subj_enc`가 존재한다.
- `timing_entropy`는 default에서 제외되었고 variant는 `source_with_timing_entropy`로 기록되었다.
- `date_and_rolling_alignment_requires_manual_review`가 known risk로 남아 있다.

## Feature family register

| family | raw status | 현재 해석 | 필요한 후속 검증 |
|---|---|---|---|
| Train/test transductive feature statistics | `documented_transductive_reproduction` | notebook reproduction의 일부로 존재하지만 local diagnostic boundary를 좁히는 위험이다. | train-only 또는 fold-only statistics로 바꾼 ablation |
| Global train median imputer | `documented_not_fold_safe` | grouped OOF 전에 전체 train median을 쓰므로 fold-safe OOF claim에는 부적합할 수 있다. | fold별 imputer fit으로 재실험 |
| Subject identity and subject target encoding | `present` | subject signal이 강할 수 있으나 target encoding leakage와 generalization risk가 있다. | OOF train-fold means 정책 검증, subject feature 제거/대체 ablation |
| Date and rolling alignment | `requires_manual_review` | 시계열 정렬이 target 이후 정보를 쓰지 않는지 확인해야 한다. | feature generation audit와 fold-aware alignment test |
| `timing_entropy` | `excluded_from_default` | default result에는 들어가지 않았다. | 안전한 variant 조건과 metric 비교 |
| LGB/CB source diversity | Q2 reblend에서만 사용 | feature라기보다 model output diversity이며 Q2에만 작은 OOF 이득이 관측되었다. | Q2 nested weight search와 seed/fold stability |

## 성능 페이지와의 관계

[LGB CB Reproduction Local OOF Diagnostic](../performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic.md)의 지원 claim은 LGB/CB feature set이 전반적으로 우수하다는 뜻이 아니다. raw `metrics.json` 기준 standalone LightGBM, CatBoost, fixed LGB/CB blend는 Wave41 maintained line보다 macro log-loss가 높다. feature 관점의 현재 결론은 Q2에 한해 model output diversity가 아주 작은 local OOF 개선을 만들었다는 것이다.

## 평가 결정과 open questions

Feature family를 leaderboard claim으로 승격하려면 [Sleep Lifelog Evaluation Protocol](../decisions/sleep-lifelog-evaluation-protocol.md)의 claim boundary를 따라야 한다. 미해결 검증은 [Sleep Lifelog Open Questions](../questions/sleep-lifelog-open-questions.md)의 `sleep-lifelog-oq-001`, `sleep-lifelog-oq-004`, `sleep-lifelog-oq-006`에서 추적한다.

## Provenance

- packet id: `2026-06-01-lgb-cb-reproduction-local-oof-diagnostic`
- raw packet root: `raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/`
- raw evidence: `leakage_audit.json`, `performance.yaml`, `packet.md`, `metrics.json`, `final_reblend_summary.json`, `blend_weights.json`
- synthesis report: [2026-06-01 Sleep Lifelog Packet Synthesis](../reports/2026-06-01-sleep-lifelog-packet-synthesis.md)
