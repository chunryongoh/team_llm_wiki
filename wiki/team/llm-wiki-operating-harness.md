---
id: llm-wiki-operating-harness
type: operating-policy
page_role: policy
status: active
title: LLM Wiki Operating Harness
---

# LLM Wiki Operating Harness

이 문서는 Team LLM Wiki가 단순 packet 요약 저장소가 아니라, raw source를 읽고 지속적으로 정리되는 Karpathy-style LLM wiki로 작동하기 위한 실행 계약이다.

## Core invariant

- `raw/`는 불변 source of truth다.
- `wiki/`는 LLM이 유지하는 compounding memory다.
- `index.md`는 content catalog다.
- `log.md`는 chronological audit trail이다.
- `latest-context.md`는 새 세션 entrypoint다.
- durable entity는 stable page 하나를 가져야 한다.
- route policy source of truth는 `automation/contracts/wiki-route-contract.v1.yaml`다.

Automation must read the contract through `src/team_llm_wiki/wiki_ingest/route_contract.py`; packet skill must vendor the same contract under `references/wiki-route-contract.v1.yaml`.

Durable pages belong under canonical namespaces: `wiki/preprocessing`, `wiki/features`, `wiki/models`, `wiki/performance`, `wiki/claims`, `wiki/targets`, `wiki/decisions`, `wiki/reports`, and `wiki/team`. Deprecated namespaces such as `wiki/datasets`, `wiki/benchmarks`, `wiki/questions`, `wiki/submissions`, `wiki/experiments`, and `wiki/sources` are compatibility-only.

## Session start

새 Codex, Claude, 또는 기타 LLM agent 세션은 다음 순서로 읽는다.

1. `wiki/latest-context.md`
2. `wiki/index.md`
3. task-relevant registry/hub pages
4. task-relevant leaf pages
5. 필요한 경우에만 raw packet evidence

세션 context는 임시다. durable한 판단은 wiki에 crystallize-back해야 한다.

## Ingest

새 raw source가 들어오면 agent는 source를 요약하는 데서 멈추지 않는다.

1. claim boundary와 evidence surface를 식별한다.
2. stable entity 후보를 찾는다.
3. packet-specific review는 provenance로 남긴다.
4. hub/registry에는 짧은 routing row를 추가한다.
5. leaf page에는 reusable entity memory를 통합한다.
6. contradiction, supersession, open question을 기록한다.
7. `wiki/index.md`와 `wiki/log.md`를 갱신한다.

좋은 ingest는 하나의 source로 여러 page를 갱신할 수 있다.

## Query

질문에 답할 때는 wiki를 먼저 읽고, raw는 provenance 확인용으로만 내려간다. 답변 중 새로 생긴 비교, 판단, 반박, 질문, 재사용 가능한 feature/model/target 해석은 chat에만 남기지 말고 wiki에 기록한다.

## Crystallize-back

다음은 wiki로 남긴다.

- supported/tentative/disputed/superseded claim 변화
- target bottleneck 해석
- feature adoption/rejection policy
- model variant boundary
- split/leakage decision
- leaderboard provenance rule
- 재사용 가능한 비교표나 review
- close condition이 있는 open question

## Lint

정기적으로 다음을 점검한다.

- 같은 개념이 여러 page에 중복 설명되는가
- hub가 leaf 없이 너무 커졌는가
- `latest-context`가 packet history dump가 되었는가
- tentative claim이 오래 방치되었는가
- supported claim에 raw evidence가 있는가
- open question에 close condition이 있는가
- index와 log가 실제 page 상태를 반영하는가

Stale tentative claim은 [Stale Tentative Claims](../claims/stale-tentative-claims.md)에 올려서 닫힘 조건을 추적한다. Registry에 명시된 stale claim은 strict health에서도 warning으로 내려가지만, registry에 없는 stale claim은 PR/ingest/synthesis 검증에서 error로 유지한다. Scheduled `wiki-health-check`는 해당 code 전체를 warning으로 낮춰 daily/weekly brief artifact를 계속 생성한다. Warning mode와 registry tracking은 claim 해결이나 승격을 의미하지 않는다.

## Briefing

daily/weekly/current brief는 entrypoint와 action routing을 위해 존재한다. briefing은 report나 raw evidence를 대체하지 않는다. 중요한 변화는 해당 entity leaf, registry, decision, target/open-issue page에도 반영되어야 한다.
