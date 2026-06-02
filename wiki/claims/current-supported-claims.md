---
id: current-supported-claims
type: claim-registry
title: Current Supported Claims
status: active
date: 2026-06-02
summary: 현재 팀이 raw evidence와 claim boundary 안에서 믿을 수 있는 claim을 관리한다.
raw_evidence:
- raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/metrics.json
- raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/blend_weights.json
- raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/leakage_audit.json
- raw/users/hyeonseokrock/experiments/2026-06-01-lifelog-section07-working-notes/packet.md
- raw/users/hyeonseokrock/experiments/2026-06-01-lifelog-section07-notebook-overview/packet.md
---

# Current Supported Claims

이 페이지는 팀원이 현재 믿어도 되는 claim과 아직 승격할 수 없는 claim을 분리한다. 성능 claim은 [DACON Leaderboard History](../submissions/dacon-leaderboard-history.md)와 [Canonical Split And Leakage Policy](../preprocessing/canonical-split-and-leakage-policy.md)를 함께 확인해야 한다.

## Supported Claims

### LGB/CB targetwise reblend local OOF diagnostic

- status: `supported`
- boundary: `local_oof_diagnostic_only`
- source: [LGB CB Reproduction Local OOF Diagnostic](../performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic.md)
- supported statement: LGB/CB reproduction은 standalone 우위가 아니라 Q2에 fixed LGB/CB blend를 `0.1` 넣은 targetwise reblend로 Wave41 local OOF line을 아주 작게 개선했다.
- key values: final macro log-loss `0.6198365213240887`, Wave41 baseline `0.6198684545582471`, delta `-3.19332341584e-05`
- guardrail: DACON public/private leaderboard claim으로 승격하지 않는다.

## Tentative Or Boundary-Limited Claims

### Section07 user-reported public score notes

- status: `tentative`
- boundary: `user_reported_public_score_only`
- source: [LifeLog Section 07 Working Notes](../experiments/2026-06-01-lifelog-section07-working-notes.md)
- note: `section9_labelwise_best_20260522_1239`의 public score `0.5986218188`와 `section07_candidate_baseline_seed_ensemble_20260529_1029`의 public score `0.6003735255`는 raw DACON submission id, leaderboard export, submission file lineage가 없으므로 verified leaderboard claim이 아니다.

### Section07 notebook-output observations

- status: `tentative`
- boundary: `notebook_output_observation_only`
- source: [LifeLog Section 07 Notebook Overview](../experiments/2026-06-01-lifelog-section07-notebook-overview.md)
- note: notebook structure, saved output summary, feature policy observations은 다음 실험 설계에는 유용하지만 재실행 evidence나 raw metric evidence가 아니다.

## Disallowed Promotions

- "LightGBM + CatBoost가 전반적으로 가장 좋다"는 현재 supported claim이 아니다.
- "Section07 public score가 검증된 DACON leaderboard score다"는 현재 supported claim이 아니다.
- "v5 feature policy가 채택됐다"는 현재 supported claim이 아니다. 현재 section07 notes는 global v5 acceptance failed 후 current labelwise additive policy를 유지한다.

## Next Review

- DACON submission lineage packet이 들어오면 Section07 score notes를 leaderboard claim으로 승격할지 검토한다.
- fold-safe ablation packet이 들어오면 LGB/CB 및 section07 feature policy의 leakage boundary를 재평가한다.
