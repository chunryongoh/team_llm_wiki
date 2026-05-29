---
id: 2026-05-29-sleep-lifelog-2024
packet_type: dataset
title: Sleep Lifelog 2024 Dataset Definition
date: "2026-05-29"
owner: chunryongoh
claim_boundary: dataset_definition_not_metric_claim
claim_status: tentative
route: wiki/datasets
---

# Sleep Lifelog 2024 Dataset Definition

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
