---
id: 2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend
type: performance
page_role: packet_review
title: dacon public 05917 lgbm xgb anchor subject hole blend
date: 2026-06-11
owner: dacon-community
status: submitted
claim_status: tentative
claim_boundary: public_lb_observation_only_from_dacon_codeshare_and_attached_notebook; not team verified; no DACON submission id, leaderboard export, submission file lineage, or same-run local reproduction is present.
summary: DACON code share 13975의 Public 0.5917 관찰을 외부 reference로 보존하되 팀 verified leaderboard claim으로 승격하지 않는다.
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

# dacon public 05917 lgbm xgb anchor subject hole blend

- packet_id: `2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend`
- run: `27325835544-1`
- source: DACON code share `13975`, attached notebook `dacon-public-05917-lgbm-xgb-anchor-subject-hole.ipynb`
- dataset: [Sleep Lifelog 2024](../datasets/sleep-lifelog-2024.md)
- related benchmark: [Sleep Health Hackathon Benchmark v0](../benchmarks/sleep-health-hackathon-v0.md)
- model route: [LGBM XGB Anchor Subject Hole Blend](../models/lgbm-xgb-anchor-subject-hole-blend.md)
- split route: [Subject Hole CV](../preprocessing/subject-hole-cv.md)
- feature route: [Stability Filtered Feature Selection](../features/stability-filtered-feature-selection.md)

## Synthesis

이 packet은 외부 DACON code share가 보고한 Public `0.5917` LGBM+XGB anchor blend를 기록한다. Pipeline은 V152 anchor OOF probability/logit, Subject-hole CV, stability filtering `23177 -> 1682`, LGBM/XGB/CatBoost targetwise models, LGBM+XGB 약 `7:3` blend를 설명한다. 그러나 V152 OOF CSV, large feature parquet, submission id, leaderboard export, submission CSV hash가 없다.

## Evidence surfaces

| item | value | surface | status |
|---|---:|---|---|
| public LB | `0.5917` | external DACON code-share observation | tentative |
| notebook local OOF | `0.514` | notebook-output summary | tentative |
| target-specific notebook OOF | `0.513` | notebook-output summary | tentative |
| feature count after filter | `1682` | notebook/metrics summary | tentative |

이 값들은 [Current Supported Claims](../claims/current-supported-claims.md)의 supported local OOF claim과 비교 ranking에 쓰지 않는다.

## Raw provenance

- `raw/users/dacon-community/performance/2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend/manifest.yaml`
- `raw/users/dacon-community/performance/2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend/performance.yaml`
- `raw/users/dacon-community/performance/2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend/metrics.json`
- `raw/users/dacon-community/performance/2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend/dacon-codeshare-13975.md`
- `raw/users/dacon-community/performance/2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend/wiki_plan.yaml`

## Review notes

Open questions: `dacon-public-05917-submission-lineage`, `v152-anchor-oof-reproduction`, `subject-hole-cv-vs-canonical-groupkfold`. 이 page는 source-specific packet review이며 stable memory는 위 leaf와 registry pages가 소유한다.
