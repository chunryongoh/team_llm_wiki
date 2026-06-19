---
claim_boundary: local_oof_diagnostic_only
claim_status: supported
date: "2026-06-18"
mode: structured
owner: chunryongoh
packet_type: performance
route: wiki/performance
title: Wave41 LGB CB Foldsafe Synthesis Smoke Local OOF Diagnostic
---

# Wave41 LGB/CB fold-safe synthesis smoke local OOF diagnostic

## 관측된 사실

- 이 packet은 ETRI local workspace의 `2026-06-18-wave41-lgb-cb-foldsafe-synthesis-v1` smoke suite를 팀 위키에 올리기 위한 performance packet이다.
- suite는 `13`개 후보를 완료했고 targetwise reblend도 완료했다.
- 최종 targetwise reblend grouped macro log-loss는 `0.6195964535023479`이다.
- 같은 local OOF 계열의 prior LGB/CB reproduction line은 `0.6198365213240887`이며, delta는 `-0.0002400678217408`이다. Log-loss 기준으로 낮을수록 좋다.
- 첫 목표 `0.61`까지는 아직 `+0.0095964535023479` 남아 있다.
- target scores는 Q1 `0.6225370998897288`, Q2 `0.6555493560477773`, Q3 `0.6309857415368405`, S1 `0.562996471228798`, S2 `0.6113857154018603`, S3 `0.595105227779678`, S4 `0.6586155626317527`이다.
- decision matrix는 `supported` 2개, `tentative` 4개, `disputed` 25개 row를 기록했다.
- supported row는 `q2_nested_platt_diagnostic_v1`과 `s4_nested_platt_diagnostic_v1`이며, 각각 targetwise reblend weight `0.1`로 지원된다. 이는 standalone target-score superiority가 아니라 blend/calibration diversity support다.

## 해석

핵심 claim은 LGB/CB raw reliability 후보가 전반적으로 강하다는 것이 아니다. 대부분의 raw reliability 후보는 macro Brier guard 때문에 disputed로 남았다. 지원되는 좁은 claim은 Q2/S4 nested Platt diagnostic이 targetwise reblend에서 선택되어 prior local OOF line을 작게 낮췄다는 것이다.

## claim boundary

이 packet의 claim boundary는 `local_oof_diagnostic_only`이다. DACON public leaderboard, private leaderboard, organizer-official validation, 또는 `0.5x` claim으로 승격하지 않는다.

## 다음 액션

Q2/S4 calibration diversity는 유지하되, disputed가 많은 reliability/sample-weight 후보를 Brier-safe하게 줄이고 full escalation 전 source-pool 정책을 더 좁힌다.

## Wiki Integration Hints

### stable_entities

- {'action': 'create_or_update', 'id': 'performance:wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof', 'kind': 'performance', 'page': 'wiki/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic.md', 'page_role': 'packet_review', 'promotion_reason': ['current_local_oof_line_update', 'claim_boundary_needed']}
- {'action': 'update', 'id': 'model:lightgbm-catboost', 'kind': 'model', 'page': 'wiki/models/lightgbm-catboost.md', 'page_role': 'leaf', 'promotion_reason': ['same_model_family_new_foldsafe_synthesis_result', 'calibration_diversity_guidance_needed']}
- {'action': 'update', 'id': 'benchmark:sleep-health-hackathon-v0', 'kind': 'benchmark', 'page': 'wiki/performance/sleep-health-hackathon-evaluation-policy.md', 'page_role': 'policy', 'promotion_reason': ['local_oof_claim_boundary_reinforcement']}
- {'action': 'update', 'id': 'claim:current-supported-local-oof', 'kind': 'claim', 'page': 'wiki/claims/current-supported-claims.md', 'page_role': 'registry', 'promotion_reason': ['supported_local_oof_claim_changes']}

### affected_pages

- {'expected_change': 'Mark as prior/superseded current-line evidence, not invalidated as raw evidence.', 'path': 'wiki/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic.md', 'role': 'packet_review'}
- {'expected_change': 'Add fold-safe synthesis smoke interpretation: useful Q2/S4 calibration diversity, not broad standalone superiority.', 'path': 'wiki/models/lightgbm-catboost.md', 'role': 'leaf'}
- {'expected_change': 'Add closeable Q2/S4 Brier-safe calibration/reliability follow-up if not already present.', 'path': 'wiki/targets/sleep-lifelog-open-issues.md', 'role': 'hub'}
- {'expected_change': 'No DACON leaderboard change; preserve evidence-surface separation.', 'path': 'wiki/performance/dacon-leaderboard-history.md', 'role': 'registry'}

### claim_registry_updates

- supported: Wave41 LGB/CB fold-safe synthesis smoke local OOF targetwise reblend scored 0.6195964535023479, improving the prior LGB/CB reproduction local line by about -0.0002400678217408 under local_oof_diagnostic_only.
- supported but narrow: Q2/S4 nested Platt diagnostics are selected by targetwise reblend weight 0.1; this is not standalone model superiority.
- disputed: most raw LGB/CB weighted reliability rows remain disputed by macro Brier guard or lack of targetwise support.

### supersedes_or_conflicts

- Supersedes the prior maintained local OOF diagnostic line 2026-06-01-lgb-cb-reproduction-local-oof-diagnostic numerically, but does not invalidate its raw evidence.
- Does not supersede DACON public/private leaderboard observations because this packet has no submission lineage.

### topic_pages

- wiki/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic.md
- wiki/models/lightgbm-catboost.md
- wiki/targets/sleep-lifelog-open-issues.md

### decisions

- Keep claim boundary local_oof_diagnostic_only; do not run as DACON/public promotion evidence.

### open_questions

- {'close_condition': 'A full or stricter smoke packet shows Brier-safe support or disputes the branch.', 'id': 'wave41-lgb-cb-full-brier-safe-escalation', 'merge_blocker': False, 'needed_evidence': ['full run decision_matrix.csv', 'macro Brier delta by candidate', 'targetwise reblend weights'], 'owner_role': 'model-owner', 'priority': 'high', 'question': 'Can Q2/S4 calibration diversity be preserved while reducing disputed macro Brier rows in a full run?'}
- {'close_condition': 'Submission lineage packet confirms or rejects leaderboard mapping.', 'id': 'wave41-lgb-cb-public-lineage', 'merge_blocker': False, 'needed_evidence': ['submission id', 'submission CSV hash', 'leaderboard export', 'local run mapping'], 'owner_role': 'validation-owner', 'priority': 'medium', 'question': 'Does any Wave41 LGB/CB synthesis output map to a DACON public/private submission?'}

### semantic_lint

- Do not promote local OOF diagnostic evidence to DACON public/private leaderboard or organizer-official validation.
- Do not call LGB/CB fold-safe synthesis broadly superior as a standalone model.
- Supported rows are supported by targetwise reblend weight, not target_delta_vs_anchor.
- Macro Brier disputed rows must remain visible in synthesis.
- This packet improves the local maintained diagnostic line but remains short of the 0.61 goal.
