# Latest Context

[[index]] [[overview]] [[log]]

## Current Best

- Supported local OOF claim: [LGB CB Reproduction Local OOF Diagnostic](performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic.md)는 여전히 좁은 `local_oof_diagnostic_only` claim이다. Q2 targetwise reblend `0.1`이 Wave41 local OOF를 `0.6198684545582471`에서 `0.6198365213240887`로 미세 개선한 것만 supported다.
- Reported public LB notes: v186 `0.5922831771`, v189 `0.5925397`, Section07 `0.5986218188`, app-context `0.6106185586` 등은 [DACON Leaderboard History](submissions/dacon-leaderboard-history.md)에 있지만 verified leaderboard claim이 아니다.

## Active Risks

- Split surfaces가 3-fold GroupKFold, 5-fold local OOF, PDF OOF summary, DOCX public LB observation, working-note mixed validation, notebook-output summary로 섞여 있다. [Canonical Split And Leakage Policy](preprocessing/canonical-split-and-leakage-policy.md)를 먼저 확인한다.
- App context, 1,875 feature pool, v186 SHAP, v200-v209 sparse splice, Section07 weekly claims는 모두 `tentative`다.
- SHAP importance, public score note, local OOF, DACON leaderboard, private leaderboard를 한 ranking surface로 합치면 안 된다.
- Broad feature addition과 broad morphology reset은 negative evidence가 있으므로 Q3/S4 target-specific ablation 없이 채택하지 않는다.

## Next Actions

- [Sleep Lifelog Open Questions](questions/sleep-lifelog-open-questions.md)의 `v186-leaderboard-provenance`, `app-context-raw-submission-lineage`, `dacon-submission-provenance-boundary`를 먼저 닫는다.
- `feature-dedup-715-raw-list`와 Q3/S4 same-split ablation을 제출해 [Sleep Lifelog Feature Landscape](features/sleep-lifelog-feature-landscape.md)를 policy로 승격할지 판단한다.
- `replay-validator-blind-spot-threshold`를 정의하기 전에는 `0.00005` 수준 local/public delta로 live submission trigger를 만들지 않는다.

## Recent packet review links

- [app context feature engineering 20260601](performance/2026-06-01-app-context-feature-engineering-20260601.md)
- [labelwise weekly progress target bottlenecks](experiments/2026-05-29-labelwise-weekly-progress-target-bottlenecks.md)
- [1875 feature domain ablation and dedup](features/2026-05-28-1875-feature-domain-ablation-and-dedup.md)
- [v200 v209 sparse splice review](experiments/2026-05-29-v200-v209-sparse-splice-review.md)
- [v186 shap leaderboard analysis](performance/2026-05-29-v186-shap-leaderboard-analysis.md)
- [2026-05-28 Sleep Lifelog Packet Synthesis](reports/2026-05-28-sleep-lifelog-packet-synthesis.md)

<!-- wiki-ingest:latest:start -->
### 27325835544-1 | 2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend

- link: [[performance/2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend]]
- publish_action: `bot_pr`
- risk_tier: `tier3-performance`
- review-required: true

### 26806097236-1 | 2026-06-01-app-context-feature-engineering-20260601

- link: [[performance/2026-06-01-app-context-feature-engineering-20260601]]
- publish_action: `bot_pr`
- risk_tier: `tier3-performance`
- review-required: true

### 26806097236-1 | 2026-05-29-labelwise-weekly-progress-target-bottlenecks

- link: [[experiments/2026-05-29-labelwise-weekly-progress-target-bottlenecks]]
- publish_action: `bot_pr`
- risk_tier: `tier2-interpretation`
- review-required: true

### 26806097236-1 | 2026-05-28-1875-feature-domain-ablation-and-dedup

- link: [[features/2026-05-28-1875-feature-domain-ablation-and-dedup]]
- publish_action: `bot_pr`
- risk_tier: `tier2-interpretation`
- review-required: true

### 26806097236-1 | 2026-05-29-v200-v209-sparse-splice-review

- link: [[experiments/2026-05-29-v200-v209-sparse-splice-review]]
- publish_action: `bot_pr`
- risk_tier: `tier2-interpretation`
- review-required: true

### 26806097236-1 | 2026-05-29-v186-shap-leaderboard-analysis

- link: [[performance/2026-05-29-v186-shap-leaderboard-analysis]]
- publish_action: `bot_pr`
- risk_tier: `tier3-performance`
- review-required: true

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
<!-- wiki-ingest:latest:end -->
