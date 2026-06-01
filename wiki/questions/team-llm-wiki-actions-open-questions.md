---
id: team-llm-wiki-actions-open-questions
type: open_questions
title: Team LLM Wiki Actions Open Questions
status: open
updated: '2026-06-01'
summary: `team-llm-wiki-actions` workflow_run smoke claim을 검증하기 위해 필요한 run linkage, `gpt-5.5` bot PR evidence, artifact schema, packet 간 역할 경계를 backlog로 추적한다.
related_feature: wiki/features/team-llm-wiki-actions-feature-landscape.md
related_decision: wiki/decisions/team-llm-wiki-actions-evaluation-protocol.md
raw_evidence:
- raw/users/chunryongoh/references/2026-06-01-workflow-run-chain-smoke-packet/manifest.yaml
- raw/users/chunryongoh/references/2026-06-01-workflow-run-chain-smoke-packet/notes.md
- raw/users/chunryongoh/references/2026-06-01-workflow-run-chain-smoke-packet/packet.md
---

# Team LLM Wiki Actions Open Questions

이 backlog는 [Workflow Run Chain Smoke Packet](../sources/2026-06-01-workflow-run-chain-smoke-packet.md)의 `tentative` claim을 안전하게 다루기 위한 open questions다. 각 항목은 close condition이 충족될 때만 claim status 재검토 대상으로 올린다.

| id | question | priority | owner_role | merge_blocker | needed_evidence | close_condition |
| --- | --- | --- | --- | --- | --- | --- |
| Q-TAWA-001 | 어떤 `wiki-main-ingest` run이 `wiki-llm-synthesis`를 `workflow_run`으로 실제 발생시켰는가? | high | github-actions-maintainer | `true` | GitHub Actions run URL, upstream `wiki-main-ingest` run id, downstream `wiki-llm-synthesis` run id, event payload 또는 run log excerpt. | 두 workflow run 사이의 `workflow_run` causality가 raw evidence 또는 reviewed report에 기록되고 source page claim 상태 변경 여부가 재검토된다. |
| Q-TAWA-002 | 해당 `wiki-llm-synthesis` run이 `gpt-5.5`를 사용하고 review-required bot PR을 열었는가? | high | llm-synthesis-maintainer | `true` | `wiki-llm-synthesis` log에서 model `gpt-5.5`, `reasoning.effort=high`, created PR URL, review-required label 또는 PR body evidence. | bot PR URL과 run artifact가 wiki report에 링크되고, `OPENAI_API_KEY` 누락 상태가 더 이상 현재 blocker가 아님이 확인된다. |
| Q-TAWA-003 | automation smoke packet을 `supported`로 올릴 때 필요한 최소 artifact schema는 무엇인가? | medium | wiki-ingest-maintainer | `false` | 필수 필드 목록, run id chain, artifact path, PR URL, failure handling을 담은 reviewed schema 또는 policy update. | evaluation protocol page가 reviewer-approved acceptance checklist를 갖고 이후 smoke packet들이 같은 schema로 제출된다. |
| Q-TAWA-004 | `2026-06-01-full-chain-smoke-packet`와 `2026-06-01-workflow-run-chain-smoke-packet`의 역할 경계와 supersession 관계를 어떻게 기록할 것인가? | medium | wiki-curator | `false` | 두 packet의 raw manifest, notes, generated runs, 그리고 어느 packet이 어떤 chain segment를 검증하는지에 대한 reviewer note. | feature landscape의 chain map에 두 packet이 별도 단계 evidence인지, 또는 일부 claim이 superseded 되었는지 명시된다. |

## Review Notes

- `Q-TAWA-001`과 `Q-TAWA-002`는 trigger verified claim을 지원 상태로 바꾸기 전 blocker다.
- 질문이 닫히기 전까지 [Team LLM Wiki Actions Evaluation Protocol](../decisions/team-llm-wiki-actions-evaluation-protocol.md)은 `proposed-for-review` 상태로 유지한다.
