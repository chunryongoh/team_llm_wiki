---
id: section07-feature-policy
type: feature-policy
title: Section07 Feature Policy
status: active-review-required
date: 2026-06-02
dataset: sleep-lifelog-2024
claim_status: tentative
summary: Section07 feature policy는 saved anchor 922 features와 labelwise Section11 additive top-k를 유지하고 global v5 change/frequency acceptance를 reject한 working-note 상태다.
raw_evidence:
- raw/users/hyeonseokrock/experiments/2026-06-01-lifelog-section07-working-notes/source/02_feature.md
- raw/users/hyeonseokrock/experiments/2026-06-01-lifelog-section07-working-notes/source/FEATURES.md
- raw/users/hyeonseokrock/experiments/2026-06-01-lifelog-section07-notebook-overview/source/notebook-output-summary.md
---

# Section07 Feature Policy

이 페이지는 Section07 feature policy를 실험 page와 분리해 관리한다.

## Current Documented Policy

- base: saved anchor feature list with `922` features
- additive source: Section11 labelwise additive top-k
- export feature source: `section11_base922_plus_labelwise_additive_policy`
- global v5 acceptance: `false`
- selected policy: current labelwise additive policy

## Labelwise Export Counts

| label | feature count | evidence class |
| --- | ---: | --- |
| Q1 | `942` | notebook-output observation |
| Q2 | `962` | notebook-output observation |
| Q3 | `962` | notebook-output observation |
| S1 | `922` | notebook-output observation |
| S2 | `932` | notebook-output observation |
| S3 | `1002` | notebook-output observation |
| S4 | `922` | notebook-output observation |

## Interpretation

Section07 does not support broad feature acceptance. The current notes support a narrower policy: keep the anchor list and add labelwise top-k features where accepted.

## Risks

- feature hashes are referenced but not packet-local evidence
- allowed input audit CSV is referenced but missing
- validation protocols are mixed and not normalized to one evidence class
- notebook was not rerun for the packet

## Follow-Up

- add `section07_allowed_input_audit.csv`
- add feature policy hash artifact
- create feature ablation packet for Q2/Q3/S4 bottlenecks
- keep v5 rejection decision linked to [Section07 Feature Policy Decision](../decisions/section07-feature-policy-decision.md)
