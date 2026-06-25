---
id: s1-total-sleep-time
type: target-entity
page_role: leaf
target: S1
title: S1 Total Sleep Time
status: active
date: 2026-06-25
claim_status: supported
raw_evidence:
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/source_artifacts/withings-metrics.json
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/metrics.json
---

# S1 Total Sleep Time

S1 is the wave43 target where bed-presence-like proxies appear strongest. The final stack records S1 calibrated log-loss `0.5084141950084338`; the Withings-mat mimic run independently records S1 `0.5059412643362348`.

## Current Interpretation

Charging/home anchoring can act as a weak Withings-mat proxy: it may capture stable nighttime bed occupancy or sleep opportunity, not direct sleep physiology. This makes it useful for S1, but it should not be generalized blindly to S4.

## Adoption Rule

S1 feature claims should include the exact charging/home anchor definition, time window, fold-safe aggregation rule, and same-split S1 metric. If a feature uses post-sleep or target-date information, it must be marked leakage-risk until audited.

## Related Pages

- [Wave43 Feature Families](../features/wave43-feature-families.md)
- [Wave43 Stacked Ensemble](../models/wave43-stacked-ensemble.md)
- [Same Subject Hole CV](../preprocessing/same-subject-hole-cv.md)
