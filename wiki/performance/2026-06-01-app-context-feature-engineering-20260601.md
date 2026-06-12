---
id: 2026-06-01-app-context-feature-engineering-20260601
type: performance
packet_type: performance
title: app context feature engineering 20260601
date: 2026-06-01
owner: cho-hyewon
claim_status: tentative
claim_boundary: DOCX-reported feature engineering and public LB observation only; raw metric JSON, submission id, leaderboard export, private score, and same-split local OOF evidence are not included.
dataset: sleep-lifelog-2024
benchmark: sleep-health-hackathon-v0
model: lgbm-catboost-app-context-ensemble
summary: app-name daily/evening feature와 presleep/night/early-morning app context feature가 public LB 관찰값을 단계적으로 개선했다는 보고지만, leaderboard lineage가 없어 tentative로 유지한다.
review_required: true
raw_evidence:
- raw/users/cho-hyewon/performance/2026-06-01-app-context-feature-engineering-20260601/manifest.yaml
- raw/users/cho-hyewon/performance/2026-06-01-app-context-feature-engineering-20260601/metrics.json
- raw/users/cho-hyewon/performance/2026-06-01-app-context-feature-engineering-20260601/performance.yaml
- raw/users/cho-hyewon/performance/2026-06-01-app-context-feature-engineering-20260601/packet.md
---

# app context feature engineering 20260601

이 page는 조혜원 packet `2026-06-01-app-context-feature-engineering-20260601`의 안정 review다. 관련 dataset은 [Sleep Lifelog 2024 Dataset](../preprocessing/sleep-lifelog-2024.md), 평가 경계는 [Sleep Lifelog Evaluation Protocol](../decisions/sleep-lifelog-evaluation-protocol.md)과 [DACON Leaderboard History](dacon-leaderboard-history.md)를 따른다.

## Claim boundary

- status: `tentative`
- evidence surface: `docx_report_public_lb_observation`
- split note: `20260526-172609-lgbcat-timesplit-public-lb-observation`
- missing: DACON submission id, leaderboard export, private score, same-split local OOF, feature list hash

따라서 이 packet은 app-context feature hypothesis로는 강하지만 verified leaderboard claim이나 final best model claim이 아니다.

## 보고된 staged observation

| stage | evidence surface | logloss |
|---|---|---:|
| sleep/HR/sequence/entropy baseline | DOCX public LB observation | `0.6218831823` |
| app-name daily/evening 추가 | DOCX public LB observation | `0.6182941107` |
| presleep/night/early-morning app context 추가 | DOCX public LB observation | `0.6106185586` |

핵심 feature family는 `kakao`, `youtube`, `instagram`, `naver`, `bible_religion`, `call_phone`, `message_sms`, `usage_entropy`, `app_switch_count`, `arousal_mix_index`, `reflection_vs_stim_ratio`이다. 이는 [Sleep Lifelog Feature Landscape](../features/sleep-lifelog-feature-landscape.md)의 app-context 후보로만 반영한다.

## 해석과 위험

이 보고는 하루 총 앱 사용보다 수면에 가까운 시간창의 app context가 더 강한 신호일 수 있음을 제안한다. 다만 Q3는 여전히 낮은 성능 target으로 남았고, app context가 Q3를 해결했다는 증거는 없다. public LB 관찰값은 [Current Supported Claims](../claims/current-supported-claims.md)에서 tentative로만 추적한다.

## 다음 확인

Open question `app-context-raw-submission-lineage`: 세 stage의 submission CSV lineage, leaderboard export, local OOF metric table, feature list hash를 제출해야 한다.
