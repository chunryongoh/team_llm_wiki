---
id: 2026-06-01-lgb-cb-reproduction-local-oof-diagnostic
packet_type: performance
type: performance
title: LGB CB Reproduction Local OOF Diagnostic
date: '2026-06-01'
owner: chunryongoh
status: submitted
task: dacon-sleep-lgb-cb-reproduction-local-oof
dataset:
  name: sleep-lifelog-2024
  version: released-package
  hash: none
split:
  name: local-groupkfold-subject-5fold-oof
  group_key: subject_id
  fold_file: null
model:
  family: lightgbm-catboost-targetwise-reblend
  weights_in_repo: false
claim_boundary: local_oof_diagnostic_only
claim_status: supported
summary: "LGB/CB reproduction\uC740 standalone \uBAA8\uB378 \uAC1C\uC120\uC774 \uC544\
  \uB2C8\uB77C Q2\uC5D0\uB9CC 0.1 \uAC00\uC911\uCE58\uB85C \uB4E4\uC5B4\uAC00\uB294\
  \ source-diversity \uBCF4\uAC15\uC73C\uB85C Wave41 local OOF line\uC744 macro log-loss\
  \ 0.6198365213240887\uAE4C\uC9C0 \uBBF8\uC138 \uAC1C\uC120\uD588\uB2E4."
raw_paths:
- blend_weights.json
- final_reblend_summary.json
- leakage_audit.json
- metrics.json
- packet.md
- performance.yaml
intended_wiki_targets:
- wiki/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic.md
metrics_to_verify:
- raw_path: metrics.json
  metric_key: targetwise_reblend_macro_log_loss
  reported_value: 0.6198365213240887
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: baseline_wave41_macro_log_loss
  reported_value: 0.6198684545582471
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: delta_vs_wave41
  reported_value: -3.19332341584e-05
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: lightgbm_macro_log_loss
  reported_value: 0.6657586405095428
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: catboost_macro_log_loss
  reported_value: 0.6538557592728997
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: fixed_lgb_cb_blend_macro_log_loss
  reported_value: 0.6536839393073466
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: macro_f1
  reported_value: 0.7405528941404763
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: macro_roc_auc
  reported_value: 0.6796841416960083
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: macro_brier_score
  reported_value: 0.21542505839915055
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
claims:
- status: supported
  text: "\uC9C0\uC6D0\uB418\uB294 local OOF diagnostic: LGB/CB reproduction\uC740\
    \ \uB2E8\uB3C5 \uC6B0\uC704\uAC00 \uC544\uB2C8\uB77C Q2\uC5D0 0.1 \uAC00\uC911\
    \uCE58\uB85C \uC11E\uC600\uC744 \uB54C Wave41 maintained line\uC744 macro log-loss\
    \ 0.6198365213240887\uAE4C\uC9C0 \uC544\uC8FC \uC791\uAC8C \uAC1C\uC120\uD588\uB2E4\
    ."
publish_action: bot_pr
risk_tier: tier4-governance
---

# LGB CB Reproduction Local OOF Diagnostic

- packet: `2026-06-01-lgb-cb-reproduction-local-oof-diagnostic`
- generated_by_run: `26741704818-1`
- publish_action: `bot_pr`
- risk_tier: `tier4-governance`
- compiled_packet: [automation/.cache/compiled/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic.json](../../automation/.cache/compiled/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic.json)
- owner: `chunryongoh`
- status: `submitted`
- task: `dacon-sleep-lgb-cb-reproduction-local-oof`
- dataset: `sleep-lifelog-2024` (`released-package`)
- split: `local-groupkfold-subject-5fold-oof`
- model: `lightgbm-catboost-targetwise-reblend`
- claim_boundary: local_oof_diagnostic_only
- claim_status: `supported`
- date: `2026-06-01`
- raw_evidence:
  - `blend_weights.json`
  - `final_reblend_summary.json`
  - `leakage_audit.json`
  - `metrics.json`
  - `packet.md`
  - `performance.yaml`
- review-required: true

## Summary

