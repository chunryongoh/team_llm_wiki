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

# Sleep Lifelog 2024 Dataset Definition

## Page Status

- packet_id: `2026-05-29-sleep-lifelog-2024`
- generated_by_run: `26628582638-1`
- publish_action: `bot_pr`
- risk_tier: `tier2-interpretation`
- review_required: `true`
- owner: `chunryongoh`
- status: `submitted`
- task: `dataset-definition`
- dataset: `sleep-lifelog-2024` (`v0`)
- split: `groupkfold-subject-3fold-oof`
- model: `not-applicable`
- claim_boundary: `dataset_definition_not_metric_claim`
- claim_status: `tentative`
- date: `2026-05-29`
- compiled_packet: [automation/.cache/compiled/2026-05-29-sleep-lifelog-2024.json](../../automation/.cache/compiled/2026-05-29-sleep-lifelog-2024.json)

## Synthesis

`sleep-lifelog-2024` is the stable dataset entity for the team's 2024 sleep-health lifelog work. This page should be used as a dataset anchor for downstream feature, model, benchmark, and experiment packets; it is not a performance-result page.

The packet evidence supports a tentative description of the released package, modality families, seven-label target set, local grouped-subject split policy, and leakage risks. It does not support any model-quality, leaderboard, or baseline claim.

한국어 메모: 현재 팀 기준은 `subject_id` 기준 3-fold `GroupKFold`를 sprint-1 로컬 기준으로 삼는 것이다. 같은 사람의 다른 날짜를 train/validation에 섞는 평가는 Q 계열 라벨에서 특히 누수 위험이 크므로 별도 트랙으로만 다룬다.

## Stable Entity Fields

- name: `sleep-lifelog-2024`
- version: `v0`
- packet_type: `dataset`
- source_type: `released-package-plus-team-summary`
- primary_label_file: `ch2026_metrics_train.csv`
- canonical_modeling_rows: `450`
- canonical_group_key: `subject_id`
- canonical_local_split: `groupkfold-subject-3fold-oof`
- organizer_official_split_available: `false`

## Released Package Contents

The packet records these released-package artifacts as the current source of record:

- `ch2025_data_items/`: modality tables; the packet narrative describes 12 parquet files.
- `ch2026_metrics_train.csv`: released training labels and the source of the current modeling table.
- `ch2026_submission_sample.csv`: submission schema reference.
- `ch2026_metrics_description.pdf`: organizer metric and label description reference.
- `data.zip`: original archive.

The manifest's tentative claim describes the dataset as about 700 days from 2024. The structured dataset YAML separately records that the current joined modeling table has 450 rows grouped by `subject_id`.

## Modalities

| source | recorded modalities or status |
| --- | --- |
| smartphone | `mACStatus`, `mActivity`, `mAmbience`, `mBle`, `mGps`, `mLight`, `mScreenStatus`, `mUsagestats`, `mWifi` |
| smartwatch | `wHr`, `wLight`, `wPedo` |
| sleep-sensor | referenced as `sleep-sensor:placeholder`; schema is not exhaustively mapped in this packet |
| self-report | `bedtime-questionnaire` |

Several modality payloads are nested or minute-level streams. The packet flags these as requiring aggregation before most tabular modeling workflows can consume them safely.

## Targets

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

The Q-family labels are participant-relative averages and therefore high risk for identity leakage under same-subject validation. The S-family labels are framed as guideline-compliance targets, but this dataset page does not validate any metric value for them.

## Split Policy

For sprint-1 local comparisons, the canonical local split is:

- split_policy: `groupkfold-subject`
- split_name: `groupkfold-subject-3fold-oof`
- group_key: `subject_id`
- n_folds: `3`
- source: `local-canonical-sprint1`
- fold_file: `null`

Same-subject temporal forecasting is recorded as a candidate alternative in the related benchmark, not as the canonical dataset split. Downstream result packets should name the split they used and should not compare same-subject temporal results against grouped-subject OOF results as if they were the same protocol.

## Working Implications

- Use this stable page, `wiki/datasets/sleep-lifelog-2024.md`, as the dataset reference rather than a dated packet mirror.
- Include all seven targets, including `S4`, in future feature manifests, benchmark references, and experiment packets unless a later packet explicitly supersedes the target set.
- Treat Q-family and S-family targets as related but analytically different tasks.
- Do not infer organizer-official validation semantics from the local `GroupKFold` policy.
- Do not attach model performance to this dataset page; result-bearing packets must provide their own raw evidence and metric verification.

## Claim Register

All current claims from this packet remain `tentative`:

- `tentative`: the dataset is a multimodal smartphone, smartwatch, sleep-sensor, and self-report release from 2024 with seven targets and a 450-row modeling table from `ch2026_metrics_train.csv`.
- `tentative`: the sprint-1 local canonical split is 3-fold `GroupKFold` by `subject_id`; older six-target notes are lower priority than the released package and metric description.
- `tentative`: Q-family labels carry very high same-subject leakage risk because they are participant-relative; S-family labels reflect objective guideline compliance.

## Provenance

- packet_id: `2026-05-29-sleep-lifelog-2024`
- raw_packet_root: `raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/`
- raw_packet_files:
  - `raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/manifest.yaml`
  - `raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/dataset.yaml`
  - `raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/packet.md`
- packet-recorded primary source path: `raw/datasets/sleep-lifelog-2024/`
- packet-recorded supporting sources:
  - `raw/references/chatgpt-share-2026-04-28-sleep-hackathon/transcript.md`
  - `raw/references/kick-off.md`
- related benchmark: `[[benchmarks/sleep-health-hackathon-v0]]`

## Open Questions, Conflicts, and Supersession Notes

- Organizer official split: the dataset YAML records `organizer_official_split_available: false`. A later organizer-published split protocol should supersede the local split note through a new packet.
- Six-target versus seven-target notes: older summaries that omit `S4` are superseded for current team work by this packet's released-package framing.
- Sleep-sensor schema: the packet only records a placeholder; a later schema packet should map sleep-sensor fields before feature claims depend on them.
- Stable path: the manifest's `intended_wiki_targets` contains a dated path, but repository policy renders dataset entities to stable paths such as `wiki/datasets/sleep-lifelog-2024.md`; the packet id remains in provenance.
