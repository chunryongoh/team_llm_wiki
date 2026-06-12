---
id: 2026-06-01-lgb-cb-reproduction-local-oof-diagnostic
packet_type: performance
type: performance
title: LGB CB Reproduction Local OOF Diagnostic
date: 2026-06-01
owner: chunryongoh
status: submitted
task: dacon-sleep-lgb-cb-reproduction-local-oof
dataset:
  name: sleep-lifelog-2024
  version: released-package
  hash: none
benchmark: sleep-health-hackathon-v0
split:
  name: local-groupkfold-subject-5fold-oof
  group_key: subject_id
  fold_file: null
model:
  family: lightgbm-catboost-targetwise-reblend
  weights_in_repo: false
claim_boundary: local_oof_diagnostic_only
claim_status: supported
summary: >-
  LGB/CB reproduction은 standalone 우위가 아니라 Q2에만 0.1 가중치로 들어간 source-diversity 보강이며, Wave41 local OOF line을 macro log-loss 0.6198684545582471에서 0.6198365213240887로 미세 개선했다.
raw_packet_root: raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic
raw_paths:
  - blend_weights.json
  - final_reblend_summary.json
  - leakage_audit.json
  - metrics.json
  - packet.md
  - performance.yaml
source_refs:
  - ETRI/wiki/experiments/2026-05-26-lgb-cb-reproduction-audit-v1.md
  - ETRI/raw/results/2026-05-26-lgb-cb-reproduction-audit-v1/metrics.json
  - ETRI/raw/results/2026-05-26-lgb-cb-reproduction-audit-v1-current-line-targetwise-reblend-min0-v1/summary.json
  - ETRI/raw/results/2026-05-26-lgb-cb-reproduction-audit-v1-current-line-targetwise-reblend-min0-v1/predictions/blend_weights.json
  - ETRI/raw/results/2026-05-26-lgb-cb-reproduction-audit-v1/diagnostics/leakage_audit.json
metrics_to_verify:
  - raw_path: metrics.json
    metric_key: targetwise_reblend_macro_log_loss
    reported_value: 0.6198365213240887
  - raw_path: metrics.json
    metric_key: baseline_wave41_macro_log_loss
    reported_value: 0.6198684545582471
  - raw_path: metrics.json
    metric_key: delta_vs_wave41
    reported_value: -3.19332341584e-05
  - raw_path: metrics.json
    metric_key: lightgbm_macro_log_loss
    reported_value: 0.6657586405095428
  - raw_path: metrics.json
    metric_key: catboost_macro_log_loss
    reported_value: 0.6538557592728997
  - raw_path: metrics.json
    metric_key: fixed_lgb_cb_blend_macro_log_loss
    reported_value: 0.6536839393073466
  - raw_path: metrics.json
    metric_key: macro_f1
    reported_value: 0.7405528941404763
  - raw_path: metrics.json
    metric_key: macro_roc_auc
    reported_value: 0.6796841416960083
  - raw_path: metrics.json
    metric_key: macro_brier_score
    reported_value: 0.21542505839915055
claims:
  - status: supported
    text: >-
      지원되는 local OOF diagnostic: LGB/CB reproduction은 단독 우위가 아니라 Q2에 0.1 가중치로 섞였을 때 Wave41 maintained line을 macro log-loss 0.6198365213240887까지 아주 작게 개선했다.
publish_action: bot_pr
risk_tier: tier4-governance
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

# LGB CB Reproduction Local OOF Diagnostic

이 페이지는 packet `2026-06-01-lgb-cb-reproduction-local-oof-diagnostic`의 안정 성능 진단 페이지다. 관련 안정 페이지는 [Sleep Lifelog 2024 Dataset](../preprocessing/sleep-lifelog-2024.md), [Sleep Health Hackathon Benchmark v0](sleep-health-hackathon-evaluation-policy.md), [Sleep Lifelog Feature Landscape](../features/sleep-lifelog-feature-landscape.md), [Sleep Lifelog Evaluation Protocol](../decisions/sleep-lifelog-evaluation-protocol.md), [Sleep Lifelog Open Questions](../targets/sleep-lifelog-open-issues.md), [2026-06-01 Sleep Lifelog Packet Synthesis](../reports/2026-06-01-sleep-lifelog-packet-synthesis.md)이다. leaderboard claim boundary는 [DACON Leaderboard and Local OOF Claim Boundary](2026-06-01-dacon-leaderboard-claim-boundary.md)를 함께 확인해야 한다.

