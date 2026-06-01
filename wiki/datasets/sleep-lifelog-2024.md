---
id: sleep-lifelog-2024
type: dataset
packet_type: dataset
title: Sleep Lifelog 2024 Dataset
version: v0
source_packets:
  - 2026-05-29-sleep-lifelog-2024
owner: chunryongoh
claim_status: tentative
claim_boundary: dataset_definition_not_metric_claim
review_required: true
canonical_split: groupkfold-subject-3fold-oof
summary: "sleep-lifelog-2024는 smartphone, smartwatch, sleep-sensor, self-report modalities와 Q1-Q3 및 S1-S4 seven targets를 포함하는 released package 기반 dataset 정의입니다. 현재 local canonical split은 `GroupKFold` by `subject_id` 3 folds입니다."
raw_evidence:
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/manifest.yaml
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/dataset.yaml
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/packet.md
---

# Sleep Lifelog 2024 Dataset

이 문서는 `sleep-lifelog-2024`의 안정 dataset entity 페이지입니다. Downstream feature, benchmark, experiment, report는 날짜별 packet 대신 이 페이지를 dataset anchor로 사용합니다.

관련 페이지: [Sleep Health Hackathon Benchmark v0](../benchmarks/sleep-health-hackathon-v0.md), [Sleep Lifelog Feature Landscape](../features/sleep-lifelog-feature-landscape.md), [Sleep Lifelog Evaluation Protocol](../decisions/sleep-lifelog-evaluation-protocol.md), [Sleep Lifelog Open Questions](../questions/sleep-lifelog-open-questions.md), [2026-05-29 synthesis report](../reports/2026-05-29-sleep-lifelog-benchmark-synthesis.md).

## Provenance

- packet id: `2026-05-29-sleep-lifelog-2024`
- packet_type: `dataset`
- owner: `chunryongoh`
- deterministic ingest run: `26628582638-1`
- raw packet root: `raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/`
- raw files: `manifest.yaml`, `dataset.yaml`, `packet.md`
- primary source path recorded by packet: `raw/datasets/sleep-lifelog-2024/`
- supporting sources recorded by packet: `raw/references/chatgpt-share-2026-04-28-sleep-hackathon/transcript.md`, `raw/references/kick-off.md`
- claim_boundary: `dataset_definition_not_metric_claim`
- claim_status: `tentative`
- review-required: true

## Released Package Contents

Packet evidence records these package files:

- `ch2025_data_items/`
- `ch2026_metrics_train.csv`
- `ch2026_submission_sample.csv`
- `ch2026_metrics_description.pdf`
- `data.zip`

`packet.md` states that `ch2025_data_items/` contains 12 parquet files, one per modality table. The released training labels produce a `450`-row modeling table when joined to canonical lifelog/sleep date keys. 이 row count는 dataset definition claim이며 performance evidence가 아닙니다.

## Modalities

Dataset packet의 modality list:

- `smartphone:mACStatus`
- `smartphone:mActivity`
- `smartphone:mAmbience`
- `smartphone:mBle`
- `smartphone:mGps`
- `smartphone:mLight`
- `smartphone:mScreenStatus`
- `smartphone:mUsagestats`
- `smartphone:mWifi`
- `smartwatch:wHr`
- `smartwatch:wLight`
- `smartwatch:wPedo`
- `sleep-sensor:placeholder`
- `self-report:bedtime-questionnaire`

Sleep sensor와 self-report modalities는 released package와 team notes에 언급되지만, 이 packet만으로 exhaustive schema mapping이 완료되지는 않았습니다. 이 gap은 [open questions](../questions/sleep-lifelog-open-questions.md)에 남아 있습니다.

## Keys and Labels

`ch2026_metrics_train.csv`에는 `subject_id`, `sleep_date`, `lifelog_date`와 seven labels가 함께 기록됩니다.

| family | labels | interpretation |
| --- | --- | --- |
| Q-family subjective | `Q1`, `Q2`, `Q3` | participant-relative perceived sleep quality, fatigue, stress입니다. |
| S-family objective | `S1`, `S2`, `S3`, `S4` | total sleep time, sleep efficiency, sleep onset latency, wakefulness after sleep onset guideline compliance입니다. |

Older six-target framing은 released package와 metric description PDF가 확인한 seven-target framing에 의해 superseded됩니다. Future feature manifests와 experiment packets는 `S4`를 누락하면 안 됩니다.

## Split Policy

현재 local canonical evaluation policy는 다음과 같습니다.

- policy: `groupkfold-subject`
- group_key: `subject_id`
- n_folds: `3`
- source: `local-canonical-sprint1`
- organizer_official_split_available: `false`
- modeling_table_rows: `450`
- split name used by manifests: `groupkfold-subject-3fold-oof`

Same-subject temporal split은 [benchmark](../benchmarks/sleep-health-hackathon-v0.md)의 Track B candidate로만 기록하며, canonical sprint-1 split으로 취급하지 않습니다.

## Leakage and Bias Risks

Dataset packet이 기록한 주요 risk는 다음과 같습니다.

- `very_high_for_Q_under_same_subject_split_participant_relative_averages`
- `subjective_label_reporting_style_bias`
- `nested_modality_payloads_require_aggregation_before_tabular_models`
- `paper_vs_released_package_target_count_mismatch_six_vs_seven`
- `minute_level_streams_must_aggregate_before_most_models`

특히 Q-family labels는 participant-relative averages라 same-subject split에서 reporting-style 또는 identity leakage가 발생할 위험이 큽니다. Feature work는 [feature landscape](../features/sleep-lifelog-feature-landscape.md)의 aggregation guidance와 [evaluation decision](../decisions/sleep-lifelog-evaluation-protocol.md)의 Track A 기준을 함께 따라야 합니다.

## Working Implications

- Dataset-level claim은 definition claim이며 metric claim이 아닙니다.
- Sprint-1 local comparison은 ad hoc split 대신 `GroupKFold` by `subject_id` 3-fold policy를 사용해야 합니다.
- Organizer-official validation semantics는 아직 raw evidence로 확인되지 않았으므로 주장하지 않습니다.
- Q-family와 S-family는 같은 benchmark 안에 있지만 diagnostic summary는 별도로 확인하는 것이 안전합니다.

## Preserved Claims

- tentative: `sleep-lifelog-2024`는 smartphone, smartwatch, sleep-sensor, self-report dataset이며 `Q1`, `Q2`, `Q3`, `S1`, `S2`, `S3`, `S4` seven targets를 포함하고 `ch2026_metrics_train.csv`가 released training labels입니다.
- tentative: sprint-1 local canonical split은 `GroupKFold` by `subject_id` 3 folds이고 older six-target docs보다 released package가 우선합니다.
- tentative: Q-family labels는 participant-relative averages라 same-subject splits에서 very high leakage risk가 있으며 S-family labels는 guideline compliance입니다.
