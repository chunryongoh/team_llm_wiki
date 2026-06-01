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
summary: First-class definition of the sleep-lifelog-2024 dataset used by the team. Lists released package contents, sensor modalities, the locally locked GroupKFold-by-subject split policy, and known leakage risks. No metric claim is made.
raw_paths:
- dataset.yaml
raw_evidence:
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/manifest.yaml
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/dataset.yaml
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/packet.md
intended_wiki_targets:
- wiki/datasets/2026-05-29-sleep-lifelog-2024.md
metrics_to_verify: []
claims:
- status: tentative
  text: sleep-lifelog-2024 is a multimodal smartphone, smartwatch, sleep-sensor, and self-report dataset of about 700 days recorded in 2024 with seven prediction targets (Q1, Q2, Q3, S1, S2, S3, S4). The released training labels are in ch2026_metrics_train.csv and produce a 450-row modeling table grouped by subject_id.
- status: tentative
  text: The local canonical evaluation split for sprint 1 is GroupKFold by subject_id with 3 folds on the released training labels. Some older docs framed only six targets; the released package takes precedence over those older notes.
- status: tentative
  text: Q-family labels are participant-relative averages and therefore at very high leakage risk under same-subject splits; objective S-family labels reflect guideline compliance.
publish_action: bot_pr
risk_tier: tier2-interpretation
---

# Sleep Lifelog 2024 Dataset

## Page Status

- stable_page: `wiki/datasets/sleep-lifelog-2024.md`
- packet_id: `2026-05-29-sleep-lifelog-2024`
- generated_by_run: `26628582638-1`
- publish_action: `bot_pr`
- risk_tier: `tier2-interpretation`
- review_required: `true`
- owner: `chunryongoh`
- source_status: `submitted`
- task: `dataset-definition`
- claim_boundary: `dataset_definition_not_metric_claim`
- claim_status: `tentative`
- metrics_to_verify: `[]`

## What This Page Is

`sleep-lifelog-2024` is the stable dataset entity for the team's sleep-health lifelog work. Downstream benchmark, feature, model, experiment, and performance packets should cite this page instead of re-describing the dataset or linking to a dated packet mirror.

This page is a dataset definition, not a performance-result page. It records the released package contents, modality families, seven-label target set, local sprint-1 split policy, and known leakage risks. It does not claim any model quality, baseline result, public leaderboard score, or organizer-official validation semantics.

## Stable Entity Fields

| field | value |
| --- | --- |
| dataset_name | `sleep-lifelog-2024` |
| version | `v0` |
| source_type | `released-package-plus-team-summary` |
| primary_label_file | `ch2026_metrics_train.csv` |
| canonical_modeling_rows | `450` |
| canonical_group_key | `subject_id` |
| canonical_local_split | `groupkfold-subject-3fold-oof` |
| n_folds | `3` |
| organizer_official_split_available | `false` |
| claim_status | `tentative` |

## Released Package Contents

The dataset packet records these released-package artifacts as the current source of record:

- `ch2025_data_items/`: modality tables; the packet narrative describes 12 parquet files.
- `ch2026_metrics_train.csv`: released training labels and the source of the current modeling table.
- `ch2026_submission_sample.csv`: submission schema reference.
- `ch2026_metrics_description.pdf`: organizer metric and label description reference.
- `data.zip`: original archive.

The manifest claim describes the dataset as approximately 700 days recorded in 2024. The structured dataset YAML records that the current joined modeling table has 450 rows grouped by `subject_id`. Both statements remain `tentative` because this page is preserving the packet status rather than independently revalidating the raw package.

## Modalities

| source | recorded modalities or status |
| --- | --- |
| smartphone | `mACStatus`, `mActivity`, `mAmbience`, `mBle`, `mGps`, `mLight`, `mScreenStatus`, `mUsagestats`, `mWifi` |
| smartwatch | `wHr`, `wLight`, `wPedo` |
| sleep sensor | recorded as `sleep-sensor:placeholder`; schema is not exhaustively mapped in this packet |
| self-report | `bedtime-questionnaire` |

Several modality payloads are nested or minute-level streams. The packet flags these as requiring aggregation before most tabular modeling workflows can consume them safely.

## Target Set

Seven labels live with `subject_id`, `sleep_date`, and `lifelog_date` in `ch2026_metrics_train.csv`:

| target | family | meaning |
| --- | --- | --- |
| `Q1` | subjective | perceived sleep quality, participant-relative |
| `Q2` | subjective | bedtime physical fatigue, participant-relative |
| `Q3` | subjective | bedtime stress level, participant-relative |
| `S1` | objective | total sleep time guideline compliance |
| `S2` | objective | sleep efficiency compliance |
| `S3` | objective | sleep onset latency compliance |
| `S4` | objective | wakefulness after sleep onset compliance |

