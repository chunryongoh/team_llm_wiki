---
id: 2026-05-29-v186-shap-leaderboard-analysis
type: performance
packet_type: performance
title: v186 shap leaderboard analysis
date: 2026-05-29
owner: moon-hyungdo
claim_status: tentative
claim_boundary: PDF and Slack-reported v186 public leaderboard and SHAP analysis only; DACON leaderboard export, submission id, private score, submission CSV lineage, and ablation evidence are not included.
dataset: sleep-lifelog-2024
benchmark: sleep-health-hackathon-v0
model: v186-target-specific-lgbm-catboost-blend
summary: v186 public LB와 SHAP 해석은 유용한 report지만 leaderboard provenance와 ablation evidence가 없어 tentative public score observation으로만 유지한다.
review_required: true
raw_evidence:
- raw/users/moon-hyungdo/performance/2026-05-29-v186-shap-leaderboard-analysis/manifest.yaml
- raw/users/moon-hyungdo/performance/2026-05-29-v186-shap-leaderboard-analysis/metrics.json
- raw/users/moon-hyungdo/performance/2026-05-29-v186-shap-leaderboard-analysis/performance.yaml
- raw/users/moon-hyungdo/performance/2026-05-29-v186-shap-leaderboard-analysis/packet.md
---

# v186 shap leaderboard analysis

문형도 packet `2026-05-29-v186-shap-leaderboard-analysis`는 v186 target-specific LGBM/CatBoost blend의 public LB report와 SHAP interpretation을 제공한다. 이 page는 [DACON Leaderboard History](../submissions/dacon-leaderboard-history.md), [Current Supported Claims](../claims/current-supported-claims.md), [Sleep Lifelog Feature Landscape](../features/sleep-lifelog-feature-landscape.md)에 연결된다.

## Evidence boundary

- status: `tentative`
- public score evidence: `user_reported_public_score_only`
- OOF evidence: `pdf_report_oof_summary`
- missing: DACON leaderboard export, submission id, private score, submission CSV lineage, ablation raw metrics

## Reported metrics

| metric | value | boundary |
|---|---:|---|
| `public_lb_logloss` | `0.5922831771` | PDF/Slack-reported public score |
| `v186_mean_oof_logloss` | `0.6167` | PDF OOF summary |
| `S1` OOF | `0.5597` | best target note |
| `S4` OOF | `0.666` | worst target note |

## Feature interpretation

Q-family는 sensor-derived daily routine proxy, S1/S2는 transition weighted refit, S3/S4는 sleep-episode, GPS stillness, quiet streak 계열로 해석된다. 그러나 SHAP feature importance는 모델이 사용한 근거일 뿐 causal proof나 ablation evidence가 아니다.

## Current-best 경계

v186은 보고된 public score 중 강한 후보일 수 있지만, [LGB CB Reproduction Local OOF Diagnostic](../performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic.md)의 supported local OOF claim과 같은 evidence surface가 아니다.

## 다음 확인

`v186-leaderboard-provenance`를 닫으려면 DACON submission id, leaderboard export, submission CSV, local run mapping이 필요하다.
