---
claim_boundary: Slack/weekly-progress and existing Section07 notes only; public scores are user-reported and target metrics lack raw metric files unless separately packetized.
claim_status: tentative
date: "2026-05-29"
mode: structured
owner: hyeonseokrock
packet_type: experiment
route: wiki/experiments
title: labelwise weekly progress target bottlenecks
---

석현석 weekly supplement는 기존 Section07 raw packet을 보강하는 target-bottleneck 기록이다. 핵심은 labelwise strategy가 가장 좋았고, temporal overlap으로 데이터를 늘리는 방식은 weighted learning/data loss 때문에 손해였으며, Q3와 S4가 다음 병목이라는 점이다. 이 packet은 기존 01_preprocessing/02_feature/03_model/04_performance docs와 weekly summary를 연결하지만, leaderboard provenance와 raw target metric files는 없다.

## Wiki Integration Hints

### stable_entities

- target:q3-bottleneck
- target:s4-waso-disturbance
- feature:temporal-window-frequency-candidates
- decision:temporal-overlap-window-policy
- submission:section9-labelwise-best-public-note

### affected_pages

- wiki/targets/q3-bottleneck.md
- wiki/targets/s4-waso-disturbance.md
- wiki/features/temporal-window-frequency-candidates.md
- wiki/decisions/section07-feature-policy-decision.md
- wiki/submissions/dacon-leaderboard-history.md
- wiki/questions/section07-followup-backlog.md

### claim_registry_updates

- tentative: labelwise strategy remains the strongest user-reported public score path at 0.5986218188, but no leaderboard provenance is present.
- tentative: temporal overlap/window augmentation hurt rather than helped in this weekly report; raw ablation evidence is needed.

### supersedes_or_conflicts

- Reinforces Section07 decision to avoid broad feature additions for S4.
- Conflicts with the assumption that more overlapped temporal samples automatically improve training.

### open_questions

- {'close_condition': 'Q3 bottleneck page records accepted/rejected frequency feature result.', 'id': 'q3-frequency-feature-design', 'merge_blocker': False, 'needed_evidence': ['feature formulas', 'same-split Q3 metrics', 'ablation table'], 'owner_role': 'target-feature-owner', 'priority': 'high', 'question': 'Which frequency-based feature family should be tested for Q3, and on which validation surface?'}
- {'close_condition': 'S4 target page records safe and rejected feature families.', 'id': 's4-broad-feature-degradation', 'merge_blocker': False, 'needed_evidence': ['S4 per-target ablation', 'feature group list', 'same-split baseline'], 'owner_role': 'target-feature-owner', 'priority': 'high', 'question': 'Which broad feature additions worsen S4, and which narrow WASO/disturbance proxies remain safe candidates?'}

### semantic_lint

- Do not treat temporal overlap as beneficial without raw ablation evidence.
- Keep S1/Q3/S4 target claims tentative until target-level metric files are added.
- Avoid merging public score notes into verified leaderboard claims.
