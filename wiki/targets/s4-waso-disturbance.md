---
id: s4-waso-disturbance
type: target-entity
page_role: leaf
target: S4
claim_status: tentative
status: active
title: S4 WASO Disturbance
raw_evidence:
- raw/users/hyeonseokrock/experiments/2026-05-29-labelwise-weekly-progress-target-bottlenecks/manifest.yaml
- raw/users/hyeonseokrock/experiments/2026-05-29-labelwise-weekly-progress-target-bottlenecks/packet.md
- raw/users/ko-nayoung/features/2026-05-28-1875-feature-domain-ablation-and-dedup/manifest.yaml
- raw/users/ko-nayoung/features/2026-05-28-1875-feature-domain-ablation-and-dedup/packet.md
---

# S4 WASO Disturbance

S4는 야간 각성/WASO disturbance 계열 병목으로 반복 언급된다. 현재 evidence는 broad feature addition이 S4를 악화시킬 수 있다는 관찰과, narrow disturbance proxy가 필요하다는 가설 수준이다.

## Current interpretation

- feature를 많이 추가할수록 S4가 악화된다는 보고가 있다.
- Light/screen/sleep disturbance 계열은 후보지만 broad addition이 아니라 target-specific guardrail이 필요하다.
- S4 claim은 causal feature proof가 아니라 ablation-backed target policy가 필요하다.

## Adoption rule

S4 feature를 채택하려면 same-split S4 target metric, removed/added feature group list, baseline comparator, leakage audit을 함께 기록한다.

## Open evidence

- safe WASO proxy feature list
- broad additions that degrade S4
- Light-W, screen, sleep domain ablation by target
- S4 confusion matrix or target-specific calibration evidence

## Related pages

- [Sleep Lifelog Feature Landscape](../features/sleep-lifelog-feature-landscape.md)
- [Sleep Lifelog Open Questions](sleep-lifelog-open-issues.md)
