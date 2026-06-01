# Latest Context

[[index]] [[overview]] [[log]]

이 페이지는 다음 agent session의 bounded entrypoint입니다. 전체 wiki dump가 아니라 현재 sleep-lifelog integration에서 바로 읽어야 할 링크만 유지합니다.

## 2026-06-01 | sleep-lifelog benchmark integration pass

- review-required: true
- synthesis model policy: `gpt-5.5`
- deterministic ingest run referenced: `26628582638-1`
- source packets: `2026-05-29-sleep-lifelog-2024`, `2026-05-29-sleep-health-hackathon-v0`
- claim_status preserved: `tentative`
- metric promotion: none

읽기 순서:

1. [[datasets/sleep-lifelog-2024]]
2. [[benchmarks/sleep-health-hackathon-v0]]
3. [[decisions/sleep-lifelog-evaluation-protocol]]
4. [[features/sleep-lifelog-feature-landscape]]
5. [[questions/sleep-lifelog-open-questions]]
6. [[reports/2026-05-29-sleep-lifelog-benchmark-synthesis]]

핵심 주의점:

- `S4`가 포함된 seven-target released package framing이 현재 기준입니다.
- `GroupKFold` by `subject_id` 3 folds는 local sprint-1 canonical policy이며 organizer-official split claim이 아닙니다.
- Track A `unseen-subject-generalization`과 Track B `same-subject-temporal-forecasting`은 분리해야 합니다.
- DACON public leaderboard observation은 local OOF diagnostic claim을 승격하지 않습니다.

<!-- wiki-ingest:latest:start -->
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
