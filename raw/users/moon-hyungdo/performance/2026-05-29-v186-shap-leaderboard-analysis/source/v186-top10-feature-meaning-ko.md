---
project: ETRI_2026
type: feature_dictionary
created: 2026-05-29
source_note: v186 SHAP top10 feature meaning guide
source_paths:
  - agent_memory/feature_importance/SHAP/v186_shap_analysis.md
  - outputs/v186_s12_target_specific_weighted_refit/shap_importance_Q1.csv
  - outputs/v186_s12_target_specific_weighted_refit/shap_importance_Q2.csv
  - outputs/v186_s12_target_specific_weighted_refit/shap_importance_Q3.csv
  - outputs/v186_s12_target_specific_weighted_refit/shap_importance_S1.csv
  - outputs/v186_s12_target_specific_weighted_refit/shap_importance_S2.csv
  - outputs/v186_s12_target_specific_weighted_refit/shap_importance_S3.csv
  - outputs/v186_s12_target_specific_weighted_refit/shap_importance_S4.csv
  - experiments/common/sensor_panel.py
  - experiments/common/calendar.py
  - experiments/active/build_v146_sleep_episode.py
  - experiments/active/build_v150_sensor_first_sleep_transition.py
---

# v186 SHAP Top10 Feature Meaning Guide

#etri2026 #feature-importance #SHAP #v186 #feature-dictionary

이 문서는 [[v186_shap_analysis]]의 타깃별 Top 10 SHAP feature를 사람이 해석할 수 있게 풀어 쓴 메모다. 피처 이름은 가능하면 실제 산출물 `outputs/v186_s12_target_specific_weighted_refit/shap_importance_*.csv`를 기준으로 정리했다. 기존 `v186_shap_analysis.md`에는 사람이 읽기 쉽게 바꾸는 과정에서 Q1/Q2 일부 이름이 축약되거나 오래된 표기로 남아 있다.

## 이름 해석 규칙

### Q 계열 sensor-window feature

형식은 대체로 다음과 같다.

```text
<sensor>_<window>_<base_signal>_<window_aggregation>
```

- `sensor`: 원본 센서 parquet. 예: `mWifi`, `mBle`, `mGps`, `mLight`, `wLight`, `wHr`, `mUsageStats`, `mAmbience`, `mScreenStatus`.
- `window`: lifelog 날짜 기준 시간창.
- `daily_00_24`: lifelog 당일 00:00-24:00.
- `day_09_18`: lifelog 당일 09:00-18:00.
- `evening_18_21`: lifelog 당일 18:00-21:00.
- `prebed_21_24`: lifelog 당일 21:00-24:00.
- `wake_06_09`: 다음날 아침 06:00-09:00 로그를 전날 lifelog row에 붙인 창.
- `base_signal`: 한 로그 row에서 먼저 만든 값. 예: WiFi/BLE scan 개수, RSSI 통계, GPS speed 통계, 앱 사용시간 통계.
- `window_aggregation`: 그 시간창 안에서 `count`, `mean`, `std`, `min`, `max`로 다시 집계한 값.

`mUsageStats_total_time_max_max`처럼 통계명이 두 번 보이는 이름은 정상이다. 앞의 `max`는 한 timestamp에서 앱별 `total_time`의 최대값이고, 뒤의 `max`는 시간창 안에서 그 값을 다시 최대 집계했다는 뜻이다.

### S 계열 sleep-episode feature

- `episode_*`: v110 sleep engine이 18:00-다음날 12:00 night frame에서 수면 episode를 추정해 만든 구조 feature.
- `raw_*`: v146이 추정 episode 내부 bin만 다시 모아 screen, charging, WiFi/BLE quiet, HR, GPS를 요약한 raw behavior feature.
- `sr_*`: subject-relative feature. 같은 subject의 과거 수면 episode 이력을 기준으로 현재 값이 median/trailing mean/percentile에서 얼마나 다른지 나타낸다.
- `cal__*`: `sleep_date` 또는 `lifelog_date`에서 만든 calendar feature.
- `subject_num`, `cal__subject_num`: subject id를 숫자로 바꾼 subject baseline proxy다. 예측력은 강할 수 있지만 train/test shift와 subject-hole validation 해석에 주의해야 한다.

