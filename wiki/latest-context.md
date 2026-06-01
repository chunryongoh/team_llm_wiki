# Latest Context

[[index]] [[overview]] [[log]]

<!-- wiki-ingest:latest:start -->
### 26747556817-1 | 2026-06-01-lifelog-section07-working-notes

- link: [[experiments/2026-06-01-lifelog-section07-working-notes]]
- publish_action: `bot_pr`
- risk_tier: `tier2-interpretation`
- review-required: true

### local-run-section07 | 2026-06-01-lifelog-section07-working-notes

- link: [[experiments/2026-06-01-lifelog-section07-working-notes]]
- publish_action: `bot_pr`
- risk_tier: `tier2-interpretation`
- review-required: true

### 26741704818-1 | 2026-06-01-sleep-lifelog-packet-synthesis

- link: [[reports/2026-06-01-sleep-lifelog-packet-synthesis]]
- related: [[performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic]], [[features/sleep-lifelog-feature-landscape]], [[decisions/sleep-lifelog-evaluation-protocol]], [[questions/sleep-lifelog-open-questions]]
- publish_action: `bot_pr`
- risk_tier: `tier4-governance`
- review-required: true
- 핵심: `local_oof_diagnostic_only` claim을 보존하고 leaderboard claim으로 승격하지 않는 통합 pass.

### 26741704818-1 | 2026-06-01-lgb-cb-reproduction-local-oof-diagnostic

- link: [[performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic]]
- dataset: [[datasets/sleep-lifelog-2024]]
- benchmark: [[benchmarks/sleep-health-hackathon-v0]]
- publish_action: `bot_pr`
- risk_tier: `tier4-governance`
- review-required: true
- claim_boundary: `local_oof_diagnostic_only`
- claim_status: `supported`
- 핵심 metric: `targetwise_reblend_macro_log_loss` `0.6198365213240887`, `baseline_wave41_macro_log_loss` `0.6198684545582471`, `delta_vs_wave41` `-3.19332341584e-05`.

### 26740055632-1 | 2026-06-01-dacon-leaderboard-claim-boundary

- link: [[sources/2026-06-01-dacon-leaderboard-claim-boundary]]
- publish_action: `direct_commit`
- risk_tier: `tier0-catalog`
- 핵심: local OOF와 DACON leaderboard claim은 별도 provenance가 필요하다.

### 26628582638-1 | 2026-05-29-sleep-health-hackathon-v0

- link: [[benchmarks/sleep-health-hackathon-v0]]
- publish_action: `bot_pr`
- risk_tier: `tier2-interpretation`
- review-required: true

### 26628582638-1 | 2026-05-29-sleep-lifelog-2024

- link: [[datasets/sleep-lifelog-2024]]
- publish_action: `bot_pr`
- risk_tier: `tier2-interpretation`
- review-required: true
<!-- wiki-ingest:latest:end -->
