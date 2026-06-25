---
id: 2026-06-25-wave43-claude-campaign-stack-local-oof-projection
type: performance
owner: chunryongoh
date: 2026-06-25
claim_status: supported
---

# Wave43 Claude Campaign Stack Local OOF Projection

## 요약

현재 디렉토리에서 Claude가 별도로 진행한 wave43 캠페인 결과를 team LLM wiki에 연결하기 위한 raw packet이다.
핵심 결론은 `raw/results/2026-06-24-wave43-stack-v2/metrics.json` 기준 최종 `stack-v2`가
same-subject-hole local OOF에서 calibrated macro log-loss `0.5897217743642561`을 기록했다는 점이다.
이 값은 subject-mean baseline `0.6245305092520156` 대비 `-0.0348087348877595` 개선이다.

public leaderboard에 대해서는 claim boundary를 분리한다. Claude 진행 로그에는 public `0.60761`까지의 개선이 기록되어 있고,
최종 calibrated stack의 projected public은 `0.5927217743642561`로 계산되었지만, 이 packet에는 official leaderboard export가 없다.
따라서 wiki에서는 local OOF claim과 public observation/projection claim을 같은 강도로 취급하면 안 된다.

## Claude 작업 흐름

Claude는 2026-06-23부터 2026-06-25까지 wave43 캠페인을 누적 진행했다.
초기에는 targetwise LightGBM/CatBoost baseline과 subject prior, spectral/circadian 계열을 확인했고,
이후 sliding-window, sequence/SSL, deep-tabular, XGB bag, Withings-mat mimic, actigraphy scorer, transfer/domain-shift 계열을 순차적으로 탐색했다.

중요한 전환점은 feature family가 단일 대형 feature set이 아니라 target별 약점을 보완하는 여러 후보 모델군으로 확장된 것이다.
최종 `stack-v2`는 target별 236-238개 후보를 모아 nested same-subject-hole stack과 target별 calibration을 적용했다.

## Preprocessing / Validation

- split: `same-subject-hole-5fold-temporal-by-subject`
- 원칙: 같은 subject의 temporal hole을 fold별로 비워 local OOF를 만들고, test/full-train에서는 subject prior를 fold-safe 방식으로 사용한다.
- leakage boundary: pseudo-labeling은 사용하지 않았고, public/private leaderboard claim과 local OOF claim은 분리한다.
- 불확실성: organizer-official split과 private leaderboard semantics가 공개되면 이 split 정책은 재검토되어야 한다.

## Feature Families

- sliding-window/intraday: 일중 시간대별 aggregation과 window feature로 Q2/Q3 신호를 처음 유의미하게 끌어냈다.
- Withings-mat mimic: 충전/집-정박 상태를 이용해 침대 체류 또는 수면 환경을 간접 추정했고 S1에서 강했다.
- actigraphy scorer: Cole-Kripke/Sadeh 계열 fixed coefficient를 사용해 S3를 크게 개선했다.
- WASO/sleep physiology: S2/S4 보완을 노렸지만 최종 stack을 직접 이기지는 못했다.
- SSL/contrastive/deep-tabular/sequence: standalone로 최종 stack을 대체하지는 못했으나 candidate pool 확장에 쓰였다.
- transfer/domain shift: SLEEPACCEL external LOSO AUC는 높았지만 ETRI final target log-loss 개선으로 직접 연결되지는 않았다.

## Model / Stacking

최종 모델은 단일 모델이 아니라 target별 후보 모델 pool 위의 stacked ensemble이다.
후보에는 LightGBM/CatBoost/XGBoost, subject prior 변형, temporal/window feature 모델, sequence/SSL/deep-tabular 계열, domain-specific sleep feature 모델이 포함된다.
최종 선택은 nested same-subject-hole OOF와 target별 calibration으로 이루어졌다.

Calibration은 Q1/Q2/S3/S4에 temperature, S2에 platt, Q3/S1에는 none으로 기록되어 있다.

## Performance

| Surface | Metric |
| --- | ---: |
| Subject-mean baseline macro | 0.6245305092520156 |
| Equal-all baseline macro | 0.6157419292915838 |
| Stack nested macro | 0.5946367652711365 |
| Calibrated stack macro | 0.5897217743642561 |
| Projected public macro | 0.5927217743642561 |
| Best observed public in Claude log | 0.60761 |

Target-level calibrated log-loss:

| Target | Log-loss | Calibration |
| --- | ---: | --- |
| Q1 | 0.6450606619738299 | temp |
| Q2 | 0.6455155286285766 | temp |
| Q3 | 0.650460985046031 | none |
| S1 | 0.5084141950084338 | none |
| S2 | 0.5561343457335379 | platt |
| S3 | 0.5168327857279124 | temp |
| S4 | 0.6056339184314705 | temp |

## 해석

`0.57`대가 불가능하다는 이전 판단은 아직 완전히 반증된 것은 아니지만, Q-family 신호가 거의 없다는 식의 강한 판단은 superseded로 봐야 한다.
sliding-window와 stack campaign이 Q2/Q3 신호를 일부 끌어냈고, S1/S3는 각각 Withings-mat mimic과 actigraphy scorer가 분명한 후보 방향을 보여줬다.

반면 S4는 여전히 가장 어려운 축이다. WASO와 transfer 방향은 의미 있는 domain hypothesis이지만 final stack을 안정적으로 넘는 성능 증거는 아직 없다.

## Wiki 업데이트 의도

이 packet은 wiki에 raw packet mirror 하나를 만드는 것이 목적이 아니다.
ingest/synthesis는 다음 stable entity들을 갱신해야 한다.

- wave43 campaign performance summary
- same-subject-hole validation policy
- leaderboard claim boundary
- wave43 feature family map
- wave43 stacked ensemble model page
- S1/S3 target insight pages
- Q3/S4 bottleneck pages
- open validation gaps and next actions

## Evidence Gaps

- `0.60761` public score에 대한 official leaderboard export 또는 submission hash가 필요하다.
- `0.59272`는 projected public이며 official public/private result가 아니다.
- OOF prediction arrays와 final submission CSV는 로컬 ETRI raw tree에 남아 있고 packet에는 metric/code snapshot만 복사했다.
- confusion matrix, AUROC, AUPRC는 final stack evidence로 정리되어 있지 않다.
- batch correction/domain adaptation 계열은 partial run이 많아 final claim으로 승격하지 않는다.
