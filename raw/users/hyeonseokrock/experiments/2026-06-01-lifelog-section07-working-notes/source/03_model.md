# 03. Model

작성일: 2026-05-29
담당자: 팀 공용
상태: draft
관련 폴더: `Y2025LifeLogDB/experiments/260519_recovered_feature_model_v1/notebooks/`
관련 산출물: `section07_model_optuna_seed_ensemble_summary.md`, `section07_retrain_challenger_summary.md`, `section9_labelwise_fixed_optuna_summary.md`

## 핵심 요약

07 노트북의 현재 모델 축은 `mix_lgbm_catboost` 하나로 고정되어 있다.
각 label마다 LightGBM과 CatBoost를 각각 Optuna로 튜닝하고, 두 모델의 예측을 probability mean으로 섞는다. 이후 seed ensemble 후보는 seed offset별 예측을 logit mean으로 합친다.

## 현재 기준

- 모델 이름: `mix_lgbm_catboost`
- base model: `lgbm`, `catboost`
- XGBoost: 07 현재 모델 최적화 경로에서 제거됨
- CNN/LSTM/Attention: 07 현재 코드에 없음
- full mode labels: `Q1`, `Q2`, `Q3`, `S1`, `S2`, `S3`, `S4`
- smoke mode labels: `Q2`, `Q3`, `S4`
- Optuna trials: full `50`, smoke `3`
- CPU threads: `6`
- Optuna n_jobs: `1`
- early stopping rounds: `80`
- seed ensemble offsets: `[0, 20000, 40000]`
- baseline 내부 blend: `probability_mean`
- seed ensemble candidate blend: `logit_mean`

## 작성해야 할 내용

- 각 label에서 실제 사용한 feature count와 feature hash
- 각 label에서 LGBM/CatBoost Optuna best params
- seed별 prediction 차이
- public score와 local validation score 차이
- 모델을 채택하거나 폐기한 이유
- 실험 모델과 최종 제출 모델 구분

## 기록 템플릿

| label | 모델 후보 | 사용 feature pool | validation 방식 | 주요 metric | 채택 여부 | 채택 또는 폐기 이유 |
|---|---|---|---|---|---|---|
| Q1 | `mix_lgbm_catboost` | base 922 + additive top20 | inner `StratifiedShuffleSplit(20%)`, v5 probe는 tail validations | Log Loss | 사용 | current 07 policy |
| Q2 | `mix_lgbm_catboost` | base 922 + additive top40 | inner `StratifiedShuffleSplit(20%)`, v5 probe는 tail validations | Log Loss | 사용 | XGB branch 제거 후 seed ensemble 축으로 단순화 |
| Q3 | `mix_lgbm_catboost` | base 922 + additive top40 | inner `StratifiedShuffleSplit(20%)`, v5 probe는 tail validations | Log Loss | 사용 | 가장 중요한 병목. v5는 미채택 |
| S1 | `mix_lgbm_catboost` | base 922 | inner `StratifiedShuffleSplit(20%)` | Log Loss | 사용 | 추가 feature 기본 제외 |
| S2 | `mix_lgbm_catboost` | base 922 + additive top10 | inner `StratifiedShuffleSplit(20%)` | Log Loss | 사용 | 소량 additive |
| S3 | `mix_lgbm_catboost` | base 922 + additive top80 | inner `StratifiedShuffleSplit(20%)` | Log Loss | 사용 | additive top-k 사용 |
| S4 | `mix_lgbm_catboost` | base 922 | inner `StratifiedShuffleSplit(20%)` | Log Loss | 사용 | broad feature 추가 주의 |

### 모델 구조

| 모델 | 코드 기준 역할 | 주요 설정 |
|---|---|---|
| LightGBM | tabular binary classifier | objective `binary`, boosting `gbdt`, `n_jobs=6` |
| CatBoost | tabular binary classifier | loss `Logloss`, eval `Logloss`, `thread_count=6` |
| mix_lgbm_catboost | LGBM/CatBoost 예측 결합 | 내부 blend는 probability mean |
| seed ensemble | seed offset별 mix 예측 결합 | 최종 candidate blend는 logit mean |

### Optuna/학습 기준

| 항목 | 값 |
|---|---|
| full trials | `50` |
| smoke trials | `3` |
| Optuna n_jobs | `1` |
| early stopping | `80` |
| inner validation | `StratifiedShuffleSplit(test_size=0.2)` |
| objective metric | binary log loss |
| prediction clip | `[1e-6, 1 - 1e-6]` |

## 주의사항

- validation에서 선택한 feature와 submission 생성 시 사용한 feature가 달라지면 안 된다.
- 전체 평균 성능만 보고 모델을 선택하면 안 된다.
- 특정 label만 좋아지고 다른 label이 크게 악화되면 채택하지 않는다.
- old validation score와 current validation score는 protocol이 다르면 직접 비교하지 않는다.
- 07 현재 코드에서 XGB/CatBoost-heavy challenger는 제거되어 있으므로 현재 모델 문서에는 별도 후보로 쓰지 않는다.
- public score는 코드 입력으로 쓰지 않고 결과 기록으로만 남긴다.

## TODO

- [ ] `section07_model_optuna_seed_ensemble_summary.md` 생성 여부 확인
- [ ] label별 LGBM/CatBoost best params 정리
- [ ] seed offset별 prediction drift 기록
- [ ] Q3 전용 temporal/window 모델을 별도 challenger로 설계
- [ ] public `0.6003735255` 후보와 local metric 차이 정리