## 문서 표기와 실제 산출물 차이

`v186_shap_analysis.md`의 표는 의미 설명을 사람이 다듬은 버전이고, 실제 SHAP CSV와 일부 feature명이 다르다. 이 문서는 실제 산출물 기준 이름을 우선한다.

| Target | 문서 표기 | 실제 산출물 표기 | 해석 |
| :--- | :--- | :--- | :--- |
| Q1 | `mScreenStatus_day_09_18_mScreenStatus_m_screen_on_count` | `mScreenStatus_day_09_18_mScreenStatus_m_screen_use_count` | 낮 시간대 screen-use 관측 수 |
| Q1 | `mScreenStatus_wake_06_09_mScreenStatus_m_screen_on_count` | `mScreenStatus_wake_06_09_mScreenStatus_m_screen_use_mean` | 다음날 아침 screen-use 평균 |
| Q2 | `mUsageStats_evening_18_21_mUsageStats_total_time_mean` | `mUsageStats_evening_18_21_mUsageStats_total_time_max_max` | 저녁 시간창의 앱 사용시간 최대값 |
| Q2 | `mUsageStats_daily_00_24_mUsageStats_total_time_sum` | `mUsageStats_daily_00_24_mUsageStats_total_time_min_mean` | 하루 로그별 최소 앱 사용시간의 평균 |
| Q2 | `mUsageStats_evening_18_21_mUsageStats_total_time_max` | `mUsageStats_evening_18_21_mUsageStats_total_time_mean_std` | 저녁 로그별 평균 앱 사용시간의 변동성 |
| Q2 | `mAmbience_prebed_21_24_mAmbience_speech_vehicle_noise_ratio_mean` | `mAmbience_prebed_21_24_mAmbience_speech_vehicle_score_mean` | 취침 전 말소리/차량소리 ambience 점수 평균 |

## Q1 Top 10

Q1은 subjective sleep quality 계열이라 직접 수면 구조보다 취침 전 장소 안정성, 아침 이동성, 화면 사용 패턴 같은 proxy가 상위에 온다.

| Rank | Feature | 계산 방식 | 의미 |
| ---: | :--- | :--- | :--- |
| 1 | `mWifi_prebed_21_24_mWifi_scan_count_mean` | 21-24시 WiFi list 길이의 평균 | 취침 전 주변 AP 밀도. 수면 장소/실내 환경/주변 무선기기 밀도 proxy다. |
| 2 | `mScreenStatus_day_09_18_mScreenStatus_m_screen_use_count` | 09-18시 screen-use 값의 관측 count | 낮 동안 screen status 로그가 얼마나 자주 관측됐는지. 활동성 또는 데이터 커버리지 성격도 섞인다. |
| 3 | `mWifi_prebed_21_24_mWifi_rssi_max_mean` | 21-24시 각 로그의 가장 강한 WiFi RSSI 평균 | 취침 전 가까운 AP 또는 익숙한 실내 위치 proxy. RSSI는 보통 0에 가까울수록 강하다. |
| 4 | `mScreenStatus_wake_06_09_mScreenStatus_m_screen_use_mean` | 다음날 06-09시 screen-use 평균 | 기상 무렵 화면 사용 비율. wake routine, 이른 기상, 알림 반응의 proxy다. |
| 5 | `mGps_wake_06_09_mGps_speed_max_max` | 다음날 06-09시 GPS speed 최대값의 최대 | 기상 무렵 최고 이동 속도. 아침 이동/외출/교통 이동 proxy다. |
| 6 | `mGps_wake_06_09_mGps_speed_mean_max` | 다음날 06-09시 GPS speed 평균값의 최대 | 아침 시간대 이동 강도의 peak. 낮을수록 정적인 아침을 의미한다. |
| 7 | `wLight_prebed_21_24_wLight_w_light_count` | 21-24시 watch light 관측 count | 취침 전 웨어러블 조도 데이터 커버리지/노출 proxy. 야간 착용 상태도 섞인다. |
| 8 | `mWifi_day_09_18_mWifi_rssi_max_std` | 09-18시 가장 강한 WiFi RSSI의 표준편차 | 낮 동안 장소나 AP proximity 변화. 변동성이 크면 이동/환경 변화가 컸다는 뜻이다. |
| 9 | `mGps_wake_06_09_mGps_speed_min_max` | 다음날 06-09시 GPS speed 최소값의 최대 | 아침 GPS 로그들 중 저속 기준의 peak. 완전 정지보다 이동 신호가 자주 잡힌 상황을 반영한다. |
| 10 | `mBle_daily_00_24_mBle_scan_count_std` | 하루 BLE scan count 표준편차 | 하루 동안 주변 BLE 기기 수의 변동성. 장소 변화/혼잡도/주변 기기 환경 proxy다. |

