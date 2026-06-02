---
id: 2026-06-02-team-packet-entity-coverage-audit
type: audit-report
title: Team Packet Entity Coverage Audit
date: 2026-06-02
status: review-required
summary: 팀원 Slack 요약과 첨부 bundle 대비 현재 wiki/raw coverage 및 새 세션 subagent 사용성을 점검한 결과.
raw_evidence:
- raw/users/hyeonseokrock/experiments/2026-06-01-lifelog-section07-working-notes/manifest.yaml
- raw/users/hyeonseokrock/experiments/2026-06-01-lifelog-section07-notebook-overview/manifest.yaml
- raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/manifest.yaml
---

# Team Packet Entity Coverage Audit

이 보고서는 팀원이 공유한 Slack 요약과 첨부 bundle이 현재 [Team LLM Wiki](../index.md)에 얼마나 반영되어 있는지, 그리고 새 세션 AI가 [Latest Context](../latest-context.md)와 [Index](../index.md)만 읽고 팀 작업을 중복 없이 이해할 수 있는지 점검한 기록이다.

## 결론

현재 wiki 구조는 entity-first 방향으로 작동한다. 새 세션 subagent는 `wiki/index.md`와 `wiki/latest-context.md`에서 시작해 dataset, benchmark, claim boundary, Section07 feature/model/submission/backlog를 중복 없이 재구성했다.

하지만 coverage는 아직 팀 전체 기준으로 부족하다. 현재 raw/wiki는 `chunryongoh`의 benchmark/dataset/local OOF diagnostic과 `hyeonseokrock`의 Section07 bundle 중심이다. 이번 Slack/첨부에 포함된 문형도, 구나영, 조혜원 bundle은 아직 packet-local raw evidence와 wiki entity로 반영되지 않았다.

## 현재 반영된 bundle

| owner | 반영 상태 | 현재 wiki entity | 주의 |
|---|---|---|---|
| `chunryongoh` | 반영됨 | dataset, benchmark, LGB/CB local OOF diagnostic, claim boundary | supported claim은 `local_oof_diagnostic_only`로 제한된다. |
| `hyeonseokrock` | 부분 반영됨 | [Section07 Feature Policy](../features/section07-feature-policy.md), [Section07 Mix LGBM CatBoost](../models/section07-mix-lgbm-catboost.md), [Section07 Follow-Up Backlog](../questions/section07-followup-backlog.md), [DACON Leaderboard History](../submissions/dacon-leaderboard-history.md) | 최신 packet skill 이전 산출물이어서 `wiki_plan.yaml`이 없고 preview `entity_coverage` warning이 난다. |

## 미반영 bundle

| contributor | 첨부/요약 핵심 | 현재 wiki 상태 | 필요한 packet |
|---|---|---|---|
| 문형도 | v186 LB `0.5922831771`, v186 SHAP, target-specific lineages, v200-v209 DPSleep/SleepMore 기반 sparse splice 시행착오 | `v186`, `0.592283`, `DPSleep`, `SleepMore`, `v200`, `v209`가 raw/wiki에 없음 | `v186-shap-leaderboard-analysis`, `v200-v209-sparse-splice-review` |
| 구나영 | `1,875` feature, `715` duplicate/high-correlation cleanup need, Light-W noise, Screen/Sleep core, V2 CatBoost avg `-0.0063` 개선, Q3 BLE/WiFi 제거 악화 | 해당 owner packet, `1875`, `715`, Light-W ablation, V2 CatBoost 개선 entity 없음 | `1875-feature-domain-ablation-and-dedup` |
| 조혜원 | LGBM+CatBoost `1,695` feature, app daily/evening feature `0.6219 -> 0.6183`, app context `0.6183 -> 0.6106`, Q3 병목 | `0.610618`, `appctx`, `20260526_172609` 등이 raw/wiki에 없음 | `app-context-feature-engineering-20260601` |

## 새 세션 subagent 테스트

테스트 방식:

