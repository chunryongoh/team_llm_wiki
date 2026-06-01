# 02. Feature

작성일: 2026-05-29
담당자: 팀 공용
상태: draft
관련 폴더: `Y2025LifeLogDB/experiments/260519_recovered_feature_model_v1/`
관련 산출물: `section07_section4_retrain_feature_policy.csv`, `section07_v5_feature_manifest.json`, `feature_domain_catalog_current.md`

## 핵심 요약

07 노트북의 현재 feature 기준은 `saved_anchor_feature_list_922`를 보존하고, label별로 Section 11 additive top-k를 붙이는 방식이다.
v5 change/frequency feature도 생성하고 probe는 하지만, 2026-05-29 실행 기준 `v5_full_acceptance=false`라서 최종 export feature set은 `current_07_policy`로 되돌아간다.

## 현재 기준

- base feature: label별 anchor feature list `922`개
- additive feature 전체 생성 수: `127`
- v5 change feature 생성 수: `87`
- v5 frequency feature 생성 수: `47`
- 최종 export feature source: `section11_base922_plus_labelwise_additive_policy`
- v5 probe validation: `public_start_tail`, `subject_time_tail_25`, `subject_time_tail_35`
- v5 acceptance: `false`

## 작성해야 할 내용

- feature가 어느 파일/코드에서 생성됐는지 기록한다.
- feature가 어떤 domain인지 기록한다.
- label별 feature count와 hash를 기록한다.
- 새 feature가 성능을 올렸는지, 또는 악화시켰는지 기록한다.
- broad feature를 전체 label에 넣지 말고 label별로 채택 여부를 따로 적는다.

## 기록 템플릿

| feature 이름 | domain | 계산 방식 | 예상 label | 기대 효과 | 위험 요소 | 사용 여부 |
|---|---|---|---|---|---|---|
| `v4_q2_fatigue_proxy_raw` | 활동/회복 | 낮 부하 composite - 저녁 회복 composite | Q2, Q3 | 피로 누적 proxy | source feature가 noisy하면 과적합 | 후보 |
| `v4_q3_presleep_screen_to_sleep_light_ratio` | 스크린/빛 | presleep screen / sleep light | Q3, S2, S3 | 취침 전 자극 대비 수면 환경 | 분모가 작을 때 불안정 | 후보 |
| `v4_s4_sleep_disturbance_entropy` | 수면 분절 | sleep disturbance entropy alias | S4 | WASO/각성 proxy | S4는 broad feature 추가 시 악화 가능 | 좁은 후보 |
| `v5_change_*` | 변화량 | prev3/prev7, lag, first/last, slope 등에서 파생 | Q2, Q3, S3 | 변동성/추세 보완 | 2026-05-29 probe에서 Q3 악화 | 보류 |
| `v5_frequency_*` | frequency proxy | sequence proxy가 있는 feature 묶음에서만 생성 | Q3, S3 | 진동/불안정성 proxy | 진짜 raw FFT가 아니므로 해석 제한 | 보류 |

### Label별 Feature 정책

| label | 주로 볼 feature domain | 강제 포함 feature | 후보 feature | 제외 또는 주의 feature |
|---|---|---|---|---|
| Q1 | 수면 안정성, presleep 안정성, WiFi/BLE, light | base 922 | additive top20 | v5 change는 probe에서 악화 |
| Q2 | 낮 활동량, 피로/회복, 취침/기상 리듬, 빛 노출 | base 922 + additive top40 | v5 change top30, v5 frequency top10은 후보였으나 미채택 | 검증 없는 frequency feature |
| Q3 | presleep screen/social, 낮 restlessness, temporal/window signal | base 922 + additive top40 | window/temporal feature | broad v5 change/frequency |
| S1 | 수면 시간, bed/wake, circadian | base 922 | 없음 | 추가 feature 기본 제외 |
| S2 | HR/HRV 회복, 수면 연속성, presleep 자극 | base 922 + additive top10 | subject-relative 후보 | 과도한 feature 확장 |
| S3 | HR/HRV baseline, light rhythm, presleep screen ratio | base 922 + additive top80 | v5 change/frequency는 후보였으나 미채택 | 너무 넓은 additive |
| S4 | sleep disturbance, WASO proxy, light/movement spike | base 922 | v5 change top10은 challenger | broad additive, broad v5 |

### Feature count 정책

| label | base feature count | additive top-k | 최종 feature count | 현재 선택 feature set |
|---|---:|---:|---:|---|
| Q1 | 922 | 20 | 942 | `current_07_policy` |
| Q2 | 922 | 40 | 962 | `current_07_policy` |
| Q3 | 922 | 40 | 962 | `current_07_policy` |
| S1 | 922 | 0 | 922 | `current_07_policy` |
| S2 | 922 | 10 | 932 | `current_07_policy` |
| S3 | 922 | 80 | 1002 | `current_07_policy` |
| S4 | 922 | 0 | 922 | `current_07_policy` |

### Feature domain map

| domain | 코드에서 확인된 source 예시 | 의미 |
|---|---|---|
| 수면 시간/일주기 | `circ_sleep_duration_h`, `circ_bed_hour`, `circ_wake_hour_dev7` | 수면량과 수면-기상 리듬 |
| HR/HRV | `hr_sleep_*`, `hrv_sleep_rmssd_*`, `hrv_pnn50_*` | 자율신경, 회복, 스트레스 proxy |
| 활동량/이동 | `activity`, `wPedo`, `mobility_gps` | 낮 부하, 움직임, restlessness |
| 스크린/앱 | `screen_app`, `mScreenStatus`, `mUsageStats`, `presleep_app` | 취침 전 자극, 디지털 사용 |
| 빛 | `light_env`, `mLight`, `wLight` | 주간 entrainment, 야간 빛 노출 |
| 소리/ambient | `ambient`, `noise`, `snoring` | 수면 환경 proxy |
| WiFi/BLE/social | `mWifi`, `mBle`, `social_wifi_ble` | 장소/사회적 활동/환경 변화 |
| GPS | `mGps`, `mobility_gps` | 이동량, 이동 변동성 |
| 충전 | `charging_mean`, `charging_std` | 생활 패턴, 기기 사용 proxy |
| coverage | `coverage`, `valid`, `notna` | sensor 관측률과 결측 구조 |

## 주의사항

- 07 코드상 v5 feature는 생성되지만 acceptance가 false면 최종 export에는 들어가지 않는다.
- feature 이름에 시간 구간이 들어 있어도 실제 의미는 source column 계산식을 다시 확인해야 한다.
- `subject-relative`는 07 현재 final export의 기본 feature가 아니다.
- feature ranking은 train split 내부에서만 해야 한다.
- S4는 feature 추가가 자주 악화되므로 base 922 유지가 기본이다.

## TODO

- [ ] `section07_section4_retrain_feature_policy.csv`의 label별 feature hash를 Wiki에 복사
- [ ] Q3 window/temporal feature를 별도 후보로 설계
- [ ] S4 WASO/sleep disturbance proxy를 좁은 feature로 재설계
- [ ] feature별 public 결과와 local 결과를 연결
