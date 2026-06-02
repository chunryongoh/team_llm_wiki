---
id: 2026-06-01-app-context-feature-engineering-20260601
packet_type: performance
type: performance
title: app context feature engineering 20260601
date: '2026-06-01'
owner: cho-hyewon
status: submitted
task: source-ingest
dataset:
  name: sleep-lifelog-2024
  version: released-package
  hash: none
split:
  name: 20260526-172609-lgbcat-timesplit-public-lb-observation
  group_key: subject_id
  fold_file: null
model:
  family: lgbm-catboost-app-context-ensemble
  weights_in_repo: false
claim_boundary: DOCX-reported feature engineering and public LB observation only;
  raw metric JSON, submission id, leaderboard export, private score, and same-split
  local OOF evidence are not included.
claim_status: tentative
summary: "\uC870\uD61C\uC6D0 bundle reports LGBM+CatBoost over 1,695 features with\
  \ app-name daily/evening features improving LB 0.6218831823 to 0.6182941107, then\
  \ presleep/night/early-morning app context improving to 0.6106185586."
raw_paths:
- metrics.json
- packet.md
- performance.yaml
- source/feature-engineering-result-report-20260601.docx
- source/feature-engineering-result-report-20260601.txt
- wiki_plan.yaml
intended_wiki_targets:
- wiki/performance/2026-06-01-app-context-feature-engineering-20260601.md
metrics_to_verify:
- raw_path: metrics.json
  metric_key: baseline_public_lb_logloss
  reported_value: 0.6218831823
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: daily_evening_app_public_lb_logloss
  reported_value: 0.6182941107
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: final_public_lb_logloss
  reported_value: 0.6106185586
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: first_delta
  reported_value: -0.0035890716
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: second_delta
  reported_value: -0.0076755521
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: total_delta
  reported_value: -0.0112646237
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
claims:
- status: tentative
  text: "\uC870\uD61C\uC6D0 bundle reports LGBM+CatBoost over 1,695 features with\
    \ app-name daily/evening features improving LB 0.6218831823 to 0.6182941107, then\
    \ presleep/night/early-morning app context improving to 0.6106185586."
publish_action: bot_pr
risk_tier: tier3-performance
---

# app context feature engineering 20260601

- packet: `2026-06-01-app-context-feature-engineering-20260601`
- generated_by_run: `26806097236-1`
- publish_action: `bot_pr`
- risk_tier: `tier3-performance`
- compiled_packet: [automation/.cache/compiled/2026-06-01-app-context-feature-engineering-20260601.json](../../automation/.cache/compiled/2026-06-01-app-context-feature-engineering-20260601.json)
- owner: `cho-hyewon`
- status: `submitted`
- task: `source-ingest`
- dataset: `sleep-lifelog-2024` (`released-package`)
- split: `20260526-172609-lgbcat-timesplit-public-lb-observation`
- model: `lgbm-catboost-app-context-ensemble`
- claim_boundary: DOCX-reported feature engineering and public LB observation only; raw metric JSON, submission id, leaderboard export, private score, and same-split local OOF evidence are not included.
- claim_status: `tentative`
- date: `2026-06-01`
- raw_evidence:
  - `metrics.json`
  - `packet.md`
  - `performance.yaml`
  - `source/feature-engineering-result-report-20260601.docx`
  - `source/feature-engineering-result-report-20260601.txt`
  - `wiki_plan.yaml`
- review-required: true

## Summary

조혜원 bundle reports LGBM+CatBoost over 1,695 features with app-name daily/evening features improving LB 0.6218831823 to 0.6182941107, then presleep/night/early-morning app context improving to 0.6106185586.

## Packet Synthesis

조혜원 app-context report는 실제 앱명 기반 daily/evening feature와 취침 전·야간·새벽 app context feature가 leaderboard logloss를 두 차례 개선했다고 보고한다. 핵심 feature family는 kakao, youtube, instagram, naver, bible/religion, call/message, stimulating/reflection/task app groups, app switching, usage entropy, arousal mix 등이다. Q3는 여전히 가장 낮은 성능 target으로 남아 target-specific feature-set 정리가 필요하다.

## Wiki Integration Hints

### stable_entities

- feature:app-context-features
- performance:app-context-lgbcat-20260526
- target:q3-app-context-next-tests
- model:lgbm-catboost-app-context-ensemble
- claim:app-context-public-lb-observation

### affected_pages

- wiki/features/app-context-features.md
- wiki/performance/app-context-lgbcat-20260526.md
- wiki/questions/q3-app-context-next-tests.md
- wiki/models/lightgbm-catboost.md
- wiki/claims/current-supported-claims.md
- wiki/submissions/dacon-leaderboard-history.md

### claim_registry_updates

- tentative: app-name and app-context features are reported to improve public LB from 0.6218831823 to 0.6106185586, but leaderboard/submission provenance is missing.

### supersedes_or_conflicts

- May supersede weaker generic app-category-only feature assumptions if raw evidence confirms the staged improvements.

### open_questions

- {'close_condition': 'App context performance page can promote the claim from tentative to supported or keep it as public-LB observation.', 'id': 'app-context-raw-submission-lineage', 'merge_blocker': False, 'needed_evidence': ['submission CSV lineage', 'leaderboard export', 'local OOF metric table', 'feature list hash'], 'owner_role': 'feature-performance-owner', 'priority': 'high', 'question': 'Which submission ids and raw metric files correspond to the 0.6218831823, 0.6182941107, and 0.6106185586 app-context stages?'}

### semantic_lint

- Do not call the app-context model final best without verified leaderboard lineage.
- Keep public LB observation separate from local validation and private LB claims.
- Record Q3 as a remaining bottleneck rather than solved by app context.

## Metrics

raw-evidence-backed metric checks:
- `baseline_public_lb_logloss`: reported `0.6218831823`, raw_path `metrics.json`, tolerance `0.0`
- `daily_evening_app_public_lb_logloss`: reported `0.6182941107`, raw_path `metrics.json`, tolerance `0.0`
- `final_public_lb_logloss`: reported `0.6106185586`, raw_path `metrics.json`, tolerance `0.0`
- `first_delta`: reported `-0.0035890716`, raw_path `metrics.json`, tolerance `0.0`
- `second_delta`: reported `-0.0076755521`, raw_path `metrics.json`, tolerance `0.0`
- `total_delta`: reported `-0.0112646237`, raw_path `metrics.json`, tolerance `0.0`

## Claims

- tentative: 조혜원 bundle reports LGBM+CatBoost over 1,695 features with app-name daily/evening features improving LB 0.6218831823 to 0.6182941107, then presleep/night/early-morning app context improving to 0.6106185586.
