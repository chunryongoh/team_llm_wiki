---
id: wave43-feature-families
type: feature-map
page_role: hub
title: Wave43 Feature Families
status: active
date: 2026-06-25
dataset: sleep-lifelog-2024
claim_status: supported
review_required: true
raw_evidence:
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/packet.md
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/packet_entity_graph.json
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/source_artifacts/withings-metrics.json
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/source_artifacts/actigraphy-metrics.json
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/source_artifacts/sliding-window-metrics.json
---

# Wave43 Feature Families

Wave43 should be read as a feature-family portfolio, not a single magic feature set. The useful wiki unit is the target-specific hypothesis plus its evidence boundary.

## Family Map

| family | target pressure | evidence | current status |
|---|---|---|---|
| sliding-window / intraday aggregation | Q2, Q3 | standalone macro around `0.62146`; first clear Q-family movement | supported as candidate family |
| Withings-mat mimic | S1, partly S2/S4 | Withings run macro `0.60538`, S1 `0.50594` | supported for S1 insight |
| fixed actigraphy scorers | S3, S1 | actigraphy run macro `0.60573`, S3 `0.51125` | supported for S3 insight |
| WASO / sleep physiology | S2, S4 | WASO run macro `0.60947`, did not beat final stack | tentative/negative |
| sequence, SSL, deep tabular | candidate diversity | deeptab macro around `0.61198`, seqbag best around `0.62226` | useful for pool diversity, not standalone winner |
| external transfer / SLEEPACCEL | S2, S4 | transfer macro `0.61759`, external LOSO AUC `0.84332` | negative for final ETRI log-loss |

## Adoption Policy

Feature adoption should be target-specific. S1 can justify bed-presence or charging/home anchored proxies; S3 can justify validated actigraphy coefficients; Q3 still needs presleep stress/frequency features with same-split target metrics; S4 needs narrow fragmentation or WASO proxies, not broad disturbance feature dumping.

## Superseded Assumptions

- "Q-family has no extractable signal" is superseded by the sliding-window and final stack evidence.
- "More sleep physiology features should automatically improve S4" is not supported; current evidence is negative or tentative.
- "External sleep transfer AUC transfers directly to ETRI target log-loss" is not supported by the wave43 transfer run.

## Links

- [Wave43 Claude Campaign Stack](../performance/wave43-claude-campaign-stack.md)
- [Wave43 Stacked Ensemble](../models/wave43-stacked-ensemble.md)
- [S1 Total Sleep Time](../targets/s1-total-sleep-time.md)
- [S3 Sleep Onset Latency](../targets/s3-sleep-onset-latency.md)
- [Q3 Stress Bottleneck](../targets/q3-stress-bottleneck.md)
- [S4 WASO Disturbance](../targets/s4-waso-disturbance.md)
