---
id: team-llm-wiki-actions-feature-landscape
type: feature_landscape
title: Team LLM Wiki Actions Feature Landscape
status: review-required
owner: wiki-curation
updated: '2026-06-01'
summary: `team-llm-wiki-actions` 자동화 체인의 deterministic ingest, `workflow_run` trigger, `gpt-5.5` LLM synthesis, review-required bot PR 경계를 안정적인 feature map으로 정리한다.
sources:
- wiki/sources/2026-06-01-workflow-run-chain-smoke-packet.md
- wiki/sources/2026-06-01-full-chain-smoke-packet.md
related_decisions:
- wiki/decisions/team-llm-wiki-actions-evaluation-protocol.md
related_questions:
- wiki/questions/team-llm-wiki-actions-open-questions.md
related_reports:
- wiki/reports/2026-06-01-team-llm-wiki-actions-packet-synthesis.md
raw_evidence:
- raw/users/chunryongoh/references/2026-06-01-workflow-run-chain-smoke-packet/manifest.yaml
- raw/users/chunryongoh/references/2026-06-01-workflow-run-chain-smoke-packet/notes.md
- raw/users/chunryongoh/references/2026-06-01-workflow-run-chain-smoke-packet/packet.md
---

# Team LLM Wiki Actions Feature Landscape

이 페이지는 `team-llm-wiki-actions`를 날짜별 packet mirror가 아니라 repo 자동화 기능의 stable topic으로 정리한다. 현재 raw evidence는 automation smoke 성격이며, 모델 성능이나 sleep-health benchmark 결과를 주장하지 않는다.

## Feature Map

| Feature area | Intended behavior | Current evidence | Claim handling |
| --- | --- | --- | --- |
| packet merge to raw evidence | 사용자가 packet을 PR로 제출하고 merge하면 `raw/users/**` evidence가 append-only source가 된다. | packet skill implementation report와 2026-06-01 smoke packets가 관련된다. | 기능 맥락으로만 기록한다. |
| `wiki-main-ingest` deterministic output | raw packet merge 후 deterministic ingest가 source page와 ingest report를 만든다. | [Workflow Run Chain Smoke Packet](../sources/2026-06-01-workflow-run-chain-smoke-packet.md)의 `generated_by_run: 26739337778-1`이 source catalog 산출물을 보여준다. | catalog fact로만 사용한다. |
| `workflow_run` trigger | `wiki-main-ingest` 완료가 `wiki-llm-synthesis`를 자동으로 trigger해야 한다. | 새 packet의 manifest claim은 이 trigger 검증을 목표로 하지만 raw execution log는 제공되지 않았다. | `tentative` 유지. |
| `gpt-5.5` LLM synthesis | `wiki-llm-synthesis`는 policy상 `gpt-5.5`와 high reasoning을 사용해 review-required bot PR을 열어야 한다. | [LLM Synthesis Policy](../team/llm-synthesis-policy.md)와 prior implementation log에 근거한 expected behavior가 있다. 이번 packet만으로 live call 성공은 증명하지 않는다. | open question으로 추적. |
| stable wiki integration | source, feature, decision, question, report, overview, latest context, index, log가 함께 갱신되어야 한다. | 이 synthesis pass가 해당 allowed pages를 작성한다. | review-required output. |

## Scope Boundaries

- 이 feature는 GitHub Actions 및 wiki automation에 관한 것이다.
- [Sleep Lifelog 2024 Dataset](../datasets/sleep-lifelog-2024.md)과 [Sleep Health Hackathon Benchmark v0](../benchmarks/sleep-health-hackathon-v0.md)는 stable entity page 예시로 cross-link하지만, 이번 smoke packet은 해당 dataset 또는 benchmark의 metric evidence가 아니다.
- `metrics_to_verify: []`이므로 metric validation이나 split validation을 요구하는 performance claim은 없다.

## Dependencies and Review Points

1. `raw/` evidence는 append-only source로 유지한다.
2. deterministic ingest는 LLM API key 없이 재현 가능해야 한다.
3. LLM-assisted synthesis는 `gpt-5.5` default model policy를 따르되 review-required로 남겨야 한다.
4. `workflow_run` claim을 지원하려면 upstream run, downstream run, bot PR URL의 연결 evidence가 필요하다.

## Related Pages

- Source: [Workflow Run Chain Smoke Packet](../sources/2026-06-01-workflow-run-chain-smoke-packet.md)
- Prior source: [Full Chain Actions Smoke Packet](../sources/2026-06-01-full-chain-smoke-packet.md)
- Decision: [Team LLM Wiki Actions Evaluation Protocol](../decisions/team-llm-wiki-actions-evaluation-protocol.md)
- Questions: [Team LLM Wiki Actions Open Questions](../questions/team-llm-wiki-actions-open-questions.md)
- Report: [2026-06-01 Team LLM Wiki Actions Packet Synthesis](../reports/2026-06-01-team-llm-wiki-actions-packet-synthesis.md)
