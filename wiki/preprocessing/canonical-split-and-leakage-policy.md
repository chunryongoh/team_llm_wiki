---
id: canonical-split-and-leakage-policy
type: preprocessing-policy
page_role: registry
title: Canonical Split And Leakage Policy
status: active
date: 2026-06-12
dataset: sleep-lifelog-2024
benchmark: sleep-health-hackathon-v0
summary: sleep-lifelog split surface와 leakage boundary를 claim 옆에 붙여 local OOF, notebook-output, external public score를 혼합하지 않게 한다.
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

# Canonical Split And Leakage Policy

이 page는 [Sleep Lifelog 2024 Dataset](sleep-lifelog-2024.md) 성능 claim의 split, group key, fit scope, feature cutoff를 관리한다. Split-specific detail은 [Subject Hole CV](subject-hole-cv.md) 같은 leaf로 분리한다.

## Known split and evidence surfaces

| split surface | fold count | group key | evidence class | note |
|---|---:|---|---|---|
| `groupkfold-subject-3fold-oof` | 3 | `subject_id` | local canonical sprint definition | 초기 dataset/benchmark 기준 |
| `local-groupkfold-subject-5fold-oof` | 5 | `subject_id` | `local_oof_diagnostic_only` | LGB/CB supported diagnostic 기준 |
| `subject-hole-cv-5fold-reference` | 5 | `subject_id` | external code-share and notebook-output reference | DACON code share `13975`; `2026-06-12` recheck에서도 fold file 없음 |
| `v186-report-oof-plus-public-lb-observation` | unknown | `subject_id` | PDF OOF + user-reported public score | submission lineage 없음 |
| `20260526-172609-lgbcat-timesplit-public-lb-observation` | unknown | `subject_id` | DOCX public LB observation | app-context stage report |
| `notebook-output-and-slack-summary-observation` | mixed | `subject_id` | notebook-output observation | 1875 feature/dedup report |
| `public-lb-observation-and-local-proxy-review` | mixed | `subject_id` | public score note + proxy review | v200-v209 sparse splice |
| `section07-working-notes-and-weekly-progress-observation` | mixed | `subject_id` | working-note observation | labelwise target bottleneck |

서로 다른 surface는 같은 validation metric처럼 비교하지 않는다.

## Subject-hole CV boundary

Subject-hole CV는 각 subject를 `sleep_date` 순으로 나누고 early+late chunk를 validation hole로 쓰는 external reference split이다. Test의 interleaving 구조를 의식한 아이디어지만, 팀 canonical policy가 되려면 same feature/model run, leakage audit, public/private correlation evidence가 필요하다.

## Fit scope rules

- imputation, normalization, target encoding은 fold-safe claim을 하려면 train-fold-only fit이어야 한다.
- global train median imputer, train/test transductive statistics, subject target encoding은 leakage risk로 남긴다.
- V152 anchor OOF는 train rows에서 strict out-of-fold로 생성되고 row-aligned임이 증명되어야 feature로 허용된다.
- high-correlation pruning, stability filtering, subject-relative statistics가 full data fit이면 feature policy로 승격하지 않는다.

## Current known risks

- LGB/CB reproduction: transductive statistics, global imputer, subject encoding, date/rolling alignment risk
- DACON 0.5917 reference: V152 OOF CSV, feature parquet, fold file, submission lineage 없음
- 2026-06-12 graph-first packet: `packet_entity_graph`는 split signal만 재확인하며 fold assignment artifact를 제공하지 않음
- app-context: feature list hash, submission lineage, same-split OOF 없음
- 1875 pool: exact `715` list와 fold-scoped dedup 증거 없음
- v186/v200/Section07: leaderboard provenance와 target-level audit 부족

## Promotion gate

성능 claim을 `supported` 또는 `verified_public_lb`로 승격하려면 split surface, preprocessing fit scope, raw metric, leakage audit, submission lineage가 같은 provenance chain으로 연결되어야 한다.

<!-- llm-synthesis:github-models-required-page-fill:2026-06-18:wiki-preprocessing-canonical-split-and-leakage-policy-md -->
## GitHub Models Fallback Synthesis | 2026-06-18

- packet_ids: `2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic`
- llm_summary: 2026-06-18 Wave41 LGB/CB Foldsafe Synthesis smoke local OOF diagnostic 결과를 packet review 및 performance leaf에 반영하였으며, claim registry에 기존 local_oof_diagnostic_only claim의 supported 상태를 유지하였다. DACON leaderboard, organizer validation, local OOF, notebook output...
- claim_status: preserved_from_raw_packet
- evidence_boundary: local_oof, notebook_output, DACON_public, DACON_private, and organizer_official evidence must stay separate.
- review_note: This page was conservatively filled in GitHub Actions because the compact fallback model omitted a required wiki page.
- synthesis_report: `wiki/reports/2026-06-18-sleep-lifelog-packet-synthesis.md`
