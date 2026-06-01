---
type: synthesis-report
title: Sleep Lifelog Dataset and Benchmark Synthesis
source_date: 2026-05-29
synthesis_date: 2026-06-01
claim_status: tentative
review_required: true
source_packets:
  - 2026-05-29-sleep-lifelog-2024
  - 2026-05-29-sleep-health-hackathon-v0
related_pages:
  - wiki/datasets/sleep-lifelog-2024.md
  - wiki/benchmarks/sleep-health-hackathon-v0.md
  - wiki/features/sleep-lifelog-feature-landscape.md
  - wiki/decisions/sleep-lifelog-evaluation-protocol.md
  - wiki/questions/sleep-lifelog-open-questions.md
raw_evidence:
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/manifest.yaml
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/benchmark.yaml
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/packet.md
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/manifest.yaml
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/dataset.yaml
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/packet.md
---

# Sleep Lifelog Dataset and Benchmark Synthesis

## Summary

This report records the LLM-assisted integration pass for two tentative packets:

- `2026-05-29-sleep-lifelog-2024`
- `2026-05-29-sleep-health-hackathon-v0`

The pass converts packet-level evidence into stable wiki memory: a dataset entity, a benchmark entity, a feature landscape, a provisional evaluation decision, and an open-question register. No raw evidence was changed and no performance claim was introduced.

## Inputs

| packet | type | raw root | claim boundary | claim status |
| --- | --- | --- | --- | --- |
| `2026-05-29-sleep-lifelog-2024` | dataset | `raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/` | `dataset_definition_not_metric_claim` | `tentative` |
| `2026-05-29-sleep-health-hackathon-v0` | benchmark | `raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/` | `benchmark_definition_not_metric_claim` | `tentative` |

## Integrated pages

- [Sleep Lifelog 2024](../datasets/sleep-lifelog-2024.md)
- [Sleep Health Hackathon Benchmark v0](../benchmarks/sleep-health-hackathon-v0.md)
- [Sleep Lifelog Feature Landscape](../features/sleep-lifelog-feature-landscape.md)
- [Sleep Lifelog Evaluation Protocol](../decisions/sleep-lifelog-evaluation-protocol.md)
- [Sleep Lifelog Open Questions](../questions/sleep-lifelog-open-questions.md)

## Claim register

All claims below retain their source status.

- tentative: sleep-health-hackathon-v0 evaluates seven sleep-health prediction targets (Q1, Q2, Q3, S1, S2, S3, S4) on sleep-lifelog-2024 under a locally locked GroupKFold-by-subject-id sprint-1 policy with 3 folds, and reports a grouped macro log-loss aggregated as a macro mean across targets.
- tentative: Allowed claim boundaries against this benchmark are local_oof_diagnostic_only, same_split_baseline_comparison, and public_lb_observation_only. Public leaderboard scores require a DACON submission and are reported separately from local OOF diagnostic scores.
- tentative: An unseen-subject generalization track (Track A) is the recommended main track; a same-subject temporal forecasting track (Track B) is recorded as a separate candidate and must not be conflated with Track A, especially for Q-family targets that are participant-relative averages.
- tentative: sleep-lifelog-2024 is a multimodal smartphone, smartwatch, sleep-sensor, and self-report dataset of about 700 days recorded in 2024 with seven prediction targets (Q1, Q2, Q3, S1, S2, S3, S4). The released training labels are in ch2026_metrics_train.csv and produce a 450-row modeling table grouped by subject_id.
- tentative: The local canonical evaluation split for sprint 1 is GroupKFold by subject_id with 3 folds on the released training labels. Some older docs framed only six targets; the released package takes precedence over those older notes.
- tentative: Q-family labels are participant-relative averages and therefore at very high leakage risk under same-subject splits; objective S-family labels reflect guideline compliance.

## Supersession and conflict notes

- Older six-target summaries are recorded by the packets as superseded by the released package and metric description that include seven targets, including `S4`.
- Track A and Track B are separate evaluation tracks and must not be combined in a single unqualified benchmark claim.
- DACON public leaderboard observations do not supersede local OOF diagnostics or private leaderboard outcomes.
- The current local split policy is not organizer-official unless a future raw source proves that status.

## Open questions created

The integration pass created [Sleep Lifelog Open Questions](../questions/sleep-lifelog-open-questions.md), covering organizer protocol availability, fold artifact versioning, schema gaps, aggregation recipes, six-versus-seven target provenance, family-specific reporting, DACON submission evidence, and Track B reporting.

## Reviewer checklist

- Confirm that the released package contains the seven label columns including `S4`.
- Confirm the 450-row modeling table construction and date-key join semantics.
- Confirm whether a durable fold file should be created for the local GroupKFold split.
- Confirm whether sleep-sensor and self-report schema gaps should block feature work.
- Verify that future result packets include raw metric evidence before any performance claim is added.
