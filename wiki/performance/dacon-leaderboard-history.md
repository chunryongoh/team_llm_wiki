---
id: dacon-leaderboard-history
type: submission-history
page_role: registry
title: DACON Leaderboard History
status: active
date: 2026-06-12
summary: 현재 기록된 DACON public score 값은 external code-share, user-reported, DOCX/PDF observation이며 verified_public_lb row는 없다.
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

# DACON Leaderboard History

이 page는 DACON submission evidence를 local OOF diagnostic과 분리한다. 현재 기록된 public score는 submission id, leaderboard export, private score, submission CSV lineage가 없으므로 모두 tentative다.

## Evidence classes

- `verified_public_lb`: DACON submission id, public score, leaderboard export, submission CSV lineage가 있음
- `verified_private_lb`: private/final score artifact와 lineage가 있음
- `external_codeshare_public_lb_observation`: DACON code share 또는 attached notebook의 public score note, lineage 없음
- `user_reported_public_score_only`: report, Slack, PDF에 적힌 public score note
- `docx_report_public_lb_observation`: DOCX에 적힌 staged public LB observation
- `local_oof_diagnostic_only`: DACON leaderboard가 아닌 local validation evidence
- `notebook_output_observation_only`: notebook/PDF output summary

## Current records

| candidate | score | evidence_class | packet/source | status |
|---|---:|---|---|---|
| `dacon-public-05917-lgbm-xgb-anchor-reference` | `0.5917` | `external_codeshare_public_lb_observation` | DACON code share `13975`; packets `2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend`, `2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck` | tentative |
| `v186-target-specific-lgbm-catboost-blend` | `0.5922831771` | `user_reported_public_score_only` | `2026-05-29-v186-shap-leaderboard-analysis` | tentative |
| `v189-anchor` | `0.5925397` | `user_reported_public_score_only` | `2026-05-29-v200-v209-sparse-splice-review` | tentative |
| `v200` | `0.608842` | `user_reported_public_score_only` | `2026-05-29-v200-v209-sparse-splice-review` | tentative |
| `v204` | `0.592557` | `user_reported_public_score_only` | `2026-05-29-v200-v209-sparse-splice-review` | tentative |
| `v208` | `0.592547` | `user_reported_public_score_only` | `2026-05-29-v200-v209-sparse-splice-review` | tentative |
| `v209-q3-low` | `0.592543` | `user_reported_public_score_only` | `2026-05-29-v200-v209-sparse-splice-review` | tentative |
| `v209-q23-low` | `0.592551` | `user_reported_public_score_only` | `2026-05-29-v200-v209-sparse-splice-review` | tentative |
| `section9_labelwise_best_20260522_1239` | `0.5986218188` | `user_reported_public_score_only` | `2026-05-29-labelwise-weekly-progress-target-bottlenecks` | tentative |
| `section07_candidate_baseline_seed_ensemble_20260529_1029` | `0.6003735255` | `user_reported_public_score_only` | `2026-05-29-labelwise-weekly-progress-target-bottlenecks` | tentative |
| `app-context-stage0-baseline` | `0.6218831823` | `docx_report_public_lb_observation` | `2026-06-01-app-context-feature-engineering-20260601` | tentative |
| `app-context-stage1-daily-evening` | `0.6182941107` | `docx_report_public_lb_observation` | `2026-06-01-app-context-feature-engineering-20260601` | tentative |
| `app-context-stage2-presleep-night` | `0.6106185586` | `docx_report_public_lb_observation` | `2026-06-01-app-context-feature-engineering-20260601` | tentative |

## 2026-06-12 recheck note

Graph-first packet은 `0.5917`을 새 score row로 만들지 않는다. 같은 DACON code share reference의 추가 provenance이며 missing lineage는 그대로다: DACON submission id, leaderboard export/screenshot, submission CSV hash, private result가 없다.

## Boundary preserved

[Current Supported Claims](../claims/current-supported-claims.md)의 LGB/CB local OOF claim은 verified leaderboard row가 아니다. 반대로 위 public score notes는 local OOF metric으로 재해석하지 않는다. Code share notebook Local OOF `0.514`도 이 leaderboard table의 score가 아니다.

## Promotion evidence

Verified row로 승격하려면 DACON submission id, leaderboard export, timestamp, 제출 CSV lineage, local run mapping, feature/model policy mapping이 필요하다.

<!-- llm-synthesis:github-models-required-page-fill:2026-06-18:wiki-performance-dacon-leaderboard-history-md -->
## GitHub Models Fallback Synthesis | 2026-06-18

- packet_ids: `2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic`
- llm_summary: 2026-06-18 Wave41 LGB/CB Foldsafe Synthesis smoke local OOF diagnostic 결과를 packet review 및 performance leaf에 반영하였으며, claim registry에 기존 local_oof_diagnostic_only claim의 supported 상태를 유지하였다. DACON leaderboard, organizer validation, local OOF, notebook output...
- claim_status: preserved_from_raw_packet
- evidence_boundary: local_oof, notebook_output, DACON_public, DACON_private, and organizer_official evidence must stay separate.
- review_note: This page was conservatively filled in GitHub Actions because the compact fallback model omitted a required wiki page.
- synthesis_report: `wiki/reports/2026-06-18-sleep-lifelog-packet-synthesis.md`
