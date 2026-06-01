---
id: sleep-lifelog-2024
type: dataset
title: Sleep Lifelog 2024
entity_name: sleep-lifelog-2024
version: v0
owner: chunryongoh
status: submitted
claim_boundary: dataset_definition_not_metric_claim
claim_status: tentative
review_required: true
publish_action: bot_pr
risk_tier: tier2-interpretation
latest_packet_id: 2026-05-29-sleep-lifelog-2024
latest_packet_date: '2026-05-29'
source_packets:
  - id: 2026-05-29-sleep-lifelog-2024
    packet_type: dataset
    title: Sleep Lifelog 2024 Dataset Definition
    date: '2026-05-29'
    owner: chunryongoh
    status: submitted
    claim_boundary: dataset_definition_not_metric_claim
    claim_status: tentative
    raw_paths:
      - raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/manifest.yaml
      - raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/dataset.yaml
      - raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/packet.md
primary_raw_paths:
  - raw/datasets/sleep-lifelog-2024/
supporting_sources:
  - raw/references/chatgpt-share-2026-04-28-sleep-hackathon/transcript.md
  - raw/references/kick-off.md
metrics_to_verify: []
claims:
  - status: tentative
    text: sleep-lifelog-2024 is a multimodal smartphone, smartwatch, sleep-sensor, and self-report dataset of about 700 days recorded in 2024 with seven prediction targets (Q1, Q2, Q3, S1, S2, S3, S4). The released training labels are in ch2026_metrics_train.csv and produce a 450-row modeling table grouped by subject_id.
  - status: tentative
    text: The local canonical evaluation split for sprint 1 is GroupKFold by subject_id with 3 folds on the released training labels. Some older docs framed only six targets; the released package takes precedence over those older notes.
  - status: tentative
    text: Q-family labels are participant-relative averages and therefore at very high leakage risk under same-subject splits; objective S-family labels reflect guideline compliance.
raw_evidence:
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/manifest.yaml
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/dataset.yaml
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/packet.md
---

# Sleep Lifelog 2024

This page is the stable team-memory page for the `sleep-lifelog-2024` dataset. It synthesizes the submitted dataset-definition packet and records how the team currently anchors downstream benchmark, feature, model, and experiment work.

**Current status:** review-required, `tentative`. This page defines the dataset entity and local split policy. It does **not** claim any metric, baseline score, model result, or leaderboard position.

## Entity Summary

`sleep-lifelog-2024` is a multimodal sleep-health dataset used by the team for the Sleep Health Hackathon work. The submitted packet describes smartphone, smartwatch, sleep-sensor, and self-report sources; seven released training targets; and a local sprint-1 canonical split based on GroupKFold by `subject_id`.

The paired benchmark page is [[benchmarks/sleep-health-hackathon-v0]], which defines target taxonomy and metric policy for evaluating models on this dataset.

## Provenance

| field | value |
| --- | --- |
| latest packet id | `2026-05-29-sleep-lifelog-2024` |
| packet type | `dataset` |
| owner | `chunryongoh` |
| packet date | `2026-05-29` |
| packet status | `submitted` |
| claim boundary | `dataset_definition_not_metric_claim` |
| claim status | `tentative` |

Raw packet evidence:

- `raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/manifest.yaml`
- `raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/dataset.yaml`
- `raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/packet.md`

Dataset/source provenance recorded by the packet:

- primary raw path: `raw/datasets/sleep-lifelog-2024/`
- supporting source: `raw/references/chatgpt-share-2026-04-28-sleep-hackathon/transcript.md`
- supporting source: `raw/references/kick-off.md`
- provenance note: ETRI source repo paths are recorded for traceability; the packet itself ships only its own manifest, `dataset.yaml`, and `packet.md`.

## Released Package Contents

The source packet records these released-package items:

- `ch2025_data_items/`
  - packet narrative records 12 parquet files, one per modality table
- `ch2026_metrics_train.csv`
  - label source for the current training pipeline
- `ch2026_submission_sample.csv`
  - submission schema reference
- `ch2026_metrics_description.pdf`
  - organizer metric description
- `data.zip`
  - original archive

The released training labels produce a 450-row modeling table when joined to the canonical lifelog/sleep date keys, according to the submitted packet. This remains a tentative dataset-definition claim.

## Modalities

The packet records these modalities:

