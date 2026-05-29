---
id: 2026-05-29-sleep-lifelog-2024
packet_type: dataset
type: dataset
title: Sleep Lifelog 2024 Dataset Definition
date: '2026-05-29'
owner: chunryongoh
status: submitted
task: dataset-definition
dataset:
  name: sleep-lifelog-2024
  version: v0
  hash: null
split:
  name: groupkfold-subject-3fold-oof
  group_key: subject_id
  fold_file: null
model:
  family: not-applicable
  weights_in_repo: false
claim_boundary: dataset_definition_not_metric_claim
claim_status: tentative
summary: First-class definition of the sleep-lifelog-2024 dataset used by the team.
  Lists released package contents, sensor modalities, the locally locked GroupKFold-by-subject
  split policy, and known leakage risks. No metric claim is made.
raw_paths:
- dataset.yaml
intended_wiki_targets:
- wiki/datasets/2026-05-29-sleep-lifelog-2024.md
metrics_to_verify: []
claims:
- status: tentative
  text: sleep-lifelog-2024 is a multimodal smartphone, smartwatch, sleep-sensor, and
    self-report dataset of about 700 days recorded in 2024 with seven prediction targets
    (Q1, Q2, Q3, S1, S2, S3, S4). The released training labels are in ch2026_metrics_train.csv
    and produce a 450-row modeling table grouped by subject_id.
- status: tentative
  text: The local canonical evaluation split for sprint 1 is GroupKFold by subject_id
    with 3 folds on the released training labels. Some older docs framed only six
    targets; the released package takes precedence over those older notes.
- status: tentative
  text: Q-family labels are participant-relative averages and therefore at very high
    leakage risk under same-subject splits; objective S-family labels reflect guideline
    compliance.
publish_action: bot_pr
risk_tier: tier2-interpretation
---

# Sleep Lifelog 2024 Dataset Definition

- packet: `2026-05-29-sleep-lifelog-2024`
- generated_by_run: `26628582638-1`
- publish_action: `bot_pr`
- risk_tier: `tier2-interpretation`
- compiled_packet: [automation/.cache/compiled/2026-05-29-sleep-lifelog-2024.json](../../automation/.cache/compiled/2026-05-29-sleep-lifelog-2024.json)
- owner: `chunryongoh`
- status: `submitted`
- task: `dataset-definition`
- dataset: `sleep-lifelog-2024` (`v0`)
- split: `groupkfold-subject-3fold-oof`
- model: `not-applicable`
- claim_boundary: dataset_definition_not_metric_claim
- claim_status: `tentative`
- date: `2026-05-29`
- raw_evidence:
  - `dataset.yaml`
- review-required: true

## Summary

First-class definition of the sleep-lifelog-2024 dataset used by the team. Lists released package contents, sensor modalities, the locally locked GroupKFold-by-subject split policy, and known leakage risks. No metric claim is made.

## Dataset Entity

- name: `sleep-lifelog-2024`
- version: `v0`

### Modalities

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

### Package Files

- `ch2025_data_items/`
- `ch2026_metrics_train.csv`
- `ch2026_submission_sample.csv`
- `ch2026_metrics_description.pdf`
- `data.zip`

### Split Policy

- policy: `groupkfold-subject`
- group_key: `subject_id`
- n_folds: `3`
- source: `local-canonical-sprint1`
- organizer_official_split_available: `false`
- modeling_table_rows: `450`
- notes: `Same-subject temporal split is recorded as a separate candidate track, not as the canonical sprint-1 split.`

### Leakage Risks

- `very_high_for_Q_under_same_subject_split_participant_relative_averages`
- `subjective_label_reporting_style_bias`
- `nested_modality_payloads_require_aggregation_before_tabular_models`
- `paper_vs_released_package_target_count_mismatch_six_vs_seven`
- `minute_level_streams_must_aggregate_before_most_models`

### Provenance

- source_type: `released-package-plus-team-summary`
- primary_raw_paths:
  - `raw/datasets/sleep-lifelog-2024/`
