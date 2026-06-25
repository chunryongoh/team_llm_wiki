---
id: same-subject-hole-cv
type: validation-policy
page_role: policy
title: Same Subject Hole CV
status: active
date: 2026-06-25
dataset: sleep-lifelog-2024
claim_status: tentative
raw_evidence:
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/manifest.yaml
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/packet.md
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/performance.yaml
---

# Same Subject Hole CV

Same-subject-hole CV is the local validation surface used by the wave43 campaign. It is local-canonical for this packet, not organizer-official validation.

## Policy

- Group key: `subject_id`.
- Shape: five folds with temporal holes per subject.
- Goal: simulate missing target dates while preserving same-subject temporal structure.
- Fit scope: target encoders, priors, imputers, scaling, calibration, and stack layers must be fold-safe for local OOF claims.
- Claim boundary: local OOF and DACON public/private leaderboard evidence remain separate.

## Why It Matters

The wave43 result depends on subject-aware temporal information. A random row split would overstate performance, while a strict unseen-subject split may underrepresent the competition surface if the test includes familiar subjects. Same-subject-hole is therefore a pragmatic local proxy, but it must be superseded if organizer split semantics become known.

## Required Evidence For Promotion

To treat this as a team canonical split, future packets should attach fold assignment files, row counts per fold/target, leakage audit notes, and correlation against public/private leaderboard submissions.

## Related Pages

- [Canonical Split And Leakage Policy](canonical-split-and-leakage-policy.md)
- [Wave43 Claude Campaign Stack](../performance/wave43-claude-campaign-stack.md)
- [Wave43 Open Validation Gaps](../targets/wave43-open-validation-gaps.md)
