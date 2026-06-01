---
type: decision
decision_id: sleep-lifelog-evaluation-protocol
title: Sleep Lifelog Evaluation Protocol
status: provisional
claim_status: tentative
review_required: true
source_packets:
  - 2026-05-29-sleep-lifelog-2024
  - 2026-05-29-sleep-health-hackathon-v0
related_pages:
  - wiki/datasets/sleep-lifelog-2024.md
  - wiki/benchmarks/sleep-health-hackathon-v0.md
  - wiki/features/sleep-lifelog-feature-landscape.md
  - wiki/questions/sleep-lifelog-open-questions.md
raw_evidence:
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/manifest.yaml
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/benchmark.yaml
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/packet.md
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/manifest.yaml
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/dataset.yaml
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/packet.md
---

# Sleep Lifelog Evaluation Protocol

## Decision status

Status: provisional, review-required.

The current local sprint-1 protocol is derived from tentative dataset and benchmark packets. It should be followed for local diagnostic comparisons until a reviewed packet or organizer-official protocol supersedes it.

## Decision

For local Track A evaluation on [Sleep Lifelog 2024](../datasets/sleep-lifelog-2024.md), use:

- Split: `GroupKFold` by `subject_id`.
- Folds: 3.
- Prediction table: out-of-fold predictions over the released training labels.
- Primary metric: `grouped_macro_logloss` as defined by [Sleep Health Hackathon v0](../benchmarks/sleep-health-hackathon-v0.md).
- Aggregation: compute log-loss per target on concatenated OOF predictions, then macro-average across `Q1`, `Q2`, `Q3`, `S1`, `S2`, `S3`, and `S4`.

## Rationale

The packet rationale is leakage control. Q-family labels are participant-relative and can encode reporting style. A same-subject split can therefore overstate generalization, especially for `Q1`, `Q2`, and `Q3`. Grouping by `subject_id` makes Track A an unseen-subject generalization diagnostic.

## Alternatives and boundaries

| option | status | boundary |
| --- | --- | --- |
| Track A: unseen-subject generalization | Recommended main local track | `local_oof_diagnostic_only` or `same_split_baseline_comparison` when comparing runs on identical folds |
| Track B: same-subject temporal forecasting | Candidate alternative | Must be reported separately and not conflated with Track A |
| DACON public leaderboard | Observation channel | `public_lb_observation_only`; requires specific submission evidence |
| DACON private leaderboard | Final external signal if available | Requires raw submission and score evidence in a result packet |

## Rules for future result packets

A result packet that targets this benchmark should include:

1. Dataset reference: `sleep-lifelog-2024`.
2. Benchmark reference: `sleep-health-hackathon-v0`.
3. Split name and group key.
4. Fold count and, when available, a durable fold assignment artifact.
5. Target list including `S4`.
6. Primary metric calculation evidence.
7. Claim boundary, chosen from the benchmark allowed boundaries.
8. Separate notes for Q-family and S-family behavior when making interpretation claims.

## Supersession triggers

This decision should be updated if any of the following appears in raw evidence:

- Organizer-official split or validation protocol.
- Reviewed fold assignment artifact for the canonical local split.
- Correction to target count or label columns in the released package.
- Result packet showing that a different local protocol has been explicitly approved.

## Non-decisions

- This page does not choose a model family.
- This page does not validate any feature set.
- This page does not claim any metric value.
- This page does not make Track B the main benchmark.