## 판정 요약

현재 raw evidence로 지원되는 claim은 좁다. LGB/CB reproduction은 standalone 모델로 Wave41 line을 이긴 것이 아니라, `target_wise_greedy` reblend에서 Q2에만 fixed LGB/CB blend를 `0.1` 넣어 Wave41 maintained local OOF line을 아주 작게 개선했다. 이 개선은 `local-groupkfold-subject-5fold-oof`의 diagnostic이며, DACON public leaderboard, private leaderboard, organizer-official validation claim으로 승격하지 않는다.

- packet id: `2026-06-01-lgb-cb-reproduction-local-oof-diagnostic`
- generated_by_run: `26741704818-1`
- owner: `chunryongoh`
- dataset: `sleep-lifelog-2024` `released-package`
- benchmark context: `sleep-health-hackathon-v0`
- split: `local-groupkfold-subject-5fold-oof`, group key `subject_id`, `5` folds
- primary metric: `grouped_macro_log_loss`, lower is better
- claim_boundary: `local_oof_diagnostic_only`
- claim_status: `supported`
- review-required: true

## Raw metric evidence

| metric_key | value | raw_path | 해석 |
|---|---:|---|---|
| `targetwise_reblend_macro_log_loss` | `0.6198365213240887` | `metrics.json` | 최종 targetwise reblend local OOF score |
| `baseline_wave41_macro_log_loss` | `0.6198684545582471` | `metrics.json` | 비교 기준 Wave41 maintained line |
| `delta_vs_wave41` | `-3.19332341584e-05` | `metrics.json` | log-loss 기준 미세 개선 |
| `lightgbm_macro_log_loss` | `0.6657586405095428` | `metrics.json` | standalone LightGBM은 Wave41보다 약함 |
| `catboost_macro_log_loss` | `0.6538557592728997` | `metrics.json` | standalone CatBoost는 Wave41보다 약함 |
| `fixed_lgb_cb_blend_macro_log_loss` | `0.6536839393073466` | `metrics.json` | fixed 0.5 LGB/CB blend도 Wave41보다 약함 |
| `macro_f1` | `0.7405528941404763` | `metrics.json`, `final_reblend_summary.json` | 보조 metric |
| `macro_roc_auc` | `0.6796841416960083` | `metrics.json`, `final_reblend_summary.json` | 보조 metric |
| `macro_brier_score` | `0.21542505839915055` | `metrics.json`, `final_reblend_summary.json` | 보조 metric |

## Targetwise blend 구조

`final_reblend_summary.json`와 `blend_weights.json` 기준 최종 `blend_id`는 `lgb-cb-notebook-reproduction-v1-current-line-targetwise-reblend-min0`이다. 선택 후보는 `wave41-all-seed-plus-wave40-targetwise-reblend-min0`와 `lgb-cb-notebook-reproduction-v1-fixed-blend`이지만, 실제 target별 가중치는 대부분 Wave41 line을 그대로 유지한다.

| target | log_loss | selected_candidate_ids | weights | 비고 |
|---|---:|---|---|---|
| `Q1` | `0.6227600448650603` | `wave41-all-seed-plus-wave40-targetwise-reblend-min0` | Wave41 `1.0` | flat |
| `Q2` | `0.6556358809986518` | Wave41 + `lgb-cb-notebook-reproduction-v1-fixed-blend` | Wave41 `0.9`, LGB/CB fixed `0.1` | 유일한 LGB/CB 보강 target |
| `Q3` | `0.6309857415368405` | `wave41-all-seed-plus-wave40-targetwise-reblend-min0` | Wave41 `1.0` | flat |
| `S1` | `0.562996471228798` | `wave41-all-seed-plus-wave40-targetwise-reblend-min0` | Wave41 `1.0` | flat |
| `S2` | `0.6113857154018603` | `wave41-all-seed-plus-wave40-targetwise-reblend-min0` | Wave41 `1.0` | flat |
| `S3` | `0.595105227779678` | `wave41-all-seed-plus-wave40-targetwise-reblend-min0` | Wave41 `1.0` | flat |
| `S4` | `0.6599865674577321` | `wave41-all-seed-plus-wave40-targetwise-reblend-min0` | Wave41 `1.0` | flat |

