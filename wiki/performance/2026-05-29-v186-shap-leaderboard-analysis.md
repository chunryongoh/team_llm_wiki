---
id: 2026-05-29-v186-shap-leaderboard-analysis
packet_type: performance
type: performance
title: v186 shap leaderboard analysis
date: '2026-05-29'
owner: moon-hyungdo
status: submitted
task: source-ingest
dataset:
  name: sleep-lifelog-2024
  version: released-package
  hash: none
split:
  name: v186-report-oof-plus-public-lb-observation
  group_key: subject_id
  fold_file: null
model:
  family: v186-target-specific-lgbm-catboost-blend
  weights_in_repo: false
claim_boundary: PDF and Slack-reported v186 public leaderboard and SHAP analysis only;
  DACON leaderboard export, submission id, private score, submission CSV lineage,
  and ablation evidence are not included.
claim_status: tentative
summary: v186 is reported as the strongest submitted line with public LB 0.5922831771,
  mean OOF logloss 0.6167, S1 as best target, S4 as worst target, and SHAP-driven
  feature interpretation by Q/S target family.
raw_paths:
- metrics.json
- packet.md
- performance.yaml
- source/etri-2026-v186-shap-analysis.pdf
- source/etri-2026-v186-shap-analysis.txt
- source/v186-top10-feature-meaning-ko.md
- wiki_plan.yaml
intended_wiki_targets:
- wiki/performance/2026-05-29-v186-shap-leaderboard-analysis.md
metrics_to_verify:
- raw_path: metrics.json
  metric_key: public_lb_logloss
  reported_value: 0.5922831771
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: v186_mean_oof_logloss
  reported_value: 0.6167
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: q1_oof_logloss
  reported_value: 0.6406
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: q2_oof_logloss
  reported_value: 0.6466
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: q3_oof_logloss
  reported_value: 0.6408
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: s1_oof_logloss
  reported_value: 0.5597
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: s2_oof_logloss
  reported_value: 0.6005
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: s3_oof_logloss
  reported_value: 0.5629
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: s4_oof_logloss
  reported_value: 0.666
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
claims:
- status: tentative
  text: v186 is reported as the strongest submitted line with public LB 0.5922831771,
    mean OOF logloss 0.6167, S1 as best target, S4 as worst target, and SHAP-driven
    feature interpretation by Q/S target family.
publish_action: bot_pr
risk_tier: tier3-performance
---

# v186 shap leaderboard analysis

- packet: `2026-05-29-v186-shap-leaderboard-analysis`
- generated_by_run: `26806097236-1`
- publish_action: `bot_pr`
- risk_tier: `tier3-performance`
- compiled_packet: [automation/.cache/compiled/2026-05-29-v186-shap-leaderboard-analysis.json](../../automation/.cache/compiled/2026-05-29-v186-shap-leaderboard-analysis.json)
- owner: `moon-hyungdo`
- status: `submitted`
- task: `source-ingest`
- dataset: `sleep-lifelog-2024` (`released-package`)
- split: `v186-report-oof-plus-public-lb-observation`
- model: `v186-target-specific-lgbm-catboost-blend`
- claim_boundary: PDF and Slack-reported v186 public leaderboard and SHAP analysis only; DACON leaderboard export, submission id, private score, submission CSV lineage, and ablation evidence are not included.
- claim_status: `tentative`
- date: `2026-05-29`
- raw_evidence:
  - `metrics.json`
  - `packet.md`
  - `performance.yaml`
  - `source/etri-2026-v186-shap-analysis.pdf`
  - `source/etri-2026-v186-shap-analysis.txt`
  - `source/v186-top10-feature-meaning-ko.md`
  - `wiki_plan.yaml`
- review-required: true

## Summary

v186 is reported as the strongest submitted line with public LB 0.5922831771, mean OOF logloss 0.6167, S1 as best target, S4 as worst target, and SHAP-driven feature interpretation by Q/S target family.

## Packet Synthesis

문형도 v186 bundle은 public LB 0.5922831771과 v186 SHAP 해석을 제공한다. Q-family는 sensor-derived daily routine proxy, S1/S2는 transition weighted refit, S3/S4는 sleep-episode/GPS stillness 계열로 해석된다. 이 packet은 SHAP/보고서 기반 관찰이며 leaderboard provenance와 ablation raw evidence는 없다.

## Wiki Integration Hints

### stable_entities

- submission:v186-public-lb-note
- model:v186-target-specific-lgbm-catboost-blend
- feature:v186-shap-feature-importance
- target:q2-fatigue-bottleneck
- target:s4-waso-disturbance

### affected_pages

- wiki/submissions/dacon-leaderboard-history.md
- wiki/claims/current-supported-claims.md
- wiki/models/v186-target-specific-lgbm-catboost.md
- wiki/features/v186-shap-feature-importance.md
- wiki/targets/s4-waso-disturbance.md

### claim_registry_updates

- tentative: v186 public LB 0.5922831771 is a user/PDF-reported public score observation, not a verified DACON leaderboard claim.
- tentative: SHAP identifies Q/S target-specific feature drivers, but this is feature-importance evidence, not ablation evidence.

### supersedes_or_conflicts

- Conflicts with any current-best statement that omits evidence surface; v186 may be public-LB best by report, while LGB/CB local OOF diagnostic remains a separate local evidence surface.

### open_questions

- {'close_condition': 'Leaderboard history page records v186 as verified_public_lb or downgrades it permanently.', 'id': 'v186-leaderboard-provenance', 'merge_blocker': False, 'needed_evidence': ['DACON leaderboard export', 'submission CSV', 'submission timestamp', 'local run mapping'], 'owner_role': 'submission-owner', 'priority': 'high', 'question': 'Can v186 public LB 0.5922831771 be verified with DACON submission id, leaderboard export, and submission CSV lineage?'}

### semantic_lint

- Keep v186 public LB observation separate from local OOF diagnostics.
- Do not treat SHAP feature importance as causal feature proof.
- Do not merge v186 target-specific model memory with Section07 or Q2-only LGB/CB reblend without explicit lineage.

## Metrics

raw-evidence-backed metric checks:
- `public_lb_logloss`: reported `0.5922831771`, raw_path `metrics.json`, tolerance `0.0`
- `v186_mean_oof_logloss`: reported `0.6167`, raw_path `metrics.json`, tolerance `0.0`
- `q1_oof_logloss`: reported `0.6406`, raw_path `metrics.json`, tolerance `0.0`
- `q2_oof_logloss`: reported `0.6466`, raw_path `metrics.json`, tolerance `0.0`
- `q3_oof_logloss`: reported `0.6408`, raw_path `metrics.json`, tolerance `0.0`
- `s1_oof_logloss`: reported `0.5597`, raw_path `metrics.json`, tolerance `0.0`
- `s2_oof_logloss`: reported `0.6005`, raw_path `metrics.json`, tolerance `0.0`
- `s3_oof_logloss`: reported `0.5629`, raw_path `metrics.json`, tolerance `0.0`
- `s4_oof_logloss`: reported `0.666`, raw_path `metrics.json`, tolerance `0.0`

## Claims

- tentative: v186 is reported as the strongest submitted line with public LB 0.5922831771, mean OOF logloss 0.6167, S1 as best target, S4 as worst target, and SHAP-driven feature interpretation by Q/S target family.
