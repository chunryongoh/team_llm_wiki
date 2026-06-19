---
id: sleep-lifelog-evaluation-protocol
type: decision
page_role: decision
title: Sleep Lifelog Evaluation Protocol
status: active-review-required
date: 2026-06-12
dataset: sleep-lifelog-2024
benchmark: sleep-health-hackathon-v0
summary: sleep-lifelog 평가는 local OOF, notebook-output, external public note, DACON public/private leaderboard, organizer-official validation을 절대 합치지 않는다.
review_required: true
raw_evidence:
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/manifest.yaml
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/artifact_summary.json
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/dacon-public-05917-lgbm-xgb-anchor-subject-hole.ipynb
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/metrics.json
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/packet.md
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/packet_entity_graph.json
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/performance.yaml
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/question_queue.yaml
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/scan-metrics.csv
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/semantic_lint.json
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/dacon-codeshare-13975.md
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/wiki_plan.yaml
---

# Sleep Lifelog Evaluation Protocol

## Decision

Sleep-lifelog 성능과 feature claim은 evidence surface를 분리한다.

1. `local_oof_diagnostic_only`: split, group key, metric raw가 있는 local diagnostic. 현재 supported claim은 [LGB CB Reproduction Local OOF Diagnostic](../performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic.md)뿐이다.
2. `notebook_output_observation_only`: notebook saved output, PDF/DOCX summary, SHAP note. hypothesis에는 쓸 수 있으나 supported performance claim은 아니다.
3. `user_reported_public_score_only` 또는 `external_codeshare_public_lb_observation`: source note나 DACON code share에 적힌 public score. submission id와 leaderboard export 없이는 tentative다.
4. `verified_public_lb`와 `verified_private_lb`: DACON submission id, score, timestamp, submission CSV lineage가 있어야 한다.
5. `organizer_official_validation`: 주최 측 official split 또는 official result artifact가 있어야 한다.

## Current application

- supported: LGB/CB Q2 targetwise reblend local OOF delta `-3.19332341584e-05`, boundary `local_oof_diagnostic_only`.
- tentative external reference: DACON code share `13975` Public `0.5917` for [LGBM XGB Anchor Subject Hole Blend](../models/lgbm-xgb-anchor-subject-hole-blend.md). `2026-06-12` graph-first recheck도 submission id, export, CSV lineage를 제공하지 않았다.
- notebook-output only: same code share notebook Local OOF `0.514`, target-specific `0.513`, feature count `23177 -> 1682`.
- tentative public notes: v186 `0.5922831771`, v189/v200-v209 series, Section07 `0.5986218188`, app context `0.6106185586`.

이 값들은 서로 ranking surface가 아니다. External public note가 supported local OOF claim보다 강한 claim이 되지 않는다.

## Promotion gates

| target claim | required evidence |
|---|---|
| public leaderboard | DACON submission id, public score, leaderboard export, submission CSV lineage |
| private leaderboard | private/final score artifact와 same lineage |
| fold-safe local OOF | fold별 preprocessing fit, target encoding policy, feature cutoff audit |
| feature policy | exact feature list, same-split ablation, target-specific deltas |
| anchor OOF feature | out-of-fold generation proof, row identity, no target leakage audit |

## Guardrails

V152 anchor OOF, Subject-hole CV, stability filtering, window-pair features는 useful reference지만 adoption decision이 아니다. Raw replay validator와 same-split ablation 전에는 final decision이나 supported claim으로 쓰지 않는다.

## Links

- [DACON Leaderboard History](../performance/dacon-leaderboard-history.md)
- [Canonical Split And Leakage Policy](../preprocessing/canonical-split-and-leakage-policy.md)
- [Current Supported Claims](../claims/current-supported-claims.md)
- [Sleep Lifelog Open Questions](../targets/sleep-lifelog-open-issues.md)

<!-- llm-synthesis:github-models-required-page-fill:2026-06-18:wiki-decisions-sleep-lifelog-evaluation-protocol-md -->
## GitHub Models Fallback Synthesis | 2026-06-18

- packet_ids: `2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic`
- packet_summary: 2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic: Wave41 LGB/CB fold-safe synthesis smoke improved the prior LGB/CB reproduction local OOF diagnostic line from 0.6198365213240887 to 0.6195964535023479, but remains local OOF only and short of the 0.61 goal.
- claim_status: preserved_from_raw_packet
- evidence_boundary: local_oof, notebook_output, DACON_public, DACON_private, and organizer_official evidence must stay separate.
- review_note: This page was conservatively filled in GitHub Actions because the compact fallback model omitted a required wiki page.
- synthesis_report: `wiki/reports/2026-06-18-sleep-lifelog-packet-synthesis.md`
