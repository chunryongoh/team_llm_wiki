---
id: page-taxonomy
type: operating-policy
page_role: policy
status: active
title: Page Taxonomy
---

# Page Taxonomy

Team LLM Wiki는 하나의 거대한 markdown summary가 아니라 작은 stable page들의 graph로 성장해야 한다.

## Roles

| role | purpose | examples |
|---|---|---|
| `entrypoint` | 새 세션이 시작하는 routing page | `latest-context.md`, `index.md`, `overview.md` |
| `registry` | 같은 종류의 claim/entity를 catalog | `claims/current-supported-claims.md`, `submissions/dacon-leaderboard-history.md` |
| `hub` | topic 요약과 leaf route | `features/sleep-lifelog-feature-landscape.md` |
| `leaf` | durable entity 하나의 기억 | `targets/q3-stress-bottleneck.md` |
| `packet_review` | 특정 raw packet의 source-specific 정리 | `performance/2026-05-29-v186-shap-leaderboard-analysis.md` |
| `report` | 특정 wave나 milestone synthesis | `reports/2026-06-01-sleep-lifelog-packet-synthesis.md` |
| `policy` | 운영 규칙 | `team/wiki-ingest-policy.md` |

## Leaf promotion rule

아래 중 2개 이상이면 leaf page로 승격한다.

- 2개 이상 packet에서 반복 등장한다.
- 독립 claim status가 필요하다.
- target/model/feature/preprocessing/submission/decision으로 재사용된다.
- adoption guidance가 필요하다.
- conflict, supersession, rejected alternative가 있다.
- future agent가 직접 검색해 들어갈 필요가 있다.
- hub section이 계속 커지고 있다.

## Current required leaves

- `wiki/targets/q3-stress-bottleneck.md`
- `wiki/targets/s4-waso-disturbance.md`
- `wiki/features/app-context-windows.md`
- `wiki/models/v186-targetwise-lgbm-catboost.md`

Hub pages should link to these leaves instead of absorbing all detail.
