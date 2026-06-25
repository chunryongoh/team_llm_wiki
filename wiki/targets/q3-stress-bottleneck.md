---
id: q3-stress-bottleneck
type: target-entity
page_role: leaf
target: Q3
claim_status: tentative
status: active
title: Q3 Stress Bottleneck
raw_evidence:
- raw/users/hyeonseokrock/experiments/2026-05-29-labelwise-weekly-progress-target-bottlenecks/manifest.yaml
- raw/users/hyeonseokrock/experiments/2026-05-29-labelwise-weekly-progress-target-bottlenecks/packet.md
- raw/users/cho-hyewon/performance/2026-06-01-app-context-feature-engineering-20260601/manifest.yaml
- raw/users/cho-hyewon/performance/2026-06-01-app-context-feature-engineering-20260601/packet.md
---

# Q3 Stress Bottleneck

Q3는 취침 전 스트레스 계열 target으로 기록된 병목이다. 현재 evidence는 weekly progress와 app-context 보고서 기반이며, same-split target metric과 feature hash가 부족하므로 `tentative` 상태다.

## Current interpretation

- 기존 Q feature 추가는 직접적인 개선 신호가 약했다.
- Q3는 BLE/WiFi 제거 시 악화될 수 있어 global feature removal rule의 예외 후보다.
- app-context window, frequency-based feature, presleep/night context가 후보지만 Q3 전용 ablation이 필요하다.

## Adoption rule

Q3 개선 claim은 전체 average score가 아니라 same-split Q3 metric, feature group hash, baseline comparator를 함께 요구한다.

## Open evidence

- Q3 frequency/window feature formula
- same-split Q3 ablation table
- app-context feature stage와 submission/local run lineage
- BLE/WiFi removal exception 여부

## Related pages

- [Sleep Lifelog Feature Landscape](../features/sleep-lifelog-feature-landscape.md)
- [Sleep Lifelog Open Questions](sleep-lifelog-open-issues.md)
- [App Context Windows](../features/app-context-windows.md)

## Wave43 Update | 2026-06-25

Wave43 supersedes the strongest version of "Q-family has no extractable signal." The final stack records Q3 calibrated log-loss `0.650460985046031`, and sliding-window/intraday candidates helped Q2/Q3 enough to justify continued Q-family feature work. The bottleneck remains: Q3 is still one of the weakest targets and needs dedicated presleep stress, frequency, and routine-disruption features with same-split ablation.
