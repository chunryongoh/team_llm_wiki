---
id: section07-followup-backlog
type: open-questions
title: Section07 Follow-Up Backlog
status: active
date: 2026-06-02
dataset: sleep-lifelog-2024
summary: Section07를 다음 사람이 보완하기 위해 필요한 closeable backlog.
raw_evidence:
- raw/users/hyeonseokrock/experiments/2026-06-01-lifelog-section07-working-notes/packet.md
- raw/users/hyeonseokrock/experiments/2026-06-01-lifelog-section07-notebook-overview/packet.md
---

# Section07 Follow-Up Backlog

| id | priority | owner_role | merge_blocker | question | needed_evidence | close_condition |
| --- | --- | --- | --- | --- | --- | --- |
| `section07-oq-001` | P0 | feature owner | false | allowed input audit가 실제로 forbidden submission/prediction input을 배제했는가? | `section07_allowed_input_audit.csv`, notebook rerun log | audit artifact가 packet-local raw evidence로 제출되고 policy page가 갱신된다. |
| `section07-oq-002` | P0 | feature owner | false | anchor 922와 Section11 additive feature hashes가 재현 가능한가? | feature policy CSV/hash artifact | [Section07 Feature Policy](../features/section07-feature-policy.md)의 evidence boundary가 갱신된다. |
| `section07-oq-003` | P1 | evaluation owner | false | public score notes를 verified DACON leaderboard record로 승격할 수 있는가? | submission id, leaderboard export, submission CSV lineage | [DACON Leaderboard History](../submissions/dacon-leaderboard-history.md)에 verified entry가 추가된다. |
| `section07-oq-004` | P1 | modeling owner | false | Q2/Q3/S4 bottleneck에 대해 current feature policy보다 나은 target-specific challenger가 있는가? | per-target metrics, same-split baseline, feature ablation | feature/model/performance packet이 같은 split surface에서 개선 또는 rejection을 기록한다. |
| `section07-oq-005` | P2 | modeling owner | false | seed ensemble/logit mean candidate가 rerun에서도 유지되는가? | training config, rerun metrics, seed logs | [Section07 Mix LGBM CatBoost](../models/section07-mix-lgbm-catboost.md)가 rerun evidence로 업데이트된다. |
