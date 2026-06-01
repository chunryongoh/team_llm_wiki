# gen_LOG_feature — 피처 요약 체크리스트

키: `subject_id`, `lifelog_date` / 타깃: `Q1 Q2 Q3 S1 S2 S3 S4`

---

## Base — 12 센서 daily 집계 (셀 4, 96개)

12개 센서 × {mean, std, min, max, sum, count} + list_count + activity_ratio.

- [x] `mACStatus_*` — 충전 상태 daily 집계 (numeric_daily)
- [x] `mActivity_*` — 활동 코드 numeric 집계와 ratio/dominant/entropy/transition 계열을 함께 후보로 유지
- [x] `mAmbience_*` — 환경음 list_count (list_count_daily)
- [x] `mBle_*` — BLE 스캔 list_count
- [x] `mGps_*` — GPS dict list_count
- [x] `mLight_*` — 조도 numeric
- [x] `mScreenStatus_*` — 스크린 on/off numeric
- [x] `mUsageStats_*` — 앱 사용 list_count
- [x] `mWifi_*` — WiFi AP list_count
- [x] `wHr_*` — 심박 numeric
- [x] `wLight_*` — 손목 조도 numeric
- [x] `wPedo_*` — 걸음/거리/속도/칼로리 numeric. `step_frequency`, `speed`는 고상관이지만 성능 후보로 유지

**구현**: `numeric_daily()` / `activity_ratio_daily()` / `list_count_daily()` → `groupby(KEY_COLS).agg(...)`

---

## P1 — 심박 / HRV 근사 (셀 6, wHr)

네이밍: `hr_*` = 원시 bpm, `hrv_*` = HRV 지표. window ∈ {night=0-6h, day=10-18h, presleep=21-24h, full=0-24h, sleep=D 20:00-D+1 11:59}.

- [x] `hr_{night|day|presleep|full}_mean/std/min/max` — 시간대별 bpm 기초통계 (`window_daily`)
- [x] `hr_{night|full}_resting` — 5-percentile 저심박 (groupby quantile)
- [x] `hr_night_slope` — 22-04h 선형회귀 기울기 (np.polyfit, bpm/s)
- [x] `hr_dip_depth` — `hr_day_mean − hr_night_min` (주간-야간 낙폭)
- [x] `hrv_{night|full}_avnn/sdnn/rmssd/pnn50` — 시간영역 HRV (60000/HR → R-R ms 근사, `_time_hrv`)
- [x] `hrv_{night|full}_lf/hf/lfhf_ratio` — Welch PSD 기반 주파수영역 (RR ms 단위, LF 0.04-0.15Hz, HF 0.15-0.40Hz, 4Hz 재샘플, Hann window, linear detrend)
- [x] `hr_sleep_mean/std/min/max/resting` — sleep-aligned window 심박 통계 (`lifelog_date D`의 D 20:00-D+1 11:59)
- [x] `hrv_sleep_avnn/sdnn/rmssd/pnn50/lf/hf/lfhf_ratio` — sleep-aligned window HRV 근사

**주의**: 원시 R-R/IBI가 아니라 HR 기반 `RR(ms)=60000/HR` 근사입니다. 표준 HRV와 절대값 차이가 있으므로 상대 비교 피처로 사용합니다.
b
---

## P2 — 취침전 스크린타임 + 앱 카테고리 (셀 7, mScreenStatus + mUsageStats)

- [x] `screen_bed_hour` — 당일 마지막 `m_screen_use=True` 시각 (hour)
- [x] `screen_presleep_{1,2,3}h_cnt` — 취침 추정 시각 이전 1/2/3시간 내 screen on 이벤트 수
- [x] `screen_night_wake_cnt` — 00-05h screen on 이벤트 수 (야간 각성)
- [x] `screen_sleep_bed_hour` — sleep-aligned D 20:00-D+1 04:00 마지막 screen on 시각, 0-4h는 +24
- [x] `screen_sleep_night_wake_cnt` — D+1 00-05h screen on 이벤트를 `lifelog_date D`로 귀속한 야간 각성 count
- [x] `app_presleep2h_{sns|game|work|video|health|other}` + `{_log1p|_present}` — 취침 2시간 전 앱 카테고리별 foreground raw 사용량, log1p, 사용 여부 flag (`APP_CATEGORIES` 규칙 매칭 → pivot)

**구현**: `bed_est` merge → `_delta_h` 계산 → 구간 필터 → groupby size / sum

---

## P3 — 캘린더 / 공휴일 / 일출일몰 / 월 위상 (셀 8)

