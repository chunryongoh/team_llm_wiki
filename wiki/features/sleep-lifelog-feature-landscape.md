---
id: sleep-lifelog-feature-landscape
type: feature-landscape
page_role: hub
title: Sleep Lifelog Feature Landscape
dataset: sleep-lifelog-2024
benchmark: sleep-health-hackathon-v0
status: active-review-required
last_updated: 2026-06-12
summary: sleep-lifelog feature memory는 app context, 1875 pool, v186 SHAP, sparse splice, stability filtering, window-pair reference를 evidence surface별로 분리해 관리한다.
review_required: true
raw_evidence:
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/manifest.yaml
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/artifact_summary.json
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/dacon-public-05917-lgbm-xgb-anchor-subject-hole.ipynb
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/metrics.json
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/packet.md
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/packet_entity_graph.json
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/performance.yaml
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/question_queue.yaml
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/scan-metrics.csv
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/semantic_lint.json
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/dacon-codeshare-13975.md
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/wiki_plan.yaml
---

# Sleep Lifelog Feature Landscape

이 page는 [Sleep Lifelog 2024 Dataset](../preprocessing/sleep-lifelog-2024.md) feature families의 hub다. 성능 승격은 [Sleep Lifelog Evaluation Protocol](../decisions/sleep-lifelog-evaluation-protocol.md), split/leakage 판단은 [Canonical Split And Leakage Policy](../preprocessing/canonical-split-and-leakage-policy.md), unresolved work는 [Sleep Lifelog Open Questions](../targets/sleep-lifelog-open-issues.md)를 따른다.

상세 durable memory는 leaf가 소유한다: [App Context Windows](app-context-windows.md), [Stability Filtered Feature Selection](stability-filtered-feature-selection.md), [Q3 Stress Bottleneck](../targets/q3-stress-bottleneck.md), [S4 WASO Disturbance](../targets/s4-waso-disturbance.md), [v186 Targetwise LGBM CatBoost](../models/v186-targetwise-lgbm-catboost.md).

## Feature memory by surface

| family | provenance | 현재 해석 | status |
|---|---|---|---|
| LGB/CB reproduction feature scope | `2026-06-01-lgb-cb-reproduction-local-oof-diagnostic` | transductive statistics, global imputer, subject encoding risk 때문에 supported claim은 local diagnostic으로 좁다. | supported boundary |
| [app-name and app-context windows](app-context-windows.md) | `2026-06-01-app-context-feature-engineering-20260601` | presleep/night/early-morning context는 strong hypothesis이나 submission lineage가 없다. | tentative |
| 1875 sensor/Timing Entropy pool | `2026-05-28-1875-feature-domain-ablation-and-dedup` | raw ablation/correlation evidence 장기 미보강으로 active claim이 아니라 historical source review다. | superseded |
| [stability-filtered feature selection](stability-filtered-feature-selection.md) | DACON code share `13975`, `2026-06-11`, `2026-06-12` recheck | `23177 -> 1682` filter와 target별 max 300 idea는 유용하지만 exact list, feature hash, fold-safe proof가 없다. | tentative |
| window-pair interactions | DACON code share notebook | sleep-window pair idea는 일부 placeholder code라 parquet-backed implementation 전에는 feature로 채택하지 않는다. | reference-only |
| [v186 SHAP target drivers](../models/v186-targetwise-lgbm-catboost.md) | `2026-05-29-v186-shap-leaderboard-analysis` | Q는 routine proxy, S는 sleep-episode/transition proxy라는 interpretation evidence다. | tentative |
| v200-v209 sparse splice | `2026-05-29-v200-v209-sparse-splice-review` | broad morphology reset은 negative evidence이고 sparse micro-splice만 후보로 남는다. | tentative |
| Section07 target bottlenecks | `2026-05-29-labelwise-weekly-progress-target-bottlenecks` | Q3 frequency/window, S4 narrow WASO proxy가 next ablation 후보다. | tentative |

## Compounded rules

1. SHAP importance, notebook-output ablation, external public score, verified DACON leaderboard는 서로 다른 evidence surface다.
2. `Public 0.5917` reference가 낮아 보여도 feature policy를 자동 승격하지 않는다.
3. Stability filtering은 exact feature list, fold-safe score 계산, same-split ablation 전까지 adoption guide가 아니라 candidate method다.
4. Window-pair features는 parquet-backed implementation evidence가 들어오기 전에는 placeholder caveat를 유지한다.
5. Q2/Q3/S4처럼 fragile target은 macro score보다 per-target regression을 먼저 확인한다.

## Raw provenance roots

- `raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/`
- `raw/users/dacon-community/performance/2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend/`
- `raw/users/cho-hyewon/performance/2026-06-01-app-context-feature-engineering-20260601/`
- `raw/users/ko-nayoung/features/2026-05-28-1875-feature-domain-ablation-and-dedup/`
- `raw/users/moon-hyungdo/performance/2026-05-29-v186-shap-leaderboard-analysis/`
- `raw/users/moon-hyungdo/experiments/2026-05-29-v200-v209-sparse-splice-review/`
- `raw/users/hyeonseokrock/experiments/2026-05-29-labelwise-weekly-progress-target-bottlenecks/`

<!-- llm-synthesis:github-models-required-page-fill:2026-06-18:wiki-features-sleep-lifelog-feature-landscape-md -->
## GitHub Models Fallback Synthesis | 2026-06-18

- packet_ids: `2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic`
- llm_summary: 2026-06-18 Wave41 LGB/CB Foldsafe Synthesis smoke local OOF diagnostic 결과를 packet synthesis report와 performance leaf page에 반영하였다. 기존 local OOF claim boundary를 유지하며, DACON leaderboard 및 organizer validation evidence gap을 명확히 기록하였다. claim registry와 leaderboar...
- claim_status: preserved_from_raw_packet
- evidence_boundary: local_oof, notebook_output, DACON_public, DACON_private, and organizer_official evidence must stay separate.
- review_note: This page was conservatively filled in GitHub Actions because the compact fallback model omitted a required wiki page.
- synthesis_report: `wiki/reports/2026-06-18-sleep-lifelog-packet-synthesis.md`
