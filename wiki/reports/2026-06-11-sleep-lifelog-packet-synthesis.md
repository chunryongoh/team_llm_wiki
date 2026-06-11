---
id: 2026-06-11-sleep-lifelog-packet-synthesis
type: report
page_role: report
title: 2026-06-11 Sleep Lifelog Packet Synthesis
date: 2026-06-11
status: review-required
summary: DACON code share 13975 Public 0.5917 reference를 model, split, feature, leaderboard registry, claim boundary로 통합했다.
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

# 2026-06-11 Sleep Lifelog Packet Synthesis

## Scope

통합 대상은 `raw/users/dacon-community/performance/2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend/` packet이다. Source는 DACON code share `13975`와 attached notebook이다. Public `0.5917`은 external observation으로 기록하고, notebook Local OOF `0.514`는 notebook-output summary로 분리했다.

## Entity integration

- model leaf: [LGBM XGB Anchor Subject Hole Blend](../models/lgbm-xgb-anchor-subject-hole-blend.md)
- preprocessing leaf: [Subject Hole CV](../preprocessing/subject-hole-cv.md)
- feature leaf: [Stability Filtered Feature Selection](../features/stability-filtered-feature-selection.md)
- source review: [DACON Public 0.5917 LGBM XGB Anchor Reference](../performance/dacon-public-05917-lgbm-xgb-anchor-reference.md)
- packet review: [dated packet page](../performance/2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend.md)

## Claim outcome

No supported claim was added. [Current Supported Claims](../claims/current-supported-claims.md)는 기존 LGB/CB Q2 targetwise local OOF diagnostic만 supported로 유지한다. [DACON Leaderboard History](../submissions/dacon-leaderboard-history.md)는 `0.5917`을 `external_codeshare_public_lb_observation`으로 추가했다. Submission id, leaderboard export, submission CSV lineage, private score가 없으므로 verified row가 아니다.

## Policy outcome

[Canonical Split And Leakage Policy](../preprocessing/canonical-split-and-leakage-policy.md)는 `subject-hole-cv-5fold-reference`를 exploratory split surface로 추가했다. V152 anchor OOF는 strict out-of-fold generation과 row identity proof가 없으면 high leakage-risk feature다. Stability filtering은 exact list와 fold-safe score evidence 전까지 feature policy가 아니다.

## Open questions

새로 추적할 질문은 `dacon-public-05917-submission-lineage`, `v152-anchor-oof-reproduction`, `subject-hole-cv-vs-canonical-groupkfold`, `stability-filter-selected-list`다. 모두 merge blocker는 아니지만 claim promotion blocker다.

## Raw evidence

- `manifest.yaml`, `performance.yaml`, `metrics.json`, `packet.md`, `wiki_plan.yaml`
- `dacon-codeshare-13975.md`
- `dacon-public-05917-lgbm-xgb-anchor-subject-hole.ipynb`
