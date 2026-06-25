# Latest Context

[[index]] [[overview]] [[log]]

## Current Best

- Current best local OOF evidence is [Wave43 Claude Campaign Stack](performance/wave43-claude-campaign-stack.md): calibrated macro log-loss `0.5897217743642561` under same-subject-hole five-fold validation.
- The leaderboard surface is not verified. `0.59272` is projected public, and `0.60761` is a Claude/user progress-log observation until leaderboard export or submission hash is attached.
- Key model context is [Wave43 Stacked Ensemble](models/wave43-stacked-ensemble.md), not a single LGBM/CatBoost line.

## Active Research Context

- [Wave43 Feature Families](features/wave43-feature-families.md) separates sliding-window, Withings-mat mimic, actigraphy, WASO, SSL/sequence/deep-tabular, and transfer feature evidence.
- S1 is currently tied to bed-presence-like Withings mimic features; S3 is tied to actigraphy scorers.
- Q3 remains hard but "Q-family has no extractable signal" is superseded by sliding-window/stack evidence.
- S4 remains the main unresolved disturbance/WASO target.

## Active Risks

- Same-subject-hole is local-canonical for wave43, not organizer-official validation.
- Local OOF, projected public, observed public, private leaderboard, and official validation must stay separate.
- GitHub Actions primary OpenAI synthesis hit HTTP 429 for this wave; the bot fallback scaffold was manually refined in Codex before merge consideration.

## Next Actions

- Attach DACON leaderboard export or submission hash for the actual public `0.60761` observation and final stack submission.
- Add fold assignment/row membership evidence for [Same Subject Hole CV](preprocessing/same-subject-hole-cv.md).
- Prioritize S4 fragmentation/WASO ablation with same-split target metrics.

<!-- wiki-ingest:latest:start -->
### 2026-06-25 | sleep-lifelog wave43 synthesis

- link: [[reports/2026-06-25-sleep-lifelog-packet-synthesis]]
- packets: `2026-06-25-wave43-claude-campaign-stack-local-oof-projection`
<!-- wiki-ingest:latest:end -->
