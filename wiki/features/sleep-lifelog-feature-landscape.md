---
id: sleep-lifelog-feature-landscape
type: feature-synthesis
title: Sleep Lifelog Feature Landscape
source_packets:
  - 2026-05-29-sleep-lifelog-2024
  - 2026-05-29-sleep-health-hackathon-v0
claim_status: tentative
review_required: true
related_dataset: sleep-lifelog-2024
related_benchmark: sleep-health-hackathon-v0
summary: "sleep-lifelog-2024의 modality별 feature surface와 aggregation risk를 정리한 합성 페이지입니다. 현재 성능 claim이나 feature importance claim은 없으며, Q-family leakage와 nested/minute-level payload aggregation을 주요 주의점으로 기록합니다."
raw_evidence:
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/manifest.yaml
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/benchmark.yaml
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/packet.md
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/manifest.yaml
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/dataset.yaml
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/packet.md
---

# Sleep Lifelog Feature Landscape

이 페이지는 [Sleep Lifelog 2024 Dataset](../datasets/sleep-lifelog-2024.md)과 [Sleep Health Hackathon Benchmark v0](../benchmarks/sleep-health-hackathon-v0.md)에서 파생된 feature engineering landscape입니다. 목적은 feature packet과 experiment packet이 같은 vocabulary를 쓰도록 돕는 것이며, 어떤 feature가 성능을 개선한다는 claim은 하지 않습니다.

## Provenance and Boundary

- source packet ids: `2026-05-29-sleep-lifelog-2024`, `2026-05-29-sleep-health-hackathon-v0`
- source raw roots: `raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/`, `raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/`
- claim_status: `tentative`
- boundary: feature taxonomy and risk synthesis only, not metric evidence
- related decision: [Sleep Lifelog Evaluation Protocol](../decisions/sleep-lifelog-evaluation-protocol.md)
- related questions: [Sleep Lifelog Open Questions](../questions/sleep-lifelog-open-questions.md)

## Feature Surface by Modality

| modality family | raw tables or references | current synthesis |
| --- | --- | --- |
| smartphone context/activity | `mACStatus`, `mActivity`, `mAmbience`, `mBle`, `mGps`, `mLight`, `mScreenStatus`, `mUsagestats`, `mWifi` | event, context, location/proximity, light, screen, app usage style features의 후보 surface입니다. |
| smartwatch physiology/activity | `wHr`, `wLight`, `wPedo` | heart-rate, wearable light, step/activity aggregates의 후보 surface입니다. |
| sleep sensor | `sleep-sensor:placeholder` | released package/team notes에 존재가 기록되었지만 schema mapping은 이 packet만으로 확정되지 않았습니다. |
| self-report | `self-report:bedtime-questionnaire` | labels와 별개로 questionnaire-derived covariates가 있을 수 있으나 leakage boundary 확인이 필요합니다. |

## Required Aggregation Shape

Raw evidence는 여러 modality payload가 nested list/struct 또는 minute-level streams라고 경고합니다. 대부분의 tabular models는 row-level modeling table을 필요로 하므로 feature work는 최소한 아래를 명시해야 합니다.

- join keys: `subject_id`, `sleep_date`, `lifelog_date`
- row grain: released labels와 align되는 450-row modeling table
- aggregation window: sleep episode 전후 어느 기간을 포함했는지
- fold safety: `GroupKFold` by `subject_id`에서 validation subject의 정보가 train aggregate에 섞이지 않았는지
- target coverage: `Q1`, `Q2`, `Q3`, `S1`, `S2`, `S3`, `S4` 모두 고려했는지

## Target-family Implications

Q-family labels는 participant-relative averages입니다. 따라서 per-subject historical mean, participant reporting style, same-subject temporal artifacts는 Track A `unseen-subject-generalization`에서는 leakage 또는 overfitting source가 될 수 있습니다. S-family labels는 objective guideline compliance지만, sleep duration/efficiency/onset/WASO와 직접 관련된 feature는 temporal alignment를 엄격히 설명해야 합니다.

## Feature Packet Checklist

Future feature packets should include:

- dataset anchor: `sleep-lifelog-2024`
- benchmark anchor: `sleep-health-hackathon-v0`
- split anchor: `groupkfold-subject-3fold-oof` unless explicitly Track B
- source modalities and raw columns/tables used
- aggregation window around `sleep_date` and `lifelog_date`
- train/validation leakage controls for `subject_id`
- target family affected: Q-family, S-family, or both
- claim_boundary if paired with metrics: `local_oof_diagnostic_only`, `same_split_baseline_comparison`, or `public_lb_observation_only`

## Non-claims

현재 wiki에는 feature importance, ablation gain, model leaderboard improvement에 대한 raw metric/split evidence가 없습니다. 따라서 이 페이지는 feature 후보와 위험을 정리할 뿐, 어떤 modality 또는 feature group이 더 좋다고 주장하지 않습니다.
