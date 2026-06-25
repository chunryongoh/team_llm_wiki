---
id: s3-sleep-onset-latency
type: target-entity
page_role: leaf
target: S3
title: S3 Sleep Onset Latency
status: active
date: 2026-06-25
claim_status: supported
raw_evidence:
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/source_artifacts/actigraphy-metrics.json
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/metrics.json
---

# S3 Sleep Onset Latency

S3 is the target where fixed actigraphy-style scorers are the clearest wave43 clue. The final stack records S3 calibrated log-loss `0.5168327857279124`; the actigraphy run records S3 `0.5112450274138282`.

## Current Interpretation

Sleep onset is better captured by motion/light/activity transitions than by broad daily summary statistics. Cole-Kripke/Sadeh-style fixed coefficient features are therefore a reusable feature family for S3, provided the windowing is anchored before or around the relevant sleep episode without leaking future labels.

## Adoption Rule

S3 claims should attach scorer formula, window anchor, sensor modality coverage, missing-data handling, and same-split S3 ablation. Broad feature count increases are not enough.

## Related Pages

- [Wave43 Feature Families](../features/wave43-feature-families.md)
- [Wave43 Stacked Ensemble](../models/wave43-stacked-ensemble.md)
- [Same Subject Hole CV](../preprocessing/same-subject-hole-cv.md)
