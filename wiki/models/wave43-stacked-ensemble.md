---
id: wave43-stacked-ensemble
type: model-entity
page_role: leaf
title: Wave43 Stacked Ensemble
status: active
date: 2026-06-25
dataset: sleep-lifelog-2024
claim_status: supported
weights_in_repo: false
raw_evidence:
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/performance.yaml
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/source_artifacts/stack-v2-metrics.json
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/source_artifacts/stack-v2-build.py
---

# Wave43 Stacked Ensemble

The final wave43 model is a targetwise stacked ensemble over a large candidate pool. It is not a single LightGBM/CatBoost line. The model page exists to prevent future agents from flattening the result into one base architecture.

## Architecture

- Base families: LightGBM, CatBoost, XGBoost, subject-prior variants, sliding-window models, Withings-mimic models, actigraphy/WASO feature models, sequence/SSL/deep-tabular candidates.
- Candidate count: 236 for Q1/Q2/Q3/S1/S2/S4 and 238 for S3.
- Validation: nested same-subject-hole local OOF.
- Calibration: target-specific, selected after stack scoring.
- Weight policy: no learned weights are stored in the wiki repo.

## Calibration

| target | calibration |
|---|---|
| Q1 | temperature |
| Q2 | temperature |
| Q3 | none |
| S1 | none |
| S2 | platt |
| S3 | temperature |
| S4 | temperature |

## Model Interpretation

The stack works because different targets are explained by different modality proxies. S1 responds to bed-presence-like features, S3 responds to actigraphy scorers, Q-family responds weakly to temporal/window context, and S4 remains a fragmentation/disturbance problem.

This model should be compared to previous LGB/CB or LGBM/XGB entries only when the split surface is explicit. It should not be summarized as "LGBM+CatBoost is best"; the final evidence is a broad candidate stack.

## Open Risks

- Public/private leaderboard lineage is not attached for the projected `0.59272` line.
- OOF prediction arrays are not copied into this packet.
- Candidate selection stability across seeds and organizer split is unknown.
- External transfer features did not prove robust target-level gains.
