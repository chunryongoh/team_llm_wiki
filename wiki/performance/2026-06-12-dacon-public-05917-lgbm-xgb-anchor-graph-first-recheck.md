---
id: 2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck
packet_type: performance
type: performance
title: dacon public 05917 lgbm xgb anchor graph first recheck
date: '2026-06-12'
owner: dacon-community
status: submitted
task: source-ingest
dataset:
  name: sleep-lifelog-2024
  version: dacon-competition-package
  hash: not-provided
split:
  name: subject-hole-cv-5fold-reference
  group_key: subject_id
  fold_file: null
model:
  family: lgbm-xgb-anchor-blend
  weights_in_repo: false
claim_boundary: External DACON code-share Public 0.5917 observation only; not team
  verified; no DACON submission id, leaderboard export, submission CSV hash, private
  leaderboard result, or same-run local reproduction is present.
claim_status: tentative
summary: DACON code share 13975 reports Public 0.5917 for an LGBM+XGB anchor blend
  using V152 OOF anchor probabilities, Subject-hole CV, stability-filtered features,
  and blend search. This packet rechecks the latest graph-first packet flow and keeps
  the observation tentative until submission lineage is verified.
raw_paths:
- artifact_summary.json
- dacon-public-05917-lgbm-xgb-anchor-subject-hole.ipynb
- metrics.json
- packet.md
- packet_entity_graph.json
- performance.yaml
- question_queue.yaml
- scan-metrics.csv
- semantic_lint.json
- dacon-codeshare-13975.md
- wiki_plan.yaml
intended_wiki_targets:
- wiki/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck.md
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
    using V152 OOF anchor probabilities, Subject-hole CV, stability-filtered features,
    and blend search. This packet rechecks the latest graph-first packet flow and
    keeps the observation tentative until submission lineage is verified.
publish_action: bot_pr
risk_tier: tier3-performance
---

# dacon public 05917 lgbm xgb anchor graph first recheck

- packet: `2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck`
- generated_by_run: `27396372321-1`
- publish_action: `bot_pr`
- risk_tier: `tier3-performance`
- compiled_packet: [automation/.cache/compiled/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck.json](../../automation/.cache/compiled/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck.json)
- owner: `dacon-community`
- status: `submitted`
- task: `source-ingest`
- dataset: `sleep-lifelog-2024` (`dacon-competition-package`)
- split: `subject-hole-cv-5fold-reference`
- model: `lgbm-xgb-anchor-blend`
- claim_boundary: External DACON code-share Public 0.5917 observation only; not team verified; no DACON submission id, leaderboard export, submission CSV hash, private leaderboard result, or same-run local reproduction is present.
- claim_status: `tentative`
- date: `2026-06-12`
- raw_evidence:
  - `artifact_summary.json`
  - `dacon-public-05917-lgbm-xgb-anchor-subject-hole.ipynb`
  - `metrics.json`
  - `packet.md`
  - `packet_entity_graph.json`
  - `performance.yaml`
  - `question_queue.yaml`
  - `scan-metrics.csv`
  - `semantic_lint.json`
  - `dacon-codeshare-13975.md`
  - `wiki_plan.yaml`
- review-required: true

## Summary

DACON code share 13975 reports Public 0.5917 for an LGBM+XGB anchor blend using V152 OOF anchor probabilities, Subject-hole CV, stability-filtered features, and blend search. This packet rechecks the latest graph-first packet flow and keeps the observation tentative until submission lineage is verified.

## Packet Synthesis

# DACON Public 0.5917 Graph-First Recheck

This packet packages DACON code share 13975 as an external reference for the team wiki. The useful durable knowledge is the combination of LGBM+XGB blending, V152 anchor OOF probability features, Subject-hole CV, and stability-filtered feature selection.

## Claim Boundary

Public 0.5917 is an external code-share observation only. It is not a team-verified DACON submission result, and it must not be merged with team canonical local OOF or private leaderboard evidence.

## Evidence Included

- DACON source note captured from the public code-share page.
- Attached notebook from the shared example.
- Metric CSV used by the graph scanner.
- Graph-first sidecars: artifact summary, entity graph, semantic lint, and question queue.

## Interpretation

The packet should update existing stable entities rather than create a new standalone research direction. The main reusable concepts are Subject-hole CV, anchor OOF lineage risk, stability-filtered feature selection, and public leaderboard provenance handling.

## Wiki Integration Hints

### stable_entities

