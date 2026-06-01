# 04. Performance

작성일: 2026-05-29
담당자: 팀 공용
상태: draft
관련 폴더: `Y2025LifeLogDB/version_registry/reports/`, `Y2025LifeLogDB/experiments/260519_recovered_feature_model_v1/reports/`
관련 산출물: `weekly_progress_20260521_20260529_ko_short.md`, `section07_retrain_challenger_summary.md`, `section07_v5_feature_probe_summary.csv`

## 핵심 요약

현재 public best는 `section9_labelwise_best_20260522_1239.csv`이며 public score는 `0.5986218188`이다.
07에서 Section4 방식으로 다시 학습한 seed ensemble 후보는 `0.6003735255`로 근접했지만 아직 best를 넘지는 못했다.

## 현재 기준

- 현재 best submission:
  - `submission/20260522_1239/section9_labelwise_best_20260522_1239.csv`
- 현재 best public score:
  - `0.5986218188`
- 최신 near-best challenger:
  - `submission/20260529_1029/section07_candidate_baseline_seed_ensemble_20260529_1029.csv`
- near-best public score:
  - `0.6003735255`
- 07 v5 probe 결과:
  - v5 full acceptance: `false`
  - Q3는 v5 change/frequency 추가 시 current policy보다 악화
  - 최종 feature policy는 `current_07_policy`

## 작성해야 할 내용

- 전체 성능 요약
- label별 성능
- validation protocol별 성능
- metric 설명
- public score와 local validation score 차이 해석
- label별 개선 여부
- label별 악화 여부
- 안정적인 모델과 불안정한 모델 구분
- 제출 후보 기록
- 최종 선택 근거

## 기록 템플릿

| 실험명 | label | validation 방식 | log loss | AUROC | AUPRC | confusion matrix 경로 | 채택 여부 | 비고 |
|---|---|---|---:|---:|---:|---|---|---|
| Section 07 v5 probe | Q3 | `public_start_tail`, `subject_time_tail_25`, `subject_time_tail_35` | current policy mean `0.764988`; v5 change mean `0.779161` | 07 코드에서 계산 안 함 | 07 코드에서 계산 안 함 | 07 코드에서 생성 안 함 | 미채택 | v5가 Q3 악화 |
| Section 07 v5 probe | S4 | `public_start_tail`, `subject_time_tail_25`, `subject_time_tail_35` | current policy mean `0.812963`; v5 change mean `0.812899` | 07 코드에서 계산 안 함 | 07 코드에서 계산 안 함 | 07 코드에서 생성 안 함 | 미채택 | 개선폭이 작고 v5 full acceptance 실패 |

### Label별 최종 성능

| label | best model | log loss | AUROC | AUPRC | 안정성 평가 | 최종 사용 여부 |
|---|---|---:|---:|---:|---|---|
| Q1 | `mix_lgbm_catboost` | 07 v5 current policy mean `0.772244` | 07 코드에서 계산 안 함 | 07 코드에서 계산 안 함 | v5 change 악화 | current policy 사용 |
| Q2 | `mix_lgbm_catboost` | 07 v5 current policy mean `0.718284` | 07 코드에서 계산 안 함 | 07 코드에서 계산 안 함 | v5 change는 일부 score 개선 후보였으나 full acceptance 실패 | current policy 사용 |
| Q3 | `mix_lgbm_catboost` | 07 v5 current policy mean `0.764988` | 07 코드에서 계산 안 함 | 07 코드에서 계산 안 함 | v5 추가 시 악화 | current policy 사용 |
| S1 | `mix_lgbm_catboost` | 07 v5 current policy mean `0.583197` | 07 코드에서 계산 안 함 | 07 코드에서 계산 안 함 | base only | current policy 사용 |
| S2 | `mix_lgbm_catboost` | 07 v5 current policy mean `0.776610` | 07 코드에서 계산 안 함 | 07 코드에서 계산 안 함 | v5 미채택 | current policy 사용 |
| S3 | `mix_lgbm_catboost` | 07 v5 current policy mean `0.727348` | 07 코드에서 계산 안 함 | 07 코드에서 계산 안 함 | additive top80 사용, v5 미채택 | current policy 사용 |
| S4 | `mix_lgbm_catboost` | 07 v5 current policy mean `0.812963` | 07 코드에서 계산 안 함 | 07 코드에서 계산 안 함 | base 유지, v5 change 소폭 후보지만 미채택 | current policy 사용 |

### 제출 후보 기록

| 제출 파일 | 생성일 | public score | local 기준 | 채택 여부 | 비고 |
|---|---:|---:|---|---|---|
| `section9_labelwise_best_20260522_1239.csv` | 2026-05-22 | 0.5986218188 | Section 9 labelwise fixed Optuna | 채택 | 현재 best |
| `section07_candidate_baseline_seed_ensemble_20260529_1029.csv` | 2026-05-29 | 0.6003735255 | Section4-style retrain + seed ensemble | 보류 | near-best challenger |

## Metric 설명

- Log Loss: 예측 확률이 정답에 얼마나 잘 맞는지 보는 지표이며, 낮을수록 좋다.
- AUROC: positive와 negative를 얼마나 잘 구분하는지 보는 지표이며, 높을수록 좋다.
- AUPRC: positive class를 얼마나 잘 잡는지 보는 지표이며, class imbalance가 있을 때 중요하다.
- Confusion Matrix: TP, FP, TN, FN을 나눠 어떤 오류가 많은지 확인하는 표다.

## 주의사항

- 07 현재 코드에서 AUROC, AUPRC, confusion matrix는 계산하지 않는다.
- 07 v5 probe log loss는 local validation 값이며 public score와 직접 비교하면 안 된다.
- `0.5986218188`, `0.6003735255`는 사용자가 기록한 public score다.
- `0.604568`, `0.607733` 같은 과거 값은 subset/local proxy이므로 full public score처럼 쓰면 안 된다.
- protocol이 다른 실험끼리는 직접 비교하지 않는다.

## TODO

- [ ] 07 최종 seed ensemble 실행 완료 후 `section07_candidate_scoreboard.csv` 위치 확인
- [ ] label별 public은 알 수 없으므로 local labelwise metric과 public score를 분리 기록
- [ ] AUROC/AUPRC가 필요하면 별도 evaluation cell 추가
- [ ] Q3 전용 window/temporal challenger 성능 표 추가