## Q2 Top 10

Q2는 fatigue 성격이 강해 취침 전 빛, 저녁 앱 사용, BLE/WiFi 환경, 아침 HR 변동성이 상위에 온다.

| Rank | Feature | 계산 방식 | 의미 |
| ---: | :--- | :--- | :--- |
| 1 | `mLight_prebed_21_24_mLight_m_light_mean` | 21-24시 스마트폰 조도 평균 | 취침 전 밝은 환경 노출. late-light exposure와 수면 준비 상태 proxy다. |
| 2 | `mBle_evening_18_21_mBle_rssi_max_min` | 18-21시 BLE 최대 RSSI의 최소값 | 저녁 내내 가장 가까운 BLE 기기의 신호가 어느 정도 유지됐는지. 주변 기기/장소 안정성 proxy다. |
| 3 | `mUsageStats_evening_18_21_mUsageStats_total_time_max_max` | 18-21시 timestamp별 앱 사용시간 최대값의 최대 | 저녁 시간대 특정 앱 사용이 길게 튄 peak. 강한 저녁 폰 사용 proxy다. |
| 4 | `mUsageStats_daily_00_24_mUsageStats_total_time_min_mean` | 하루 timestamp별 앱 사용시간 최소값의 평균 | 하루 앱 사용 분포의 낮은 쪽 baseline. 사용 패턴의 바닥값/로그 구조 proxy 성격이 있다. |
| 5 | `mBle_prebed_21_24_mBle_rssi_max_std` | 21-24시 BLE 최대 RSSI 표준편차 | 취침 전 가까운 BLE 기기 신호의 변동성. 침실 내 안정성 또는 이동 proxy다. |
| 6 | `mActivity_evening_18_21_mActivity_m_activity_mean` | 18-21시 activity code 평균 | 저녁 활동 수준. 원본 activity code의 숫자 의미에 의존하므로 절대값보다 subject 내 패턴으로 해석한다. |
| 7 | `wHr_wake_06_09_wHr_std_mean` | 다음날 06-09시 HR 배열 표준편차의 평균 | 기상 무렵 심박 변동성. 각 HR 로그 내부의 variability를 시간창 평균한 값이다. |
| 8 | `mWifi_prebed_21_24_mWifi_scan_count_mean` | 21-24시 WiFi list 길이 평균 | 취침 전 AP 밀도/장소 proxy. Q1에서도 중요한 공통 feature다. |
| 9 | `mUsageStats_evening_18_21_mUsageStats_total_time_mean_std` | 18-21시 앱 사용시간 평균값의 표준편차 | 저녁 앱 사용 강도의 변동성. 사용이 들쭉날쭉한 정도를 반영한다. |
| 10 | `mAmbience_prebed_21_24_mAmbience_speech_vehicle_score_mean` | 21-24시 speech 또는 vehicle ambience 점수 평균 | 취침 전 말소리/차량소리로 추정되는 소음 맥락. 조용한 침실과 대비되는 환경 proxy다. |

## Q3 Top 10

