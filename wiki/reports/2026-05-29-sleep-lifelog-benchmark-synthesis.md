---
id: 2026-05-29-sleep-lifelog-benchmark-synthesis
type: report
title: Sleep Lifelog Benchmark Synthesis
source_packets:
  - 2026-05-29-sleep-lifelog-2024
  - 2026-05-29-sleep-health-hackathon-v0
claim_status: tentative
review_required: true
summary: "2026-05-29 sleep-lifelog dataset packet과 sleep-health benchmark packet을 안정 entity page, feature landscape, evaluation decision, open questions로 통합한 review-required synthesis report입니다."
raw_evidence:
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/manifest.yaml
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/benchmark.yaml
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/packet.md
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/manifest.yaml
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/dataset.yaml
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/packet.md
---

# Sleep Lifelog Benchmark Synthesis

이 report는 `2026-05-29-sleep-lifelog-2024` dataset packet과 `2026-05-29-sleep-health-hackathon-v0` benchmark packet을 Karpathy-style wiki integration pass로 합성한 결과입니다. Packet mirror가 아니라 stable memory graph를 만드는 것이 목적입니다.

## Sources Integrated

| packet id | packet_type | raw packet root | claim_status | claim_boundary |
| --- | --- | --- | --- | --- |
| `2026-05-29-sleep-lifelog-2024` | `dataset` | `raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/` | `tentative` | `dataset_definition_not_metric_claim` |
| `2026-05-29-sleep-health-hackathon-v0` | `benchmark` | `raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/` | `tentative` | `benchmark_definition_not_metric_claim` |

Deterministic ingest run recorded in existing pages: `26628582638-1`.

## Pages Created or Updated

Created:

- [Sleep Lifelog Feature Landscape](../features/sleep-lifelog-feature-landscape.md)
- [Sleep Lifelog Evaluation Protocol](../decisions/sleep-lifelog-evaluation-protocol.md)
- [Sleep Lifelog Open Questions](../questions/sleep-lifelog-open-questions.md)
- this report

Updated:

- [Sleep Lifelog 2024 Dataset](../datasets/sleep-lifelog-2024.md)
- [Sleep Health Hackathon Benchmark v0](../benchmarks/sleep-health-hackathon-v0.md)
- [Overview](../overview.md)
- [Latest Context](../latest-context.md)
- [Index](../index.md)
- [Log](../log.md)

## Synthesis Outcome

- Dataset page now anchors package files, modalities, seven targets, split policy, leakage risks, and provenance.
- Benchmark page now anchors target taxonomy, `grouped_macro_logloss`, Track A/Track B separation, public leaderboard boundary, and allowed claim boundaries.
- Feature landscape captures modality surfaces and aggregation/leakage checklist without claiming feature performance.
- Evaluation decision records `GroupKFold` by `subject_id` 3-fold OOF as provisional local sprint-1 policy.
- Open questions track official split absence, schema gaps, aggregation windows, DACON submission evidence, and target-family diagnostics.

## Claim Register

| status | preserved claim |
| --- | --- |
| `tentative` | `sleep-lifelog-2024` includes smartphone, smartwatch, sleep-sensor, self-report modalities and seven targets `Q1`, `Q2`, `Q3`, `S1`, `S2`, `S3`, `S4`. |
| `tentative` | Released labels are in `ch2026_metrics_train.csv` and produce a `450`-row modeling table grouped by `subject_id`. |
| `tentative` | sprint-1 local split is `GroupKFold` by `subject_id` with `3` folds. |
| `tentative` | Q-family labels are participant-relative and high risk under same-subject splits. |
| `tentative` | `sleep-health-hackathon-v0` uses `grouped_macro_logloss` as primary local metric. |
| `tentative` | Track A is recommended main track; Track B is candidate alternative and must not be conflated. |

No claim was promoted to `supported`.

## Conflicts and Supersession Notes

- older six-target summaries are superseded by released package evidence that includes `S4`.
- public leaderboard observations are not equivalent to local OOF diagnostics.
- Track B same-subject temporal forecasting is not a replacement for Track A unseen-subject generalization.
- local canonical split is not an organizer-official split unless future raw evidence says so.

## Reviewer Checklist

- Confirm that all claim statuses remain `tentative`.
- Confirm that no performance metric value or leaderboard rank was introduced without raw evidence.
- Confirm that downstream result packets will include `metrics_to_verify` and split artifacts before making metric claims.
- Confirm that Korean prose is understandable while preserving ids, metrics, file paths, and model names verbatim.