- {'action': 'update', 'id': 'model:lgbm-xgb-anchor-subject-hole-blend', 'kind': 'model', 'page': 'wiki/models/lgbm-xgb-anchor-subject-hole-blend.md', 'page_role': 'leaf', 'promotion_reason': ['external public LB reference', 'reusable anchor OOF and blend pattern', 'needs independent claim boundary']}
- {'action': 'update', 'id': 'preprocessing:subject-hole-cv', 'kind': 'preprocessing', 'page': 'wiki/preprocessing/subject-hole-cv.md', 'page_role': 'leaf', 'promotion_reason': ['validation strategy differs from canonical GroupKFold', 'high leakage-risk concept requiring separate policy']}
- {'action': 'update', 'id': 'feature:stability-filtered-feature-selection', 'kind': 'feature', 'page': 'wiki/features/stability-filtered-feature-selection.md', 'page_role': 'leaf', 'promotion_reason': ['feature selection method is reusable', 'requires ablation before adoption']}
- {'action': 'record_observation', 'id': 'submission:dacon-public-05917-external-codeshare', 'kind': 'submission', 'page': 'wiki/submissions/dacon-leaderboard-history.md', 'page_role': 'registry', 'promotion_reason': ['public LB observation must stay separated from team verified leaderboard claims']}

### affected_pages

- {'expected_change': 'Record graph-first recheck as another provenance-limited external observation, not a verified submission.', 'path': 'wiki/submissions/dacon-leaderboard-history.md', 'role': 'registry'}
- {'expected_change': 'Route stability filtering and anchor OOF feature risk to existing leaf pages.', 'path': 'wiki/features/sleep-lifelog-feature-landscape.md', 'role': 'hub'}
- {'expected_change': 'Keep Subject-hole CV separate from canonical local validation surfaces.', 'path': 'wiki/preprocessing/canonical-split-and-leakage-policy.md', 'role': 'registry'}
- {'expected_change': 'Keep closeable lineage and V152 anchor reproduction questions active.', 'path': 'wiki/questions/sleep-lifelog-open-questions.md', 'role': 'hub'}
- {'expected_change': 'Update existing source-specific review page instead of creating a duplicate conclusion.', 'path': 'wiki/performance/dacon-public-05917-lgbm-xgb-anchor-reference.md', 'role': 'packet_review'}

### claim_registry_updates

- tentative: external DACON code share reports Public 0.5917 for LGBM+XGB anchor blend; not team verified and not promoted to supported leaderboard claim.
- tentative: notebook reports Local OOF 0.514; not comparable to team canonical OOF until split and feature provenance are matched.

### supersedes_or_conflicts

- Does not supersede team v186/v189/Section07 public notes because submission lineage and evaluation surfaces differ.
- Does not replace team LGBM+CatBoost direction; this external reference emphasizes LGBM+XGB blend and anchor OOF structure.

### open_questions

- {'close_condition': 'Evidence proves or rejects that the 0.5917 observation is reproducible and traceable.', 'id': 'dacon-public-05917-submission-lineage', 'merge_blocker': False, 'needed_evidence': ['DACON submission id', 'leaderboard export or screenshot', 'submission CSV hash or file lineage'], 'owner_role': 'validation-owner', 'priority': 'high', 'question': 'Can the external 0.5917 public score be linked to a DACON submission id, leaderboard export, and exact submission CSV lineage?'}
- {'close_condition': 'Team can reproduce anchor OOF or documents why it is not portable.', 'id': 'v152-anchor-oof-reproduction', 'merge_blocker': False, 'needed_evidence': ['V152 training recipe', 'OOF CSV with subject_id, sleep_date, lifelog_date and Q/S probability columns', 'fold assignment and leakage audit'], 'owner_role': 'model-owner', 'priority': 'high', 'question': "Can the V152 anchor OOF probabilities be reproduced without leakage using the team's canonical row identity?"}

### semantic_lint

- Public 0.5917 remains tentative because submission lineage is absent.
- Local OOF, notebook output, public leaderboard observation, private leaderboard, and organizer-official validation must remain separate evidence surfaces.
- The synthesis bot should update stable model/preprocessing/feature/submission/question pages rather than treat this as an isolated packet mirror.

## Metrics

raw-evidence-backed metric checks:
- `cat_only_notebook_oof_log_loss`: reported `0.528`, raw_path `metrics.json`, tolerance `0.0`
- `feature_count_after_stability_filter`: reported `1682.0`, raw_path `metrics.json`, tolerance `0.0`
- `feature_count_before_stability_filter`: reported `23177.0`, raw_path `metrics.json`, tolerance `0.0`
- `lgbm_only_notebook_oof_log_loss`: reported `0.525`, raw_path `metrics.json`, tolerance `0.0`
- `log_loss`: reported `0.5917`, raw_path `metrics.json`, tolerance `0.0`
- `notebook_local_oof_log_loss`: reported `0.514`, raw_path `metrics.json`, tolerance `0.0`
- `public_lb_log_loss`: reported `0.5917`, raw_path `metrics.json`, tolerance `0.0`
- `target_specific_notebook_oof_log_loss`: reported `0.513`, raw_path `metrics.json`, tolerance `0.0`
- `xgb_only_notebook_oof_log_loss`: reported `0.53`, raw_path `metrics.json`, tolerance `0.0`

## Claims

- tentative: DACON code share 13975 reports Public 0.5917 for an LGBM+XGB anchor blend using V152 OOF anchor probabilities, Subject-hole CV, stability-filtered features, and blend search. This packet rechecks the latest graph-first packet flow and keeps the observation tentative until submission lineage is verified.
