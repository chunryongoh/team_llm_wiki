---
id: team-llm-wiki-actions-evaluation-protocol
type: decision
title: Team LLM Wiki Actions Evaluation Protocol
status: proposed-for-review
date: '2026-06-01'
summary: `team-llm-wiki-actions` smoke packet은 performance benchmark가 아니라 automation chain evidence로 평가하며, `workflow_run` claim 승격에는 upstream and downstream run linkage가 필요하다.
related_features:
- wiki/features/team-llm-wiki-actions-feature-landscape.md
related_questions:
- wiki/questions/team-llm-wiki-actions-open-questions.md
related_sources:
- wiki/sources/2026-06-01-workflow-run-chain-smoke-packet.md
raw_evidence:
- raw/users/chunryongoh/references/2026-06-01-workflow-run-chain-smoke-packet/manifest.yaml
- raw/users/chunryongoh/references/2026-06-01-workflow-run-chain-smoke-packet/notes.md
- raw/users/chunryongoh/references/2026-06-01-workflow-run-chain-smoke-packet/packet.md
---

# Team LLM Wiki Actions Evaluation Protocol

## Decision

`team-llm-wiki-actions` smoke packet은 dataset 또는 benchmark 성능 평가가 아니라 automation chain 평가로 다룬다. 특히 `workflow_run` trigger 검증은 GitHub Actions run linkage, synthesis run evidence, review-required bot PR evidence가 있어야 `supported`로 재검토할 수 있다.

현재 [Workflow Run Chain Smoke Packet](../sources/2026-06-01-workflow-run-chain-smoke-packet.md)의 claim은 raw manifest에서 `tentative`로 제출되었고, 이번 synthesis는 이를 승격하지 않는다.

## Acceptance Criteria for Supported Automation Claim

1. raw packet manifest가 packet id, owner, task, claim_boundary, claim_status를 포함한다.
2. `wiki-main-ingest` run id와 deterministic output path가 기록된다.
3. `wiki-main-ingest` 완료 event가 `wiki-llm-synthesis` run을 발생시켰다는 `workflow_run` linkage가 run log 또는 event payload로 확인된다.
4. `wiki-llm-synthesis` run이 policy에 따라 `gpt-5.5`를 사용했고 review-required bot PR을 생성했다는 evidence가 있다.
5. reviewer가 해당 packet이 metric, split, model ranking claim을 포함하지 않는다고 확인한다.

## Current Evidence Table

| Evidence item | Status | Notes |
| --- | --- | --- |
| raw manifest | present | `raw/users/chunryongoh/references/2026-06-01-workflow-run-chain-smoke-packet/manifest.yaml` |
| deterministic source page | present | generated_by_run `26739337778-1` |
| metrics to verify | not applicable | `metrics_to_verify: []` |
| downstream `wiki-llm-synthesis` run URL | missing | open question `Q-TAWA-001` |
| `gpt-5.5` bot PR URL | missing | open question `Q-TAWA-002` |
| sleep-health modeling evidence | out of scope | notes.md explicitly says this is not such evidence |

## Claim Status Rule

- raw `claim_status: tentative`는 explicit raw metric, split, 또는 automation execution evidence 없이 변경하지 않는다.
- performance claim은 이 protocol에서 다루지 않는다. 관련 stable pages는 [Sleep Lifelog 2024 Dataset](../datasets/sleep-lifelog-2024.md)과 [Sleep Health Hackathon Benchmark v0](../benchmarks/sleep-health-hackathon-v0.md)를 참조하되, 이번 smoke packet과 분리한다.

## Related Pages

- [Team LLM Wiki Actions Feature Landscape](../features/team-llm-wiki-actions-feature-landscape.md)
- [Team LLM Wiki Actions Open Questions](../questions/team-llm-wiki-actions-open-questions.md)
- [2026-06-01 Team LLM Wiki Actions Packet Synthesis](../reports/2026-06-01-team-llm-wiki-actions-packet-synthesis.md)
