---
id: dacon-leaderboard-history
type: submission-history
title: DACON Leaderboard History
status: active
date: 2026-06-02
summary: DACON public/private leaderboard score, submission id, file lineage, local run mapping을 관리한다.
raw_evidence:
- raw/users/hyeonseokrock/experiments/2026-06-01-lifelog-section07-working-notes/source/04_performance.md
- raw/users/hyeonseokrock/experiments/2026-06-01-lifelog-section07-working-notes/packet.md
---

# DACON Leaderboard History

이 페이지는 DACON submission evidence와 local OOF diagnostic을 분리한다. 현재 section07 score는 user-reported note일 뿐 verified leaderboard claim이 아니다.

## Evidence Classes

- `verified_public_lb`: DACON submission id, public score, submission file lineage가 있는 public leaderboard evidence
- `verified_private_lb`: private score 또는 final score evidence
- `user_reported_public_score_only`: source note에 적힌 score지만 leaderboard export와 submission id가 없는 evidence
- `local_oof_diagnostic_only`: local validation 또는 OOF evidence
- `notebook_output_observation_only`: notebook output summary에서 나온 observation

## Current Records

| candidate | score | evidence_class | source | status |
| --- | ---: | --- | --- | --- |
| `section9_labelwise_best_20260522_1239` | `0.5986218188` | `user_reported_public_score_only` | `source/04_performance.md` | tentative |
| `section07_candidate_baseline_seed_ensemble_20260529_1029` | `0.6003735255` | `user_reported_public_score_only` | `source/04_performance.md` | tentative |

## Required Promotion Evidence

Leaderboard claim을 verified로 승격하려면 다음 packet-local evidence가 필요하다.

- DACON submission id 또는 leaderboard export
- public/private score와 timestamp
- 제출 CSV lineage
- local run id 또는 notebook export mapping
- model family and feature policy mapping
- leakage or forbidden-input audit 결과

## Semantic Lint

- local OOF score와 DACON public score를 같은 metric surface로 비교하지 않는다.
- user-reported public score를 verified leaderboard score라고 쓰지 않는다.
- private leaderboard 또는 final score가 없으면 final ranking claim을 하지 않는다.
