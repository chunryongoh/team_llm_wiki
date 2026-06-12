---
id: 2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck
packet_type: performance
type: performance
page_role: packet_review
title: dacon public 05917 lgbm xgb anchor graph first recheck
date: 2026-06-12
owner: dacon-community
status: submitted
claim_status: tentative
dataset: sleep-lifelog-2024
split: subject-hole-cv-5fold-reference
model: lgbm-xgb-anchor-blend
summary: graph-first sidecars로 DACON code share 13975의 Public 0.5917 reference를 재확인했지만 submission lineage가 없어 tentative를 유지한다.
review_required: true
raw_evidence:
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/manifest.yaml
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/dacon-codeshare-13975.md
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/dacon-public-05917-lgbm-xgb-anchor-subject-hole.ipynb
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/metrics.json
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/performance.yaml
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/wiki_plan.yaml
---

# dacon public 05917 lgbm xgb anchor graph first recheck

이 packet은 DACON code share `13975`를 graph-first sidecars로 다시 스캔한 source review다. 핵심 관찰은 기존 [DACON Public 0.5917 LGBM XGB Anchor Reference](dacon-public-05917-lgbm-xgb-anchor-reference.md)와 같다. Public `0.5917`은 외부 code-share observation이며, team submission이나 verified leaderboard row가 아니다.

## 확인된 signal

- model: [LGBM XGB Anchor Subject Hole Blend](../models/lgbm-xgb-anchor-subject-hole-blend.md)
- split idea: [Subject Hole CV](../preprocessing/subject-hole-cv.md)
- feature idea: [Stability Filtered Feature Selection](../features/stability-filtered-feature-selection.md)
- public score surface: `external_codeshare_public_lb_observation`
- notebook surface: `notebook_output_summary`

## Metrics by surface

| metric | value | surface | status |
|---|---:|---|---|
| `public_lb_log_loss` | `0.5917` | public LB observation | tentative |
| `notebook_local_oof_log_loss` | `0.514` | notebook output | tentative |
| `target_specific_notebook_oof_log_loss` | `0.513` | notebook output | tentative |
| `feature_count_before_stability_filter` | `23177` | notebook output | descriptive |
| `feature_count_after_stability_filter` | `1682` | notebook output | descriptive |

## Claim boundary

Submission id, leaderboard export/screenshot, submission CSV hash, private score, same-run team reproduction이 없다. V152 anchor OOF CSV와 large feature parquet도 없다. 따라서 이 packet은 `0.5917` claim을 보강 provenance로 추가할 뿐, [Current Supported Claims](../claims/current-supported-claims.md)를 바꾸지 않는다.

## Review outcome

`public-lb-lineage` question은 [Sleep Lifelog Open Questions](../questions/sleep-lifelog-open-questions.md)의 `dacon-public-05917-submission-lineage`로 병합한다. Window-pair code는 일부 placeholder라 implemented feature로 승격하지 않는다.
