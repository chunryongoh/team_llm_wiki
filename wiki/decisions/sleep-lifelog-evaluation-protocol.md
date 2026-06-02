---
id: sleep-lifelog-evaluation-protocol
type: decision
title: Sleep Lifelog Evaluation Protocol
status: active-review-required
date: 2026-06-02
dataset: sleep-lifelog-2024
benchmark: sleep-health-hackathon-v0
summary: sleep-lifelog 평가는 local OOF, notebook-output, user-reported public score, DACON public/private leaderboard, organizer-official validation을 절대 합치지 않는다.
review_required: true
raw_evidence:
- raw/users/cho-hyewon/performance/2026-06-01-app-context-feature-engineering-20260601/manifest.yaml
- raw/users/cho-hyewon/performance/2026-06-01-app-context-feature-engineering-20260601/metrics.json
- raw/users/cho-hyewon/performance/2026-06-01-app-context-feature-engineering-20260601/packet.md
- raw/users/cho-hyewon/performance/2026-06-01-app-context-feature-engineering-20260601/performance.yaml
- raw/users/cho-hyewon/performance/2026-06-01-app-context-feature-engineering-20260601/source/feature-engineering-result-report-20260601.docx
- raw/users/cho-hyewon/performance/2026-06-01-app-context-feature-engineering-20260601/source/feature-engineering-result-report-20260601.txt
- raw/users/cho-hyewon/performance/2026-06-01-app-context-feature-engineering-20260601/wiki_plan.yaml
- raw/users/hyeonseokrock/experiments/2026-05-29-labelwise-weekly-progress-target-bottlenecks/manifest.yaml
- raw/users/hyeonseokrock/experiments/2026-05-29-labelwise-weekly-progress-target-bottlenecks/evidence.yaml
- raw/users/hyeonseokrock/experiments/2026-05-29-labelwise-weekly-progress-target-bottlenecks/metrics.json
- raw/users/hyeonseokrock/experiments/2026-05-29-labelwise-weekly-progress-target-bottlenecks/packet.md
- raw/users/hyeonseokrock/experiments/2026-05-29-labelwise-weekly-progress-target-bottlenecks/source/weekly-progress-20260521-20260529-ko-short.md
- raw/users/hyeonseokrock/experiments/2026-05-29-labelwise-weekly-progress-target-bottlenecks/source/prompt4llmwiki.txt
- raw/users/hyeonseokrock/experiments/2026-05-29-labelwise-weekly-progress-target-bottlenecks/wiki_plan.yaml
- raw/users/ko-nayoung/features/2026-05-28-1875-feature-domain-ablation-and-dedup/manifest.yaml
- raw/users/ko-nayoung/features/2026-05-28-1875-feature-domain-ablation-and-dedup/features.yaml
- raw/users/ko-nayoung/features/2026-05-28-1875-feature-domain-ablation-and-dedup/packet.md
- raw/users/ko-nayoung/features/2026-05-28-1875-feature-domain-ablation-and-dedup/source/20260528-notebook-outputs.docx
- raw/users/ko-nayoung/features/2026-05-28-1875-feature-domain-ablation-and-dedup/source/20260528-notebook-outputs.txt
- raw/users/ko-nayoung/features/2026-05-28-1875-feature-domain-ablation-and-dedup/source/feature-info.pdf
- raw/users/ko-nayoung/features/2026-05-28-1875-feature-domain-ablation-and-dedup/source/feature-info.txt
- raw/users/ko-nayoung/features/2026-05-28-1875-feature-domain-ablation-and-dedup/wiki_plan.yaml
- raw/users/moon-hyungdo/experiments/2026-05-29-v200-v209-sparse-splice-review/manifest.yaml
- raw/users/moon-hyungdo/experiments/2026-05-29-v200-v209-sparse-splice-review/evidence.yaml
- raw/users/moon-hyungdo/experiments/2026-05-29-v200-v209-sparse-splice-review/metrics.json
- raw/users/moon-hyungdo/experiments/2026-05-29-v200-v209-sparse-splice-review/packet.md
- raw/users/moon-hyungdo/experiments/2026-05-29-v200-v209-sparse-splice-review/source/etri-2026-v2-review.pdf
- raw/users/moon-hyungdo/experiments/2026-05-29-v200-v209-sparse-splice-review/source/etri-2026-v2-review.txt
- raw/users/moon-hyungdo/experiments/2026-05-29-v200-v209-sparse-splice-review/wiki_plan.yaml
- raw/users/moon-hyungdo/performance/2026-05-29-v186-shap-leaderboard-analysis/manifest.yaml
- raw/users/moon-hyungdo/performance/2026-05-29-v186-shap-leaderboard-analysis/metrics.json
- raw/users/moon-hyungdo/performance/2026-05-29-v186-shap-leaderboard-analysis/packet.md
- raw/users/moon-hyungdo/performance/2026-05-29-v186-shap-leaderboard-analysis/performance.yaml
- raw/users/moon-hyungdo/performance/2026-05-29-v186-shap-leaderboard-analysis/source/etri-2026-v186-shap-analysis.pdf
- raw/users/moon-hyungdo/performance/2026-05-29-v186-shap-leaderboard-analysis/source/etri-2026-v186-shap-analysis.txt
- raw/users/moon-hyungdo/performance/2026-05-29-v186-shap-leaderboard-analysis/source/v186-top10-feature-meaning-ko.md
- raw/users/moon-hyungdo/performance/2026-05-29-v186-shap-leaderboard-analysis/wiki_plan.yaml
---