- [x] `cal_dow` — 요일 (0-6)
- [x] `cal_is_weekend` — 주말 플래그
- [x] `cal_month`, `cal_season` — 월, 계절 (0-3)
- [x] `cal_moon_phase` — 월 위상 0-1 (간이 공식)
- [ ] `cal_is_holiday` — 공휴일 플래그 (`holidays` 패키지 필요)
- [ ] `cal_hol_prev` / `cal_hol_next` — 공휴일 전/후일
- [ ] `cal_is_long_holiday` — 3일+ 연휴
- [ ] `cal_sunrise_h` / `cal_sunset_h` / `cal_daylen_h` — 서울 기준 일출·일몰·낮길이 (`astral` 필요)

**구현**: 날짜 루프 + `holidays.KR()` + `astral.sun()`. 미설치 시 해당 피처 자동 스킵.

---

## P4 — 일주기 리듬 규칙성 (셀 9, mScreenStatus)

- [x] `circ_wake_hour` — D+1 05-12h 첫 screen on 시각을 `lifelog_date D`로 귀속 (없으면 NaN)
- [x] `circ_bed_hour` — D 20:00-D+1 04:00 마지막 screen on 시각, 0-4h는 +24 선형화 (20-28 스케일)
- [x] `circ_wake_hour_std7` / `circ_bed_hour_std7` — 7일 롤링 표준편차 (social jet lag 근사)
- [x] `circ_wake_hour_diff` / `circ_bed_hour_diff` — 전일 대비 절대 차이
- [x] `circ_sleep_duration_h` — `wake_hour + 24 - bed_hour` 수면 지속시간 근사
- [x] `circ_sleep_detected` — bed/wake 모두 있고 duration이 3-14h면 1, 범위 밖이면 0, 미검출은 NaN
- [x] `circ_sleep_short` / `circ_sleep_long` — 유효 duration 기준 7h 미만 / 9h 초과 플래그, 미검출·비정상 duration은 NaN
- [x] `circ_sleep_duration_h_roll7_mean` / `circ_sleep_duration_h_roll7_std` — subject별 수면 지속시간 7일 rolling baseline
- [x] `circ_wake_hour_roll7_mean` / `circ_bed_hour_roll7_mean` — bed/wake hour 7일 rolling mean (dev7 baseline)
- [x] `circ_sleep_duration_h_dev7` / `circ_bed_hour_dev7` / `circ_wake_hour_dev7` — **Q1 타깃형** 개인 baseline 편차 (오늘 − roll7_mean)
- [x] `circ_sleep_debt_3d` / `circ_sleep_debt_7d` — **Q1 타깃형** 권장 8h 대비 누적 수면부채 (`clip(lower=0).rolling.sum()`)
- [x] `screen_in_sleep_cnt` — **S4(WASO) 타깃형** `[bed_est, wake_est)` 수면창 내 screen-on 이벤트 수 (각성 직접 proxy)
- [x] `hr_in_sleep_std` / `hr_in_sleep_peaks` — **S4(WASO) 타깃형** 수면창 내 HR 변동성 / 개인 median+10bpm 초과 peak 수

**구현**: screen_on 필터 + sleep-date alignment(새벽/아침 이벤트는 `lifelog_date - 1`) + `rolling(7).std()` / `.diff().abs()`. `circ_` prefix는 XGBoost native missing 처리를 위해 NaN 유지. in-sleep 집계는 subject-정렬 후 `np.searchsorted`로 `[bed_est, wake_est)` 구간 슬라이스.

---

## P5 — 활동 강도 + 실내외 (셀 10, wHr + wPedo + mLight + mGps)

- [x] `act_stress_hours` — hourly (HR > subject median) & (step=0) 합계 시간 (스트레스 대리)
- [x] `act_exercise_hours` — hourly (HR > subject median) & (step>100) 합계 (운동 대리)
- [x] `light_day_mean` / `light_day_max` — 10-18h 조도 평균/최대
- [x] `gps_lat_std` / `gps_lon_std` / `gps_lat_range` / `gps_lon_range` — GPS 분산·변동폭 (이동반경 대리)

**구현**: hourly bucket groupby → HR/step merge → subject median 비교 → daily sum. `_coerce_numeric`으로 object dtype 방어.

---

## P6 — 사회적 활동 + 야간 환경음 (셀 11, mBle + mWifi + mAmbience)

- [x] `social_ble_mean/max/std` — 주변 BLE 기기 수 daily (혼자/사람 많음 대리)
- [x] `social_wifi_mean/max/std` — 주변 WiFi AP 수 daily
- [x] `ambient_night_events` — 22-06h 환경음 이벤트 수
- [x] `ambient_sleep_night_events` — sleep-aligned D 22:00-D+1 06:00 환경음 이벤트 수
- [x] `ambient_all_events` — 전일 환경음 이벤트 수

**구현**: `_count_list()`로 list/dict 안 항목 수 추출 → groupby agg.

---

## P7 — 외부 날씨 / 대기질 (셀 12, **API 키 미입력 상태**)

슬롯만 작성 — 빈 DataFrame 반환하여 파이프라인 통과.

