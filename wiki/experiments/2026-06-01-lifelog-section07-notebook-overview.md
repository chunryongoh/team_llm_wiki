---
id: 2026-06-01-lifelog-section07-notebook-overview
packet_type: experiment
type: experiment
title: LifeLog Section 07 Notebook Overview
date: '2026-06-01'
owner: hyeonseokrock
status: submitted
task: dacon-sleep-lifelog-section07-notebook-overview
dataset:
  name: sleep-lifelog-2024
  version: released-package
  hash: none
split:
  name: existing-notebook-local-validation-probes
  group_key: subject_id
  fold_file: null
model:
  family: mix-lgbm-catboost-section07-seed-ensemble-export
  weights_in_repo: false
claim_boundary: Existing 07_labelwise_feature_generation_integrated.ipynb structure
  and saved notebook-output summary only; data files, model weights, submission CSVs,
  full Optuna logs, rerun evidence, and verified leaderboard claims are excluded.
claim_status: tentative
summary: The notebook rebuilds Section 07 LifeLog features from allowed project inputs,
  probes additive and v5 feature policies, keeps the current labelwise additive export
  policy after global v5 rejection, and exports a LightGBM/CatBoost seed-ensemble
  candidate; this packet includes a no-output notebook copy plus outline/output summaries,
  not the underlying data.
raw_paths:
- packet.md
- source/07_labelwise_feature_generation_integrated.no-output.ipynb
- source/notebook-outline.md
- source/notebook-output-summary.md
intended_wiki_targets:
- wiki/experiments/2026-06-01-lifelog-section07-notebook-overview.md
metrics_to_verify: []
claims:
- status: tentative
  text: The notebook is configured to rebuild Section 07 train and test features from
    project label, sample, feature, entropy, anchor-parameter, and Section 11 top-feature
    inputs rather than from previous submissions or prediction files.
- status: tentative
  text: Existing notebook outputs show all configured inputs existed at execution
    time and were not marked as forbidden inputs, but this packet does not include
    the raw audit CSV or a rerun log.
- status: tentative
  text: Existing notebook outputs show global v5 feature acceptance failed, so the
    export policy retained the current labelwise additive policy with per-label feature
    counts from 922 to 1002.
- status: tentative
  text: The candidate export path uses per-label LightGBM and CatBoost packs across
    seed offsets 0, 20000, and 40000, with probability-mean internal blending and
    logit-mean candidate blending.
publish_action: bot_pr
risk_tier: tier2-interpretation
---

# LifeLog Section 07 Notebook Overview

- packet: `2026-06-01-lifelog-section07-notebook-overview`
- generated_by_run: `26749076720-1`
- publish_action: `bot_pr`
- risk_tier: `tier2-interpretation`
- compiled_packet: [automation/.cache/compiled/2026-06-01-lifelog-section07-notebook-overview.json](../../automation/.cache/compiled/2026-06-01-lifelog-section07-notebook-overview.json)
- owner: `hyeonseokrock`
- status: `submitted`
- task: `dacon-sleep-lifelog-section07-notebook-overview`
- dataset: `sleep-lifelog-2024` (`released-package`)
- split: `existing-notebook-local-validation-probes`
- model: `mix-lgbm-catboost-section07-seed-ensemble-export`
- claim_boundary: Existing 07_labelwise_feature_generation_integrated.ipynb structure and saved notebook-output summary only; data files, model weights, submission CSVs, full Optuna logs, rerun evidence, and verified leaderboard claims are excluded.
- claim_status: `tentative`
- date: `2026-06-01`
- raw_evidence:
  - `packet.md`
  - `source/07_labelwise_feature_generation_integrated.no-output.ipynb`
  - `source/notebook-outline.md`
  - `source/notebook-output-summary.md`
- review-required: true

## Summary

The notebook rebuilds Section 07 LifeLog features from allowed project inputs, probes additive and v5 feature policies, keeps the current labelwise additive export policy after global v5 rejection, and exports a LightGBM/CatBoost seed-ensemble candidate; this packet includes a no-output notebook copy plus outline/output summaries, not the underlying data.

## Packet Synthesis

This packet summarizes `07_labelwise_feature_generation_integrated.ipynb` from the local `Y2025LifeLogDB` workspace. It is intended to make the notebook-level workflow readable in Team LLM Wiki without uploading private data, submission CSVs, model weights, or full notebook outputs.

## Claim Boundary

The evidence is limited to the notebook source structure, a no-output copy of the notebook, and a compact summary of selected outputs already saved in the notebook file. The notebook was not re-executed for this packet.

Numeric values copied from notebook outputs are treated as tentative local-output observations. They are not `metrics_to_verify` evidence, not a leaderboard claim, and not proof that the underlying data or model artifacts are available in this wiki repository.

## Included Source Files

- `source/07_labelwise_feature_generation_integrated.no-output.ipynb`: output-stripped notebook copy for code and markdown review.
- `source/notebook-outline.md`: generated outline with cell map, section map, and main constants.
- `source/notebook-output-summary.md`: compact summary of selected outputs that were present in the original notebook.

## Notebook Purpose

The notebook records a Section 07 LifeLog experiment path for rebuilding labelwise features and exporting a seed-ensemble model candidate. It combines feature-policy replay, validation probing, and model export into one integrated notebook.

The observed notebook title is `07 Section4-Retrain Seed-Ensemble Model Optimization`. Its top markdown states that it trains from scratch, does not read existing submission files, does not read saved prediction files, and uses source labels plus current feature artifacts as inputs.