`target_delta_summary`는 `improved_target_count`를 `1`, `flat_target_count`를 `6`, `worsened_target_count`를 `0`, `mean_delta_vs_best_source`를 `-3.193323415833544e-05`로 기록한다. 따라서 올바른 narrative는 Q2 source-diversity 보강이지 LGB/CB 전면 우위가 아니다.

## Leakage audit와 claim boundary

`leakage_audit.json`의 전체 상태는 `completed_with_known_risks`이다. `group_overlap`은 5 folds 모두 `overlap_count` `0`으로 `passed`지만, 다음 위험이 claim boundary를 제한한다.

- `feature_statistics_scope`: `train_test_transductive_notebook_reproduction`
- `imputer_scope`: `SimpleImputer(strategy='median') is fit on all training rows before grouped OOF`, status `documented_not_fold_safe`
- `subject_target_encoding`: `Q1_subj_enc`, `Q2_subj_enc`, `Q3_subj_enc`, `S1_subj_enc`, `S2_subj_enc`, `S3_subj_enc`, `S4_subj_enc` present
- `timing_entropy`: `excluded_from_default`, variant `source_with_timing_entropy`
- known risks: `train_test_transductive_feature_statistics`, `global_train_median_imputer_before_cv`, `subject_identity_and_target_encoding_features`, `date_and_rolling_alignment_requires_manual_review`

이 위험은 local diagnostic 기록 자체를 폐기하지 않지만, leaderboard claim 또는 official validation claim으로 확장하는 것을 막는다. 평가 정책은 [Sleep Lifelog Evaluation Protocol](../decisions/sleep-lifelog-evaluation-protocol.md)에 기록한다.

## Supersession and conflict notes

- `LGB/CB가 전체적으로 가장 강하다`는 넓은 claim은 현재 packet으로 지원되지 않는다.
- `LGB/CB blend가 모든 target을 개선한다`는 claim도 지원되지 않는다. Q2만 LGB/CB fixed blend `0.1`이 들어갔다.
- local OOF score는 DACON public/private leaderboard score가 아니다. leaderboard claim은 별도 raw provenance와 [DACON Leaderboard and Local OOF Claim Boundary](2026-06-01-dacon-leaderboard-claim-boundary.md)의 boundary를 따라야 한다.

## 다음 검증

후속 작업은 [Sleep Lifelog Open Questions](../targets/sleep-lifelog-open-issues.md)에 backlog로 관리한다. 우선순위가 높은 항목은 fold-safe feature ablation, Q2 blend-weight 재검증, date/rolling alignment audit이다.

## Provenance

- raw packet root: `raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/`
- raw files: `manifest.yaml`, `packet.md`, `performance.yaml`, `metrics.json`, `final_reblend_summary.json`, `blend_weights.json`, `leakage_audit.json`
- source refs: `ETRI/wiki/experiments/2026-05-26-lgb-cb-reproduction-audit-v1.md`, `ETRI/raw/results/2026-05-26-lgb-cb-reproduction-audit-v1/metrics.json`, `ETRI/raw/results/2026-05-26-lgb-cb-reproduction-audit-v1-current-line-targetwise-reblend-min0-v1/summary.json`, `ETRI/raw/results/2026-05-26-lgb-cb-reproduction-audit-v1-current-line-targetwise-reblend-min0-v1/predictions/blend_weights.json`, `ETRI/raw/results/2026-05-26-lgb-cb-reproduction-audit-v1/diagnostics/leakage_audit.json`