- [ ] `wx_temp_mean` / `wx_temp_min` / `wx_temp_max` — KMA ASOS 기온
- [ ] `wx_humidity` — 습도
- [ ] `wx_precip` — 강수량
- [ ] `wx_sunshine_h` — 일조시간
- [ ] `wx_pm25` / `wx_pm10` — AirKorea 대기질

**TODO(seokhyun)**: `KMA_API_KEY`, `AIRKOREA_API_KEY`, `STATION_COORDS` 채우고 `fetch_weather()` / `fetch_air_quality()` 구현.

---

## 저장 (셀 13)

**결측 정책**: `circ_*`, `hrv_*`, `hr_*`, `wx_*` prefix = NaN 유지 (XGBoost 네이티브). 나머지 = subject median → 전체 median → 0.

**중복/overlap 정책**: exact duplicate 컬럼은 assert로 실패 처리. 의미상 overlap(`wHr_*` vs `hr_*`, `screen_*` vs `circ_*`, daily vs sleep-aligned)은 삭제하지 않고 이름으로 역할을 분리한 뒤 label별 feature selection에 맡김.

**연속성 피처**: sleep 핵심 피처와 일부 활동/조도 피처에 대해 subject별 날짜 정렬 후 `shift(1)` 기반 `{col}_lag1`, `{col}_prev3_mean`, `{col}_prev7_mean`, `{col}_prev7_std`, `{col}_diff1` 생성. target lag는 사용하지 않음.

출력 구조:
- `features/{YYYYMMDD_HHMM}/` — 해당 실행 시점의 feature snapshot
- `features/latest/` — 가장 최근 snapshot mirror, `predict_LOG_XGB.ipynb` 기본 입력
- `features/latest_feature_run.json` — 최신 feature snapshot pointer

파일: `X_train_full.parquet` (450×N), `X_test_full.parquet` (250×N), `y_train.parquet` (450×7), `feature_manifest.json`.

모델/제출 구조:
- `models_xgb_optuna/{YYYYMMDD_HHMM}/` — 모델, OOF, metric, debug 산출물
- `submission/{YYYYMMDD_HHMM}/` — 실제 제출 후보 CSV만 저장

---

## 타깃 레이블 설명

**출처**: `ch2026_metrics_description.pdf` (ETRI 2026 LifeLog Challenge 공식 문서)
**크로스체크**: `ch2026_metrics_train.csv` 직접 조사 — 7개 모두 `int64`, unique=`{0,1}`, NaN=0. **전부 이진 분류. 다중클래스 없음.**

| 컬럼 | 0 / 1 (counts) | pos rate | 의미 | 극성 |
|---|---|---|---|---|
| **Q1** | 227 / 223 | 0.496 | **Overall sleep quality** — 기상 직후 수면 품질 자기평가 (리커트 → 이진화) | 1 = 개인 평균 이상 (좋음) |
| **Q2** | 197 / 253 | 0.562 | **Physical fatigue** — 취침 직전 신체 피로도 | **1 = 피로 낮음 (역방향, 좋음)** |
| **Q3** | 180 / 270 | 0.600 | **Stress level** — 취침 직전 스트레스 수준 | **1 = 스트레스 낮음 (역방향, 좋음)** |
| **S1** | 143 / 307 | 0.682 | **TST (Total Sleep Time)** — NSF 권장 총 수면시간 범위 준수 | 1 = 권장 준수 (좋음) |
| **S2** | 157 / 293 | 0.651 | **SE (Sleep Efficiency)** — NSF 권장 수면 효율 준수 | 1 = 권장 준수 (좋음) |
| **S3** | 152 / 298 | 0.662 | **SOL (Sleep Onset Latency)** — NSF 권장 입면 지연시간 준수 | 1 = 권장 준수 (좋음) |
| **S4** | 198 / 252 | 0.560 | **WASO (Wake After Sleep Onset)** — NSF 권장 수면 중 각성시간 준수 ⚡ **2026 신규** | 1 = 권장 준수 (좋음) |

### 해석 시 주의
- **Q2 · Q3 는 극성 역방향**: 모델이 "Q2=1 예측" = "피로 낮음 예측". 피처 방향성 해석 시 부호 주의.
- **S1~S4 는 1=권장(좋음) 으로 통일**. S1~S3 은 비교적 불균형(pos ~66%)이라 AUPRC 기준선이 높음 → 모델 개선 마진이 좁음.
- **S4 는 2026 챌린지부터 신규 추가**된 WASO 지표. 이전 2024 챌린지 대비 검증 데이터 없음.
- **base rate (pos rate)** 가 AUPRC 하한선. 예: S1 모델의 AUPRC 가 0.682 이하면 무작위 예측보다 나쁘다는 뜻.
- 출처 측정: Q1~Q3 = 설문, S1~S4 = Withings Sleep Analyzer.