## Workflow Outline

1. `Config / Allowed Input Path Check`
   Defines labels, execution mode, Optuna trial counts, model settings, seed offsets, input paths, output folders, and a forbidden-input audit.

2. `Utilities`
   Defines JSON cleanup, feature hashing, key coercion, optional feature merge, clipped log-loss, split helpers, filename sanitization, and logit blending helpers.

3. `Section 4 Feature Build Replay`
   Reloads labels, sample submission template, base features, entropy features, anchor parameters, and Section 11 top features. It checks row identity, merges optional entropy features, resolves the saved anchor feature list, creates additive and v5 feature candidates, probes v5 candidates, and selects an export feature policy.

4. `Section 4 Model Utility Replay`
   Defines LightGBM and CatBoost constructors, Optuna search spaces, early-stopping split logic, and base-model fit/predict helpers.

5. `Seed-Ensemble Model Optuna Export`
   Trains per-label LightGBM/CatBoost packs across configured seed offsets, builds baseline and seed-ensemble candidate submissions, writes scoreboards/configs/reports, and records a drift audit.

## Observed Configuration

The notebook constants identify the row key as `subject_id` plus `lifelog_date`, and the labels as `Q1`, `Q2`, `Q3`, `S1`, `S2`, `S3`, and `S4`.

The observed run configuration is:

| field | value |
| --- | --- |
| mode | `full` |
| Optuna trials | `50` |
| model name | `mix_lgbm_catboost` |
| feature source | `saved_anchor_feature_list_922` |
| export feature source | `section11_base922_plus_labelwise_additive_policy` |
| internal blend | `probability_mean` |
| candidate blend | `logit_mean` |
| seed offsets | `[0, 20000, 40000]` |
| model CPU threads | `6` |
| early stopping rounds | `80` |

## Input Audit Observation

Existing notebook outputs show that all configured input paths existed at execution time and were not marked as forbidden inputs. The configured inputs covered labels, sample submission template, base train/test features, entropy train/test features, anchor parameters, and Section 11 top features.

The raw audit CSV is not included in this packet, so this remains a tentative notebook-output observation.

## Feature Policy Observation

Existing notebook outputs show `V5_FULL_ACCEPTANCE` as `False`. The displayed selected feature set is `current_07_policy` for all seven labels, with the selected reason `global_v5_acceptance_failed_revert_to_current`.

The notebook-output summary records these export feature counts:

| label | export feature count |
| --- | ---: |
| Q1 | 942 |
| Q2 | 962 |
| Q3 | 962 |
| S1 | 922 |
| S2 | 932 |
| S3 | 1002 |
| S4 | 922 |

This means the notebook kept the saved anchor feature list plus labelwise Section 11 additive top-k features, rather than adopting the full v5 change/frequency policy.

## V5 Probe Observation

The notebook-output summary records local selected log-loss probe rows for `public_start_tail`, `subject_time_tail_25`, and `subject_time_tail_35` style validation checks. All labels retained the current policy in the displayed selected summary.

Because this packet does not include raw fold files, raw metrics files, or a rerun report, these values should be used only as notebook-output context for follow-up analysis.

## Candidate Export Observation

The candidate export output identifies one candidate row:

| candidate_name | uses_seed_ensemble | internal_blend | candidate_blend | seed_offsets | n_trials | n_labels |
| --- | --- | --- | --- | --- | ---: | ---: |
| `baseline_seed_ensemble` | true | `probability_mean` | `logit_mean` | `[0, 20000, 40000]` | 50 | 7 |

The notebook printed an output submission directory of `Y2025LifeLogDB/submission/20260529_1800`, but this packet does not upload that submission folder or assert any leaderboard result from it.

## Drift Audit Observation

The notebook-output summary includes per-label prediction distribution and mean absolute difference versus baseline. The largest displayed mean absolute differences are for `Q2` and `Q3`, with `Q1` and `S4` lower in that summary. These are local notebook-output diagnostics only.

## Evidence Gaps

- The notebook was not re-executed during this packet creation.
- Raw data files, feature parquet files, submission CSVs, model weights, and full Optuna logs are not included.
- `section07_allowed_input_audit.csv` is referenced by notebook outputs but not included here.
- Raw validation split definitions and metric JSON/YAML are not included, so `metrics_to_verify` is empty.
- Public leaderboard provenance and submission lineage are not included.

## Next Actions

- Add a follow-up audit packet if `section07_allowed_input_audit.csv` and feature-policy hashes should become reviewable raw evidence.
- Add a performance packet with raw JSON/YAML metrics if any local validation values should become verified wiki metrics.
- Add a leaderboard-provenance packet only if public/private DACON score claims need to be promoted beyond tentative notes.
- Use the no-output notebook copy as a code-review artifact for future Section 07 refactoring or rerun planning.

## Claims

- tentative: The notebook is configured to rebuild Section 07 train and test features from project label, sample, feature, entropy, anchor-parameter, and Section 11 top-feature inputs rather than from previous submissions or prediction files.
- tentative: Existing notebook outputs show all configured inputs existed at execution time and were not marked as forbidden inputs, but this packet does not include the raw audit CSV or a rerun log.
- tentative: Existing notebook outputs show global v5 feature acceptance failed, so the export policy retained the current labelwise additive policy with per-label feature counts from 922 to 1002.
- tentative: The candidate export path uses per-label LightGBM and CatBoost packs across seed offsets 0, 20000, and 40000, with probability-mean internal blending and logit-mean candidate blending.
