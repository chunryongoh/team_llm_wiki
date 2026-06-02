# 이번 주 진행 요약: 2026-05-21 ~ 2026-05-29

## 한 줄 결론

현재 최고 제출은 `section9_labelwise_best_20260522_1239.csv`이고 public score는 `0.5986218188`이다.  
가장 가까운 재학습 후보는 `section07_candidate_baseline_seed_ensemble_20260529_1029.csv`이며 public score는 `0.6003735255`로, 아직 교체 대상은 아니다.

## 버전별 핵심

| 버전 | 내용 | 판단 |
|---|---|---|
| `04` | 922 feature 기반 clean anchor 재현 | 기본 축 확인 |
| `09` | labelwise fixed Optuna, label별 feature/model 고정 | 현재 최고 public `0.5986218188` |
| `10` | 2h/2.5h/3h window bag 학습 | Q3 쪽 temporal signal 확인 |
| `11` | additive feature top-k selection | Q2/Q3/S3는 추가 feature 후보, S4는 base 유지 |
| `05` | subject-relative + subject-hole CV | stress 검증용. primary 기준으로 쓰기엔 약함 |
| `06` | Boruta/shadow + constrained XGB | Q2/Q3 개선 없음, S4 소폭 local gain |
| `07` | Section4 방식 재학습 + seed ensemble | public `0.6003735255`, near-best지만 best는 아님 |
| `07-v5` | change/frequency feature probe | Q3 악화. 전역 추가는 보류 |

## 지금까지 가장 중요한 판단

- `0.5986218188`이 현재 기준점이다.
- `0.6003735255`는 재학습 가능한 근접 baseline이지만, 점수상 후퇴다.
- 단순히 feature를 더 늘리면 좋아지는 구조가 아니다.
- Q3가 가장 중요한 병목으로 보이고, daily aggregate feature 추가보다 window/temporal representation 쪽이 더 설득력 있다.
- S4는 feature 추가가 자주 악화된다. 좁은 sleep disturbance/WASO proxy만 조심스럽게 봐야 한다.

## 다음 작업 우선순위

1. `mix_lgbm_catboost + seed ensemble` 축에서 모델 최적화부터 한다.
2. Q3는 Section 10 window 결과를 바탕으로 별도 temporal feature 또는 Q3-only blend를 만든다.
3. v5 change/frequency feature는 전체 적용하지 않는다.
4. subject-hole CV는 최종 선택 기준이 아니라 위험도 체크용으로만 쓴다.
5. Q2/Q3/S4만 별도 개선 대상으로 두고, S1/S2/S3의 안정 label은 과도하게 흔들지 않는다.
