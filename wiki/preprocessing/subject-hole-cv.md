---
id: subject-hole-cv
type: preprocessing
page_role: leaf
title: Subject Hole CV
status: active-review-required
date: 2026-06-11
dataset: sleep-lifelog-2024
claim_status: tentative
summary: Subject별 chronological chunks에서 early+late validation holes를 만드는 external reference CV이며 canonical split replacement가 아니다.
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

# Subject Hole CV

Subject-hole CV는 DACON code share `13975`가 사용한 split idea다. 각 `subject_id`를 `sleep_date` 순으로 정렬하고, subject 내부를 여러 chunk로 나눈 뒤 fold마다 early chunk와 late chunk를 validation hole로 뽑는다. 목적은 test의 interleaving 구조를 local validation에서 더 비슷하게 만들려는 것이다.

## Boundary

- status: `tentative`
- source: [DACON Public 0.5917 LGBM XGB Anchor Reference](../performance/dacon-public-05917-lgbm-xgb-anchor-reference.md)
- packet split id: `subject-hole-cv-5fold-reference`
- group key: `subject_id`
- fold file: not provided
- canonical status: exploratory reference only

## Why it is separate from canonical policy

현재 팀의 supported local claim은 `local-groupkfold-subject-5fold-oof` surface에 있다. Subject-hole CV는 same-run comparison이 없고 fold assignment artifact도 없다. 따라서 [Canonical Split And Leakage Policy](canonical-split-and-leakage-policy.md)를 대체하지 않는다.

## Leakage and audit risks

- Subject 내부 temporal chunks가 target 이후 정보를 허용하지 않는지 확인해야 한다.
- V152 anchor OOF가 train rows에서 strict out-of-fold인지 증명해야 한다.
- Stability filtering이나 feature selection이 validation fold 정보를 보지 않았는지 확인해야 한다.
- Public LB correlation을 주장하려면 private/final mapping 또는 repeated submissions가 필요하다.

## Close condition for adoption

`subject-hole-cv-vs-canonical-groupkfold` 질문은 same feature/model run을 canonical GroupKFold와 Subject-hole CV 양쪽에서 실행하고, local OOF와 public/private leaderboard mapping 및 leakage audit를 제출하면 닫을 수 있다.

## Links

- [LGBM XGB Anchor Subject Hole Blend](../models/lgbm-xgb-anchor-subject-hole-blend.md)
- [Sleep Lifelog Open Questions](../questions/sleep-lifelog-open-questions.md)
- [Sleep Lifelog Evaluation Protocol](../decisions/sleep-lifelog-evaluation-protocol.md)
