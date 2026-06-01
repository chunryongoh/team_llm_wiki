---
type: dataset
entity_id: sleep-lifelog-2024
title: Sleep Lifelog 2024
version: v0
claim_status: tentative
claim_boundary: dataset_definition_not_metric_claim
review_required: true
packet_ids:
  - 2026-05-29-sleep-lifelog-2024
source_paths:
  - raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/manifest.yaml
  - raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/dataset.yaml
  - raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/packet.md
related_pages:
  - wiki/benchmarks/sleep-health-hackathon-v0.md
  - wiki/features/sleep-lifelog-feature-landscape.md
  - wiki/decisions/sleep-lifelog-evaluation-protocol.md
  - wiki/questions/sleep-lifelog-open-questions.md
  - wiki/reports/2026-05-29-sleep-lifelog-benchmark-synthesis.md
raw_evidence:
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/manifest.yaml
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/dataset.yaml
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/packet.md
---

# Sleep Lifelog 2024

This is the stable dataset entity page for `sleep-lifelog-2024`. It anchors the [Sleep Health Hackathon v0 benchmark](../benchmarks/sleep-health-hackathon-v0.md), the [feature landscape](../features/sleep-lifelog-feature-landscape.md), and the [evaluation protocol decision](../decisions/sleep-lifelog-evaluation-protocol.md). It is not a performance or leaderboard page.

## Provenance

| field | value |
| --- | --- |
| packet id | `2026-05-29-sleep-lifelog-2024` |
| owner | `chunryongoh` |
| packet type | `dataset` |
| packet status | `submitted` |
| deterministic ingest run | `26628582638-1` |
| claim status | `tentative` |
| claim boundary | `dataset_definition_not_metric_claim` |
| raw sources | `manifest.yaml`, `dataset.yaml`, `packet.md` under `raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/` |
| referenced released package location | `raw/datasets/sleep-lifelog-2024/` |

## Dataset identity

- Name: `sleep-lifelog-2024`
- Version: `v0`
- Source type in packet: `released-package-plus-team-summary`
- Claimed scope: multimodal smartphone, smartwatch, sleep-sensor, and self-report data recorded in 2024.
- Claimed size: about 700 days, with a 450-row modeling table after joining released training labels to canonical lifelog and sleep date keys.

The size and scope statements are preserved as tentative packet claims.

## Released package contents

The packet records these package files:

- `ch2025_data_items/`
- `ch2026_metrics_train.csv`
- `ch2026_submission_sample.csv`
- `ch2026_metrics_description.pdf`
- `data.zip`

The packet narrative further says `ch2025_data_items/` contains 12 parquet files, one per modality table. That detail remains tentative until reviewed directly against the released package.

## Modalities

### Smartphone

- `mACStatus`
- `mActivity`
- `mAmbience`
- `mBle`
- `mGps`
- `mLight`
- `mScreenStatus`
- `mUsagestats`
- `mWifi`

### Smartwatch

- `wHr`
- `wLight`
- `wPedo`

### Other referenced sources

- `sleep-sensor:placeholder`
- `self-report:bedtime-questionnaire`

The packet does not exhaustively schema-map sleep-sensor or self-report payloads. This is tracked in [open questions](../questions/sleep-lifelog-open-questions.md).

## Labels and targets

The released training labels are in `ch2026_metrics_train.csv`. Seven target columns are recorded:

- `Q1`: perceived sleep quality, subjective.
- `Q2`: bedtime physical fatigue, subjective.
- `Q3`: bedtime stress level, subjective.
- `S1`: total sleep time guideline compliance, objective.
- `S2`: sleep efficiency compliance, objective.
- `S3`: sleep onset latency compliance, objective.
- `S4`: wakefulness after sleep onset compliance, objective.

The benchmark page owns the scoring taxonomy and metric policy for these targets.

## Local split policy

The packet locks the sprint-1 local canonical policy as:

- Split policy: `groupkfold-subject`.
- Group key: `subject_id`.
- Number of folds: 3.
- Source: `local-canonical-sprint1`.
- Modeling table rows: 450.
- Organizer-official split available: false.

Same-subject temporal forecasting is recorded as a separate candidate track in the benchmark page, not as this dataset page default.

## Known risks

- Q-family labels are participant-relative averages and have very high leakage risk under same-subject splits.
- Subjective labels may encode participant-specific reporting style.
- Several modality payloads are nested list or struct values and need aggregation before tabular models consume them.
- Minute-level streams need aggregation before most tabular models can use them.
- Older paper or summary material may describe six targets; the current packet says the released package and metric description take precedence and include seven targets.

## Working implications

- Use stable links to this page rather than re-describing the dataset in experiment packets.
- Include `S4` in future feature manifests and experiment outputs unless a reviewed source says otherwise.
- Report Q-family and S-family behavior separately when result packets arrive.
- Treat the local GroupKFold policy as local sprint-1 semantics, not organizer-official validation semantics.
- See the [feature landscape](../features/sleep-lifelog-feature-landscape.md) before adding feature packets.

## Claims preserved from source

- tentative: sleep-lifelog-2024 is a multimodal smartphone, smartwatch, sleep-sensor, and self-report dataset of about 700 days recorded in 2024 with seven prediction targets (Q1, Q2, Q3, S1, S2, S3, S4). The released training labels are in ch2026_metrics_train.csv and produce a 450-row modeling table grouped by subject_id.
- tentative: The local canonical evaluation split for sprint 1 is GroupKFold by subject_id with 3 folds on the released training labels. Some older docs framed only six targets; the released package takes precedence over those older notes.
- tentative: Q-family labels are participant-relative averages and therefore at very high leakage risk under same-subject splits; objective S-family labels reflect guideline compliance.
