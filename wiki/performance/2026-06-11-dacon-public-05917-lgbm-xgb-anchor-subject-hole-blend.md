---
id: 2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend
packet_type: performance
type: performance
title: dacon public 05917 lgbm xgb anchor subject hole blend
date: '2026-06-11'
owner: dacon-community
status: submitted
task: source-ingest
dataset:
  name: sleep-lifelog-2024
  version: dacon-competition-package
  hash: not-provided
split:
  name: subject-hole-cv-5fold-reference
  group_key: null
  fold_file: null
model:
  family: lgbm-xgb-anchor-blend
  weights_in_repo: false
claim_boundary: public_lb_observation_only_from_dacon_codeshare_and_attached_notebook;
  not team verified; no DACON submission id, leaderboard export, submission file lineage,
  or same-run local reproduction is present in this packet. Notebook local OOF values
  are notebook-output summaries and must not be merged with team canonical local OOF.
claim_status: tentative
summary: DACON code share 13975 reports Public 0.5917 for an LGBM+XGB anchor blend
  using V152 anchor OOF features, Subject-hole CV, stability-based feature selection,
  and blend search. Treat as an external reference and tentative public leaderboard
  observation until our team verifies submission lineage and same-split reproduction.
raw_paths:
- dacon-public-05917-lgbm-xgb-anchor-subject-hole.ipynb
- dacon-codeshare-13975.md
- metrics.json
- packet.md
- performance.yaml
- wiki_plan.yaml
intended_wiki_targets:
- wiki/performance/2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend.md
metrics_to_verify:
- raw_path: metrics.json
  metric_key: cat_only_notebook_oof_log_loss
  reported_value: 0.528
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: feature_count_after_stability_filter
  reported_value: 1682.0
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: feature_count_before_stability_filter
  reported_value: 23177.0
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: lgbm_only_notebook_oof_log_loss
  reported_value: 0.525
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: log_loss
  reported_value: 0.5917
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: notebook_local_oof_log_loss
  reported_value: 0.514
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: notebook_local_public_gap
  reported_value: 0.075
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: public_lb_log_loss
  reported_value: 0.5917
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: target_specific_notebook_oof_log_loss
  reported_value: 0.513
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: xgb_only_notebook_oof_log_loss
  reported_value: 0.53
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
claims:
- status: tentative
  text: DACON code share 13975 reports Public 0.5917 for an LGBM+XGB anchor blend
    using V152 anchor OOF features, Subject-hole CV, stability-based feature selection,
    and blend search. Treat as an external reference and tentative public leaderboard
    observation until our team verifies submission lineage and same-split reproduction.
publish_action: bot_pr
risk_tier: tier3-performance
---

# dacon public 05917 lgbm xgb anchor subject hole blend

- packet: `2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend`
- generated_by_run: `27325835544-1`
- publish_action: `bot_pr`
- risk_tier: `tier3-performance`
- compiled_packet: [automation/.cache/compiled/2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend.json](../../automation/.cache/compiled/2026-06-11-dacon-public-05917-lgbm-xgb-anchor-subject-hole-blend.json)
- owner: `dacon-community`
- status: `submitted`
- task: `source-ingest`
- dataset: `sleep-lifelog-2024` (`dacon-competition-package`)
- split: `subject-hole-cv-5fold-reference`
- model: `lgbm-xgb-anchor-blend`
- claim_boundary: public_lb_observation_only_from_dacon_codeshare_and_attached_notebook; not team verified; no DACON submission id, leaderboard export, submission file lineage, or same-run local reproduction is present in this packet. Notebook local OOF values are notebook-output summaries and must not be merged with team canonical local OOF.
- claim_status: `tentative`
- date: `2026-06-11`
- raw_evidence:
  - `dacon-public-05917-lgbm-xgb-anchor-subject-hole.ipynb`
  - `dacon-codeshare-13975.md`
  - `metrics.json`
  - `packet.md`
  - `performance.yaml`
  - `wiki_plan.yaml`
