---
id: sleep-lifelog-open-questions
type: open-questions
page_role: open-questions
title: Sleep Lifelog Open Questions
status: active
last_updated: 2026-06-12
summary: leaderboard provenance, V152 anchor OOF, Subject-hole CV, feature ablation, split/leakage audit를 닫기 위한 실행 backlog다.
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

# Sleep Lifelog Open Questions

이 backlog는 [Feature Landscape](../features/sleep-lifelog-feature-landscape.md), [Evaluation Protocol](../decisions/sleep-lifelog-evaluation-protocol.md), [DACON Leaderboard History](../performance/dacon-leaderboard-history.md), [Canonical Split And Leakage Policy](../preprocessing/canonical-split-and-leakage-policy.md)에 연결된다. 아래 질문이 닫히기 전에는 tentative claim을 supported 또는 verified leaderboard claim으로 승격할 수 없다.

| id | priority | owner_role | merge_blocker | question | needed_evidence | close_condition |
|---|---|---|---|---|---|---|
| `dacon-public-05917-submission-lineage` | high | validation-owner | false | External `0.5917` public score를 DACON submission id, leaderboard export, exact submission CSV lineage에 연결할 수 있는가? | submission id, export/screenshot, CSV hash, timestamp | 관찰이 traceable하면 verified 후보로 바꾸고, 아니면 reference-only로 고정 |
| `v152-anchor-oof-reproduction` | high | model-owner | false | V152 anchor OOF probabilities를 팀 row identity와 fold-safe 절차로 재현할 수 있는가? | V152 recipe, OOF CSV, fold assignment, leakage audit | 재현 또는 non-portable 판단 기록 |
| `subject-hole-cv-vs-canonical-groupkfold` | medium | validation-owner | false | Subject-hole CV가 canonical GroupKFold보다 public/private correlation을 더 잘 설명하는가? | same-run dual split metrics, leaderboard mapping, leakage audit | adopt/reject/exploratory decision 기록 |
| `stability-filter-selected-list` | medium | feature-owner | false | `23177 -> 1682` stability filter의 exact selected list와 target별 delta는 무엇인가? | selected list, score formula, fold-safe proof, ablation | feature policy 승격 또는 reference-only 결정 |
| `window-pair-parquet-implementation` | medium | feature-owner | false | Window-pair features가 실제 sensor parquet에서 구현되어 성능 기여를 보였는가? | parquet-backed code, feature hash, same-split ablation | placeholder caveat 제거 또는 reference-only 고정 |
| `app-context-raw-submission-lineage` | high | feature-performance-owner | false | app-context stage scores가 어떤 submission lineage에 대응하는가? | submission CSV, leaderboard export, local OOF, feature hash | app-context claim 승격 또는 permanent tentative 결정 |
| `q3-frequency-feature-design` | high | target-feature-owner | false | Q3 frequency/window feature를 어떤 validation surface에서 시험할 것인가? | formulas, same-split Q3 metrics, ablation table | Q3 후보 채택/폐기 기록 |
| `s4-broad-feature-degradation` | high | target-feature-owner | false | S4를 악화시키는 broad additions와 안전한 WASO proxy는 무엇인가? | S4 ablation, feature group list, baseline | safe/rejected S4 feature policy 기록 |
| `feature-dedup-715-raw-list` | high | feature-owner | false | exact `715` duplicate/high-correlation candidates는 무엇인가? | correlation matrix, duplicate list, post-pruning metrics | dedup policy와 target exception 기록 |
| `replay-validator-blind-spot-threshold` | high | validation-owner | false | `0.00005` public LB movement를 감지할 local replay threshold는 무엇인가? | submission table, local replay metrics, public deltas | validator blind-spot threshold 정의 |
| `v186-leaderboard-provenance` | high | submission-owner | false | v186 public LB `0.5922831771`를 검증할 수 있는가? | leaderboard export, submission CSV, timestamp, run mapping | verified 또는 tentative 고정 |
| `fold-safe-leakage-ablation` | P0 | modeling-lead | false | transductive statistics와 global imputer를 fold-safe하게 바꾸면 local OOF가 어떻게 변하는가? | fold-safe run, OOF metrics, leakage audit | supported local claim boundary 갱신 |

## Aliases and merge notes

`2026-06-12` question_queue의 `public-lb-lineage`는 `dacon-public-05917-submission-lineage`와 같은 backlog로 병합한다. 새 질문은 `window-pair-parquet-implementation`뿐이며, 이는 placeholder code를 feature evidence로 오해하지 않기 위한 closeable item이다.

## Review rule

질문을 닫는 packet은 raw metric, split, provenance, claim boundary를 함께 포함해야 한다. Notebook screenshot, Slack note, DOCX/PDF summary만으로는 close할 수 없다.

<!-- llm-synthesis:github-models-required-page-fill:2026-06-18:wiki-targets-sleep-lifelog-open-issues-md -->
## GitHub Models Fallback Synthesis | 2026-06-18

- packet_ids: `2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic`
- packet_summary: 2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic: Wave41 LGB/CB fold-safe synthesis smoke improved the prior LGB/CB reproduction local OOF diagnostic line from 0.6198365213240887 to 0.6195964535023479, but remains local OOF only and short of the 0.61 goal.
- claim_status: preserved_from_raw_packet
- evidence_boundary: local_oof, notebook_output, DACON_public, DACON_private, and organizer_official evidence must stay separate.
- review_note: This page was conservatively filled in GitHub Actions because the compact fallback model omitted a required wiki page.
- synthesis_report: `wiki/reports/2026-06-18-sleep-lifelog-packet-synthesis.md`

<!-- llm-synthesis:github-models-required-page-fill:2026-06-25:wiki-targets-sleep-lifelog-open-issues-md -->
## GitHub Models Fallback Synthesis | 2026-06-25

- packet_ids: `2026-06-25-wave43-claude-campaign-stack-local-oof-projection`
- packet_summary: 2026-06-25-wave43-claude-campaign-stack-local-oof-projection: Claude 별도 작업으로 수행된 wave43 캠페인 결과를 team LLM wiki에 올리기 위한 성능 packet입니다. 최종 stack-v2는 subject-mean baseline 0.62453 대비 calibrated local OOF macro log-loss 0.58972를 기록했고, projected public은 0.59272로 추정되었습니다. 실제 확인된 public score 0.60761은 Claude 진행 로그 기반 관측치이므로 leaderboard export가 추가되기 전까지는 별도 claim boundary를 유지해야 합니다.
- claim_status: preserved_from_raw_packet
- evidence_boundary: local_oof, notebook_output, DACON_public, DACON_private, and organizer_official evidence must stay separate.
- review_note: This page was conservatively filled in GitHub Actions because the compact fallback model omitted a required wiki page.
- synthesis_report: `wiki/reports/2026-06-25-sleep-lifelog-packet-synthesis.md`
