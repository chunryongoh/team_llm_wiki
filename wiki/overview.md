# Team LLM Wiki Overview

이 wiki는 team LLM experiments, sources, model notes, feature work, benchmark outcomes를 위한 유지보수형 synthesis layer다. 원천 evidence는 `raw/` 아래에 append-only로 남기고, `wiki/`는 reviewer가 읽을 수 있는 stable memory로 정리한다.

## 현재 구조

- stable source pages: packet별 raw provenance와 claim boundary를 보존한다.
- stable entity pages: dataset과 benchmark는 날짜별 packet mirror가 아니라 durable entity page로 관리한다. 예시는 [Sleep Lifelog 2024 Dataset](datasets/sleep-lifelog-2024.md), [Sleep Health Hackathon Benchmark v0](benchmarks/sleep-health-hackathon-v0.md)이다.
- compounding topic pages: 여러 packet이 같은 기능이나 결정에 영향을 주면 feature, decision, question, report page로 합성한다.
- automation feature pages: [Team LLM Wiki Actions Feature Landscape](features/team-llm-wiki-actions-feature-landscape.md)는 deterministic ingest, `workflow_run`, `gpt-5.5` synthesis, review-required bot PR의 연결을 추적한다.

## 최신 주의점

`2026-06-01-workflow-run-chain-smoke-packet`은 automation smoke evidence다. 이 packet의 claim은 `tentative`이며, sleep-health modeling claim이나 benchmark metric claim으로 승격하면 안 된다. 자세한 기준은 [Team LLM Wiki Actions Evaluation Protocol](decisions/team-llm-wiki-actions-evaluation-protocol.md)과 [Team LLM Wiki Actions Open Questions](questions/team-llm-wiki-actions-open-questions.md)를 참조한다.

## Review Policy Reminder

LLM-assisted synthesis는 `gpt-5.5` default model policy를 따르지만, output은 review-required로 남는다. performance, model, feature, supported claim은 raw evidence와 metric 또는 execution validation 없이 승격하지 않는다.

## Raw Evidence

raw_evidence:
- raw/users/chunryongoh/references/2026-06-01-workflow-run-chain-smoke-packet/manifest.yaml
- raw/users/chunryongoh/references/2026-06-01-workflow-run-chain-smoke-packet/notes.md
- raw/users/chunryongoh/references/2026-06-01-workflow-run-chain-smoke-packet/packet.md