- review-required: true

## Summary

DACON code share 13975 reports Public 0.5917 for an LGBM+XGB anchor blend using V152 anchor OOF features, Subject-hole CV, stability-based feature selection, and blend search. Treat as an external reference and tentative public leaderboard observation until our team verifies submission lineage and same-split reproduction.

## Packet Synthesis

External DACON code share reference for ETRI sleep-health competition. The public post and attached notebook describe a multi-target binary classification pipeline for Q1, Q2, Q3, S1, S2, S3, S4. The pipeline defines calendar features, sleep windows, placeholder window-pair interactions, stability-based feature filtering from 23,177 to 1,682 features, Subject-hole CV, targetwise LGBM/XGB/CatBoost models, and LGBM+XGB 7:3 style blending. The post states Public 0.5917, but the supporting V152 OOF anchor, large feature parquet, submission id, and leaderboard export are not included, so this is reference evidence rather than a verified team result.

## Wiki Integration Hints

### stable_entities

- {'action': 'create_or_update', 'id': 'model:lgbm-xgb-anchor-subject-hole-blend', 'kind': 'model', 'page': 'wiki/models/lgbm-xgb-anchor-subject-hole-blend.md', 'page_role': 'leaf', 'promotion_reason': ['external 0.59 public LB reference', 'contains reusable anchor OOF and blend pattern', 'needs independent claim boundary']}
- {'action': 'create_or_update', 'id': 'preprocessing:subject-hole-cv', 'kind': 'preprocessing', 'page': 'wiki/preprocessing/subject-hole-cv.md', 'page_role': 'leaf', 'promotion_reason': ['validation strategy differs from team canonical GroupKFold', 'high leakage-risk concept requiring separate policy']}
- {'action': 'create_or_update', 'id': 'feature:stability-filtered-feature-selection', 'kind': 'feature', 'page': 'wiki/features/stability-filtered-feature-selection.md', 'page_role': 'leaf', 'promotion_reason': ['feature selection method is reusable across team experiments', 'requires ablation before adoption']}
- {'action': 'record_observation', 'id': 'submission:dacon-public-05917-external-codeshare', 'kind': 'submission', 'page': 'wiki/submissions/dacon-leaderboard-history.md', 'page_role': 'registry', 'promotion_reason': ['public LB observation must stay separated from team verified leaderboard claims']}

### affected_pages

- {'expected_change': 'Add an external DACON code share public 0.5917 observation with explicit unverified lineage boundary.', 'path': 'wiki/submissions/dacon-leaderboard-history.md', 'role': 'registry'}
- {'expected_change': "Cross-link that this reference uses LGBM+XGB rather than the team's current LGBM+CatBoost best direction.", 'path': 'wiki/models/lightgbm-catboost.md', 'role': 'leaf'}
- {'expected_change': 'Add routing row for stability-filtered feature selection and window-pair feature caveat.', 'path': 'wiki/features/sleep-lifelog-feature-landscape.md', 'role': 'hub'}
- {'expected_change': 'Record Subject-hole CV as external reference, not canonical sprint policy.', 'path': 'wiki/preprocessing/canonical-split-and-leakage-policy.md', 'role': 'registry'}
- {'expected_change': 'Add closeable questions for reproducing V152 anchor OOF and verifying public score lineage.', 'path': 'wiki/questions/sleep-lifelog-open-questions.md', 'role': 'hub'}
- {'expected_change': 'Create source-specific performance review page for the DACON code share.', 'path': 'wiki/performance/dacon-public-05917-lgbm-xgb-anchor-reference.md', 'role': 'packet_review'}

### claim_registry_updates

- tentative: external DACON code share reports Public 0.5917 for LGBM+XGB anchor blend; not team verified and not promoted to supported leaderboard claim.
- tentative: notebook reports local OOF 0.514 and Local-Public gap about 0.075, but this is notebook-output evidence only.

