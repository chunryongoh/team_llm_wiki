---
id: 2026-05-29-v200-v209-sparse-splice-review
type: experiment
packet_type: experiment
title: v200 v209 sparse splice review
date: 2026-05-29
owner: moon-hyungdo
claim_status: tentative
claim_boundary: PDF review and Slack summary of v200-v209 only; score trend is user-reported public LB observation without leaderboard export, submission ids, or private score.
dataset: sleep-lifelog-2024
benchmark: sleep-health-hackathon-v0
model: v200-v209-sparse-splice-public-consensus
summary: broad morphology reset은 실패했고 sparse splice guardrail이 필요하다는 review지만 score trend는 user-reported public LB observation으로만 보존한다.
review_required: true
raw_evidence:
- raw/users/moon-hyungdo/experiments/2026-05-29-v200-v209-sparse-splice-review/manifest.yaml
- raw/users/moon-hyungdo/experiments/2026-05-29-v200-v209-sparse-splice-review/evidence.yaml
- raw/users/moon-hyungdo/experiments/2026-05-29-v200-v209-sparse-splice-review/metrics.json
- raw/users/moon-hyungdo/experiments/2026-05-29-v200-v209-sparse-splice-review/packet.md
---

# v200 v209 sparse splice review

문형도 packet `2026-05-29-v200-v209-sparse-splice-review`는 DPSleep/SleepMore-inspired morphology, 5분 raw sequence, validator blind spot, Q2/Q3 residual edit, sparse splice guardrail을 정리한다. 이 page의 수치는 [DACON Leaderboard History](../submissions/dacon-leaderboard-history.md)에 `user_reported_public_score_only`로만 반영한다.

## Reported public LB observations

| version | score | interpretation |
|---|---:|---|
| `v189-anchor` | `0.5925397` | review 기준 anchor |
| `v200` | `0.608842` | broad reset failure |
| `v204` | `0.592557` | insufficient S2 calibration gain |
| `v208` | `0.592547` | near-best Q2/Q3 residual edit |
| `v209-q3-low` | `0.592543` | near-best Q3-only edit |
| `v209-q23-low` | `0.592551` | Q2 포함으로 악화 보고 |

## 통합 판단

현재 packet은 broad replacement를 피하고 v189 anchor에서 독립 물리 신호가 합의할 때만 sparse splice를 쓰라는 guardrail을 제안한다. 다만 leaderboard export, submission ids, local replay metric table, private LB evidence가 없으므로 decision은 conservative working rule로만 취급한다.

## 충돌과 supersession

이 review는 local proxy gain만 보고 anchor를 wholesale replace하는 계획을 supersede한다. 또한 Q2는 수정이 public score 하락으로 이어졌다는 반복 관찰 때문에 conservative target으로 유지한다.

## 다음 확인

`replay-validator-blind-spot-threshold`를 닫기 전에는 `0.00005` 수준의 local improvement를 live submission trigger로 쓰지 않는다.