Q3는 stress/mood 계열로 보이며, 낮 시간대 장소 변화, 하루 빛 노출, 주변 기기 밀도, calendar seasonality가 많이 잡힌다.

| Rank | Feature | 계산 방식 | 의미 |
| ---: | :--- | :--- | :--- |
| 1 | `mWifi_day_09_18_mWifi_rssi_max_std` | 09-18시 가장 강한 WiFi RSSI 표준편차 | 낮 동안 장소 안정성/이동성. Q3에서 가장 큰 wireless variability signal이다. |
| 2 | `mLight_daily_00_24_mLight_m_light_mean` | 하루 스마트폰 조도 평균 | 전체 일과의 빛 노출 수준. 야외 활동, 실내 조명, 휴대폰 노출 환경 proxy다. |
| 3 | `mBle_daily_00_24_mBle_scan_count_max` | 하루 BLE scan count 최대값 | 하루 중 주변 BLE 기기가 가장 많았던 순간. 혼잡도/장소 특성 proxy다. |
| 4 | `mGps_day_09_18_mGps_speed_min_std` | 09-18시 GPS speed 최소값 표준편차 | 낮 시간대 GPS 속도 저점들의 변동성. 정지/이동 상태 전환 proxy다. |
| 5 | `cal__lifelog_dayofweek` | lifelog date의 요일 숫자 | 요일 효과. 생활 루틴, 업무일/주말 구조를 반영한다. |
| 6 | `mWifi_evening_18_21_mWifi_rssi_min_std` | 18-21시 가장 약한 WiFi RSSI 표준편차 | 저녁 주변 AP 환경의 변동성. 이동 또는 환경 전환 proxy다. |
| 7 | `wLight_prebed_21_24_wLight_w_light_std` | 21-24시 watch light 표준편차 | 취침 전 조도 변동성. 안정적인 어두움과 화면/조명 변화의 proxy다. |
| 8 | `mWifi_day_09_18_mWifi_rssi_max_min` | 09-18시 가장 강한 WiFi RSSI의 최소값 | 낮 동안 강한 AP 신호가 가장 약했던 순간. 장소 안정성의 하한 proxy다. |
| 9 | `cal__sleep_doy_sin` | sleep date day-of-year의 sine 변환 | 계절 위치를 원형 변수로 표현. train/test season shift에 민감한 calendar proxy다. |
| 10 | `mBle_day_09_18_mBle_rssi_mean_max` | 09-18시 BLE 평균 RSSI의 최대값 | 낮 동안 가까운 BLE 기기 proximity peak. 사람/기기/장소 밀접도 proxy다. |

## S1 Top 10

S1은 transition weighted refit 계열에서 수면 구조 feature가 강하다. 짧은 sleep-onset latency, 충분한 episode duration, weekend/calendar, subject history가 중요하게 잡힌다.

| Rank | Feature | 계산 방식 | 의미 |
| ---: | :--- | :--- | :--- |
| 1 | `episode_sol_proxy` | `max(0, episode_onset_nf - 4.0) * 60` | sleep onset latency proxy. night frame에서 기준 시점보다 늦게 수면 episode가 시작될수록 커진다. |
| 2 | `episode_tst_hours` | 추정 episode bin 수 * 5분 / 60 | total sleep time proxy. 수면 episode 길이를 시간 단위로 환산한 값이다. |
| 3 | `cal__subject_num` | subject id 숫자화 후 calendar prefix | subject별 baseline 차이. 설명력은 강하지만 일반화 해석에는 주의가 필요하다. |
| 4 | `cal__sleep_is_weekend` | sleep date가 토/일인지 여부 | 주말 수면 여부. 평일/주말 루틴 차이를 반영한다. |
| 5 | `episode_mean_score` | episode 내부 sleep rule score 평균 | 수면 episode로 선택된 구간의 평균 rule score. stillness, screen-off, HR 등 복합 신호다. |
| 6 | `episode_onset_nf` | night frame에서 episode 시작 bin / 12 | episode 시작 시각. 18:00 이후 몇 시간 지점에서 수면이 시작됐는지 나타낸다. |
| 7 | `sr_history_count` | 같은 subject의 과거 episode history 개수 | subject-relative 계산에 사용할 과거 일수. 데이터/루틴 안정성 proxy도 된다. |
| 8 | `sr_gps_still_ratio_trailing_gap` | 현재 `raw_gps_still_ratio` - 최근 subject history 평균 | 최근 본인 평소보다 episode 중 GPS stillness가 얼마나 높은지. |
| 9 | `raw_duration_hours` | raw inferred episode bin 수 / 12 | v146 raw episode duration. `episode_tst_hours`와 유사하지만 raw episode 요약 쪽 feature다. |
| 10 | `cal__sleep_doy_sin` | sleep date day-of-year sine | 계절성/시즌 위치 proxy. |

