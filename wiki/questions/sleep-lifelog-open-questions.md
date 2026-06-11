---
id: sleep-lifelog-open-questions
type: open-questions
page_role: open-questions
title: Sleep Lifelog Open Questions
status: active
last_updated: 2026-06-11
summary: leaderboard provenance, V152 anchor OOF, Subject-hole CV, feature ablation, split/leakage audit를 닫기 위한 실행 backlog다.
review_required: true
raw_evidence:
- raw/users/dacon-community/performance/2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend/manifest.yaml
- raw/users/dacon-community/performance/2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend/dacon-public-05917-lgbm-xgb-anchor-subject-hole.ipynb
- raw/users/dacon-community/performance/2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend/dacon-codeshare-13975.md
- raw/users/dacon-community/performance/2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend/metrics.json
- raw/users/dacon-community/performance/2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend/packet.md
- raw/users/dacon-community/performance/2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend/performance.yaml
- raw/users/dacon-community/performance/2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend/wiki_plan.yaml
---

# Sleep Lifelog Open Questions

이 backlog는 [Feature Landscape](../features/sleep-lifelog-feature-landscape.md), [Evaluation Protocol](../decisions/sleep-lifelog-evaluation-protocol.md), [DACON Leaderboard History](../submissions/dacon-leaderboard-history.md), [Canonical Split And Leakage Policy](../preprocessing/canonical-split-and-leakage-policy.md)에 연결된다. 아래 질문이 닫히기 전에는 tentative claim을 supported 또는 verified leaderboard claim으로 승격할 수 없다.

| id | priority | owner_role | merge_blocker | question | needed_evidence | close_condition |
|---|---|---|---|---|---|---|
| `dacon-public-05917-submission-lineage` | high | validation-owner | false | External `0.5917` public score를 DACON submission id, leaderboard export, exact submission CSV lineage에 연결할 수 있는가? | submission id, export/screenshot, CSV hash, timestamp | 관찰이 traceable하면 verified 후보로 바꾸고, 아니면 reference-only로 고정 |
| `v152-anchor-oof-reproduction` | high | model-owner | false | V152 anchor OOF probabilities를 팀 row identity와 fold-safe 절차로 재현할 수 있는가? | V152 recipe, OOF CSV, fold assignment, leakage audit | 재현 또는 non-portable 판단 기록 |
| `subject-hole-cv-vs-canonical-groupkfold` | medium | validation-owner | false | Subject-hole CV가 canonical GroupKFold보다 public/private correlation을 더 잘 설명하는가? | same-run dual split metrics, leaderboard mapping, leakage audit | adopt/reject/exploratory decision 기록 |
| `stability-filter-selected-list` | medium | feature-owner | false | `23177 -> 1682` stability filter의 exact selected list와 target별 delta는 무엇인가? | selected list, score formula, fold-safe proof, ablation | feature policy 승격 또는 reference-only 결정 |
| `app-context-raw-submission-lineage` | high | feature-performance-owner | false | app-context stage scores가 어떤 submission lineage에 대응하는가? | submission CSV, leaderboard export, local OOF, feature hash | app-context claim 승격 또는 permanent tentative 결정 |
| `q3-frequency-feature-design` | high | target-feature-owner | false | Q3 frequency/window feature를 어떤 validation surface에서 시험할 것인가? | formulas, same-split Q3 metrics, ablation table | Q3 후보 채택/폐기 기록 |
| `s4-broad-feature-degradation` | high | target-feature-owner | false | S4를 악화시키는 broad additions와 안전한 WASO proxy는 무엇인가? | S4 ablation, feature group list, baseline | safe/rejected S4 feature policy 기록 |
| `feature-dedup-715-raw-list` | high | feature-owner | false | exact `715` duplicate/high-correlation candidates는 무엇인가? | correlation matrix, duplicate list, post-pruning metrics | dedup policy와 target exception 기록 |
| `replay-validator-blind-spot-threshold` | high | validation-owner | false | `0.00005` public LB movement를 감지할 local replay threshold는 무엇인가? | v200-v209 submission table, local replay metrics, public deltas | validator blind-spot threshold 정의 |
| `v186-leaderboard-provenance` | high | submission-owner | false | v186 public LB `0.5922831771`를 검증할 수 있는가? | leaderboard export, submission CSV, timestamp, run mapping | verified 또는 tentative 고정 |
| `fold-safe-leakage-ablation` | P0 | modeling-lead | false | transductive statistics와 global imputer를 fold-safe하게 바꾸면 local OOF가 어떻게 변하는가? | fold-safe run, OOF metrics, leakage audit | supported local claim boundary 갱신 |
| `dacon-submission-provenance-boundary` | high | benchmark-owner | false | user-reported public notes를 verified DACON evidence로 바꿀 provenance가 있는가? | submission ids, public/private scores, leaderboard export | DACON history row class 갱신 |

## Review rule

질문을 닫는 packet은 raw metric, split, provenance, claim boundary를 함께 포함해야 한다. Notebook screenshot, Slack note, DOCX/PDF summary만으로는 close할 수 없다.
