---
id: stale-tentative-claims
type: claim-triage
page_role: registry
status: active
title: Stale Tentative Claims
last_reviewed: "2026-06-18"
review_required: true
---

# Stale Tentative Claims

이 registry는 `claim_status: tentative` 상태로 오래 남아 strict health gate를 막는 claim을 추적한다. 여기에 있는 항목은 자동 승격 대상이 아니다. 각 row는 새 raw evidence, 반박 evidence, 또는 명시적 폐기 판단이 들어올 때 원 page에서 `supported`, `disputed`, `superseded` 중 하나로 닫는다.

## Operating Rule

- PR, ingest bot PR, synthesis bot PR 검증은 registry에 없는 stale tentative claim을 error로 유지한다.
- 이 registry에 명시된 stale tentative claim은 strict health에서도 warning으로 내려간다.
- scheduled `wiki-health-check`는 stale tentative claim만 warning으로 낮춰 daily/weekly brief artifact를 계속 만든다.
- warning 처리는 해결이 아니라 attention routing이다.
- stale claim을 닫을 때는 근거 surface를 분리한다. local OOF, notebook output, DACON public LB, private LB, organizer official validation은 서로 다른 claim boundary다.

## Current Queue

| page | owner surface | close condition |
| --- | --- | --- |
| [Section07 Feature Policy](../features/section07-feature-policy.md) | Section07 feature policy | exact feature list/hash, ablation evidence, or supersession decision |
| [Section07 Mix LGBM CatBoost](../models/section07-mix-lgbm-catboost.md) | Section07 model note | train-valid strategy, targetwise metric evidence, and comparison boundary |
| [v186 SHAP Leaderboard Analysis](../performance/2026-05-29-v186-shap-leaderboard-analysis.md) | v186 public note and SHAP interpretation | submission lineage or explicit downgrade to historical interpretation |
| [App Context Feature Engineering](../performance/2026-06-01-app-context-feature-engineering-20260601.md) | app-context staged public note | raw submission lineage, feature hash, and per-target evidence |
| [DACON Leaderboard Claim Boundary](../performance/2026-06-01-dacon-leaderboard-claim-boundary.md) | leaderboard boundary policy | current official/public/private interpretation evidence |
| [Sleep Health Hackathon Evaluation Policy](../performance/sleep-health-hackathon-evaluation-policy.md) | evaluation policy | organizer-official split/protocol evidence or explicit local-only policy |
| [Sleep Lifelog 2024](../preprocessing/sleep-lifelog-2024.md) | dataset definition | raw schema, row lineage, and released package evidence |
| [Labelwise Weekly Progress Target Bottlenecks](../reports/2026-05-29-labelwise-weekly-progress-target-bottlenecks.md) | weekly target report | targetwise metric evidence or report archived as historical |
| [v200-v209 Sparse Splice Review](../reports/2026-05-29-v200-v209-sparse-splice-review.md) | sparse splice report | implementation-backed feature evidence or supersession |
| [LifeLog Section07 Notebook Overview](../reports/2026-06-01-lifelog-section07-notebook-overview.md) | notebook overview | notebook-output evidence promoted to stable entities or archived |
| [LifeLog Section07 Working Notes](../reports/2026-06-01-lifelog-section07-working-notes.md) | working notes | reusable decisions/questions extracted or archived |

## Review Protocol

1. Start from [Current Supported Claims](current-supported-claims.md), [DACON Leaderboard History](../performance/dacon-leaderboard-history.md), and [Canonical Split And Leakage Policy](../preprocessing/canonical-split-and-leakage-policy.md).
2. For each stale row, read the original page and its linked raw evidence before changing status.
3. If the claim is still useful but unsupported, keep it tentative and add a close condition to the relevant target or decision page.
4. If a newer packet contradicts it, mark the original page `superseded` and link the replacement.
5. If raw metric evidence supports it, move the durable statement into [Current Supported Claims](current-supported-claims.md) and keep the boundary narrow.
