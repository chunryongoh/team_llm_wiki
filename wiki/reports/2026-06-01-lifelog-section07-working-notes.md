---
id: 2026-06-01-lifelog-section07-working-notes
packet_type: experiment
type: experiment
title: LifeLog Section 07 Working Notes
date: '2026-06-01'
owner: hyeonseokrock
status: submitted
task: dacon-sleep-lifelog-section07-working-notes
dataset:
  name: sleep-lifelog-2024
  version: released-package
  hash: none
split:
  name: local-working-notes-mixed-validation-protocols
  group_key: subject_id
  fold_file: null
model:
  family: mix-lgbm-catboost-section07-working-candidate
  weights_in_repo: false
claim_boundary: Local Y2025LifeLogDB working notes only; public scores are user-reported
  notes and are not verified leaderboard or organizer-official evidence.
claim_status: tentative
summary: Section 07 working notes consolidate preprocessing, feature policy, model
  structure, and performance notes for the LifeLog sleep-health task, while keeping
  local validation, user-reported public scores, and final leaderboard claims separate.
raw_paths:
- packet.md
- source/01_preprocessing.md
- source/02_feature.md
- source/03_model.md
- source/04_performance.md
- source/FEATURES.md
intended_wiki_targets:
- wiki/experiments/2026-06-01-lifelog-section07-working-notes.md
metrics_to_verify: []
claims:
- status: tentative
  text: Section 07 rebuilds train and test features from source label/sample files
    and feature parquet inputs rather than using previous submission or prediction
    files as model input.
- status: tentative
  text: The current documented Section 07 feature policy keeps the saved anchor feature
    list and adds labelwise Section 11 additive top-k features, while rejecting full
    v5 change/frequency acceptance in the 2026-05-29 notes.
- status: tentative
  text: The current documented Section 07 model path uses a LightGBM and CatBoost
    probability-mean blend per label, with optional seed ensemble candidates blended
    by logit mean.
- status: tentative
  text: The user-reported public score notes identify section9_labelwise_best_20260522_1239
    as current best at 0.5986218188 and section07_candidate_baseline_seed_ensemble_20260529_1029
    as a near-best challenger at 0.6003735255, but this packet does not verify leaderboard
    provenance.
publish_action: bot_pr
risk_tier: tier2-interpretation
---

# LifeLog Section 07 Working Notes

- packet: `2026-06-01-lifelog-section07-working-notes`
- generated_by_run: `local-run-section07`
- publish_action: `bot_pr`
- risk_tier: `tier2-interpretation`
- compiled_packet: [automation/.cache/compiled/2026-06-01-lifelog-section07-working-notes.json](../../automation/.cache/compiled/2026-06-01-lifelog-section07-working-notes.json)
- owner: `hyeonseokrock`
- status: `submitted`
- task: `dacon-sleep-lifelog-section07-working-notes`
- dataset: `sleep-lifelog-2024` (`released-package`)
- split: `local-working-notes-mixed-validation-protocols`
- model: `mix-lgbm-catboost-section07-working-candidate`
- claim_boundary: Local Y2025LifeLogDB working notes only; public scores are user-reported notes and are not verified leaderboard or organizer-official evidence.
- claim_status: `tentative`
- date: `2026-06-01`
- raw_evidence:
  - `packet.md`
  - `source/01_preprocessing.md`
  - `source/02_feature.md`
  - `source/03_model.md`
  - `source/04_performance.md`
  - `source/FEATURES.md`
- review-required: true

## Summary

Section 07 working notes consolidate preprocessing, feature policy, model structure, and performance notes for the LifeLog sleep-health task, while keeping local validation, user-reported public scores, and final leaderboard claims separate.

## Packet Synthesis

This packet captures the current Y2025LifeLogDB working notes for the Section 07 labelwise feature generation and model pipeline. It is intended as team memory for future review, not as a final performance claim.

## Claim Boundary

The evidence in this packet is a set of local project notes copied from `Y2025LifeLogDB`. It does not include raw DACON submission metadata, a verified leaderboard export, organizer-official validation output, or re-executed notebook logs from this session.

Public scores mentioned in the source notes are treated as user-reported result notes. They should remain separate from local validation metrics and should not be promoted to verified leaderboard claims without a follow-up packet containing submission lineage and raw score evidence.

## Source Notes