# Sleep Lifelog Evaluation Protocol

## 결정

Sleep-lifelog 성능과 feature claim은 다음 evidence surface를 분리한다.

1. `local_oof_diagnostic_only`: split, group key, metric이 raw로 있는 local diagnostic. 현재 supported claim은 [LGB CB Reproduction Local OOF Diagnostic](../performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic.md)뿐이다.
2. `notebook_output_observation_only`: notebook saved output, PDF/DOCX summary, SHAP note. feature hypothesis에는 쓸 수 있으나 supported performance claim은 아니다.
3. `user_reported_public_score_only`: source note나 report에 적힌 DACON public score. submission id와 leaderboard export 없이는 tentative다.
4. `verified_public_lb`와 `verified_private_lb`: DACON submission id, score, timestamp, submission CSV lineage가 있어야 한다.
5. `organizer_official_validation`: 주최 측 official split 또는 official result artifact가 있어야 한다.

## 현재 적용

- supported: LGB/CB Q2 targetwise reblend local OOF delta `-3.19332341584e-05`, boundary `local_oof_diagnostic_only`.
- tentative public notes: v186 `0.5922831771`, v189/v200-v209 series, Section07 `0.5986218188`, app context `0.6106185586`.
- tentative feature notes: 1,875 pool, app context, v186 SHAP, temporal overlap negative report.

이 값들은 서로 ranking 비교에 사용할 수 없다. 특히 reported public LB가 낮다고 해서 supported local OOF claim보다 강한 claim이 되지 않는다.

## Promotion gates

| target claim | required evidence |
|---|---|
| public leaderboard | DACON submission id, public score, leaderboard export, submission CSV lineage |
| private leaderboard | private score or final score artifact, same lineage |
| fold-safe local OOF | fold별 preprocessing fit, target encoding policy, feature cutoff audit |
| feature policy | exact feature list, same-split ablation, target-specific deltas |
| small-delta robustness | repeated split or multi-seed uncertainty table |

## Operational guardrails

Sparse splice, Q2 conservative edit, Q3 frequency feature, S4 narrow WASO proxy는 현재 working guardrail이다. raw replay validator와 same-split ablation이 들어오기 전에는 final decision이나 supported claim으로 쓰지 않는다.

## Links

- [DACON Leaderboard History](../submissions/dacon-leaderboard-history.md)
- [Canonical Split And Leakage Policy](../preprocessing/canonical-split-and-leakage-policy.md)
- [Current Supported Claims](../claims/current-supported-claims.md)
- [Sleep Lifelog Open Questions](../questions/sleep-lifelog-open-questions.md)