---

## P8 Bulk Sequence / Feature Quality Control

`gen_LOG_feature.ipynb`는 sensor sequence를 subject 전체로 뭉개지 않고 반드시 `subject_id + lifelog_date` 단위로 집계한다.

- `bulk_daily_*`: calendar day D 기준 sequence 통계. raw daily의 mean/std/min/max/sum/count와 중복을 줄이기 위해 `median`, `iqr`, `mad`, `range`, `first`, `last`, `last_minus_first`, `slope_per_hour`, diff 계열, pct-change, direction-change, EMA, rolling-last 계열만 생성.
- `bulk_sleep_*`: sleep-aligned window `D 20:00 ~ D+1 11:59` 기준 sequence 통계. 컬럼명은 daily와 분리한다.
- 대상 센서: `wHr`, `wPedo`, `mLight`, `wLight`, `mScreenStatus`, 제한된 numeric-code trajectory로 복구한 `mActivity`, 그리고 list-count 변환한 `mBle`, `mWifi`, `mAmbience`, `mUsageStats`.
- raw daily 단계에도 timestamp 정렬 기반 `*_diff_mean`, `*_diff_std`를 추가한다. `wHr.heart_rate`처럼 numeric array로 저장된 object 컬럼은 list-count가 아니라 numeric scalar 평균으로 변환 후 diff를 계산한다.
- HR/HRV는 sparse해도 삭제하지 않는다. 대신 `hr_{night|full|sleep}_count`, `hr_{night|full|sleep}_span_min`, `hrv_{night|full|sleep}_available` 품질 피처를 같이 저장한다.
- HRV는 원시 IBI/RR이 아니라 `RR(ms)=60000/HR` 기반 근사 피처다. 절대값보다 같은 생성 규칙 안에서의 상대 비교 신호로 사용한다.
- HRV 원본 피처는 유지하지만, 이미 별도 도메인 피처이므로 `hrv_*_lag1`, `hrv_*_prev*`, `hrv_*_diff1` 같은 2차 temporal history는 만들지 않는다.
- circadian rolling baseline은 current day를 포함하지 않고 subject별 날짜 정렬 후 `shift(1)` 기반 previous-only rolling으로 계산한다.
- 자동 제거 대상은 train+test 기준 상수 피처와 완전 중복 피처만이다. high-NaN 및 near-duplicate는 삭제하지 않고 report로 남긴다.

산출 report:

- `feature_quality_report_{RUN_TIMESTAMP}.csv`
- `feature_drop_log_{RUN_TIMESTAMP}.csv`
- `feature_near_duplicate_pairs_{RUN_TIMESTAMP}.csv`
- `sleep_alignment_audit_{RUN_TIMESTAMP}.csv`

---

## P9 Feature Cleanup Update

- `mActivity`는 이전 run에서 강한 신호였으므로 numeric code 집계를 복구한다. 동시에 `mActivity_ratio_{code}`, `mActivity_dominant_code`, `mActivity_dominant_ratio`, `mActivity_entropy`, `mActivity_transition_count`, `mActivity_transition_rate`를 함께 사용한다.
- sleep-aligned 활동 요약은 `mActivity_sleep_*` prefix로 분리한다. 기준 window는 `lifelog_date D`의 `D 20:00 ~ D+1 11:59`이다.
- `app_presleep2h_{category}` raw duration sum은 복구하고, `app_presleep2h_{category}_log1p`, `app_presleep2h_{category}_present`를 추가 후보로 둔다.
- `wPedo.step_frequency`, `wPedo.speed`는 고상관이지만 이전 성능 후보로 복구한다. 제거 여부는 label별 feature selection에 맡긴다.
- bulk sequence의 `median` 통계는 유지하며, `bulk_daily_*_median`, `bulk_sleep_*_median` 생성 여부를 feature assembly 단계에서 검증한다.
- `cal_month`, `cal_season`은 삭제하지 않는다. drift-sensitive 후보로 보고 `cal_month_sin`, `cal_month_cos`를 함께 생성해 label별 모델 선택에서 비교한다.

---

---

## P10 Full Feature Compression Embedding

- `embed_full_pca_00` ~ `embed_full_pca_31` are dense PCA features built from the full numeric feature matrix after merge and cleanup.
- Fit policy: train-only median imputation, train-only z-score scaling, then PCA with `n_components=32`.
- Apply policy: the same fitted transform is applied to test.
- Storage policy: hybrid merge only. The PCA embedding is appended into `X_train_full.parquet` and `X_test_full.parquet` together with existing handcrafted, bulk, and anchor features.
- Extra intermediate artifacts are also saved:
  - `intermediate/embed_full_pca_train.parquet`
  - `intermediate/embed_full_pca_test.parquet`
  - `intermediate/embed_full_pca_meta.json`

