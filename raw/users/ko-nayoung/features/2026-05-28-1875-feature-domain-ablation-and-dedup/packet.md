---
claim_boundary: DOCX/PDF and Slack-reported feature analysis only; raw ablation metric files, feature correlation matrix, duplicate list, and submission lineage are not included.
claim_status: tentative
date: "2026-05-28"
mode: structured
owner: ko-nayoung
packet_type: feature
route: wiki/features
title: 1875 feature domain ablation and dedup
---

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
