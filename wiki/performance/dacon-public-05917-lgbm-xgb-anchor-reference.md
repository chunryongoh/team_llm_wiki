---
id: dacon-public-05917-lgbm-xgb-anchor-reference
type: performance
page_role: packet_review
title: DACON Public 0.5917 LGBM XGB Anchor Reference
date: 2026-06-12
owner: dacon-community
status: review-required
claim_status: tentative
summary: DACON code share 13975의 Public 0.5917 LGBM+XGB anchor blend를 source-specific external reference로 보존한다.
review_required: true
raw_evidence:
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/dacon-codeshare-13975.md
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/dacon-public-05917-lgbm-xgb-anchor-subject-hole.ipynb
- raw/users/dacon-community/performance/2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend/dacon-codeshare-13975.md
---

# DACON Public 0.5917 LGBM XGB Anchor Reference

이 page는 DACON code share `13975`를 팀 내부 모델 결과가 아니라 외부 reference로 검토한다. Source title은 `[Public 0.5917] LGBM+XGB 앵커·Subject-hole CV·안정성 피처선별·블렌드`이며 author는 `비비드백`이다. `2026-06-12` graph-first recheck는 기존 `2026-06-11` packet과 같은 conclusion을 재확인했다.

## What is useful

Reference pipeline은 [LGBM XGB Anchor Subject Hole Blend](../models/lgbm-xgb-anchor-subject-hole-blend.md), [Subject Hole CV](../preprocessing/subject-hole-cv.md), [Stability Filtered Feature Selection](../features/stability-filtered-feature-selection.md)로 분리해 재사용한다. 특히 V152 anchor OOF probability/logit, LGBM+XGB diversity, target-specific blend search는 follow-up 후보가 된다.

## What is not proven

Public `0.5917`은 [DACON Leaderboard History](dacon-leaderboard-history.md)의 `external_codeshare_public_lb_observation`이다. Submission id, leaderboard export, submission CSV lineage, private score가 없다. Notebook Local OOF `0.514`와 target-specific `0.513`은 notebook-output summary이며 [Current Supported Claims](../claims/current-supported-claims.md)의 local OOF diagnostic과 비교하지 않는다.

## Evidence gaps

- DACON submission id and leaderboard export missing
- submission CSV hash or file lineage missing
- V152 anchor OOF CSV missing
- large feature parquet missing
- window-pair implementation partly placeholder

## Next review

`dacon-public-05917-submission-lineage`, `v152-anchor-oof-reproduction`, `subject-hole-cv-vs-canonical-groupkfold`, `window-pair-parquet-implementation` 질문이 닫히기 전에는 이 reference를 team best claim으로 쓰지 않는다.
