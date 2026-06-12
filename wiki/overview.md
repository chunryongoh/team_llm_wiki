# Team LLM Wiki Overview

이 위키는 팀의 LLM-assisted 연구 기억, raw packet ingest 결과, 모델 실험, feature landscape, benchmark outcome을 사람이 리뷰할 수 있는 안정 synthesis layer로 유지한다. Raw evidence는 `raw/` 아래에 있고, `wiki/`는 review-aware automation과 LLM-assisted synthesis가 만든 팀 memory다.

## 현재 sleep-lifelog entrypoints

- Dataset: [Sleep Lifelog 2024 Dataset](datasets/sleep-lifelog-2024.md)
- Benchmark: [Sleep Health Hackathon Benchmark v0](benchmarks/sleep-health-hackathon-v0.md)
- Evaluation decision: [Sleep Lifelog Evaluation Protocol](decisions/sleep-lifelog-evaluation-protocol.md)
- Feature synthesis: [Sleep Lifelog Feature Landscape](features/sleep-lifelog-feature-landscape.md)
- Claim registry: [Current Supported Claims](claims/current-supported-claims.md)
- Submission history: [DACON Leaderboard History](submissions/dacon-leaderboard-history.md)
- Split/leakage policy: [Canonical Split And Leakage Policy](preprocessing/canonical-split-and-leakage-policy.md)
- Open questions: [Sleep Lifelog Open Questions](questions/sleep-lifelog-open-questions.md)
- Latest integration report: [2026-06-12 Sleep Lifelog Packet Synthesis](reports/2026-06-12-sleep-lifelog-packet-synthesis.md)

## Current best by evidence surface

현재 supported claim은 [LGB CB Reproduction Local OOF Diagnostic](performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic.md)의 `local_oof_diagnostic_only` claim 하나다. LGB/CB reproduction은 standalone 우위가 아니라 Q2 targetwise reblend `0.1`로 Wave41 local OOF `grouped_macro_log_loss`를 `0.6198684545582471`에서 `0.6198365213240887`로 미세 개선했다.

Reported public notes에는 DACON code share external `0.5917`, v186 `0.5922831771`, v189 `0.5925397`, Section07 `0.5986218188`, app-context `0.6106185586`가 있다. 그러나 모두 submission id, leaderboard export, private score, submission CSV lineage가 없어 verified DACON leaderboard claim이 아니다.

## 최근 통합된 packet themes

- external DACON 0.5917 reference: `2026-06-12` graph-first recheck가 [LGBM XGB Anchor Subject Hole Blend](models/lgbm-xgb-anchor-subject-hole-blend.md), [Subject Hole CV](preprocessing/subject-hole-cv.md), [Stability Filtered Feature Selection](features/stability-filtered-feature-selection.md)을 재확인했다. Claim status는 `tentative` 그대로다.
- app context: app-name과 presleep/night/early-morning window feature가 강한 hypothesis이지만 tentative다.
- 1875 feature pool: dedup, Light-W noise, Screen/Sleep core, Q3 BLE/WiFi exception은 raw artifact 없이 보고되어 historical source review로 남는다.
- v186 SHAP: target별 feature importance 해석은 유용하지만 ablation proof가 아니다.
- v200-v209: broad morphology reset은 negative evidence이고 sparse splice guardrail만 후보로 남았다.
- Section07 weekly: labelwise strategy, Q3/S4 bottleneck, temporal overlap negative observation을 보강한다.

## Operating principles

- `raw/`는 append-only source evidence다.
- `wiki/`는 packet mirror가 아니라 stable entity page와 topic page 중심의 synthesis다.
- local OOF, notebook-output, user-reported public score, DACON public/private leaderboard, organizer-official validation은 절대 한 evidence surface로 합치지 않는다.
- tentative claim은 raw metric, split, provenance 없이는 supported로 승격하지 않는다.
- LLM-assisted synthesis 결과는 review-required로 취급한다.

## Raw Evidence

raw_evidence:
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/manifest.yaml
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/dacon-codeshare-13975.md
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/dacon-public-05917-lgbm-xgb-anchor-subject-hole.ipynb
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/metrics.json
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/performance.yaml
- raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/wiki_plan.yaml