- 새 subagent에 Slack 요약과 첨부를 주지 않았다.
- `wiki/index.md`와 `wiki/latest-context.md`에서만 시작하게 했다.
- 필요한 경우 linked wiki pages만 읽게 했고, raw는 provenance가 불명확할 때만 허용했다.

결과:

- 성공: dataset `sleep-lifelog-2024`, benchmark `sleep-health-hackathon-v0`, seven targets, LGB/CB supported boundary, Section07 feature/model/submission/backlog entity를 재구성했다.
- 성공: `LightGBM CatBoost` page와 `Section07 Mix LGBM CatBoost` page가 서로 다른 claim surface라는 점을 구분했다.
- 한계: 팀원 전체 결과는 알 수 없었다. wiki에 없는 v186, v200-v209, 1,875-feature ablation, app-context `0.6106` claim은 대화에 활용할 수 없었다.

## Packet Skill Compatibility Check

기존 `hyeonseokrock` Section07 packets를 최신 preview로 다시 확인하면 hard fail은 없지만 다음 warning이 나온다.

- `metric_claim_evidence`: experiment packet에 public score note와 metric-like claim이 있으나 `metrics_to_verify`가 없다.
- `entity_coverage`: 최신 skill이 요구하는 `wiki_plan.yaml`이 없다.

이는 현재 wiki가 나중에 entity page를 잘 만들었더라도, raw packet 자체가 최신 `team-llm-wiki-packet` skill의 `stable_entities`, `affected_pages`, `claim_registry_updates`, `semantic_lint` 계약을 만족한 것은 아니라는 뜻이다.

## Required Next Packet Wave

다음 packet wave는 단일 experiment page 생성을 피하고, 각 bundle이 다음 stable pages를 갱신하도록 `wiki_plan.yaml`을 포함해야 한다.

| packet | required affected pages |
|---|---|
| `v186-shap-leaderboard-analysis` | `wiki/submissions/dacon-leaderboard-history.md`, `wiki/claims/current-supported-claims.md`, `wiki/models/v186-target-specific-lgbm-catboost.md`, `wiki/features/v186-shap-feature-importance.md` |
| `v200-v209-sparse-splice-review` | `wiki/decisions/sparse-splice-guardrails.md`, `wiki/questions/replay-validator-blind-spot.md`, `wiki/features/sparse-splice-feature-policy.md` |
| `labelwise-window-q3-s4-bottleneck-update` | `wiki/targets/q3-bottleneck.md`, `wiki/targets/s4-waso-disturbance.md`, `wiki/features/temporal-window-frequency-candidates.md` |
| `1875-feature-domain-ablation-and-dedup` | `wiki/features/feature-deduplication-and-correlation-policy.md`, `wiki/features/light-screen-sleep-domain-landscape.md`, `wiki/decisions/noisy-domain-removal-policy.md` |
| `app-context-feature-engineering-20260601` | `wiki/features/app-context-features.md`, `wiki/performance/app-context-lgbcat-20260526.md`, `wiki/questions/q3-app-context-next-tests.md` |

## Audit Commands

- `find raw/users -maxdepth 5 -type f`
- `grep -RniE 'v186|v200|v209|0\.59228|DPSleep|SleepMore' wiki raw/users`
- `grep -RniE '1875|715|Light-W|0\.0063' wiki raw/users`
- `grep -RniE '0\.610618|appctx|20260526_172609' wiki raw/users`
- `PYTHONPATH=src python -m team_llm_wiki.cli preview-wiki-ingest --repo-root . --changed-path raw/users/hyeonseokrock/experiments/2026-06-01-lifelog-section07-working-notes/manifest.yaml --run-id audit-section07-working`
- `PYTHONPATH=src python -m team_llm_wiki.cli check-wiki-health --repo-root .`

## Decision

현재 wiki framework는 방향이 맞다. 다만 팀원 전체 자료를 기반으로 한 협업 보조자로 쓰기에는 아직 raw packet coverage가 부족하다. 다음 단계는 최신 `team-llm-wiki-packet` skill로 문형도, 구나영, 조혜원, 그리고 석현석 최신 Slack 요약 보강 packet을 생성해 entity-first ingest/synthesis chain을 다시 검증하는 것이다.
