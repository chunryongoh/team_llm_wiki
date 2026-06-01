# Notebook Output Summary

This file summarizes selected existing notebook outputs. The notebook was not re-executed for this packet.

## Config Output

- Mode: `full`
- Labels: `Q1`, `Q2`, `Q3`, `S1`, `S2`, `S3`, `S4`
- Trials: `50`
- Model: `mix_lgbm_catboost`
- Feature source: `saved_anchor_feature_list_922`
- Export feature source: `section11_base922_plus_labelwise_additive_policy`
- Internal blend: `probability_mean`
- Candidate blend: `logit_mean`
- V5 probe enabled: `true`
- V5 validation names: `public_start_tail`, `subject_time_tail_25`, `subject_time_tail_35`
- Submission directory printed by notebook: `Y2025LifeLogDB/submission/20260529_1800`

## Input Audit Output

- The notebook display shows all configured input paths existed at execution time.
- The notebook display shows `forbidden_input` was `False` for all configured input paths.
- The configured inputs were labels, sample submission template, base train/test features, entropy train/test features, anchor params, and Section 11 top features.

## Feature Policy Output

- Export feature counts printed by the notebook: `Q1=942`, `Q2=962`, `Q3=962`, `S1=922`, `S2=932`, `S3=1002`, `S4=922`.
- `V5_FULL_ACCEPTANCE` printed by the notebook: `False`.
- Selected feature set displayed for all labels: `current_07_policy`.
- Selected reason displayed for all labels: `global_v5_acceptance_failed_revert_to_current`.

## V5 Probe Output Highlights

| label | selected_mean_logloss | selected_worst_validation_logloss | selected_score | note |
| --- | ---: | ---: | ---: | --- |
| Q1 | 0.772244 | 0.840547 | 0.772244 | current policy retained |
| Q2 | 0.718284 | 0.733383 | 0.724324 | current policy retained despite some v5-change candidate improvement |
| Q3 | 0.764988 | 0.806824 | 0.781722 | current policy retained; v5 variants worse in displayed summary |
| S1 | 0.583197 | 0.617737 | 0.583197 | current policy retained |
| S2 | 0.776610 | 0.806099 | 0.776610 | current policy retained |
| S3 | 0.727348 | 0.780639 | 0.727348 | current policy retained |
| S4 | 0.812963 | 0.857525 | 0.830788 | current policy retained |

## Candidate Export Output

| candidate_name | uses_seed_ensemble | internal_blend | candidate_blend | seed_offsets | n_trials | n_labels |
| --- | --- | --- | --- | --- | ---: | ---: |
| `baseline_seed_ensemble` | true | `probability_mean` | `logit_mean` | `[0, 20000, 40000]` | 50 | 7 |

## Drift Audit Output

| label | mean | std | min | max | mean_abs_diff_vs_baseline |
| --- | ---: | ---: | ---: | ---: | ---: |
| Q1 | 0.500282 | 0.152882 | 0.206480 | 0.854269 | 0.029755 |
| Q2 | 0.569930 | 0.101914 | 0.282926 | 0.830819 | 0.045210 |
| Q3 | 0.615134 | 0.117726 | 0.255376 | 0.820790 | 0.044851 |
| S1 | 0.710474 | 0.187345 | 0.211366 | 0.947297 | 0.033505 |
| S2 | 0.677847 | 0.161144 | 0.330466 | 0.943438 | 0.039533 |
| S3 | 0.640532 | 0.159058 | 0.245193 | 0.900698 | 0.042307 |
| S4 | 0.588636 | 0.114333 | 0.310440 | 0.852038 | 0.030132 |

## Printed Artifact Paths

- `section07_candidate_scoreboard.csv` under `experiments/260519_recovered_feature_model_v1/data/section07_model_optuna_seed_ensemble/`
- `section07_model_optuna_seed_ensemble_summary.md` under `experiments/260519_recovered_feature_model_v1/reports/`
- submission directory: `Y2025LifeLogDB/submission/20260529_1800`

## Boundary Notes

- The numeric values above are copied from existing notebook outputs and are not validated by `metrics_to_verify`.
- No data files, submission files, model weights, or full Optuna logs are included in this packet.