- `source/01_preprocessing.md`: documents source files, key columns, train/test row counts, forbidden input rules, validation split names, missing-value policy, and TODO checks for Section 07.
- `source/02_feature.md`: documents the current anchor-plus-labelwise-additive feature policy, v5 change/frequency feature rejection, labelwise feature counts, and feature domain map.
- `source/03_model.md`: documents the Section 07 model family as a LightGBM/CatBoost blend with Optuna tuning, early stopping, and seed ensemble candidates.
- `source/04_performance.md`: documents current best and near-best user-reported public score notes, local validation caveats, and labelwise local probe summaries.
- `source/FEATURES.md`: preserves broader feature inventory and feature-generation policy across raw daily, HR/HRV proxy, screen/app, calendar, circadian, activity, social, raw-flat, raw-minute, PCA, and DNN sequence feature families.

## Observed Facts From The Notes

- The documented row identity is `subject_id` plus `lifelog_date`; the source notes record 450 train rows and 250 test rows.
- The target labels are `Q1`, `Q2`, `Q3`, `S1`, `S2`, `S3`, and `S4`.
- The notes state that Section 07 should avoid previous `submission/` files or previous prediction files as model inputs.
- The current feature policy keeps a saved anchor list of 922 features and adds labelwise Section 11 additive top-k features.
- The documented final export feature source is `section11_base922_plus_labelwise_additive_policy`.
- The notes record `v5_full_acceptance=false`, so v5 change/frequency features are not accepted as the final full feature set in the 2026-05-29 working notes.
- The documented model family is `mix_lgbm_catboost`, using LightGBM and CatBoost per label.
- The notes identify XGBoost, CNN, LSTM, and attention models as outside the current Section 07 optimization path.

## Decisions Captured

- Keep local validation scores and public score notes separate.
- Treat Q2/Q3/S4 as bottleneck labels that need targeted feature/model work.
- Do not use broad feature acceptance when only a subset of labels improves.
- Keep S4 feature expansion conservative unless a narrow sleep-disturbance or WASO proxy is validated.
- Preserve the current best submission line while writing challengers to new timestamp folders.

## Tentative Performance Notes

The performance source note records the following as user-reported public score notes:

| candidate | user-reported public score | status in notes |
| --- | ---: | --- |
| `submission/20260522_1239/section9_labelwise_best_20260522_1239.csv` | `0.5986218188` | current best |
| `submission/20260529_1029/section07_candidate_baseline_seed_ensemble_20260529_1029.csv` | `0.6003735255` | near-best challenger |

This packet does not include the raw leaderboard page, submission id, private score, or organizer-official validation evidence needed to verify those values.

## Evidence Gaps

- `section07_allowed_input_audit.csv` is referenced but not included in this packet.
- Labelwise feature hashes from `section07_section4_retrain_feature_policy.csv` are not included.
- Local validation protocols and public leaderboard scores are not normalized to one evidence class.
- AUROC, AUPRC, and confusion matrices are not calculated by the current Section 07 notes.
- Section 07 notebook execution was not rerun for this packet.
- DACON submission lineage for the public score notes is not included.

## Next Actions

- Add a follow-up performance packet with raw metric JSON or YAML if metric claims should be verified by the ingest guard.
- Add leaderboard provenance if the public score notes should become verified DACON leaderboard claims.
- Add an audit packet for `section07_allowed_input_audit.csv` and feature-policy hashes after the notebook artifacts are available.
- Design a Q3 temporal/window challenger and an S4 narrow WASO proxy experiment as separate packets.

## Claims

- tentative: Section 07 rebuilds train and test features from source label/sample files and feature parquet inputs rather than using previous submission or prediction files as model input.
- tentative: The current documented Section 07 feature policy keeps the saved anchor feature list and adds labelwise Section 11 additive top-k features, while rejecting full v5 change/frequency acceptance in the 2026-05-29 notes.
- tentative: The current documented Section 07 model path uses a LightGBM and CatBoost probability-mean blend per label, with optional seed ensemble candidates blended by logit mean.
- tentative: The user-reported public score notes identify section9_labelwise_best_20260522_1239 as current best at 0.5986218188 and section07_candidate_baseline_seed_ensemble_20260529_1029 as a near-best challenger at 0.6003735255, but this packet does not verify leaderboard provenance.
