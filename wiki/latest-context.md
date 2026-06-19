# Latest Context

[[index]] [[overview]] [[log]]

## Current Best

- Supported local OOF claim: [LGB CB Reproduction Local OOF Diagnostic](performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic.md)는 여전히 좁은 `local_oof_diagnostic_only` claim이다. Q2 targetwise reblend `0.1`이 Wave41 local OOF를 `0.6198684545582471`에서 `0.6198365213240887`로 미세 개선한 것만 supported다.
- External/public notes: DACON code share `13975` Public `0.5917`, v186 `0.5922831771`, v189 `0.5925397`, Section07 `0.5986218188`, app-context `0.6106185586` 등은 [DACON Leaderboard History](performance/dacon-leaderboard-history.md)에 있지만 verified leaderboard claim이 아니다.
- Reference route: [LGBM XGB Anchor Subject Hole Blend](models/lgbm-xgb-anchor-subject-hole-blend.md), [Subject Hole CV](preprocessing/subject-hole-cv.md), [Stability Filtered Feature Selection](features/stability-filtered-feature-selection.md), [DACON Public 0.5917 LGBM XGB Anchor Reference](performance/dacon-public-05917-lgbm-xgb-anchor-reference.md).

## Active Risks

- Split surfaces가 3-fold GroupKFold, 5-fold local OOF, Subject-hole CV, PDF OOF summary, DOCX public LB observation, notebook-output summary로 섞여 있다. [Canonical Split And Leakage Policy](preprocessing/canonical-split-and-leakage-policy.md)를 먼저 확인한다.
- DACON code share `0.5917`은 `2026-06-12` recheck 이후에도 submission id, leaderboard export, submission CSV lineage가 없다. Notebook Local OOF `0.514`는 team canonical local OOF가 아니다.
- V152 anchor OOF는 strict out-of-fold generation과 row identity proof가 없으면 high leakage-risk feature다.
- Window-pair section은 일부 placeholder code라 parquet-backed feature evidence 전에는 implemented feature로 쓰지 않는다.
- App context, stability filtering, v186 SHAP, v200-v209 sparse splice, Section07 weekly claims는 모두 `tentative`; 1875 pool은 historical source review다.
- 오래된 tentative claim은 [Stale Tentative Claims](claims/stale-tentative-claims.md)에서 추적한다. registry에 등록된 stale claim은 warning으로 관리하고, 등록되지 않은 stale claim은 PR/ingest/synthesis gate에서 error로 유지한다.
- SHAP importance, public score note, local OOF, DACON leaderboard, private leaderboard를 한 ranking surface로 합치면 안 된다.

## Next Actions

- [Sleep Lifelog Open Questions](targets/sleep-lifelog-open-issues.md)의 `dacon-public-05917-submission-lineage`, `v152-anchor-oof-reproduction`, `subject-hole-cv-vs-canonical-groupkfold`를 우선 추적한다.
- `stability-filter-selected-list`와 exact feature hash를 확보하기 전에는 `23177 -> 1682`를 feature policy로 쓰지 않는다.
- `window-pair-parquet-implementation`을 닫기 전에는 window-pair code를 reusable implementation으로 홍보하지 않는다.
- `v186-leaderboard-provenance`, `app-context-raw-submission-lineage`, `dacon-submission-provenance-boundary`도 계속 promotion blocker다.
- [Stale Tentative Claims](claims/stale-tentative-claims.md)의 각 row는 새 packet evidence가 들어오면 `supported`, `disputed`, `superseded` 중 하나로 닫는다.
- `replay-validator-blind-spot-threshold`를 정의하기 전에는 `0.00005` 수준 local/public delta로 live submission trigger를 만들지 않는다.

## Recent packet review links

- [dacon public 05917 lgbm xgb anchor graph first recheck](performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck.md)
- [DACON Public 0.5917 LGBM XGB Anchor Reference](performance/dacon-public-05917-lgbm-xgb-anchor-reference.md)
- [2026-06-12 Sleep Lifelog Packet Synthesis](reports/2026-06-12-sleep-lifelog-packet-synthesis.md)
- [dacon public 05917 lgbm xgb anchor subject hole blend](performance/2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend.md)
- [app context feature engineering 20260601](performance/2026-06-01-app-context-feature-engineering-20260601.md)

<!-- wiki-ingest:latest:start -->
### 27396372321-1 | 2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck

- link: [[performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck]]
- related: [[models/lgbm-xgb-anchor-subject-hole-blend]], [[preprocessing/subject-hole-cv]], [[features/stability-filtered-feature-selection]], [[reports/2026-06-12-sleep-lifelog-packet-synthesis]]
- publish_action: `bot_pr`
- risk_tier: `tier3-performance`
- review-required: true
- 핵심: graph-first recheck는 external Public `0.5917` observation을 재확인하지만 submission lineage가 없어 `tentative`를 유지한다.

### 27325835544-1 | 2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend

- link: [[performance/2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend]]
- related: [[models/lgbm-xgb-anchor-subject-hole-blend]], [[preprocessing/subject-hole-cv]], [[features/stability-filtered-feature-selection]], [[reports/2026-06-11-sleep-lifelog-packet-synthesis]]
- publish_action: `bot_pr`
- risk_tier: `tier3-performance`
- review-required: true
- 핵심: external Public `0.5917` observation을 tentative로 보존하고 verified DACON claim으로 승격하지 않는다.
<!-- wiki-ingest:latest:end -->
