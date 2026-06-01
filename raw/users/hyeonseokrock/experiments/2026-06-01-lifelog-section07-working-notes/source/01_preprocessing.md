# 01. Preprocessing

작성일: 2026-05-29
담당자: 팀 공용
상태: draft
관련 폴더: `Y2025LifeLogDB/experiments/260519_recovered_feature_model_v1/`
관련 산출물: `section07_allowed_input_audit.csv`, `section07_section4_retrain_feature_manifest.json`, `section07_v5_feature_manifest.json`

## 핵심 요약

07 노트북은 기존 제출 파일이나 기존 prediction 파일을 읽지 않고, 원천 label/sample과 feature parquet에서 다시 학습 데이터를 만든다.
핵심 key는 `subject_id`, `lifelog_date`이고, train은 450 rows, test는 250 rows로 검증한다.

## 현재 기준

- label 파일: `Y2025LifeLogDB/ch2026_metrics_train.csv`
- sample submission 파일: `Y2025LifeLogDB/ch2026_submission_sample.csv`
- base feature train: `experiments/260519_recovered_feature_model_v1/data/raw_reverse_legacy_xgb/features_train.parquet`
- base feature test: `experiments/260519_recovered_feature_model_v1/data/raw_reverse_legacy_xgb/features_test.parquet`
- entropy feature train: `experiments/260520_timing_entropy_features_v1/data/timing_entropy_features_train.parquet`
- entropy feature test: `experiments/260520_timing_entropy_features_v1/data/timing_entropy_features_test.parquet`
- anchor parameter file: `experiments/260519_recovered_feature_model_v1/data/raw_reverse_legacy_xgb/mix_lgbm_catboost_none_full_legacy_entropy_hightrial_params.json`
- Section 11 top feature file: `experiments/260519_recovered_feature_model_v1/data/clean_anchor_exact_04/section11_feature_selection_probe/section11_top_features.csv`
- train row 수: `450`
- test row 수: `250`
- key column: `subject_id`, `lifelog_date`
- label: `Q1`, `Q2`, `Q3`, `S1`, `S2`, `S3`, `S4`

## 작성해야 할 내용

- 실제 실행 시 `section07_allowed_input_audit.csv`에서 입력 파일이 모두 존재하는지 확인한다.
- train/test의 `subject_id`, `lifelog_date` 중복 여부를 확인한다.
- feature train/test가 sample row order와 맞게 merge됐는지 확인한다.
- final submission 생성 시 기존 `submission/*.csv` 또는 기존 prediction 파일을 읽지 않았는지 확인한다.
- validation score와 public score는 protocol이 다르므로 같은 숫자로 직접 비교하지 않는다.

## 기록 템플릿

| 항목 | 내용 | 확인 여부 |
|---|---|---|
| 원천 데이터 경로 | `Y2025LifeLogDB/ch2026_metrics_train.csv`, `Y2025LifeLogDB/ch2026_submission_sample.csv` | |
| train row 수 | `450` | |
| test row 수 | `250` | |
| validation 방식 | v5 probe: `public_start_tail`, `subject_time_tail_25`, `subject_time_tail_35`; model Optuna/early stopping: train 내부 `StratifiedShuffleSplit(test_size=0.2)` | |
| leakage 방지 규칙 | 기존 submission/prediction 파일 읽기 금지, validation index와 train index overlap assert, v5 feature ranking은 train split 내부에서만 수행 | |
| 시간 구간 정의 | feature name 기준 `daytime_06_18`, `evening_18_24`, `presleep_21_24`, `presleep_22_24`, `wide_presleep_18_27`, `sleep_fixed_24_33`, `sleep_early_24_27`, `sleep_mid_27_30`, `sleep_late_30_33`, `wide_sleep_20_36` | |
| 결측 처리 방식 | `inf/-inf -> NaN`; unresolved source는 NaN; division by zero는 NaN; LightGBM/CatBoost 입력은 NaN 허용 | |
| 산출물 파일 | `data/section07_model_optuna_seed_ensemble/*`, `submission/<timestamp>/section07_candidate_baseline_seed_ensemble_<timestamp>.csv` | |

### 시간 구간 기록

| 구간 이름 | 시간 기준 | 의미 | 사용 label | 확인 여부 |
|---|---|---|---|---|
| daytime | `daytime_06_18` | 낮 활동량, 스크린, 이동, 빛 노출 | Q2, Q3, S4 | |
| evening | `evening_18_24` | 저녁 활동 감소, 회복, 빛/스크린 노출 | Q2, Q3, S4 | |
| presleep | `presleep_21_24`, `presleep_22_24`, `wide_presleep_18_27` | 취침 전 자극, 스크린, 앱, 사회적 신호 | Q1, Q2, Q3, S3 | |
| sleep proxy | `sleep_fixed_24_33`, `sleep_early_24_27`, `sleep_mid_27_30`, `sleep_late_30_33`, `wide_sleep_20_36` | 수면 중 빛, 움직임, 스크린, disturbance proxy | Q1, S2, S3, S4 | |
| wake zone | `circ_wake_hour_dev7` 중심 | 평소 기상 시각 대비 변동 | Q2 | |

### Validation 기록

| validation 이름 | 분리 기준 | 목적 | 장점 | 한계 |
|---|---|---|---|---|
| public_start_tail | sample test의 subject별 시작일 이후 train row를 validation으로 사용. 부족하면 subject별 마지막 20% fallback | public/test와 유사한 시간축 proxy | test 시작 시점 drift를 일부 반영 | public label은 없으므로 proxy일 뿐 |
| subject_time_tail_25 | subject별 날짜 정렬 후 마지막 25% | subject 내부 시간 drift 확인 | 같은 subject의 미래 구간 검증 | unseen subject 검증은 아님 |
| subject_time_tail_35 | subject별 날짜 정렬 후 마지막 35% | 더 넓은 tail 안정성 확인 | tail 민감도 확인 | train row가 줄어들 수 있음 |
| inner ES split | `StratifiedShuffleSplit(n_splits=1, test_size=0.2)` | Optuna와 early stopping 내부 검증 | label 비율을 보존 | 시간 순서 검증은 아님 |

## 주의사항

- 07 코드의 final training/export는 기존 제출 파일을 입력으로 쓰지 않는다.
- `submission/` 경로 또는 `*prediction*.csv/parquet`를 입력으로 읽으면 forbidden input으로 처리한다.
- v5 feature ranking은 validation row를 사용하지 않는다.
- `subject_hole_5fold`는 07 현재 코드의 main validation에는 포함되어 있지 않다.
- wake zone은 명시적 시간 window라기보다 `circ_wake_hour_dev7` 같은 파생 feature로 처리된다.

## TODO

- [ ] 실제 실행 후 `section07_allowed_input_audit.csv`를 문서에 링크
- [ ] sample submission column order 확인 결과 기록
- [ ] 각 validation split별 row 수 기록
- [ ] sensor coverage feature 목록을 domain별로 정리
- [ ] subject-hole CV를 07에 넣을지 별도 문서에서 결정
