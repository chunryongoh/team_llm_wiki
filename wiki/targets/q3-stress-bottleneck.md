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

<!-- llm-synthesis:github-models-required-page-fill:2026-06-25:wiki-targets-q3-stress-bottleneck-md -->
## GitHub Models Fallback Synthesis | 2026-06-25

- packet_ids: `2026-06-25-wave43-claude-campaign-stack-local-oof-projection`
- packet_summary: 2026-06-25-wave43-claude-campaign-stack-local-oof-projection: Claude 별도 작업으로 수행된 wave43 캠페인 결과를 team LLM wiki에 올리기 위한 성능 packet입니다. 최종 stack-v2는 subject-mean baseline 0.62453 대비 calibrated local OOF macro log-loss 0.58972를 기록했고, projected public은 0.59272로 추정되었습니다. 실제 확인된 public score 0.60761은 Claude 진행 로그 기반 관측치이므로 leaderboard export가 추가되기 전까지는 별도 claim boundary를 유지해야 합니다.
- claim_status: preserved_from_raw_packet
- evidence_boundary: local_oof, notebook_output, DACON_public, DACON_private, and organizer_official evidence must stay separate.
- review_note: This page was conservatively filled in GitHub Actions because the compact fallback model omitted a required wiki page.
- synthesis_report: `wiki/reports/2026-06-25-sleep-lifelog-packet-synthesis.md`