### supersedes_or_conflicts

- Does not supersede team v186/v189/Section07 public notes because submission lineage and evaluation surfaces differ.
- Does not replace team LGBM+CatBoost direction; this external reference emphasizes LGBM+XGB blend with optional CatBoost.

### open_questions

- {'close_condition': 'Evidence proves or rejects that the 0.5917 observation is reproducible and traceable.', 'id': 'dacon-public-05917-submission-lineage', 'merge_blocker': False, 'needed_evidence': ['DACON submission id', 'leaderboard export or screenshot', 'submission CSV hash or file lineage'], 'owner_role': 'validation-owner', 'priority': 'high', 'question': 'Can the external 0.5917 public score be linked to a DACON submission id, leaderboard export, and exact submission CSV lineage?'}
- {'close_condition': 'Team can reproduce anchor OOF or documents why it is not portable.', 'id': 'v152-anchor-oof-reproduction', 'merge_blocker': False, 'needed_evidence': ['V152 training recipe', 'OOF CSV with subject_id, sleep_date, lifelog_date and Q/S probability columns', 'fold assignment and leakage audit'], 'owner_role': 'model-owner', 'priority': 'high', 'question': "Can the V152 anchor OOF probabilities be reproduced without leakage using the team's canonical row identity?"}
- {'close_condition': 'Same-run comparison determines whether Subject-hole CV is adopted, rejected, or kept as exploratory.', 'id': 'subject-hole-cv-vs-canonical-groupkfold', 'merge_blocker': False, 'needed_evidence': ['same feature/model run under both split policies', 'local OOF and public/private leaderboard mapping', 'leakage audit'], 'owner_role': 'validation-owner', 'priority': 'medium', 'question': 'Does Subject-hole CV provide better public/private leaderboard correlation than the current canonical GroupKFold policy?'}

### semantic_lint

- Public 0.5917 is an external code-share observation, not a supported team leaderboard claim.
- Notebook Local OOF 0.514 is not comparable to team canonical local OOF until split and feature provenance are matched.
- V152 anchor OOF is a high-leakage-risk feature unless generated strictly out-of-fold and row-aligned.
- Do not let deterministic ingest mirror this packet only as a dated performance page; synthesis should create or update model, preprocessing, feature, submission, question, and performance entities.

## Metrics

raw-evidence-backed metric checks:
- `cat_only_notebook_oof_log_loss`: reported `0.528`, raw_path `metrics.json`, tolerance `0.0`
- `feature_count_after_stability_filter`: reported `1682.0`, raw_path `metrics.json`, tolerance `0.0`
- `feature_count_before_stability_filter`: reported `23177.0`, raw_path `metrics.json`, tolerance `0.0`
- `lgbm_only_notebook_oof_log_loss`: reported `0.525`, raw_path `metrics.json`, tolerance `0.0`
- `log_loss`: reported `0.5917`, raw_path `metrics.json`, tolerance `0.0`
- `notebook_local_oof_log_loss`: reported `0.514`, raw_path `metrics.json`, tolerance `0.0`
- `notebook_local_public_gap`: reported `0.075`, raw_path `metrics.json`, tolerance `0.0`
- `public_lb_log_loss`: reported `0.5917`, raw_path `metrics.json`, tolerance `0.0`
- `target_specific_notebook_oof_log_loss`: reported `0.513`, raw_path `metrics.json`, tolerance `0.0`
- `xgb_only_notebook_oof_log_loss`: reported `0.53`, raw_path `metrics.json`, tolerance `0.0`

## Claims

- tentative: DACON code share 13975 reports Public 0.5917 for an LGBM+XGB anchor blend using V152 anchor OOF features, Subject-hole CV, stability-based feature selection, and blend search. Treat as an external reference and tentative public leaderboard observation until our team verifies submission lineage and same-split reproduction.
