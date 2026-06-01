# Latest Context

[[index]] [[overview]] [[log]]

이 페이지는 agent session entrypoint다. 전체 wiki dump가 아니라 최근에 검토해야 할 context와 링크만 유지한다.

## 2026-06-01 세션 초점

- `2026-06-01-workflow-run-chain-smoke-packet`은 `wiki-main-ingest` 완료가 `workflow_run`으로 `wiki-llm-synthesis`를 trigger하는지 확인하려는 automation smoke packet이다.
- claim status는 `tentative`이며, downstream `wiki-llm-synthesis` run URL과 review-required bot PR evidence가 아직 open question이다.
- 관련 page: [[sources/2026-06-01-workflow-run-chain-smoke-packet]], [[features/team-llm-wiki-actions-feature-landscape]], [[decisions/team-llm-wiki-actions-evaluation-protocol]], [[questions/team-llm-wiki-actions-open-questions]], [[reports/2026-06-01-team-llm-wiki-actions-packet-synthesis]].
- sleep-health dataset 또는 benchmark metric claim을 검토하려면 별도 stable entity pages인 [[datasets/sleep-lifelog-2024]]와 [[benchmarks/sleep-health-hackathon-v0]]를 사용한다.

<!-- wiki-ingest:latest:start -->
### 26739337778-1 | 2026-06-01-workflow-run-chain-smoke-packet

- link: [[sources/2026-06-01-workflow-run-chain-smoke-packet]]
- publish_action: `direct_commit`
- risk_tier: `tier0-catalog`

### 26739124273-1 | 2026-06-01-full-chain-smoke-packet

- link: [[sources/2026-06-01-full-chain-smoke-packet]]
- publish_action: `direct_commit`
- risk_tier: `tier0-catalog`

### 26628582638-1 | 2026-05-29-sleep-health-hackathon-v0

- link: [[benchmarks/sleep-health-hackathon-v0]]
- publish_action: `bot_pr`
- risk_tier: `tier2-interpretation`
- review-required: true

### 26628582638-1 | 2026-05-29-sleep-lifelog-2024

- link: [[datasets/sleep-lifelog-2024]]
- publish_action: `bot_pr`
- risk_tier: `tier2-interpretation`
- review-required: true
<!-- wiki-ingest:latest:end -->
