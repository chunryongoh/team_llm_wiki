---
id: sleep-lifelog-open-questions
type: open-questions
title: Sleep Lifelog Open Questions
status: active
last_updated: 2026-06-02
summary: sleep-lifelog backlog는 leaderboard provenance, feature ablation, split/leakage audit, target-specific Q3/S4 policy를 닫기 위한 실행 질문을 관리한다.
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

# Sleep Lifelog Open Questions

이 backlog는 [Feature Landscape](../features/sleep-lifelog-feature-landscape.md), [Evaluation Protocol](../decisions/sleep-lifelog-evaluation-protocol.md), [DACON Leaderboard History](../submissions/dacon-leaderboard-history.md), [Canonical Split And Leakage Policy](../preprocessing/canonical-split-and-leakage-policy.md)에 연결된다. 현재 synthesis merge blocker는 없지만, 아래 질문이 닫히기 전에는 tentative claim을 supported 또는 verified leaderboard claim으로 승격할 수 없다.

| id | priority | owner_role | merge_blocker | question | needed_evidence | close_condition |
|---|---|---|---|---|---|---|
| `app-context-raw-submission-lineage` | high | feature-performance-owner | false | app-context 세 stage score가 어떤 submission lineage에 대응하는가? | submission CSV, leaderboard export, local OOF metric, feature hash | app-context claim 승격 또는 permanent tentative 결정 |
| `q3-frequency-feature-design` | high | target-feature-owner | false | Q3 frequency/window feature를 어떤 validation surface에서 시험할 것인가? | formulas, same-split Q3 metrics, ablation table | Q3 후보 채택/폐기 기록 |
| `s4-broad-feature-degradation` | high | target-feature-owner | false | S4를 악화시키는 broad additions와 안전한 WASO proxy는 무엇인가? | S4 ablation, feature group list, baseline | safe/rejected S4 feature policy 기록 |
| `feature-dedup-715-raw-list` | high | feature-owner | false | exact `715` duplicate/high-correlation candidates는 무엇인가? | correlation matrix, duplicate list, post-pruning metrics | dedup policy와 target exception 기록 |
| `replay-validator-blind-spot-threshold` | high | validation-owner | false | `0.00005` public LB movement를 감지할 local replay threshold는 무엇인가? | v200-v209 submission table, local replay metrics, public deltas | validator blind-spot threshold 정의 |
| `v186-leaderboard-provenance` | high | submission-owner | false | v186 public LB `0.5922831771`를 검증할 수 있는가? | leaderboard export, submission CSV, timestamp, run mapping | verified 또는 tentative 고정 |
| `fold-safe-leakage-ablation` | P0 | modeling-lead | false | transductive statistics와 global imputer를 fold-safe하게 바꾸면 local OOF가 어떻게 변하는가? | fold-safe run, OOF metrics, leakage audit | supported local claim boundary 갱신 |
| `date-rolling-alignment-audit` | P0 | feature-owner | false | date/rolling feature가 target 이후 정보를 쓰지 않는가? | alignment audit, feature cutoff review | pass 또는 excluded decision |
| `dacon-submission-provenance-boundary` | high | benchmark-owner | false | user-reported public notes를 verified DACON evidence로 바꿀 provenance가 있는가? | submission ids, public/private scores, leaderboard export | DACON history row class 갱신 |

## Review rule

질문을 닫는 packet은 raw metric, split, provenance, claim boundary를 함께 포함해야 한다. notebook screenshot, Slack note, DOCX summary만으로는 close할 수 없다.
