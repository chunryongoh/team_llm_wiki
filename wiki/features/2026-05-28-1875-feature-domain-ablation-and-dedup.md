---
id: 2026-05-28-1875-feature-domain-ablation-and-dedup
type: feature
packet_type: feature
title: 1875 feature domain ablation and dedup
date: 2026-05-28
owner: ko-nayoung
claim_status: superseded
claim_boundary: Historical DOCX/PDF and Slack-reported feature analysis only; raw ablation metric files, feature correlation matrix, duplicate list, and submission lineage were not provided within the stale-claim review window. Re-open with a new raw evidence packet before using as an active feature policy or performance claim.
dataset: sleep-lifelog-2024
benchmark: sleep-health-hackathon-v0
model: catboost-v2-feature-domain-ablation
summary: 1,875-feature pipeline, 중복/고상관 정리, Light-W noise, Screen/Sleep core domain, Q3 target-specific exception을 보고하지만 raw ablation artifact가 없어 active claim이 아니라 historical source packet으로 유지한다.
review_required: true
raw_evidence:
- raw/users/ko-nayoung/features/2026-05-28-1875-feature-domain-ablation-and-dedup/manifest.yaml
- raw/users/ko-nayoung/features/2026-05-28-1875-feature-domain-ablation-and-dedup/features.yaml
- raw/users/ko-nayoung/features/2026-05-28-1875-feature-domain-ablation-and-dedup/packet.md
- raw/users/ko-nayoung/features/2026-05-28-1875-feature-domain-ablation-and-dedup/wiki_plan.yaml
---

# 1875 feature domain ablation and dedup

구나영 packet `2026-05-28-1875-feature-domain-ablation-and-dedup`는 sensor daily aggregation, Timing Entropy, cross-sensor composite, target-specific features를 거쳐 `X_train` `450 x 1875` feature pool을 구성한 흐름을 기록한다. 관련 합성은 [Sleep Lifelog Feature Landscape](sleep-lifelog-feature-landscape.md)와 [Canonical Split And Leakage Policy](../preprocessing/canonical-split-and-leakage-policy.md)에 반영한다.

## Evidence boundary

- status: `superseded`
- evidence surface: DOCX/PDF notebook-output and Slack summary
- missing: raw ablation metric files, feature correlation matrix, exact duplicate list, submission lineage
- stale-review result: 2026-06-12 기준 raw ablation/correlation evidence가 확보되지 않아 활성 tentative claim으로 유지하지 않는다. 재활성화하려면 새 raw evidence packet이 필요하다.

## 보고된 feature findings

- final feature count: `1875`
- intermediate target-specific expansion: `1959`
- duplicate/high-correlation cleanup candidates: `715`
- Timing Entropy new features: `121`
- reported noisy domain: `Light-W`, `301` features, delta `-0.0209`
- reported core domains: `Screen`, `Sleep`
- target exception: Q3는 BLE/WiFi 제거 시 악화된 것으로 보고되어 global removal policy와 충돌한다.

## 해석상 주의

Feature count는 feature value가 아니다. SHAP, ablation, leaderboard evidence를 분리해야 한다. 특히 V2 CatBoost avg `-0.0063` 개선 보고는 raw metric artifact 없이 supported performance claim이 될 수 없다. subject-relative statistics, high-correlation pruning, target-specific feature selection이 fold-scoped인지도 아직 증명되지 않았다.

## 다음 확인

`feature-dedup-715-raw-list`를 닫으려면 correlation matrix, exact removal list, post-pruning metric table이 필요하다. Q3 BLE/WiFi 예외는 target-specific feature-set policy로만 다뤄야 한다. 해당 증거가 새 packet으로 들어오기 전까지 이 페이지는 현재 정책/성능 claim이 아니라 과거 source review로만 사용한다.
