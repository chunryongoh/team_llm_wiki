# Latest Context

[[index]] [[overview]] [[log]]

## Current Best

- Supported local OOF claim: [LGB CB Reproduction Local OOF Diagnostic](performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic.md) remains a narrow `local_oof_diagnostic_only` claim. It improves Wave41 by a tiny Q2 targetwise reblend contribution, not by standalone LGB/CB superiority.
- User-reported DACON public score notes live in [DACON Leaderboard History](submissions/dacon-leaderboard-history.md) and are not verified leaderboard claims yet.

## Active Risks

- Split surfaces are mixed across 3-fold GroupKFold, 5-fold local OOF, working-note validation probes, and notebook-output probes. See [Canonical Split And Leakage Policy](preprocessing/canonical-split-and-leakage-policy.md).
- Section07 evidence is useful but tentative: allowed input audit, feature hashes, raw metric files, rerun logs, and DACON submission lineage are missing.
- Do not call LightGBM + CatBoost globally best without distinguishing standalone, fixed blend, and targetwise reblend boundaries. See [LightGBM CatBoost](models/lightgbm-catboost.md).

## Next Actions

- Close [Section07 Follow-Up Backlog](questions/section07-followup-backlog.md) P0 items: allowed input audit and feature hash evidence.
- Add a verified DACON leaderboard provenance packet if section07 public score notes should become leaderboard claims.
- Ensure new experiment packets include `wiki_plan.yaml` stable entities, affected pages, and semantic lint so synthesis updates entity pages rather than only experiment mirrors.

<!-- wiki-ingest:latest:start -->
### local-run-section07-notebook | 2026-06-01-lifelog-section07-notebook-overview

- link: [[experiments/2026-06-01-lifelog-section07-notebook-overview]]
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