## Update Notes - Current Structure

- `anchor_window` is part of the final feature set and is recorded in `feature_manifest.json`.
- BLE/WiFi raw daily counts are not used as final raw features; subject-within transforms and persistence-style summaries are kept instead.
- A8 global guard runs after fill and can drop low-support / near-constant columns or winsorize outlier-heavy columns.
- Raw anchor sequence and intermediate artifacts are saved together with final parquet outputs:
  - `sequence/anchor_sequence_long_{train,test}.parquet`
  - `sequence/anchor_sequence_tensor_{train,test}.npz`
  - `sequence/anchor_sequence_index_{train,test}.parquet`
  - `intermediate/X_train_prefill_precleanup.parquet`
  - `intermediate/X_train_prefill_postcleanup.parquet`
---

## raw_flat XGB Core v2

`raw_flat/latest` is now the canonical feature builder for XGBoost input.

Default XGB input files:

- `raw_flat/latest/7_model_input/X_train.parquet`
- `raw_flat/latest/7_model_input/X_test.parquet`
- Versioned aliases:
  - `raw_flat/latest/7_model_input/X_train_xgb_core_v2.parquet`
  - `raw_flat/latest/7_model_input/X_test_xgb_core_v2.parquet`

Row unit:

- One row = `subject_id + lifelog_date + sleep_date`
- `lifelog_date` is the behavior/log day.
- `sleep_date` is the next-day sleep label date.
- XGB loaders keep keys for alignment, then exclude `sleep_date` from model features.

Design policy:

- 10-minute bins are intermediate artifacts, not direct XGB input.
- XGB receives compact row-level scalar features only.
- Full expanded raw_flat feature tables remain for debug/ablation, not default modeling.
- Existing `features/latest/X_train_full.parquet` is kept only for `features_full` or hybrid comparison modes.

Feature groups in `xgb_core_v2`:

- `idx_*`: sleep onset/wake/duration/midpoint, confidence, regularity, and presleep gap proxies.
- phase scalar features: daytime/evening/presleep/sleep/late-sleep/postwake activity, HR, HRV proxy, screen, app, movement, ambient ratios, and coverage.
- `raw_*`: fixed-clock period summaries for day/evening/night/after-midnight/morning.
- `cal_*`, `circ_*`, `activity_*`, `app_presleep2h_*`: compact reimplemented context blocks from the raw_flat builder.
- `subjhist_*`: same-subject history normalization features. Train rows use same-subject past rows only; test rows use same-subject train history.

Quality/debug files:

- `raw_flat/latest/7_model_input/xgb_core_feature_manifest_v2.json`
- `raw_flat/latest/7_model_input/xgb_core_feature_quality_report_v2.csv`
- `raw_flat/latest/7_model_input/sleep_proxy_quality_report_v2.csv`

Default XGB loader mode:

- `FEATURE_INPUT_MODE = "raw_minute_features"`

Comparison modes remain available:

- `features_full`
- `raw_flat_v2`
- `hybrid_raw_flat_v2`

---

## raw_minute_features XGB Input

`raw_minute_features/latest` is the current compact scalar input used by `predict_LOG_XGB.ipynb` when `FEATURE_INPUT_MODE = "raw_minute_features"`.

- Source input: `raw_minute_basic/latest/raw_minute_basic_filled.parquet`.
- Output tables:
  - `train_daily_clock_features.parquet`
  - `test_daily_clock_features.parquet`
  - `train_qs_timing_features.parquet`
  - `test_qs_timing_features.parquet`
  - `label_feature_manifest.json`
- Row unit: one row per `subject_id + lifelog_date + sleep_date`.
- XGB input is daily + Q/S timing scalar features merged one-to-one. The 1-minute table remains an intermediate source, not direct XGB input.

Fixed-clock window policy:

- `full_00_24`: `lifelog_date 00:00` to `sleep_date 00:00`.
- `morning_06_12`: `sleep_date 06:00` to `12:00`, for postwake morning activity.
- `afternoon_12_18`: `lifelog_date 12:00` to `18:00`, for daytime activity.
- `night_18_24`: `lifelog_date 18:00` to `sleep_date 00:00`, for evening/presleep behavior.
- `dawn_00_06`: `sleep_date 00:00` to `06:00`, for sleep disturbance.
- `evening_18_24` and `late_night_00_06` remain legacy-compatible aliases where already generated.
- `sleep_00_09`: `sleep_date 00:00` to `09:00`, a fixed sleep proxy, not a true sleep interval.
- `presleep_21_24`: `lifelog_date 21:00` to `sleep_date 00:00`.

Window-level scalar groups:

