---
id: current-supported-claims
type: claim-registry
title: Current Supported Claims
status: active
date: 2026-06-02
summary: 현재 supported claim은 LGB/CB targetwise reblend local OOF diagnostic 하나이며, 새 public LB 및 feature 분석 claim은 모두 tentative로 보존한다.
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

# Current Supported Claims

이 registry는 팀원이 믿어도 되는 claim과 아직 승격할 수 없는 claim을 분리한다. 성능 claim은 반드시 [DACON Leaderboard History](../submissions/dacon-leaderboard-history.md), [Canonical Split And Leakage Policy](../preprocessing/canonical-split-and-leakage-policy.md), [Sleep Lifelog Evaluation Protocol](../decisions/sleep-lifelog-evaluation-protocol.md)을 함께 확인한다.

## Supported Claims

### LGB/CB targetwise reblend local OOF diagnostic

- status: `supported`
- boundary: `local_oof_diagnostic_only`
- source: [LGB CB Reproduction Local OOF Diagnostic](../performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic.md)
- statement: LGB/CB reproduction은 standalone 우위가 아니라 Q2에 fixed LGB/CB blend `0.1`을 넣은 targetwise reblend로 Wave41 local OOF line을 아주 작게 개선했다.
- values: final `grouped_macro_log_loss` `0.6198365213240887`, baseline `0.6198684545582471`, delta `-3.19332341584e-05`
- guardrail: DACON public/private leaderboard 또는 organizer-official validation claim으로 승격하지 않는다.

## Tentative Or Boundary-Limited Claims

| claim | status | boundary | source |
|---|---|---|---|
| app context staged public LB `0.6218831823 -> 0.6106185586` | tentative | DOCX public LB observation | [app context](../performance/2026-06-01-app-context-feature-engineering-20260601.md) |
| Section07 labelwise public note `0.5986218188` | tentative | user-reported public score only | [labelwise weekly](../experiments/2026-05-29-labelwise-weekly-progress-target-bottlenecks.md) |
| temporal overlap/window augmentation hurt | tentative | weekly progress observation | [labelwise weekly](../experiments/2026-05-29-labelwise-weekly-progress-target-bottlenecks.md) |
| 1,875 feature pool and `715` dedup candidates | tentative | DOCX/PDF notebook-output | [1875 feature](../features/2026-05-28-1875-feature-domain-ablation-and-dedup.md) |
| V2 CatBoost avg `-0.0063` report | tentative | contributor-reported notebook output | [1875 feature](../features/2026-05-28-1875-feature-domain-ablation-and-dedup.md) |
| v186 public LB `0.5922831771` | tentative | user/PDF-reported public score only | [v186 SHAP](../performance/2026-05-29-v186-shap-leaderboard-analysis.md) |
| v186 SHAP target drivers | tentative | feature-importance evidence | [v186 SHAP](../performance/2026-05-29-v186-shap-leaderboard-analysis.md) |
| v200-v209 sparse splice guardrail | tentative | PDF review and public-score notes | [v200-v209](../experiments/2026-05-29-v200-v209-sparse-splice-review.md) |

## Disallowed Promotions

- `LightGBM + CatBoost`가 전역 최선이라는 claim은 supported가 아니다.
- v186, v189, Section07, app-context score를 verified DACON leaderboard score로 부르면 안 된다.
- SHAP feature importance를 causal feature proof로 쓰면 안 된다.
- local OOF, notebook-output, user-reported public score, DACON public/private leaderboard, official validation을 한 ranking surface로 합치면 안 된다.

## Next Review

Leaderboard provenance packet, fold-safe ablation packet, feature hash/audit packet이 들어오면 해당 row의 status를 재검토한다.
