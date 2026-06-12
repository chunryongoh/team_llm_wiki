---
id: 2026-06-12-sleep-lifelog-packet-synthesis
type: report
page_role: report
title: 2026-06-12 Sleep Lifelog Packet Synthesis
date: 2026-06-12
status: review-required
summary: DACON code share 13975 graph-first recheck를 stable model, split, feature, claim, submission pages에 통합했으며 claim status 변화는 없다.
review_required: true
packets:
- 2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck
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

# 2026-06-12 Sleep Lifelog Packet Synthesis

## Scope

`2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck`는 DACON code share `13975`를 graph-first sidecars로 다시 확인한 performance packet이다. 새 source는 [LGBM XGB Anchor Subject Hole Blend](../models/lgbm-xgb-anchor-subject-hole-blend.md), [Subject Hole CV](../preprocessing/subject-hole-cv.md), [Stability Filtered Feature Selection](../features/stability-filtered-feature-selection.md), [DACON Leaderboard History](../submissions/dacon-leaderboard-history.md)를 업데이트할 만큼 reusable하지만, claim promotion evidence는 없다.

## Integrated conclusions

- Public `0.5917`은 `external_codeshare_public_lb_observation`이며 `tentative`다.
- Notebook Local OOF `0.514`, target-specific `0.513`, LGBM-only `0.525`, XGB-only `0.530`, Cat-only `0.528`은 `notebook_output_summary`다.
- Stability filter `23177 -> 1682`는 descriptive count이며 exact selected list와 fold-safe proof가 없다.
- Subject-hole CV는 external reference split이고 canonical GroupKFold replacement가 아니다.
- V152 anchor OOF는 strict OOF generation과 row identity proof가 없으면 high leakage-risk feature다.

## Page updates

Stable entity pages were updated instead of absorbing all detail into the hub: model, split, and feature leaves now own the reusable memory. The feature landscape routes to those leaves. Evaluation protocol, claim registry, leaderboard history, and canonical split policy preserve the evidence-surface boundary. Open questions keep `dacon-public-05917-submission-lineage`, `v152-anchor-oof-reproduction`, and `subject-hole-cv-vs-canonical-groupkfold` active, and add a window-pair implementation question.

## Claim register outcome

No new supported claim. The only supported claim remains the LGB/CB targetwise reblend local OOF diagnostic. The `0.5917` reference remains useful for strategy search but not for team best-model ranking.

## Reviewer checklist

- Do not merge notebook OOF with team local OOF.
- Do not create a verified DACON row without submission id/export/CSV lineage.
- Do not treat placeholder window-pair code as implemented features.
- Do not create duplicate leaves for `lightgbm-xgboost-anchor-blend`; use the existing stable model leaf.