- HR/HRV proxy: `hr_{window}_{mean,std,min,max,resting,spike_cnt,spike_max,spike_density}` and `hrv_{window}_{avnn,sdnn,rmssd,pnn50}_proxy`.
- Pedometer/screen events: `step_{window}_sum`, `distance_{window}_sum`, `pedo_{window}_moving_bin_cnt`, `pedo_{window}_movement_burst_cnt`, `screen_{window}_{cnt,active_bin_cnt,burst_cnt}`.
- Light/activity/ambient: `light_{window}_{mean,max,spike_cnt}`, `activity_{window}_{not_still_cnt,moving_ratio}`, `ambient_{window}_{events,noise_ratio,speech_ratio,music_ratio}`.
- Social/app/coverage: `social_{ble,wifi}_{window}_{mean,max,std}`, `app_{window}_{minutes_sum,minutes_log1p,active_bin_cnt}`, and `cov_{sensor}_{window}`.

Fixed sleep proxy features:

- `sleep_00_09_hr_rmssd_proxy`
- `sleep_00_09_hr_spike_cnt`
- `sleep_00_09_hr_spike_max`
- `sleep_00_09_hr_spike_density`
- `sleep_00_09_pedo_step_sum`
- `sleep_00_09_movement_burst_cnt`
- `sleep_00_09_activity_not_still_cnt`
- `sleep_00_09_screen_on_cnt`
- `sleep_00_09_screen_burst_cnt`
- `sleep_00_09_light_spike_cnt`
- `sleep_00_09_fragmentation_score`

Temporal history and subject-relative policy:

- Selected high-signal daily-clock features get split-aware, subject-sorted `{feature}_lag1`, `{feature}_lag2`, `{feature}_roll3_mean`, `{feature}_roll7_mean`, `{feature}_roll7_std`, `{feature}_roll14_mean`, `{feature}_diff_lag1`, `{feature}_diff_roll7`, and `{feature}_subjz`.
- Rolling features are previous-only via `shift(1)`.
- Train and test are calculated separately; train/test rows are not mixed.
- Target encoding is intentionally excluded.

App usage policy:

- `mUsageStats.total_time` is interpreted as milliseconds.
- App time is converted to minutes, clipped to `0-10` minutes per timestamp, and category totals are rescaled when a timestamp exceeds 10 minutes.
- Default XGB features use `app_*_minutes_sum`, `app_*_minutes_log1p`, `app_*_active_bin_cnt`, and `app_presleep2h_*_{minutes_sum,minutes_log1p,present,share}`.
- Old raw-scale `app_*_time_sum` and raw `app_presleep2h_{category}` duration columns are excluded from the default output.

HRV policy:

- HRV features are HR-derived proxy signals using `RR(ms)=60000/HR`.
- Fixed-clock baseline HRV is retained: `hrv_full_*_proxy`, `hrv_day_*_proxy`, `hrv_night_*_proxy`, `hrv_presleep_*_proxy`.
- Sleep-anchor HRV is excluded from the default XGB input because screen-derived sleep-window HR coverage is sparse.
- Baseline deltas are added for model selection: `hrv_presleep_minus_day_rmssd_proxy`, `hrv_night_minus_day_rmssd_proxy`, `hr_presleep_minus_day_mean`, `hr_night_minus_day_mean`.

XGB selection/PCA policy:

- XGB feature selection uses `anchor_pair_backward_v2`, not gain-ranked prefix selection.
- When `FEATURE_INPUT_MODE = "raw_minute_features"`, candidate pools are label-aware via `raw_minute_features/latest/label_feature_manifest.json`.
- Q labels prioritize subject-relative/history and time transition features: `*_subjz`, `*_diff_lag1`, `*_diff_roll7`, `*_roll7_*`, `night_minus_afternoon_*`, `dawn_minus_night_*`, and `morning_minus_dawn_*`.
- S labels prioritize fixed sleep/dawn/presleep event features: `sleep_00_09_*`, `dawn_00_06_*`, `presleep_21_24_*`, HR/HRV proxy, screen/light/activity spike and burst counts.
- Selection flow:
  - score all single features with sampled CV logloss;
  - fix the best single feature as the anchor;
  - evaluate `anchor + candidate` for every label-manifest candidate;
  - keep only candidates whose pair logloss does not degrade versus the anchor;
  - run backward removal from the kept set, never removing the anchor.
- This keeps the "pair combination must not be negative" rule while avoiding full all-pair `O(p^2)` selection.
- PCA is supplemental, not a replacement for scalar features.
- PCA preprocessing is train-fit median fill, train 1/99 percentile clipping, `RobustScaler`, then PCA.
- PCA source tag: `pca_unsupervised_robust`.
- v21 disables seed/family XGB ensembles by default. Separate ensemble work should use exported OOF/submission files.
- XGB Optuna search now allows less regularized models (`max_depth` up to 6, lower `min_child_weight`/`reg_lambda`) and postprocess temperature includes stronger sharpening candidates down to `0.25`.

---

## Current Feature Inventory

