---
id: wave43-claude-campaign-stack
type: performance-summary
page_role: leaf
title: Wave43 Claude Campaign Stack
status: active
date: 2026-06-25
dataset: sleep-lifelog-2024
split: same-subject-hole-5fold-temporal-by-subject
model: wave43-stacked-ensemble
claim_status: supported
review_required: true
raw_evidence:
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/manifest.yaml
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/packet.md
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/performance.yaml
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/metrics.json
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/source_artifacts/stack-v2-metrics.json
---

# Wave43 Claude Campaign Stack

Wave43 is the current best local OOF evidence package from the Claude-side campaign. The supported claim is narrow: under `same-subject-hole-5fold-temporal-by-subject`, the calibrated `stack-v2` line records macro log-loss `0.5897217743642561`. This is not an official DACON public/private result.

## Claim Surface

| claim | value | status | boundary |
|---|---:|---|---|
| calibrated local OOF macro log-loss | `0.5897217743642561` | supported | copied metric snapshot |
| stack nested macro before final calibration | `0.5946367652711365` | supported | copied metric snapshot |
| subject-mean baseline macro | `0.6245305092520156` | supported | copied metric snapshot |
| projected public macro | `0.5927217743642561` | tentative | projection only |
| best public observation in Claude progress log | `0.60761` | tentative | user/Claude log, no leaderboard export |

The supported local OOF delta versus subject-mean is `-0.0348087348877595`. The projected public and public observation rows must remain outside the supported claim registry until submission lineage is attached.

## Target Metrics

| target | calibrated log-loss | calibration | note |
|---|---:|---|---|
| Q1 | `0.6450606619738299` | temp | still high but improved by candidate pool |
| Q2 | `0.6455155286285766` | temp | sliding-window/intraday signal helped |
| Q3 | `0.650460985046031` | none | remains Q-family bottleneck |
| S1 | `0.5084141950084338` | none | Withings-mat mimic is the strongest clue |
| S2 | `0.5561343457335379` | platt | sleep physiology/WASO candidates did not dominate |
| S3 | `0.5168327857279124` | temp | actigraphy scorer is the strongest clue |
| S4 | `0.6056339184314705` | temp | remains disturbance/WASO bottleneck |

## What Changed

The campaign shifted from one large tabular model toward target-specific evidence assembly. The final stack uses 236 candidates for Q1/Q2/Q3/S1/S2/S4 and 238 candidates for S3. Candidate families include LGBM/CatBoost/XGBoost, subject priors, sliding-window temporal features, Withings-mat mimic features, fixed actigraphy scorers, WASO/sleep physiology features, sequence/SSL/deep-tabular outputs, and external transfer probes.

This supersedes the stronger version of the earlier belief that Q-family signal was not extractable. Q3 remains hard, but sliding-window and stacking found non-trivial Q2/Q3 signal. It does not supersede the caution that public leaderboard correlation is uncertain.

## Guardrails

- Do not report `0.59272` as a submitted public leaderboard score.
- Do not merge local OOF, projected public, observed public, and private leaderboard into one ranking surface.
- Do not promote external transfer or WASO runs to final S4 evidence until they beat the final stack under the same split.
- Keep this page tied to [Same Subject Hole CV](../preprocessing/same-subject-hole-cv.md), [Wave43 Stacked Ensemble](../models/wave43-stacked-ensemble.md), and [Wave43 Feature Families](../features/wave43-feature-families.md).
