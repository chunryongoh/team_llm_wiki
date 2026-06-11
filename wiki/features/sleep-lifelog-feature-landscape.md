---
id: sleep-lifelog-feature-landscape
type: feature-landscape
title: Sleep Lifelog Feature Landscape
dataset: sleep-lifelog-2024
benchmark: sleep-health-hackathon-v0
status: active-review-required
last_updated: 2026-06-02
summary: sleep-lifelog feature memory는 app context, 1,875 sensor feature pool, v186 SHAP, sparse splice, Section07 target policy를 claim boundary별로 분리해 관리한다.
review_required: true
raw_evidence:
- raw/users/cho-hyewon/performance/2026-06-01-app-context-feature-engineering-20260601/manifest.yaml
- raw/users/cho-hyewon/performance/2026-06-01-app-context-feature-engineering-20260601/metrics.json
- raw/users/cho-hyewon/performance/2026-06-01-app-context-feature-engineering-20260601/packet.md
- raw/users/cho-hyewon/performance/2026-06-01-app-context-feature-engineering-20260601/performance.yaml
- raw/users/cho-hyewon/performance/2026-06-01-app-context-feature-engineering-20260601/source/feature-engineering-result-report-20260601.docx
- raw/users/cho-hyewon/performance/2026-06-01-app-context-feature-engineering-20260601/source/feature-engineering-result-report-20260601.txt
- raw/users/cho-hyewon/performance/2026-06-01-app-context-feature-engineering-20260601/wiki_plan.yaml
- raw/users/hyeonseokrock/experiments/2026-05-29-labelwise-weekly-progress-target-bottlenecks/manifest.yaml
- raw/users/hyeonseokrock/experiments/2026-05-29-labelwise-weekly-progress-target-bottlenecks/evidence.yaml
- raw/users/hyeonseokrock/experiments/2026-05-29-labelwise-weekly-progress-target-bottlenecks/metrics.json
- raw/users/hyeonseokrock/experiments/2026-05-29-labelwise-weekly-progress-target-bottlenecks/packet.md
- raw/users/hyeonseokrock/experiments/2026-05-29-labelwise-weekly-progress-target-bottlenecks/source/weekly-progress-20260521-20260529-ko-short.md
- raw/users/hyeonseokrock/experiments/2026-05-29-labelwise-weekly-progress-target-bottlenecks/source/prompt4llmwiki.txt
- raw/users/hyeonseokrock/experiments/2026-05-29-labelwise-weekly-progress-target-bottlenecks/wiki_plan.yaml
- raw/users/ko-nayoung/features/2026-05-28-1875-feature-domain-ablation-and-dedup/manifest.yaml
- raw/users/ko-nayoung/features/2026-05-28-1875-feature-domain-ablation-and-dedup/features.yaml
- raw/users/ko-nayoung/features/2026-05-28-1875-feature-domain-ablation-and-dedup/packet.md
- raw/users/ko-nayoung/features/2026-05-28-1875-feature-domain-ablation-and-dedup/source/20260528-notebook-outputs.docx
- raw/users/ko-nayoung/features/2026-05-28-1875-feature-domain-ablation-and-dedup/source/20260528-notebook-outputs.txt
- raw/users/ko-nayoung/features/2026-05-28-1875-feature-domain-ablation-and-dedup/source/feature-info.pdf
- raw/users/ko-nayoung/features/2026-05-28-1875-feature-domain-ablation-and-dedup/source/feature-info.txt
- raw/users/ko-nayoung/features/2026-05-28-1875-feature-domain-ablation-and-dedup/wiki_plan.yaml
- raw/users/moon-hyungdo/experiments/2026-05-29-v200-v209-sparse-splice-review/manifest.yaml
- raw/users/moon-hyungdo/experiments/2026-05-29-v200-v209-sparse-splice-review/evidence.yaml
- raw/users/moon-hyungdo/experiments/2026-05-29-v200-v209-sparse-splice-review/metrics.json
- raw/users/moon-hyungdo/experiments/2026-05-29-v200-v209-sparse-splice-review/packet.md
- raw/users/moon-hyungdo/experiments/2026-05-29-v200-v209-sparse-splice-review/source/etri-2026-v2-review.pdf
- raw/users/moon-hyungdo/experiments/2026-05-29-v200-v209-sparse-splice-review/source/etri-2026-v2-review.txt
- raw/users/moon-hyungdo/experiments/2026-05-29-v200-v209-sparse-splice-review/wiki_plan.yaml
- raw/users/moon-hyungdo/performance/2026-05-29-v186-shap-leaderboard-analysis/manifest.yaml
- raw/users/moon-hyungdo/performance/2026-05-29-v186-shap-leaderboard-analysis/metrics.json
- raw/users/moon-hyungdo/performance/2026-05-29-v186-shap-leaderboard-analysis/packet.md
- raw/users/moon-hyungdo/performance/2026-05-29-v186-shap-leaderboard-analysis/performance.yaml
- raw/users/moon-hyungdo/performance/2026-05-29-v186-shap-leaderboard-analysis/source/etri-2026-v186-shap-analysis.pdf
- raw/users/moon-hyungdo/performance/2026-05-29-v186-shap-leaderboard-analysis/source/etri-2026-v186-shap-analysis.txt
- raw/users/moon-hyungdo/performance/2026-05-29-v186-shap-leaderboard-analysis/source/v186-top10-feature-meaning-ko.md
- raw/users/moon-hyungdo/performance/2026-05-29-v186-shap-leaderboard-analysis/wiki_plan.yaml
---

