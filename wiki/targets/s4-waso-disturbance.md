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

<!-- llm-synthesis:github-models-required-page-fill:2026-06-25:wiki-targets-s4-waso-disturbance-md -->
## GitHub Models Fallback Synthesis | 2026-06-25

- packet_ids: `2026-06-25-wave43-claude-campaign-stack-local-oof-projection`
- packet_summary: 2026-06-25-wave43-claude-campaign-stack-local-oof-projection: Claude 별도 작업으로 수행된 wave43 캠페인 결과를 team LLM wiki에 올리기 위한 성능 packet입니다. 최종 stack-v2는 subject-mean baseline 0.62453 대비 calibrated local OOF macro log-loss 0.58972를 기록했고, projected public은 0.59272로 추정되었습니다. 실제 확인된 public score 0.60761은 Claude 진행 로그 기반 관측치이므로 leaderboard export가 추가되기 전까지는 별도 claim boundary를 유지해야 합니다.
- claim_status: preserved_from_raw_packet
- evidence_boundary: local_oof, notebook_output, DACON_public, DACON_private, and organizer_official evidence must stay separate.
- review_note: This page was conservatively filled in GitHub Actions because the compact fallback model omitted a required wiki page.
- synthesis_report: `wiki/reports/2026-06-25-sleep-lifelog-packet-synthesis.md`
