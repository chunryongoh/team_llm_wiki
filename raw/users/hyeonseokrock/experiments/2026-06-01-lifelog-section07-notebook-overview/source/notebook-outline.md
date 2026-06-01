# Notebook Outline

- source_notebook: `Y2025LifeLogDB/experiments/260519_recovered_feature_model_v1/notebooks/07_labelwise_feature_generation_integrated.ipynb`
- original_size_bytes_with_outputs: `1076359`
- no_output_copy_size_bytes: `99406`
- total_cells: `11`
- markdown_cells: `6`
- code_cells: `5`
- code_cells_with_outputs: `3`

## Cell Map

| cell | type | title_or_first_line | chars | output_count |
| ---: | --- | --- | ---: | ---: |
| 0 | markdown | # 07 Section4-Retrain Seed-Ensemble Model Optimization This notebook trains from scratch. It does not read existing submission files and does not read saved pre | 601 | 0 |
| 1 | markdown | ## 1. Config / Allowed Input Path Check | 39 | 0 |
| 2 | code | from __future__ import annotations from datetime import datetime from pathlib import Path import hashlib import json import warnings import numpy as np import p | 5623 | 2 |
| 3 | markdown | ## 2. Utilities | 15 | 0 |
| 4 | code | def clean_for_json(obj): if isinstance(obj, dict): return {str(k): clean_for_json(v) for k, v in obj.items()} if isinstance(obj, list): return [clean_for_json(v | 3244 | 0 |
| 5 | markdown | ## 3. Section 4 Feature Build Replay | 36 | 0 |
| 6 | code | train_y = coerce_key_frame(pd.read_csv(PATHS["train_labels"])) sample = coerce_key_frame(pd.read_csv(PATHS["sample_submission"])) features_train_base = coerce_k | 53735 | 5 |
| 7 | markdown | ## 4. Section 4 Model Utility Replay | 36 | 0 |
| 8 | code | def get_lgbm_classifier(params=None, random_state: int = 42): import lightgbm as lgb base = { "objective": "binary", "boosting_type": "gbdt", "random_state": ra | 5667 | 0 |
| 9 | markdown | ## 5. Seed-Ensemble Model Optuna Export | 39 | 0 |
| 10 | code | baseline_submission = sample.copy() seed_pack_submissions = {} baseline_label_rows = [] baseline_param_payload = {} all_trial_frames = [] prediction_long_frames | 10854 | 169 |

## Notebook Sections

1. `Config / Allowed Input Path Check`: defines labels, mode, trials, seed offsets, input paths, output folders, and forbidden input audit.
2. `Utilities`: JSON cleanup, feature hash, key coercion, optional feature merge, log-loss clipping, split helper, sanitize, and logit blending helpers.
3. `Section 4 Feature Build Replay`: reloads labels/sample/features, checks row identity, merges entropy features, resolves anchor features, creates additive/v5 feature candidates, probes v5 candidates, and selects export feature policy.
4. `Section 4 Model Utility Replay`: defines LightGBM and CatBoost constructors, Optuna search spaces, inner early-stopping split, and per-base-model fit/predict helpers.
5. `Seed-Ensemble Model Optuna Export`: trains per-label LGBM/CatBoost packs across seed offsets, exports candidate submission CSV and metadata, writes scoreboards/configs/reports, and records drift audit.

## Main Constants Observed In Code

| field | value |
| --- | --- |
| `ROW_KEY_COLS` | `subject_id`, `lifelog_date` |
| `LABELS` | `Q1`, `Q2`, `Q3`, `S1`, `S2`, `S3`, `S4` |
| `SECTION07_MODE` | `full` |
| `SECTION07_TRIALS` | `50` |
| `SECTION07_SMOKE_TRIALS` | `3` |
| `MODEL_CPU_THREADS` | `6` |
| `OPTUNA_N_JOBS` | `1` |
| `EARLY_STOPPING_ROUNDS` | `80` |
| `MODEL_NAME` | `mix_lgbm_catboost` |
| `FEATURE_SOURCE` | `saved_anchor_feature_list_922` |
| `EXPORT_FEATURE_SOURCE` | `section11_base922_plus_labelwise_additive_policy` |
| `BASELINE_INTERNAL_BLEND_METHOD` | `probability_mean` |
| `CANDIDATE_BLEND_METHOD` | `logit_mean` |
| `SECTION07_SEED_ENSEMBLE_OFFSETS` | `[0, 20000, 40000]` |