## S2 Top 10

S2는 S1보다 subject baseline과 subject-relative 안정성 feature 비중이 크다. HR drop, quiet streak, wireless quietness, sensor coverage가 주요 신호다.

| Rank | Feature | 계산 방식 | 의미 |
| ---: | :--- | :--- | :--- |
| 1 | `cal__subject_num` | subject id 숫자화 후 calendar prefix | subject별 S2 baseline proxy. |
| 2 | `episode_tst_hours` | 추정 episode duration hours | 총 수면 시간 proxy. |
| 3 | `sr_hr_drop_percentile` | 현재 `raw_hr_drop`이 subject 과거 값 중 어느 percentile인지 | 수면 중 초반 HR - 후반 HR drop이 본인 과거 대비 큰지. 생리적 안정화 proxy다. |
| 4 | `raw_sensor_obs_ratio` | episode bin에서 screen/charging/WiFi/BLE/HR/GPS 관측 여부 평균 | episode 내부 센서 커버리지. 높을수록 episode summary 신뢰도가 좋다. |
| 5 | `sr_quiet_longest_streak_min_percentile` | 현재 longest quiet streak의 subject 과거 percentile | 본인 평소 대비 긴 무선 quiet streak인지. 방해 적은 수면 구간 proxy다. |
| 6 | `sr_gps_still_ratio_trailing_gap` | 현재 GPS still ratio - 최근 subject 평균 | 최근 평소보다 정적인 수면 episode인지. |
| 7 | `raw_wifi_quiet_ratio` | episode bin 중 WiFi scan count가 0인 비율 | episode 내 WiFi quiet 비율. 주변 AP/스캔 활동이 적은 구간 proxy다. |
| 8 | `raw_ble_quiet_ratio` | episode bin 중 BLE scan count가 0인 비율 | episode 내 BLE quiet 비율. 주변 BLE 기기/스캔 활동이 적은 정도다. |
| 9 | `subject_num` | subject id 숫자화 | `cal__subject_num`과 같은 subject baseline 계열이지만 calendar prefix 없이 들어간 값이다. |
| 10 | `raw_quiet_longest_streak_min` | WiFi quiet 및 BLE quiet이 동시에 지속된 최장 run * 5분 | episode 중 연속적으로 무선 환경이 조용했던 최장 시간. |

## S3 Top 10

S3는 v146 sleep episode donor 계열에서 subject/calendar와 GPS stillness가 매우 강하게 잡힌다. 현재 모델은 S3를 이동성/정지성 및 seasonality로 많이 설명한다.

