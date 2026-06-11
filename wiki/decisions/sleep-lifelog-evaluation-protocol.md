---
id: sleep-lifelog-evaluation-protocol
type: decision
page_role: decision
title: Sleep Lifelog Evaluation Protocol
status: active-review-required
date: 2026-06-11
dataset: sleep-lifelog-2024
benchmark: sleep-health-hackathon-v0
summary: sleep-lifelog 평가는 local OOF, notebook-output, external public note, DACON public/private leaderboard, organizer-official validation을 절대 합치지 않는다.
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

# Sleep Lifelog Evaluation Protocol

## Decision

Sleep-lifelog 성능과 feature claim은 evidence surface를 분리한다.

1. `local_oof_diagnostic_only`: split, group key, metric raw가 있는 local diagnostic. 현재 supported claim은 [LGB CB Reproduction Local OOF Diagnostic](../performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic.md)뿐이다.
2. `notebook_output_observation_only`: notebook saved output, PDF/DOCX summary, SHAP note. hypothesis에는 쓸 수 있으나 supported performance claim은 아니다.
3. `user_reported_public_score_only` 또는 `external_codeshare_public_lb_observation`: source note나 DACON code share에 적힌 public score. submission id와 leaderboard export 없이는 tentative다.
4. `verified_public_lb`와 `verified_private_lb`: DACON submission id, score, timestamp, submission CSV lineage가 있어야 한다.
5. `organizer_official_validation`: 주최 측 official split 또는 official result artifact가 있어야 한다.

## Current application

- supported: LGB/CB Q2 targetwise reblend local OOF delta `-3.19332341584e-05`, boundary `local_oof_diagnostic_only`.
- tentative external reference: DACON code share `13975` Public `0.5917` for [LGBM XGB Anchor Subject Hole Blend](../models/lgbm-xgb-anchor-subject-hole-blend.md). Submission id, export, CSV lineage가 없다.
- notebook-output only: same code share notebook Local OOF `0.514`, target-specific `0.513`, feature count `23177 -> 1682`.
- tentative public notes: v186 `0.5922831771`, v189/v200-v209 series, Section07 `0.5986218188`, app context `0.6106185586`.

이 값들은 서로 ranking surface가 아니다. External public note가 supported local OOF claim보다 강한 claim이 되지 않는다.

## Promotion gates

| target claim | required evidence |
|---|---|
| public leaderboard | DACON submission id, public score, leaderboard export, submission CSV lineage |
| private leaderboard | private/final score artifact와 same lineage |
| fold-safe local OOF | fold별 preprocessing fit, target encoding policy, feature cutoff audit |
| feature policy | exact feature list, same-split ablation, target-specific deltas |
| anchor OOF feature | out-of-fold generation proof, row identity, no target leakage audit |

## Guardrails

V152 anchor OOF, Subject-hole CV, stability filtering, window-pair features는 useful reference지만 adoption decision이 아니다. Raw replay validator와 same-split ablation 전에는 final decision이나 supported claim으로 쓰지 않는다.

## Links

- [DACON Leaderboard History](../submissions/dacon-leaderboard-history.md)
- [Canonical Split And Leakage Policy](../preprocessing/canonical-split-and-leakage-policy.md)
- [Current Supported Claims](../claims/current-supported-claims.md)
- [Sleep Lifelog Open Questions](../questions/sleep-lifelog-open-questions.md)
