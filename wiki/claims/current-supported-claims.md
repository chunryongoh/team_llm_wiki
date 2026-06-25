---
id: current-supported-claims
type: claim-registry
page_role: registry
title: Current Supported Claims
status: active
date: 2026-06-12
summary: 현재 supported claim은 LGB/CB targetwise reblend local OOF diagnostic 하나이며, 2026-06-12 graph-first recheck도 external 0.5917 code-share와 notebook OOF 값을 tentative로 유지한다.
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

# Current Supported Claims

이 registry는 팀원이 믿어도 되는 claim과 아직 승격할 수 없는 claim을 분리한다. 성능 claim은 [DACON Leaderboard History](../performance/dacon-leaderboard-history.md), [Canonical Split And Leakage Policy](../preprocessing/canonical-split-and-leakage-policy.md), [Sleep Lifelog Evaluation Protocol](../decisions/sleep-lifelog-evaluation-protocol.md)을 함께 확인한다.

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
| external DACON code share Public `0.5917` for LGBM+XGB anchor blend | tentative | external code-share public LB observation only | [0.5917 reference](../performance/dacon-public-05917-lgbm-xgb-anchor-reference.md), `2026-06-12` recheck |
| code share notebook Local OOF `0.514`, target-specific `0.513` | tentative | notebook-output summary only | [2026-06-12 packet review](../performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck.md) |
| stability filtering `23177 -> 1682` | tentative | notebook/metrics summary, exact list missing | [Stability Filtered Feature Selection](../features/stability-filtered-feature-selection.md) |
| Subject-hole CV improves LB correlation | tentative | exploratory external split idea | [Subject Hole CV](../preprocessing/subject-hole-cv.md) |
| app context staged public LB `0.6218831823 -> 0.6106185586` | tentative | DOCX public LB observation | [app context](../performance/2026-06-01-app-context-feature-engineering-20260601.md) |
| Section07 labelwise public note `0.5986218188` | tentative | user-reported public score only | [labelwise weekly](../reports/2026-05-29-labelwise-weekly-progress-target-bottlenecks.md) |
| 1875 feature pool and `715` dedup candidates | superseded | historical DOCX/PDF notebook-output; raw ablation/correlation evidence still missing | [1875 feature](../features/2026-05-28-1875-feature-domain-ablation-and-dedup.md) |
| v186 public LB `0.5922831771` and SHAP drivers | tentative | user/PDF-reported public score plus interpretation evidence | [v186 SHAP](../performance/2026-05-29-v186-shap-leaderboard-analysis.md) |
| v200-v209 sparse splice guardrail | tentative | PDF review and public-score notes | [v200-v209](../reports/2026-05-29-v200-v209-sparse-splice-review.md) |

## Disallowed Promotions

- External `0.5917`를 team verified DACON leaderboard score로 부르면 안 된다.
- Notebook Local OOF `0.514`를 team canonical local OOF 또는 Wave41 OOF와 직접 비교하면 안 된다.
- `LightGBM + CatBoost` 또는 `LGBM + XGB`가 전역 최선이라는 claim은 supported가 아니다.
- SHAP importance, stability score, public score note를 causal feature proof로 쓰면 안 된다.
- local OOF, notebook-output, user-reported public score, DACON public/private leaderboard, official validation을 한 ranking surface로 합치면 안 된다.

## Next Review

Submission lineage packet, V152 anchor reproduction packet, fold-safe leakage ablation packet이 들어오면 해당 row의 status를 재검토한다.

<!-- llm-synthesis:github-models-required-page-fill:2026-06-18:wiki-claims-current-supported-claims-md -->
## GitHub Models Fallback Synthesis | 2026-06-18

- packet_ids: `2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic`
- packet_summary: 2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic: Wave41 LGB/CB fold-safe synthesis smoke improved the prior LGB/CB reproduction local OOF diagnostic line from 0.6198365213240887 to 0.6195964535023479, but remains local OOF only and short of the 0.61 goal.
- claim_status: preserved_from_raw_packet
- evidence_boundary: local_oof, notebook_output, DACON_public, DACON_private, and organizer_official evidence must stay separate.
- review_note: This page was conservatively filled in GitHub Actions because the compact fallback model omitted a required wiki page.
- synthesis_report: `wiki/reports/2026-06-18-sleep-lifelog-packet-synthesis.md`

<!-- llm-synthesis:github-models-required-page-fill:2026-06-25:wiki-claims-current-supported-claims-md -->
## GitHub Models Fallback Synthesis | 2026-06-25

- packet_ids: `2026-06-25-wave43-claude-campaign-stack-local-oof-projection`
- packet_summary: 2026-06-25-wave43-claude-campaign-stack-local-oof-projection: Claude 별도 작업으로 수행된 wave43 캠페인 결과를 team LLM wiki에 올리기 위한 성능 packet입니다. 최종 stack-v2는 subject-mean baseline 0.62453 대비 calibrated local OOF macro log-loss 0.58972를 기록했고, projected public은 0.59272로 추정되었습니다. 실제 확인된 public score 0.60761은 Claude 진행 로그 기반 관측치이므로 leaderboard export가 추가되기 전까지는 별도 claim boundary를 유지해야 합니다.
- claim_status: preserved_from_raw_packet
- evidence_boundary: local_oof, notebook_output, DACON_public, DACON_private, and organizer_official evidence must stay separate.
- review_note: This page was conservatively filled in GitHub Actions because the compact fallback model omitted a required wiki page.
- synthesis_report: `wiki/reports/2026-06-25-sleep-lifelog-packet-synthesis.md`