The Q-family labels are participant-relative and therefore carry very high identity-leakage risk under same-subject validation. The S-family labels are framed as objective guideline-compliance targets. This dataset page does not validate any target-specific metric value.

## Split Policy

For sprint-1 local comparisons, the canonical local split is:

- split_policy: `groupkfold-subject`
- split_name: `groupkfold-subject-3fold-oof`
- group_key: `subject_id`
- n_folds: `3`
- source: `local-canonical-sprint1`
- modeling_table_rows: `450`
- organizer_official_split_available: `false`
- fold_file: `null`

Same-subject temporal forecasting is recorded as a candidate alternative track in the related benchmark, not as the canonical dataset split. Downstream result packets should name the split they used and should not compare same-subject temporal results against grouped-subject OOF results as if they were the same protocol.

## Known Leakage and Bias Risks

The packet records these risks:

- Q-family labels are participant-relative averages and have very high leakage risk under same-subject splits.
- Subjective labels may encode participant-specific reporting style.
- Nested modality payloads require aggregation before tabular models consume them.
- Minute-level streams must be aggregated before most tabular models can use them.
- Older paper or summary material may frame the task as six targets; the released package and metric description take precedence for current work and include `S4`.

## Working Implications

- Use this stable page, `wiki/datasets/sleep-lifelog-2024.md`, as the dataset reference.
- Include all seven targets, including `S4`, in future feature manifests, benchmark references, and experiment packets unless a later packet explicitly supersedes the target set.
- Treat Q-family and S-family targets as related but analytically different tasks.
- Use the locked grouped-subject split for sprint-1 local comparisons unless a downstream packet explicitly declares a different split and claim boundary.
- Do not infer organizer-official validation semantics from the local `GroupKFold` policy.
- Do not attach model performance to this dataset page; result-bearing packets must provide their own raw evidence and split-aware metric verification.

## Related Benchmark

The benchmark entity `[[benchmarks/sleep-health-hackathon-v0]]` defines the target taxonomy in more detail, the primary local metric (`grouped_macro_logloss`), evaluation tracks, and allowed downstream claim boundaries for results on this dataset.

## Claim Register

All current dataset claims remain `tentative`:

- `tentative`: `sleep-lifelog-2024` is a multimodal smartphone, smartwatch, sleep-sensor, and self-report dataset of about 700 days recorded in 2024 with seven prediction targets (`Q1`, `Q2`, `Q3`, `S1`, `S2`, `S3`, `S4`); the released training labels are in `ch2026_metrics_train.csv` and produce a 450-row modeling table grouped by `subject_id`.
- `tentative`: the sprint-1 local canonical split is 3-fold `GroupKFold` by `subject_id` on the released training labels; older six-target notes are lower priority than the released package framing.
- `tentative`: Q-family labels are participant-relative averages and therefore at very high leakage risk under same-subject splits; S-family labels reflect objective guideline compliance.

## Provenance

- packet_id: `2026-05-29-sleep-lifelog-2024`
- raw_packet_root: `raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/`
- raw_packet_files:
  - `raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/manifest.yaml`
  - `raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/dataset.yaml`
  - `raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/packet.md`
- packet_raw_paths:
  - `dataset.yaml`
- packet_recorded_primary_source_path:
  - `raw/datasets/sleep-lifelog-2024/`
- packet_recorded_supporting_sources:
  - `raw/references/chatgpt-share-2026-04-28-sleep-hackathon/transcript.md`
  - `raw/references/kick-off.md`
- related_benchmark: `[[benchmarks/sleep-health-hackathon-v0]]`
- latest_context_run: `26628582638-1`

## Open Questions and Supersession Notes

- Organizer official split: the dataset YAML records `organizer_official_split_available: false`. A later organizer-published split protocol should supersede the local split note through a new packet.
- Six-target versus seven-target framing: older summaries that omit `S4` are superseded for current team work by this packet's released-package framing unless later evidence says otherwise.
- Sleep-sensor schema: the packet only records a placeholder; a later schema packet should map sleep-sensor fields before feature claims depend on them.
- Package-level validation: this page preserves packet claims about package contents and modeling rows, but it does not independently hash or audit the full released package.
- Stable path note: the packet manifest lists a dated intended wiki target, but repository policy renders dataset entities to stable paths. The packet id remains in provenance.

## Reviewer Checklist

- Confirm that no model performance, baseline, or leaderboard claim was added to this dataset definition.
- Confirm that downstream result pages cite their split policy and do not rely on this page for organizer-official semantics.
- Confirm that future feature and experiment packets include `S4` unless a later packet explicitly changes the target set.
- Confirm that any same-subject temporal analysis is treated as a separate track from grouped-subject local OOF evaluation.