| Rank | Feature | 계산 방식 | 의미 |
| ---: | :--- | :--- | :--- |
| 1 | `cal__subject_num` | subject id 숫자화 후 calendar prefix | 강한 subject-specific baseline. |
| 2 | `cal__sleep_doy_cos` | sleep date day-of-year cosine | 계절 위치의 cosine 성분. sine과 함께 연중 순환성을 표현한다. |
| 3 | `raw_gps_still_ratio` | episode bin의 GPS still flag 평균 | episode 중 정지 상태 비율. GPS speed mean이 0.30 이하인 bin 비중이다. |
| 4 | `cal__sleep_doy_sin` | sleep date day-of-year sine | 계절 위치의 sine 성분. |
| 5 | `raw_gps_speed_max` | episode 내부 GPS speed max | episode 중 최대 이동 속도. 낮을수록 안정적인 수면 episode와 맞는다. |
| 6 | `raw_gps_speed_mean` | episode 내부 GPS speed mean | episode 평균 이동 속도. 정적/이동성 proxy다. |
| 7 | `episode_mean_score` | selected episode의 평균 sleep rule score | episode가 수면답게 보이는 정도의 복합 점수. |
| 8 | `cal__lifelog_day` | lifelog date의 월중 일자 | 월중 날짜 효과. season/month progression의 작은 proxy다. |
| 9 | `subject_num` | subject id 숫자화 | subject baseline proxy. |
| 10 | `raw_gps_dispersion` | episode 내부 GPS latitude/longitude 분산 결합 | 수면 episode 중 위치 분산. 낮을수록 같은 장소에 머문 것으로 해석된다. |

## S4 Top 10

S4는 v186 문서에서 logloss가 가장 약한 S target으로 정리되어 있다. Top feature는 quiet streak, WiFi quietness, GPS immobility, charging start, wake burst처럼 episode 내부의 방해/각성 신호에 몰려 있다.

| Rank | Feature | 계산 방식 | 의미 |
| ---: | :--- | :--- | :--- |
| 1 | `raw_quiet_longest_streak_min` | WiFi quiet 및 BLE quiet 동시 run의 최장 길이 * 5분 | episode 중 가장 길게 주변 무선환경이 조용했던 시간. 연속 수면 안정성 proxy다. |
| 2 | `raw_wifi_quiet_ratio` | episode bin 중 WiFi scan count가 0인 비율 | WiFi quietness. 주변 AP 스캔/환경 활동이 적은 정도다. |
| 3 | `raw_gps_speed_max` | episode 내부 GPS speed max | episode 중 이동 peak. 낮을수록 수면 중 움직임/외출 가능성이 낮다. |
| 4 | `raw_charging_start_ratio` | episode 초반 head bins의 charging ratio 평균 | 잠들기 시작할 때 휴대폰 충전 상태. 취침 루틴/폰 거치 proxy다. |
| 5 | `raw_wake_burst_score` | wake tail의 screen, GPS motion, GPS speed, HR rise weighted composite | 기상부 각성 burst 점수. 높으면 episode 말미에 화면/이동/심박 상승이 강하다는 뜻이다. |
| 6 | `cal__sleep_day` | sleep date의 월중 일자 | calendar progression proxy. |
| 7 | `episode_tst_hours` | 추정 episode duration hours | 총 수면 시간 proxy. |
| 8 | `episode_mean_score` | selected episode의 평균 sleep rule score | 수면 episode답게 보이는 정도. |
| 9 | `cal__subject_num` | subject id 숫자화 후 calendar prefix | subject-specific baseline. |
| 10 | `raw_sensor_obs_ratio` | episode 내부 센서 관측 커버리지 평균 | raw episode feature 신뢰도/데이터 밀도 proxy. |

## 해석상 주의점

1. SHAP 중요도는 모델이 사용한 예측 근거이지, 원인 관계의 증거가 아니다.
2. `cal__subject_num`, `subject_num`, `cal__sleep_doy_*`는 강한 예측 feature지만 live leaderboard shift에서는 누수처럼 행동할 수 있다. 특히 S3의 calendar/subject dominance는 검증 설계가 틀리면 쉽게 과대평가된다.
3. Q 계열 feature는 센서 직접 수면 구조가 아니라 주로 daily routine proxy다. 같은 feature라도 target별 방향은 달라질 수 있다.
4. S 계열 feature는 물리적으로 해석하기 쉽지만, v188/v189 live 결과처럼 S4 단독 설명력이 곧바로 제출 이득으로 이어지지는 않았다. 현재 전략에서는 feature importance를 후보 생성의 prior로 쓰되, confirmed-LB replay와 anchor-relative guardrail을 반드시 같이 봐야 한다.
