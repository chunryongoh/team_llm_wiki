# 2026 06 18 Sleep Lifelog Packet Synthesis

## GitHub Models Deterministic Page Scaffold

- fallback_merge_policy: deterministic_new_page_scaffold
- fallback_compact_body_applied: false
- note: GitHub Models fallback identified this page as required, but compact model prose was not applied because metric provenance must come from raw packet evidence.

## Source Packets

### 2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic

- packet_type: `performance`
- title: Wave41 LGB CB Foldsafe Synthesis Smoke Local OOF Diagnostic
- date: `2026-06-18`
- owner: `chunryongoh`
- dataset: `sleep-lifelog-2024` (`released-package`)
- split: `local-groupkfold-subject-5fold-oof`
- model: `lightgbm-catboost-foldsafe-synthesis-targetwise-reblend`
- claim_boundary: `local_oof_diagnostic_only`
- claim_status: `supported`
- summary: Wave41 LGB/CB fold-safe synthesis smoke improved the prior LGB/CB reproduction local OOF diagnostic line from 0.6198365213240887 to 0.6195964535023479, but remains local OOF only and short of the 0.61 goal.

#### Raw-backed Metrics

- `Q1_log_loss`: `0.6225370998897288` (raw_path: `metrics.json`)
- `Q2_log_loss`: `0.6555493560477773` (raw_path: `metrics.json`)
- `Q3_log_loss`: `0.6309857415368405` (raw_path: `metrics.json`)
- `S1_log_loss`: `0.562996471228798` (raw_path: `metrics.json`)
- `S2_log_loss`: `0.6113857154018603` (raw_path: `metrics.json`)
- `S3_log_loss`: `0.595105227779678` (raw_path: `metrics.json`)
- `S4_log_loss`: `0.6586155626317527` (raw_path: `metrics.json`)
- `delta_vs_prior_lgb_cb_reproduction`: `-0.000240067821740797` (raw_path: `metrics.json`)
- `grouped_macro_log_loss`: `0.6195964535023479` (raw_path: `metrics.json`)
- `macro_auroc`: `0.680617701580707` (raw_path: `metrics.json`)
- `macro_brier_score`: `0.2153164638768479` (raw_path: `metrics.json`)
- `macro_f1`: `0.7417894093790057` (raw_path: `metrics.json`)
- `macro_roc_auc`: `0.680617701580707` (raw_path: `metrics.json`)
- `prior_lgb_cb_reproduction_macro_log_loss`: `0.6198365213240887` (raw_path: `metrics.json`)
- `remaining_gap_to_0p61`: `0.009596453502347946` (raw_path: `metrics.json`)
- `targetwise_reblend_macro_log_loss`: `0.6195964535023479` (raw_path: `metrics.json`)

#### Manifest Claims

- supported: Wave41 LGB/CB fold-safe synthesis smoke improved the prior LGB/CB reproduction local OOF diagnostic line from 0.6198365213240887 to 0.6195964535023479, but remains local OOF only and short of the 0.61 goal.

## Review Boundary

- Local OOF, notebook output, DACON public/private leaderboard, and organizer-official validation remain separate evidence surfaces.
- Do not treat this scaffold as a claim promotion; update it with primary LLM synthesis or human review when stronger evidence is available.

## Raw Evidence

raw_evidence:
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/manifest.yaml
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/artifact_summary.json
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/metrics.json
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/packet.md
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/packet_entity_graph.json
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/performance.yaml
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/question_queue.yaml
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/semantic_lint.json
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/wiki_plan.yaml
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/source_note.md
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/source_artifacts/suite_summary.json
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/source_artifacts/suite_metrics.json
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/source_artifacts/decision_matrix.csv
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/source_artifacts/candidate_status.csv
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/source_artifacts/fold_subjects.json
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/source_artifacts/suite_plan.json
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/source_artifacts/optuna_trials.csv
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/source_artifacts/targetwise_reblend_summary.json
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/source_artifacts/blend_weights.json
- raw/users/chunryongoh/performance/2026-06-18-wave41-lgb-cb-foldsafe-synthesis-smoke-local-oof-diagnostic/source_artifacts/target_deltas.json
