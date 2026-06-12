---
id: 2026-06-01-sleep-lifelog-packet-synthesis
type: report
title: 2026-06-01 Sleep Lifelog Packet Synthesis
date: 2026-06-01
status: review-required
summary: >-
  LGB/CB reproduction local OOF diagnostic packet을 성능, feature, evaluation decision, open questions, overview, latest context, index, log에 통합하면서 claim boundary와 raw metric provenance를 보존했다.
model_policy: gpt-5.5 default high-accuracy synthesis policy
review_required: true
raw_evidence:
- raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/manifest.yaml
- raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/blend_weights.json
- raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/final_reblend_summary.json
- raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/leakage_audit.json
- raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/metrics.json
- raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/packet.md
- raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/performance.yaml
---

# 2026-06-01 Sleep Lifelog Packet Synthesis

이 report는 packet `2026-06-01-lgb-cb-reproduction-local-oof-diagnostic`를 위키 전반에 통합한 review-required synthesis 기록이다. raw packet mirror를 늘리는 대신, 안정 topic page와 decision page에 누적 지식을 연결했다.

## Inputs

- `AGENTS.md`
- `CLAUDE.md`
- `wiki/latest-context.md`
- `wiki/team/llm-synthesis-policy.md`
- raw packet root: `raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/`
- raw files: `manifest.yaml`, `packet.md`, `performance.yaml`, `metrics.json`, `final_reblend_summary.json`, `blend_weights.json`, `leakage_audit.json`
- current wiki pages: `wiki/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic.md`, `wiki/overview.md`, `wiki/latest-context.md`, `wiki/index.md`, `wiki/log.md`

## Integrated pages

- [LGB CB Reproduction Local OOF Diagnostic](../performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic.md): metric, split, targetwise blend, leakage audit, claim boundary를 통합했다.
- [Sleep Lifelog Feature Landscape](../features/sleep-lifelog-feature-landscape.md): transductive statistics, imputer scope, subject encoding, date/rolling alignment, `timing_entropy` risk를 feature topic memory로 만들었다.
- [Sleep Lifelog Evaluation Protocol](../decisions/sleep-lifelog-evaluation-protocol.md): local OOF, leaderboard, official validation claim을 분리하는 decision page를 만들었다.
- [Sleep Lifelog Open Questions](../targets/sleep-lifelog-open-issues.md): follow-up backlog를 actionable object로 정리했다.
- [Overview](../overview.md), [Latest Context](../latest-context.md), [Index](../index.md), [Log](../log.md): entrypoint와 navigation을 갱신했다.

## Claim register

| status | claim | evidence |
|---|---|---|
| supported | LGB/CB reproduction은 standalone 우위가 아니라 Q2에 `0.1` 가중치로 섞였을 때 Wave41 maintained line을 macro log-loss `0.6198365213240887`까지 아주 작게 개선했다. | `manifest.yaml`, `packet.md`, `metrics.json`, `final_reblend_summary.json`, `blend_weights.json` |
| supported | baseline Wave41 macro log-loss는 `0.6198684545582471`, targetwise reblend는 `0.6198365213240887`, delta는 `-3.19332341584e-05`이다. | `metrics.json` |
| supported | standalone LightGBM `0.6657586405095428`, CatBoost `0.6538557592728997`, fixed LGB/CB blend `0.6536839393073466`은 Wave41 line보다 약했다. | `metrics.json` |
| supported | leakage audit는 group overlap 통과와 동시에 transductive statistics, global imputer, subject target encoding, date/rolling alignment risk를 기록한다. | `leakage_audit.json` |
| out_of_scope | DACON public/private leaderboard 또는 organizer-official validation 성능은 이 packet의 claim boundary 밖이다. | `manifest.yaml`, `packet.md`, `performance.yaml` |

## Contradictions and supersession notes

- 넓은 claim인 LGB/CB overall superiority는 현재 packet으로 superseded 된다. 지원되는 claim은 Q2 source-diversity 보강이다.
- 모든 target 개선 claim은 지원되지 않는다. 최종 reblend는 6개 target에서 Wave41 `1.0`을 유지했다.
- local OOF diagnostic은 leaderboard claim이 아니다. 관련 boundary는 [DACON Leaderboard and Local OOF Claim Boundary](../performance/2026-06-01-dacon-leaderboard-claim-boundary.md)를 참조한다.
- leakage audit가 완전 통과했다는 표현은 부정확하다. `completed_with_known_risks`가 정확한 상태다.

## Open questions created

Open questions는 [Sleep Lifelog Open Questions](../targets/sleep-lifelog-open-issues.md)에 canonical backlog로 기록했다. 가장 중요한 항목은 `sleep-lifelog-oq-001` fold-safe ablation과 `sleep-lifelog-oq-004` date/rolling alignment audit이다.

## Reviewer checklist

- raw metric 숫자가 `metrics.json`와 일치하는가?
- `claim_status: supported`가 local OOF diagnostic claim에만 적용되는가?
- leaderboard 또는 official validation claim이 암묵적으로 추가되지 않았는가?
- feature risk가 성능 narrative에서 숨겨지지 않았는가?
- open questions가 현재 PR merge blocker가 아니라 future promotion gate로 이해되는가?

## Output boundary

이 synthesis는 allowed wiki pages만 작성한다. `raw/`, `automation/`, policy files는 변경하지 않는다.