| source family | recorded modalities |
| --- | --- |
| smartphone | `mACStatus`, `mActivity`, `mAmbience`, `mBle`, `mGps`, `mLight`, `mScreenStatus`, `mUsagestats`, `mWifi` |
| smartwatch | `wHr`, `wLight`, `wPedo` |
| sleep sensor | `sleep-sensor:placeholder` |
| self-report | `self-report:bedtime-questionnaire` |

Sleep sensor and self-report modalities are referenced by the released package and team notes, but the packet does not exhaustively schema-map them.

## Released Training Targets

Seven labels are recorded alongside `subject_id`, `sleep_date`, and `lifelog_date` in `ch2026_metrics_train.csv`:

| target | family | description |
| --- | --- | --- |
| `Q1` | subjective | perceived sleep quality |
| `Q2` | subjective | bedtime physical fatigue |
| `Q3` | subjective | bedtime stress level |
| `S1` | objective | total sleep time guideline compliance |
| `S2` | objective | sleep efficiency compliance |
| `S3` | objective | sleep onset latency compliance |
| `S4` | objective | wakefulness after sleep onset compliance |

The packet records that some older documentation framed only six targets, while the released package and metric description take precedence and include `S4`.

## Local Split Policy

The sprint-1 local canonical split policy is:

| field | value |
| --- | --- |
| policy | `groupkfold-subject` |
| group key | `subject_id` |
| folds | `3` |
| source | `local-canonical-sprint1` |
| modeling table rows | `450` |
| organizer-official split available | `false` |

Same-subject temporal forecasting is recorded as a separate candidate track in [[benchmarks/sleep-health-hackathon-v0]], not as the canonical sprint-1 dataset split. If an organizer-published split protocol appears later, it should supersede this local policy through an explicit reviewed update rather than a silent overwrite.

## Known Leakage and Bias Risks

The packet records these risks:

- `very_high_for_Q_under_same_subject_split_participant_relative_averages`
- `subjective_label_reporting_style_bias`
- `nested_modality_payloads_require_aggregation_before_tabular_models`
- `paper_vs_released_package_target_count_mismatch_six_vs_seven`
- `minute_level_streams_must_aggregate_before_most_models`

Practical interpretation:

- Q-family labels are participant-relative averages and are at very high leakage risk under same-subject splits.
- Subjective labels may encode participant-specific reporting style.
- Nested list or struct modality payloads need aggregation before tabular models consume them.
- Minute-level streams need aggregation for most tabular modeling workflows.
- Feature and experiment packets should track Q-family and S-family behavior separately.

## Working Implications

- Use [[benchmarks/sleep-health-hackathon-v0]] for the benchmark target taxonomy and metric policy.
- For sprint-1 local comparisons, use the locked GroupKFold-by-`subject_id` 3-fold policy rather than ad hoc splits.
- Do not claim organizer-official validation semantics from this local canonical policy.
- Future feature manifests, experiment packets, and model outputs should include `S4` unless a later reviewed packet changes the target set.
- Any result-bearing packet must include its own raw evidence and split-aware metric validation.

## Claim Boundary

This dataset page is a definition page only. It makes no metric, baseline, model, or leaderboard claim. Downstream pages must not use this dataset definition to imply performance support without separate raw metric evidence.

## Preserved Source Claims

All source claims remain `tentative`:

- **tentative:** sleep-lifelog-2024 is a multimodal smartphone, smartwatch, sleep-sensor, and self-report dataset of about 700 days recorded in 2024 with seven prediction targets (Q1, Q2, Q3, S1, S2, S3, S4). The released training labels are in ch2026_metrics_train.csv and produce a 450-row modeling table grouped by subject_id.
- **tentative:** The local canonical evaluation split for sprint 1 is GroupKFold by subject_id with 3 folds on the released training labels. Some older docs framed only six targets; the released package takes precedence over those older notes.
- **tentative:** Q-family labels are participant-relative averages and therefore at very high leakage risk under same-subject splits; objective S-family labels reflect guideline compliance.

## Reviewer Checklist

- Verify future feature or experiment packets include `S4` when they claim coverage of all released targets.
- Require explicit raw evidence before accepting any numeric dataset statistic beyond the submitted packet claims.
- Keep same-subject temporal forecasting results separate from the canonical GroupKFold-by-subject sprint-1 policy.
- Revisit this page if the organizer publishes an official split protocol or updated released-package schema.