# Sleep Lifelog Feature Landscape

이 page는 [Sleep Lifelog 2024 Dataset](../datasets/sleep-lifelog-2024.md)와 [Sleep Health Hackathon Benchmark v0](../benchmarks/sleep-health-hackathon-v0.md)의 feature family를 성능 claim과 분리해 합성한다. 성능 승격 규칙은 [Sleep Lifelog Evaluation Protocol](../decisions/sleep-lifelog-evaluation-protocol.md), 미해결 검증은 [Sleep Lifelog Open Questions](../questions/sleep-lifelog-open-questions.md)를 따른다.

이 page는 hub다. 상세한 durable entity memory는 [App Context Windows](app-context-windows.md), [Q3 Stress Bottleneck](../targets/q3-stress-bottleneck.md), [S4 WASO Disturbance](../targets/s4-waso-disturbance.md), [v186 Targetwise LGBM CatBoost](../models/v186-targetwise-lgbm-catboost.md) 같은 leaf page에서 관리한다.

## Feature memory by evidence surface

| family | provenance | 현재 해석 | status |
|---|---|---|---|
| LGB/CB reproduction feature scope | `2026-06-01-lgb-cb-reproduction-local-oof-diagnostic` | transductive statistics, global train median imputer, subject encoding, date/rolling alignment risk가 있어 local diagnostic boundary를 좁힌다. | supported claim의 leakage boundary |
| [app-name and app-context windows](app-context-windows.md) | `2026-06-01-app-context-feature-engineering-20260601` | actual app names와 presleep/night/early-morning context가 strong hypothesis이나 public LB lineage가 없다. | tentative |
| 1,875 sensor/Timing Entropy pool | `2026-05-28-1875-feature-domain-ablation-and-dedup` | feature count보다 dedup, fold scope, target-specific exception이 중요하다. | tentative |
| [v186 SHAP target drivers](../models/v186-targetwise-lgbm-catboost.md) | `2026-05-29-v186-shap-leaderboard-analysis` | Q는 daily routine proxy, S는 sleep-episode/transition proxy가 강하다는 feature-importance note다. | tentative |
| v200-v209 sparse splice | `2026-05-29-v200-v209-sparse-splice-review` | broad morphology reset은 negative evidence이고 sparse micro-splice만 guardrail 후보로 남는다. | tentative |
| Section07 target bottlenecks | `2026-05-29-labelwise-weekly-progress-target-bottlenecks` | [Q3](../targets/q3-stress-bottleneck.md)는 frequency/window 후보, [S4](../targets/s4-waso-disturbance.md)는 narrow WASO/disturbance proxy가 필요하다. | tentative |

## Compounded feature rules

1. SHAP 중요도, notebook-output ablation, user-reported public score는 서로 다른 evidence surface다.
2. App context는 Q3 해결 claim이 아니라 feature hypothesis로만 유지한다.
3. `Light-W` removal이나 BLE/WiFi removal은 global rule이 아니다. Q3 target-specific exception이 먼저 검증되어야 한다.
4. `715` dedup candidate는 exact list와 post-pruning metric이 있어야 feature policy가 된다.
5. Q2/Q3/S4처럼 fragile target은 average score보다 per-target regression을 우선 확인한다.

## Raw provenance

- `raw/users/cho-hyewon/performance/2026-06-01-app-context-feature-engineering-20260601/`
- `raw/users/ko-nayoung/features/2026-05-28-1875-feature-domain-ablation-and-dedup/`
- `raw/users/moon-hyungdo/performance/2026-05-29-v186-shap-leaderboard-analysis/`
- `raw/users/moon-hyungdo/experiments/2026-05-29-v200-v209-sparse-splice-review/`
- `raw/users/hyeonseokrock/experiments/2026-05-29-labelwise-weekly-progress-target-bottlenecks/`
- `raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/`
