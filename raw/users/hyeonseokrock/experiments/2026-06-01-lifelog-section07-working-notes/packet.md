# LifeLog Section 07 Working Notes

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
