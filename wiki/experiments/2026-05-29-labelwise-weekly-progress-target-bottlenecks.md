---
id: 2026-05-29-labelwise-weekly-progress-target-bottlenecks
packet_type: experiment
type: experiment
title: labelwise weekly progress target bottlenecks
date: '2026-05-29'
owner: hyeonseokrock
status: submitted
task: source-ingest
dataset:
  name: sleep-lifelog-2024
  version: released-package
  hash: none
split:
  name: section07-working-notes-and-weekly-progress-observation
  group_key: subject_id
  fold_file: null
model:
  family: labelwise-lgbm-catboost-section07
  weights_in_repo: false
claim_boundary: Slack/weekly-progress and existing Section07 notes only; public scores
  are user-reported and target metrics lack raw metric files unless separately packetized.
claim_status: tentative
summary: "\uC11D\uD604\uC11D weekly update records that labelwise models reached the\
  \ strongest public score note 0.5986218188, temporal overlap/window augmentation\
  \ hurt more than helped, Q-feature additions had little direct impact, S1 can reach\
  \ about 0.48, Q3 is stuck around 0.62, S4 worsens with broad feature additions,\
  \ and frequency-based Q features remain a candidate."
raw_paths:
- evidence.yaml
- metrics.json
- packet.md
- source/weekly-progress-20260521-20260529-ko-short.md
- source/prompt4llmwiki.txt
- wiki_plan.yaml
intended_wiki_targets:
- wiki/experiments/2026-05-29-labelwise-weekly-progress-target-bottlenecks.md
metrics_to_verify:
- raw_path: metrics.json
  metric_key: section9_labelwise_best_public_lb
  reported_value: 0.5986218188
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: section07_candidate_public_lb
  reported_value: 0.6003735255
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: s1_reported_best_logloss_approx
  reported_value: 0.48
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: q3_reported_limit_logloss_approx
  reported_value: 0.62
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
claims:
- status: tentative
  text: "\uC11D\uD604\uC11D weekly update records that labelwise models reached the\
    \ strongest public score note 0.5986218188, temporal overlap/window augmentation\
    \ hurt more than helped, Q-feature additions had little direct impact, S1 can\
    \ reach about 0.48, Q3 is stuck around 0.62, S4 worsens with broad feature additions,\
    \ and frequency-based Q features remain a candidate."
publish_action: bot_pr
risk_tier: tier2-interpretation
---

# labelwise weekly progress target bottlenecks

- packet: `2026-05-29-labelwise-weekly-progress-target-bottlenecks`
- generated_by_run: `26806097236-1`
- publish_action: `bot_pr`
- risk_tier: `tier2-interpretation`
- compiled_packet: [automation/.cache/compiled/2026-05-29-labelwise-weekly-progress-target-bottlenecks.json](../../automation/.cache/compiled/2026-05-29-labelwise-weekly-progress-target-bottlenecks.json)
- owner: `hyeonseokrock`
- status: `submitted`
- task: `source-ingest`
- dataset: `sleep-lifelog-2024` (`released-package`)
- split: `section07-working-notes-and-weekly-progress-observation`
- model: `labelwise-lgbm-catboost-section07`
- claim_boundary: Slack/weekly-progress and existing Section07 notes only; public scores are user-reported and target metrics lack raw metric files unless separately packetized.
- claim_status: `tentative`
- date: `2026-05-29`
- raw_evidence:
  - `evidence.yaml`
  - `metrics.json`
  - `packet.md`
  - `source/weekly-progress-20260521-20260529-ko-short.md`
  - `source/prompt4llmwiki.txt`
  - `wiki_plan.yaml`
- review-required: true

## Summary

석현석 weekly update records that labelwise models reached the strongest public score note 0.5986218188, temporal overlap/window augmentation hurt more than helped, Q-feature additions had little direct impact, S1 can reach about 0.48, Q3 is stuck around 0.62, S4 worsens with broad feature additions, and frequency-based Q features remain a candidate.

## Packet Synthesis

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

## Metrics

raw-evidence-backed metric checks:
- `section9_labelwise_best_public_lb`: reported `0.5986218188`, raw_path `metrics.json`, tolerance `0.0`
- `section07_candidate_public_lb`: reported `0.6003735255`, raw_path `metrics.json`, tolerance `0.0`
- `s1_reported_best_logloss_approx`: reported `0.48`, raw_path `metrics.json`, tolerance `0.0`
- `q3_reported_limit_logloss_approx`: reported `0.62`, raw_path `metrics.json`, tolerance `0.0`

## Claims

- tentative: 석현석 weekly update records that labelwise models reached the strongest public score note 0.5986218188, temporal overlap/window augmentation hurt more than helped, Q-feature additions had little direct impact, S1 can reach about 0.48, Q3 is stuck around 0.62, S4 worsens with broad feature additions, and frequency-based Q features remain a candidate.
