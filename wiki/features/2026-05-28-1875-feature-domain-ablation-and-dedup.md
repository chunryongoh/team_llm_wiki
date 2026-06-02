---
id: 2026-05-28-1875-feature-domain-ablation-and-dedup
packet_type: feature
type: feature
title: 1875 feature domain ablation and dedup
date: '2026-05-28'
owner: ko-nayoung
status: submitted
task: source-ingest
dataset:
  name: sleep-lifelog-2024
  version: released-package
  hash: none
split:
  name: notebook-output-and-slack-summary-observation
  group_key: subject_id
  fold_file: null
model:
  family: catboost-v2-feature-domain-ablation
  weights_in_repo: false
claim_boundary: DOCX/PDF and Slack-reported feature analysis only; raw ablation metric
  files, feature correlation matrix, duplicate list, and submission lineage are not
  included.
claim_status: tentative
summary: "\uAD6C\uB098\uC601 bundle reports a 1,875-feature pipeline, 715 duplicate/high-correlation\
  \ cleanup candidates, Timing Entropy and target-specific features, noisy Light-W\
  \ ablation, Screen/Sleep core domains, and target-specific feature-set needs for\
  \ Q3."
raw_paths:
- features.yaml
- packet.md
- source/20260528-notebook-outputs.docx
- source/20260528-notebook-outputs.txt
- source/feature-info.pdf
- source/feature-info.txt
- wiki_plan.yaml
intended_wiki_targets:
- wiki/features/2026-05-28-1875-feature-domain-ablation-and-dedup.md
metrics_to_verify: []
claims:
- status: tentative
  text: "\uAD6C\uB098\uC601 bundle reports a 1,875-feature pipeline, 715 duplicate/high-correlation\
    \ cleanup candidates, Timing Entropy and target-specific features, noisy Light-W\
    \ ablation, Screen/Sleep core domains, and target-specific feature-set needs for\
    \ Q3."
publish_action: bot_pr
risk_tier: tier2-interpretation
---

# 1875 feature domain ablation and dedup

- packet: `2026-05-28-1875-feature-domain-ablation-and-dedup`
- generated_by_run: `26806097236-1`
- publish_action: `bot_pr`
- risk_tier: `tier2-interpretation`
- compiled_packet: [automation/.cache/compiled/2026-05-28-1875-feature-domain-ablation-and-dedup.json](../../automation/.cache/compiled/2026-05-28-1875-feature-domain-ablation-and-dedup.json)
- owner: `ko-nayoung`
- status: `submitted`
- task: `source-ingest`
- dataset: `sleep-lifelog-2024` (`released-package`)
- split: `notebook-output-and-slack-summary-observation`
- model: `catboost-v2-feature-domain-ablation`
- claim_boundary: DOCX/PDF and Slack-reported feature analysis only; raw ablation metric files, feature correlation matrix, duplicate list, and submission lineage are not included.
- claim_status: `tentative`
- date: `2026-05-28`
- raw_evidence:
  - `features.yaml`
  - `packet.md`
  - `source/20260528-notebook-outputs.docx`
  - `source/20260528-notebook-outputs.txt`
  - `source/feature-info.pdf`
  - `source/feature-info.txt`
  - `wiki_plan.yaml`
- review-required: true

## Summary

구나영 bundle reports a 1,875-feature pipeline, 715 duplicate/high-correlation cleanup candidates, Timing Entropy and target-specific features, noisy Light-W ablation, Screen/Sleep core domains, and target-specific feature-set needs for Q3.

## Packet Synthesis

구나영 feature bundle은 센서 일별 집계, Timing Entropy, cross-sensor/target-specific features를 거쳐 최종 X_train 450 x 1875 feature를 구성한 흐름을 기록한다. Slack summary는 전체 feature 중 715개가 중복/고상관 정리 대상이며 Light-W 301개가 가장 큰 noise, Screen/Sleep domain이 핵심, V2 CatBoost에서 avg -0.0063 개선이 관찰됐다고 보고한다. Q3는 BLE/WiFi 제거 시 악화되어 target-specific feature-set 전략이 필요하다.

## Wiki Integration Hints

### stable_entities

- feature:feature-deduplication-and-correlation-policy
- feature:light-screen-sleep-domain-landscape
- decision:noisy-domain-removal-policy
- target:q3-feature-set-policy
- claim:v2-catboost-domain-ablation-observation

### affected_pages

- wiki/features/feature-deduplication-and-correlation-policy.md
- wiki/features/light-screen-sleep-domain-landscape.md
- wiki/decisions/noisy-domain-removal-policy.md
- wiki/targets/q3-bottleneck.md
- wiki/claims/current-supported-claims.md

### claim_registry_updates

- tentative: 1,875-feature pipeline has 715 duplicate/high-correlation cleanup candidates and Light-W may be noisy, but raw pruning/ablation artifacts are missing.
- tentative: V2 CatBoost avg -0.0063 improvement is contributor-reported and needs raw metric evidence.

### supersedes_or_conflicts

- Supports the broader rule that adding more features is not automatically beneficial.
- Conflicts with broad BLE/WiFi removal for Q3 because Q3 reportedly worsened when BLE/WiFi were removed.

### open_questions

- {'close_condition': 'Feature dedup policy page records exact removal candidates and target-specific exceptions.', 'id': 'feature-dedup-715-raw-list', 'merge_blocker': False, 'needed_evidence': ['correlation matrix', 'duplicate feature list', 'post-pruning metric table'], 'owner_role': 'feature-owner', 'priority': 'high', 'question': 'Which exact 715 features are duplicate or high-correlation cleanup candidates?'}

### semantic_lint

- Do not convert feature count or SHAP importance into a supported performance claim.
- Keep Q3 target-specific exceptions separate from global domain-removal decisions.

## Claims

- tentative: 구나영 bundle reports a 1,875-feature pipeline, 715 duplicate/high-correlation cleanup candidates, Timing Entropy and target-specific features, noisy Light-W ablation, Screen/Sleep core domains, and target-specific feature-set needs for Q3.
