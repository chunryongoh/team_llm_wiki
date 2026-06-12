---
id: lgbm-xgb-anchor-subject-hole-blend
type: model
page_role: leaf
title: LGBM XGB Anchor Subject Hole Blend
status: active-review-required
date: 2026-06-12
dataset: sleep-lifelog-2024
claim_status: tentative
summary: DACON code share 13975의 V152 anchor OOF, Subject-hole CV, stability filtering, LGBM+XGB blend pattern을 external reference model로 기록한다.
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

# LGBM XGB Anchor Subject Hole Blend

이 leaf는 DACON code share `13975`가 보고한 [Public 0.5917 reference](../performance/dacon-public-05917-lgbm-xgb-anchor-reference.md)의 reusable model pattern을 관리한다. Team verified model이 아니라 external reference다. `2026-06-12` graph-first recheck는 같은 model signal을 재확인했지만 새로운 lineage evidence를 추가하지 않았다.

## Claim boundary

- status: `tentative`
- evidence surface: `external_codeshare_public_lb_observation` plus `notebook_output_observation_only`
- reported public score: `0.5917`
- missing: DACON submission id, leaderboard export, submission CSV lineage, V152 OOF CSV, large feature parquet, same-run team reproduction

## Model pattern

- targets: `Q1`, `Q2`, `Q3`, `S1`, `S2`, `S3`, `S4`
- base anchor: V152 OOF probabilities transformed into `base_{target}_prob` and `base_{target}_logit` when `base_oof_path` exists
- learners: LightGBM, XGBoost, optional CatBoost
- final public summary: LGBM+XGB 약 `7:3`, CatBoost weight `0`
- target-specific discussion: Q2 may prefer XGB-only, S3/S4 may prefer CatBoost-only, S1 may prefer LGBM `0.3` + CatBoost `0.7`
- split route: [Subject Hole CV](../preprocessing/subject-hole-cv.md)
- feature route: [Stability Filtered Feature Selection](../features/stability-filtered-feature-selection.md)

## Notebook metrics are not canonical OOF

| metric | value | surface |
|---|---:|---|
| `notebook_local_oof_log_loss` | `0.514` | notebook-output summary |
| `target_specific_notebook_oof_log_loss` | `0.513` | notebook-output summary |
| `lgbm_only_notebook_oof_log_loss` | `0.525` | notebook-output summary |
| `xgb_only_notebook_oof_log_loss` | `0.530` | notebook-output summary |
| `cat_only_notebook_oof_log_loss` | `0.528` | notebook-output summary |

이 값은 [LightGBM CatBoost](lightgbm-catboost.md)의 supported local diagnostic이나 Wave41 local OOF와 직접 비교하지 않는다.

## Adoption gates

1. V152 anchor OOF를 row-aligned strict out-of-fold로 재현한다.
2. Same feature/model을 canonical GroupKFold와 Subject-hole CV에서 비교한다.
3. Submission CSV lineage와 DACON leaderboard export로 public score를 검증한다.
4. Anchor feature가 target leakage를 만들지 않는다는 audit를 남긴다.

## Raw provenance

- `raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/`
- `raw/users/dacon-community/performance/2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend/`