This is the current modeling feature structure used around `predict_LOG_XGB.ipynb`.

### 1. `raw_minute_basic`

Path:

- `raw_minute_basic/latest/raw_minute_basic.parquet`
- `raw_minute_basic/latest/raw_minute_basic_filled.parquet`

Role:

- 1-minute aligned raw sensor table.
- Filled values are sampling-rate-aware nearest/limited fills.
- `obs_*` columns are observation flags and should not be used directly as model features.
- `obs_*` should be converted to window coverage features such as `cov_wHr_sleep_00_09`.

### 2. `raw_minute_features`

Path:

- `raw_minute_features/latest/train_daily_clock_features.parquet`
- `raw_minute_features/latest/test_daily_clock_features.parquet`
- `raw_minute_features/latest/train_qs_timing_features.parquet`
- `raw_minute_features/latest/test_qs_timing_features.parquet`

Role:

- Current default scalar XGB input when `FEATURE_INPUT_MODE = "raw_minute_features"`.
- One row per `subject_id + lifelog_date + sleep_date`.
- Daily clock and Q/S timing features are merged in the XGB loader.

Main feature groups:

- Fixed time windows:
  - `full_00_24`
  - `morning_06_12`
  - `afternoon_12_18`
  - `evening_18_24`
  - `late_night_00_06`
  - `sleep_00_09`
  - `presleep_21_24`
- HR:
  - `hr_{window}_mean`
  - `hr_{window}_std`
  - `hr_{window}_min`
  - `hr_{window}_max`
  - `hr_{window}_resting`
  - `hr_{window}_spike_cnt`
  - `hr_{window}_spike_max`
  - `hr_{window}_spike_density`
- HRV proxy:
  - `hrv_{window}_avnn_proxy`
  - `hrv_{window}_sdnn_proxy`
  - `hrv_{window}_rmssd_proxy`
  - `hrv_{window}_pnn50_proxy`
- Pedometer/activity:
  - `step_{window}_sum`
  - `distance_{window}_sum`
  - `pedo_{window}_moving_bin_cnt`
  - `pedo_{window}_movement_burst_cnt`
  - `activity_{window}_not_still_cnt`
  - `activity_{window}_moving_ratio`
- Screen/app:
  - `screen_{window}_cnt`
  - `screen_{window}_active_bin_cnt`
  - `screen_{window}_burst_cnt`
  - `app_{window}_minutes_sum`
  - `app_{window}_minutes_log1p`
  - `app_{window}_active_bin_cnt`
  - `app_presleep2h_{category}_{minutes_sum,minutes_log1p,present,share}`
- Light/social/ambient:
  - `light_{window}_mean`
  - `light_{window}_max`
  - `light_{window}_spike_cnt`
  - `social_ble_{window}_{mean,max,std}`
  - `social_wifi_{window}_{mean,max,std}`
  - `ambient_{window}_{events,noise_ratio,speech_ratio,music_ratio}`
- Coverage:
  - `cov_{sensor}_{window}`

### 3. Fixed Sleep Proxy Features

`sleep_00_09` is a fixed proxy window from `sleep_date 00:00` to `09:00`.
It is not treated as ground-truth sleep, but it is stable and useful for S labels.

Priority features:

- `sleep_00_09_hr_rmssd_proxy`
- `sleep_00_09_hr_spike_cnt`
- `sleep_00_09_hr_spike_max`
- `sleep_00_09_hr_spike_density`
- `sleep_00_09_pedo_step_sum`
- `sleep_00_09_movement_burst_cnt`
- `sleep_00_09_activity_not_still_cnt`
- `sleep_00_09_screen_on_cnt`
- `sleep_00_09_screen_burst_cnt`
- `sleep_00_09_light_spike_cnt`
- `sleep_00_09_fragmentation_score`

### 4. Temporal And Subject-Relative Features

Only selected high-signal scalar features should receive these expansions:

- `{feature}_lag1`
- `{feature}_lag2`
- `{feature}_roll3_mean`
- `{feature}_roll7_mean`
- `{feature}_roll7_std`
- `{feature}_roll14_mean`
- `{feature}_diff_lag1`
- `{feature}_diff_roll7`
- `{feature}_subjz`

Policy:

- Lag/rolling features are previous-only via `shift(1)`.
- Train and test are calculated separately.
- Target encoding is excluded.
- `subjz` is split-local subject normalization, not target-derived encoding.

### 5. PCA Features

`pca_raw_minute_*` features are optional supplemental features in `predict_LOG_XGB.ipynb`.

Policy:

- PCA is appended before SFS.
- It does not replace raw scalar features.
- Preprocessing is train-fit median imputation, 1/99 percentile clipping, `RobustScaler`, then PCA.

### 6. Sequence DNN Features

DNN input path:

- `raw_minute_features/latest/sequence_10m/`

Required files:

