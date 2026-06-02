---
id: canonical-split-and-leakage-policy
type: preprocessing-policy
title: Canonical Split And Leakage Policy
status: active
date: 2026-06-02
dataset: sleep-lifelog-2024
benchmark: sleep-health-hackathon-v0
summary: sleep-lifelog split surface와 leakage boundary를 claim 옆에 붙여 local OOF, public score note, notebook-output을 혼합하지 않게 한다.
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

# Canonical Split And Leakage Policy

이 page는 [Sleep Lifelog 2024 Dataset](../datasets/sleep-lifelog-2024.md) 성능 claim의 split, group key, fit scope, feature cutoff를 관리한다.

## Known split and evidence surfaces

| split surface | fold count | group key | evidence class | note |
|---|---:|---|---|---|
| `groupkfold-subject-3fold-oof` | 3 | `subject_id` | local canonical sprint definition | 초기 dataset/benchmark 기준 |
| `local-groupkfold-subject-5fold-oof` | 5 | `subject_id` | `local_oof_diagnostic_only` | LGB/CB supported diagnostic 기준 |
| `v186-report-oof-plus-public-lb-observation` | unknown | `subject_id` | PDF OOF + user-reported public score | submission lineage 없음 |
| `20260526-172609-lgbcat-timesplit-public-lb-observation` | unknown | `subject_id` | DOCX public LB observation | app-context stage report |
| `notebook-output-and-slack-summary-observation` | mixed | `subject_id` | notebook-output observation | 1,875 feature/dedup report |
| `public-lb-observation-and-local-proxy-review` | mixed | `subject_id` | public score note + proxy review | v200-v209 sparse splice |
| `section07-working-notes-and-weekly-progress-observation` | mixed | `subject_id` | working-note observation | labelwise target bottleneck |

서로 다른 surface는 같은 validation metric처럼 비교하지 않는다.

## Fit scope rules

- imputation, normalization, target encoding은 fold-safe claim을 하려면 train-fold-only fit이어야 한다.
- global train median imputer, train/test transductive statistics, subject target encoding은 leakage risk로 남긴다.
- high-correlation pruning과 subject-relative statistics가 full data fit이면 feature policy로 승격하지 않는다.
- feature hash와 allowed-input audit가 없으면 notebook-output feature claim은 tentative다.

## Current known risks

- LGB/CB reproduction: transductive statistics, global imputer, subject encoding, date/rolling alignment review risk
- app-context: feature list hash, submission lineage, same-split OOF 없음
- 1,875 pool: exact `715` list와 fold-scoped dedup 증거 없음
- v186: SHAP and OOF summary는 있으나 submission lineage와 ablation 없음
- v200-v209: replay validator raw metrics와 submission table 없음
- Section07: target-level metrics와 leaderboard provenance 부족

## Promotion gate

성능 claim을 `supported` 또는 `verified_public_lb`로 승격하려면 split surface, preprocessing fit scope, raw metric, leakage audit, submission lineage가 같은 provenance chain으로 연결되어야 한다.