LGB/CB reproduction은 standalone 모델 개선이 아니라 Q2에만 0.1 가중치로 들어가는 source-diversity 보강으로 Wave41 local OOF line을 macro log-loss 0.6198365213240887까지 미세 개선했다.

## Packet Synthesis

# LGB/CB reproduction local OOF diagnostic

## 관측된 사실

- 이 packet은 DACON sleep-lifelog 2024 작업 중 `2026-05-26-lgb-cb-reproduction-audit-v1` 결과를 팀 위키에 올리기 위한 local OOF diagnostic이다.
- audit은 LightGBM, CatBoost, fixed 0.5 LGB/CB blend, 그리고 Wave41 maintained local OOF line과의 targetwise reblend를 비교했다.
- 최종 targetwise reblend macro log-loss는 local GroupKFold subject OOF에서 `0.6198365213240887`이다.
- 비교 기준인 Wave41 macro log-loss는 `0.6198684545582471`이며, delta는 `-0.0000319332341584`이다. Log-loss 기준으로 낮을수록 좋다.
- Standalone LightGBM은 `0.6657586405095428`, standalone CatBoost는 `0.6538557592728997`, fixed LGB/CB blend는 `0.6536839393073466`으로 Wave41 line보다 약했다.
- 최종 reblend에서 LGB/CB fixed blend는 Q2에만 `0.1` 가중치로 들어갔고, 나머지 target은 Wave41 line을 유지했다.

## 해석

핵심은 "LGB/CB가 전체적으로 가장 강하다"가 아니다. 현재 evidence로 지원되는 claim은 더 좁다. 재현된 fixed LGB/CB blend는 단독 성능으로 Wave41 line을 이기지 못했지만, Q2에서 source diversity를 아주 작게 보강해 maintained Wave41 local OOF line을 미세하게 개선했다.

## claim boundary와 위험

이 packet의 claim boundary는 `local_oof_diagnostic_only`이다. DACON public leaderboard, private leaderboard, organizer-official validation claim으로 승격하지 않는다.

leakage audit에는 다음 위험이 기록되어 있다.

- notebook reproduction 과정의 train+test transductive feature statistics
- grouped OOF 전에 적용된 global train median imputer
- subject identity 및 target encoding 계열 feature
- date/rolling alignment의 manual review 필요성

이 위험들은 local diagnostic 기록 자체를 폐기하는 근거는 아니지만, public/private leaderboard나 official validation claim으로 확장하는 것을 막는다.

## 다음 액션

Q2 중심 후속 검증을 우선한다. subject stats, target encodings, imputer scope를 fold-safe하게 ablation하고, per-target LGB/CB blend-weight search를 별도로 수행한다. SHAP/manual feature selection은 fold-scope audit 이후에 진행한다.

## Metrics

raw-evidence-backed metric checks:
- `targetwise_reblend_macro_log_loss`: reported `0.6198365213240887`, raw_path `metrics.json`, tolerance `0.0`
- `baseline_wave41_macro_log_loss`: reported `0.6198684545582471`, raw_path `metrics.json`, tolerance `0.0`
- `delta_vs_wave41`: reported `-3.19332341584e-05`, raw_path `metrics.json`, tolerance `0.0`
- `lightgbm_macro_log_loss`: reported `0.6657586405095428`, raw_path `metrics.json`, tolerance `0.0`
- `catboost_macro_log_loss`: reported `0.6538557592728997`, raw_path `metrics.json`, tolerance `0.0`
- `fixed_lgb_cb_blend_macro_log_loss`: reported `0.6536839393073466`, raw_path `metrics.json`, tolerance `0.0`
- `macro_f1`: reported `0.7405528941404763`, raw_path `metrics.json`, tolerance `0.0`
- `macro_roc_auc`: reported `0.6796841416960083`, raw_path `metrics.json`, tolerance `0.0`
- `macro_brier_score`: reported `0.21542505839915055`, raw_path `metrics.json`, tolerance `0.0`

## Claims

- supported: 지원되는 local OOF diagnostic: LGB/CB reproduction은 단독 우위가 아니라 Q2에 0.1 가중치로 섞였을 때 Wave41 maintained line을 macro log-loss 0.6198365213240887까지 아주 작게 개선했다.