- `raw_sequence_10m_tensor_train.npz`
- `raw_sequence_10m_tensor_test.npz`
- `raw_sequence_10m_metadata.json`

Role:

- Used by `predict_LOG_DNN.ipynb`.
- Model is channel-wise CNN + BiLSTM with label-specific binary training for `Q1~S4`.
- Spectral features are auxiliary FFT-derived vectors, not a separate frequency CNN branch.
- Not direct XGB input.
- Normalization should be fold-train based in the DNN training code.
---

## raw_minute timeblock 260430 XGB input

Default compact XGB input files:

- `experiments/260430_timeblock_xgb/features/train_timeblock_features_260430.parquet`
- `experiments/260430_timeblock_xgb/features/test_timeblock_features_260430.parquet`
- `experiments/260430_timeblock_xgb/features/label_feature_manifest_260430.json`
- `experiments/260430_timeblock_xgb/features/raw_minute_feature_summary_260430.csv`

Compatibility copies are also kept at:

- `raw_minute_features/latest/train_timeblock_features_260430.parquet`
- `raw_minute_features/latest/test_timeblock_features_260430.parquet`
- `raw_minute_features/latest/label_feature_manifest_260430.json`
- `raw_minute_features/latest/raw_minute_feature_summary_260430.csv`

Unit: one row per `subject_id + lifelog_date + sleep_date`.

This is the compact default set. The larger `train_daily_clock_features.parquet`
and `train_qs_timing_features.parquet` remain available only for debug/ablation.

Feature blocks:

- fixed time blocks: `morning_06_12`, `afternoon_12_18`, `night_18_24`, `dawn_00_06`
- sleep proxy: `sleep_00_09`
- presleep proxy: `presleep_21_24`
- limited subject-relative/trend features: `roll7_mean`, `roll7_std`, `diff_lag1`, `subjz`
- event features: screen bursts, movement bursts, HR spikes, light spikes, ambient events
- coverage features: selected `cov_*` columns only
- public weather / air-quality slot:
  - `wx_temp_mean`, `wx_temp_min`, `wx_temp_max`, `wx_precip_sum`, `wx_humidity_mean`, `wx_wind_mean`, `wx_sunshine_h`, `wx_cloud_mean`
  - `air_pm10`, `air_pm25`, `air_o3`, `air_no2`, `air_co`, `air_so2`
  - `wx_available`, `air_available`
  - source APIs: KMA ASOS daily, AirKorea daily station statistics
  - if the public data API returns `403` or no authorized service response, these columns remain `NaN` and the pipeline continues

Current generated shape:

- train: `450 x 339`
- test: `250 x 339`
- model features: `336`

`predict_LOG_XGB.ipynb` default mode:

```python
FEATURE_INPUT_MODE = "raw_minute_timeblock_260430"
ADD_PCA_FEATURES = False
```

Label candidate pools are read from `label_feature_manifest_260430.json`.
Q labels prefer time-transition and subject-relative features. S labels prefer
sleep/dawn/presleep event and stability features.
## 260430 raw-minute timeblock compact XGB features

Active experiment files:

- `experiments/260430_timeblock_xgb/notebooks/gen_LOG_raw_minute_features_260430.ipynb`
- `experiments/260430_timeblock_xgb/features/train_timeblock_features_260430.parquet`
- `experiments/260430_timeblock_xgb/features/test_timeblock_features_260430.parquet`
- `experiments/260430_timeblock_xgb/features/label_feature_manifest_260430.json`

Feature unit: one row per `subject_id + lifelog_date + sleep_date`.

Fixed time blocks:

- `morning_06_12`
- `afternoon_12_18`
- `night_18_24`
- `dawn_00_06`
- `sleep_00_09`
- `presleep_21_24`

Compact feature policy:

- Keep scalar XGB features only. Ten-minute sequence artifacts are for DNN/TCN.
- Keep label-aware manifest pools instead of SFS search.
- Preserve outlier/disturbance signal as features, not by clipping it away.

Added derivative/outlier groups:

- HR: `median`, `iqr`, `p95`, `range`, `spike_cnt`, `spike_max`, `successive_abs_diff_mean`, `successive_abs_diff_max`.
- Light: `median`, `iqr`, `p95`, `spike_cnt`, `successive_abs_diff_max`.
- Step/social: selected successive absolute difference summaries.
- Ambience: `high_score_event_cnt` in addition to event/noise/speech ratios.
- Transition: `night_minus_afternoon_*`, `dawn_minus_night_*`, `morning_minus_dawn_*`, `sleep_00_09_minus_day_hr_mean`.
- History/relative: selected `roll7_mean`, `roll7_std`, `diff_lag1`, `diff_roll7`, `subjz`.

Current generated shape:

- train: 450 rows, 522 model features plus keys
- test: 250 rows, 522 model features plus keys

---
