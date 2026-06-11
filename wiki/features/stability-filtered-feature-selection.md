---
id: stability-filtered-feature-selection
type: feature
page_role: leaf
title: Stability Filtered Feature Selection
status: active-review-required
date: 2026-06-11
dataset: sleep-lifelog-2024
claim_status: tentative
summary: DACON code share 13975의 `23177 -> 1682` stability filtering idea를 reusable feature-selection 후보로 기록하되 exact list와 ablation 전까지 policy로 승격하지 않는다.
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

# Stability Filtered Feature Selection

이 leaf는 external DACON code share `13975`가 설명한 stability-based feature selection을 관리한다. Reported pipeline은 large feature pool `23177`개에서 `1682`개를 남겼다고 한다. Attached notebook skeleton은 absolute correlation/proxy stability threshold `min_stability 0.3`, target별 `max_features_per_target 300` 같은 형태를 보여준다.

## Claim boundary

- status: `tentative`
- evidence surface: notebook/metrics summary
- reported count before: `23177`
- reported count after: `1682`
- missing: large feature parquet, exact selected feature list, per-target stability scores, fold-safe computation proof, same-split ablation

## Interpretation

Stability filtering은 overfit-prone feature pool을 줄이는 후보 방법이다. 그러나 현재 evidence는 selection artifact가 아니라 code share summary다. 따라서 [Sleep Lifelog Feature Landscape](sleep-lifelog-feature-landscape.md)의 feature policy가 아니라 candidate method로만 둔다.

## Related feature caveat

같은 notebook의 window-pair interaction section은 sleep-window pair idea를 설명하지만 일부 code path가 placeholder다. 실제 sensor parquet에서 생성된 feature evidence가 없으므로 implemented production feature로 기록하지 않는다.

## Adoption gates

1. Exact selected feature list와 source feature hash를 제출한다.
2. Stability score가 fold-safe하게 train-fold-only로 계산됐는지 audit한다.
3. Same split에서 no-filter baseline, correlation pruning, stability filter를 target별로 비교한다.
4. Q3/S4 regression 여부를 별도로 보고한다.

## Links

- [LGBM XGB Anchor Subject Hole Blend](../models/lgbm-xgb-anchor-subject-hole-blend.md)
- [Subject Hole CV](../preprocessing/subject-hole-cv.md)
- [Sleep Lifelog Open Questions](../questions/sleep-lifelog-open-questions.md)