- supporting_sources:
  - `raw/references/chatgpt-share-2026-04-28-sleep-hackathon/transcript.md`
  - `raw/references/kick-off.md`
- notes: `ETRI source repo paths recorded for traceability; this packet itself ships only its own manifest, dataset.yaml, and packet.md.`

## Packet Synthesis

This packet locks the first-class definition of `sleep-lifelog-2024` in the team wiki so downstream feature, model, experiment, and performance packets can reference a stable entity instead of re-describing the dataset.

## Released Package Contents

Confirmed under `raw/datasets/sleep-lifelog-2024/` (ETRI source repo):

- `ch2025_data_items/` with 12 parquet files (one per modality table)
- `ch2026_metrics_train.csv` (label source for current training pipeline)
- `ch2026_submission_sample.csv` (submission schema reference)
- `ch2026_metrics_description.pdf` (organizer metric description)
- `data.zip` (original archive)

The released training labels produce a 450-row modeling table when joined to the canonical lifelog/sleep date keys.

## Modalities

Smartphone: `mACStatus`, `mActivity`, `mAmbience`, `mBle`, `mGps`, `mLight`, `mScreenStatus`, `mUsagestats`, `mWifi`.

Smartwatch: `wHr`, `wLight`, `wPedo`.

Sleep sensor and self-report modalities are referenced by the released package and team notes but are not exhaustively schema-mapped in this packet.

## Targets

Seven labels live alongside `subject_id`, `sleep_date`, and `lifelog_date` in `ch2026_metrics_train.csv`:

- `Q1` perceived sleep quality (subjective)
- `Q2` bedtime physical fatigue (subjective)
- `Q3` bedtime stress level (subjective)
- `S1` total sleep time guideline compliance (objective)
- `S2` sleep efficiency compliance (objective)
- `S3` sleep onset latency compliance (objective)
- `S4` wakefulness after sleep onset compliance (objective)

A separate `benchmark` packet defines the target taxonomy in more detail and the canonical metric policy that consumes them.

## Splits

The local canonical evaluation policy for sprint 1 is locked to:

- `GroupKFold` by `subject_id`
- 3 folds on the released training labels
- 450 rows in the canonical modeling table

Same-subject temporal forecasting is recorded as a candidate alternative track in the benchmark packet, not as the canonical split. No organizer-official split protocol has been published for the released package; if one appears it should supersede this entry rather than silently overwrite it.

## Known Leakage and Bias Risks

- Q-family labels are participant-relative averages and carry very high leakage risk under same-subject splits.
- Subjective labels may encode participant-specific reporting style.
- Several modality payloads are nested list or struct values and must be aggregated before tabular models consume them.
- Minute-level raw streams must be aggregated before most tabular models can use them.
- At least one older dataset paper summary uses a six-target framing; the released package and its metric description PDF take precedence and confirm seven targets including `S4`.

## Working Implications

- Treat Q-family and S-family targets as related but separate tasks; feature engineering should be tracked per family.
- For sprint-1 local comparisons, always use the locked canonical grouped-subject split rather than an ad hoc split.
- Do not claim organizer-official validation semantics beyond this local canonical policy unless an organizer-published split protocol appears.
- Future feature manifests and experiment packets must include `S4`.

## Claim Boundary

This packet only defines the dataset entity. No metric, baseline, or leaderboard claim is made. Performance, experiment, and model packets that reference this dataset must carry their own raw evidence and split-aware metric verification.

## Claims

- tentative: sleep-lifelog-2024 is a multimodal smartphone, smartwatch, sleep-sensor, and self-report dataset of about 700 days recorded in 2024 with seven prediction targets (Q1, Q2, Q3, S1, S2, S3, S4). The released training labels are in ch2026_metrics_train.csv and produce a 450-row modeling table grouped by subject_id.
- tentative: The local canonical evaluation split for sprint 1 is GroupKFold by subject_id with 3 folds on the released training labels. Some older docs framed only six targets; the released package takes precedence over those older notes.
- tentative: Q-family labels are participant-relative averages and therefore at very high leakage risk under same-subject splits; objective S-family labels reflect guideline compliance.
