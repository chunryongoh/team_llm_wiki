---
id: lightgbm-catboost
type: model
page_role: leaf
title: LightGBM CatBoost
status: active
date: 2026-06-11
dataset: sleep-lifelog-2024
claim_status: supported
summary: LightGBM + CatBoost는 현재 standalone winner가 아니라 Q2 targetwise reblend source-diversity로만 supported이며, external LGBM+XGB 0.5917 reference와 evidence surface가 다르다.
review_required: true
raw_evidence:
- raw/users/dacon-community/performance/2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend/manifest.yaml
- raw/users/dacon-community/performance/2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend/dacon-public-05917-lgbm-xgb-anchor-subject-hole.ipynb
- raw/users/dacon-community/performance/2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend/dacon-codeshare-13975.md
- raw/users/dacon-community/performance/2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend/metrics.json
- raw/users/dacon-community/performance/2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend/packet.md
- raw/users/dacon-community/performance/2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend/performance.yaml
- raw/users/dacon-community/performance/2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend/wiki_plan.yaml
---

# LightGBM CatBoost

이 페이지는 sleep-lifelog 작업에서 LightGBM + CatBoost family의 지원되는 claim과 제한을 관리한다.

## Current Boundary

- supported boundary: `local_oof_diagnostic_only`
- supported role: Q2 source-diversity component in targetwise reblend
- unsupported wording: `LGB/CB is globally best standalone model`
- leaderboard status: no verified DACON public/private claim

## Current Evidence

- standalone LightGBM macro log-loss: `0.6657586405095428`
- standalone CatBoost macro log-loss: `0.6538557592728997`
- fixed LGB/CB blend macro log-loss: `0.6536839393073466`
- final targetwise reblend macro log-loss: `0.6198365213240887`
- Wave41 baseline macro log-loss: `0.6198684545582471`
- selected use: fixed LGB/CB blend weight `0.1` for Q2 only

## External contrast

[DACON Public 0.5917 LGBM XGB Anchor Reference](../performance/dacon-public-05917-lgbm-xgb-anchor-reference.md)는 LGBM+XGB anchor blend를 강조한다. 그 score는 `external_codeshare_public_lb_observation`이고, notebook OOF는 `notebook_output_observation_only`다. 따라서 이 page의 supported local OOF claim을 supersede하지 않고, LGBM+CatBoost 방향을 폐기하는 근거도 아니다.

## Interpretation

LightGBM + CatBoost는 current raw evidence에서 standalone best가 아니다. 의미 있는 기록은 Q2 targetwise reblend에 작은 source-diversity signal을 제공했다는 점이다. External LGBM+XGB reference는 model diversity 후보로 참고하되 같은 split, feature, submission lineage 없이는 직접 비교하지 않는다.

## Required Follow-Up

- Q2 weight selection을 nested 또는 fold-safe procedure로 재검증한다.
- same-split, same-feature, same-baseline 조건에서 LGB/CB, LGBM+XGB, CatBoost contribution을 비교한다.
- leaderboard claim은 [DACON Leaderboard History](../performance/dacon-leaderboard-history.md) evidence 없이는 만들지 않는다.

<!-- llm-synthesis:github-models-required-page-fill:2026-06-18:wiki-models-lightgbm-catboost-md -->
## GitHub Models Fallback Synthesis | 2026-06-18

- packet_ids: `2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic`
- llm_summary: 2026-06-18 Wave41 LGB/CB Foldsafe Synthesis smoke local OOF diagnostic 결과를 packet review 및 performance leaf에 반영하였으며, claim registry에 기존 local_oof_diagnostic_only claim의 supported 상태를 유지하였다. DACON leaderboard, organizer validation, local OOF, notebook output...
- claim_status: preserved_from_raw_packet
- evidence_boundary: local_oof, notebook_output, DACON_public, DACON_private, and organizer_official evidence must stay separate.
- review_note: This page was conservatively filled in GitHub Actions because the compact fallback model omitted a required wiki page.
- synthesis_report: `wiki/reports/2026-06-18-sleep-lifelog-packet-synthesis.md`
