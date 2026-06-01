---
type: feature-landscape
title: Sleep Lifelog Feature Landscape
dataset: sleep-lifelog-2024
claim_status: tentative
review_required: true
source_packets:
  - 2026-05-29-sleep-lifelog-2024
  - 2026-05-29-sleep-health-hackathon-v0
related_pages:
  - wiki/datasets/sleep-lifelog-2024.md
  - wiki/benchmarks/sleep-health-hackathon-v0.md
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

# Sleep Lifelog Feature Landscape

This page synthesizes the feature surface implied by the [Sleep Lifelog 2024 dataset](../datasets/sleep-lifelog-2024.md) and the [Sleep Health Hackathon v0 benchmark](../benchmarks/sleep-health-hackathon-v0.md). It is a planning and risk page, not a validated feature-importance or performance report.

## Provenance and boundary

- Source packets: `2026-05-29-sleep-lifelog-2024`, `2026-05-29-sleep-health-hackathon-v0`.
- Claim status inherited from packets: `tentative`.
- No feature set, model, metric value, or leaderboard outcome is claimed here.
- Any future result-bearing feature packet must carry raw evidence and split-aware metric verification.

## Available feature surfaces

| surface | source tables or references | current synthesis |
| --- | --- | --- |
| Smartphone state and context | `mACStatus`, `mActivity`, `mAmbience`, `mLight`, `mScreenStatus` | Candidate daily summaries for activity, ambience, light exposure, charging or screen state, pending schema-specific aggregation. |
| Smartphone proximity and mobility | `mBle`, `mGps`, `mWifi` | Candidate mobility and environment context features, with privacy and leakage review required before use. |
| Smartphone app use | `mUsagestats` | Candidate behavior and routine summaries; must avoid direct subject identity shortcuts. |
| Smartwatch physiology and movement | `wHr`, `wLight`, `wPedo` | Candidate heart-rate, light, and step summaries aligned to lifelog or sleep dates. |
| Sleep sensor | `sleep-sensor:placeholder` | Referenced but not schema-mapped in the packet; open question. |
| Self-report | `self-report:bedtime-questionnaire` | Potentially close to subjective Q-family labels; leakage and target-contamination review required. |
| Labels and grouping keys | `subject_id`, `sleep_date`, `lifelog_date`, `Q1` to `S4` | Labels and group keys are evaluation infrastructure, not ordinary model features unless a future packet explicitly justifies safe use. |

## Aggregation requirements

The dataset packet records nested payloads and minute-level streams as risks. Until a reviewed feature packet supersedes this page, feature work should assume:

- Raw streams need aggregation to the modeling row grain before tabular modeling.
- Aggregation should respect the canonical date keys used to form the 450-row modeling table.
- Aggregation code should not use validation-fold information or target values.
- `subject_id` must be used for grouping folds, not as a predictive feature in local Track A experiments.
- Feature manifests should state whether features are pre-sleep, same-day, overnight, or post-outcome relative to the target.

## Target-family implications

Q-family targets (`Q1`, `Q2`, `Q3`) are subjective and participant-relative. Candidate features for these targets are vulnerable to subject identity, reporting-style, and self-report leakage.

S-family targets (`S1`, `S2`, `S3`, `S4`) are objective guideline-compliance labels. They still require split-aware evaluation, but the leakage risk described in the packets is especially severe for Q-family labels under same-subject splits.

Future feature reports should therefore include per-family diagnostics in addition to the benchmark primary metric defined on [Sleep Health Hackathon v0](../benchmarks/sleep-health-hackathon-v0.md).

## Non-claims

- No feature family is claimed to improve `grouped_macro_logloss`.
- No modality is claimed to dominate another modality.
- No same-subject result is comparable to the Track A unseen-subject benchmark unless the packet explicitly runs both and preserves claim boundaries.

## Open feature work

See [Sleep Lifelog Open Questions](../questions/sleep-lifelog-open-questions.md) for unresolved schema, aggregation, and split-versioning questions.
