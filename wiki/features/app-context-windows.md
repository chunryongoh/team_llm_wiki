---
id: app-context-windows
type: feature-entity
page_role: leaf
claim_status: tentative
status: active
title: App Context Windows
raw_evidence:
- raw/users/cho-hyewon/performance/2026-06-01-app-context-feature-engineering-20260601/manifest.yaml
- raw/users/cho-hyewon/performance/2026-06-01-app-context-feature-engineering-20260601/packet.md
- raw/users/cho-hyewon/performance/2026-06-01-app-context-feature-engineering-20260601/performance.yaml
- raw/users/cho-hyewon/performance/2026-06-01-app-context-feature-engineering-20260601/metrics.json
---

# App Context Windows

App context windows are feature families based on actual app names and presleep/night/early-morning usage context. Current reports show staged public LB observations from `0.6218831823` to `0.6106185586`, but submission lineage and local same-split metrics are not verified.

## Current interpretation

- App-name daily/evening features and presleep/night/early-morning app context are strong feature hypotheses.
- The evidence surface is DOCX/public LB observation, not verified DACON leaderboard evidence.
- Q3 is a natural target for follow-up, but current evidence does not prove Q3-specific improvement.

## Adoption rule

Do not adopt app-context features as a global improvement claim until the packet includes feature hash, local split metric, submission id or CSV lineage, and target-level ablation.

## Required evidence

- feature generation code or feature hash
- stage-to-submission lineage
- local OOF comparator on the same split
- target metrics, especially Q3

## Related pages

- [Q3 Stress Bottleneck](../targets/q3-stress-bottleneck.md)
- [DACON Leaderboard History](../submissions/dacon-leaderboard-history.md)
- [Sleep Lifelog Feature Landscape](sleep-lifelog-feature-landscape.md)
