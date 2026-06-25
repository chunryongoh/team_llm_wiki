---
id: 2026-06-25-wave43-claude-campaign-stack-local-oof-projection
packet_type: performance
type: performance
title: Wave43 Claude campaign stack local OOF projection
date: '2026-06-25'
owner: chunryongoh
status: submitted
task: dacon-etri-sleep-health-2026
dataset:
  name: sleep-lifelog-2024
  version: released-package
  hash: null
split:
  name: same-subject-hole-5fold-temporal-by-subject
  group_key: subject_id
  fold_file: null
model:
  family: wave43-stacked-ensemble
  weights_in_repo: false
claim_boundary: local same-subject-hole OOF metrics are supported by copied metric
  snapshots; public leaderboard values are user/Claude-recorded observations or projections
  unless separately exported.
claim_status: supported
summary: "Claude \uBCC4\uB3C4 \uC791\uC5C5\uC73C\uB85C \uC218\uD589\uB41C wave43 \uCEA0\
  \uD398\uC778 \uACB0\uACFC\uB97C team LLM wiki\uC5D0 \uC62C\uB9AC\uAE30 \uC704\uD55C\
  \ \uC131\uB2A5 packet\uC785\uB2C8\uB2E4. \uCD5C\uC885 stack-v2\uB294 subject-mean\
  \ baseline 0.62453 \uB300\uBE44 calibrated local OOF macro log-loss 0.58972\uB97C\
  \ \uAE30\uB85D\uD588\uACE0, projected public\uC740 0.59272\uB85C \uCD94\uC815\uB418\
  \uC5C8\uC2B5\uB2C8\uB2E4. \uC2E4\uC81C \uD655\uC778\uB41C public score 0.60761\uC740\
  \ Claude \uC9C4\uD589 \uB85C\uADF8 \uAE30\uBC18 \uAD00\uCE21\uCE58\uC774\uBBC0\uB85C\
  \ leaderboard export\uAC00 \uCD94\uAC00\uB418\uAE30 \uC804\uAE4C\uC9C0\uB294 \uBCC4\
  \uB3C4 claim boundary\uB97C \uC720\uC9C0\uD574\uC57C \uD569\uB2C8\uB2E4."
raw_paths:
- packet.md
- performance.yaml
- metrics.json
- wiki_plan.yaml
- artifact_summary.json
- packet_entity_graph.json
- semantic_lint.json
- question_queue.yaml
- source_artifacts/stack-v2-metrics.json
- source_artifacts/stack-v2-build.py
- source_artifacts/stack-v2-next-steps-post-cap-reset.md
- source_artifacts/withings-metrics.json
- source_artifacts/withings-build.py
- source_artifacts/actigraphy-metrics.json
- source_artifacts/actigraphy-build.py
- source_artifacts/waso-metrics.json
- source_artifacts/transfer-metrics.json
- source_artifacts/deeptab-metrics.json
- source_artifacts/seqbag-metrics.json
- source_artifacts/sliding-window-metrics.json
- source_artifacts/submission-v2-ledger.csv
intended_wiki_targets:
- wiki/performance/wave43-claude-campaign-stack.md
- wiki/performance/dacon-leaderboard-history.md
metrics_to_verify:
- raw_path: metrics.json
  metric_key: grouped_macro_log_loss
  reported_value: 0.5897217743642561
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: projected_public_macro_log_loss
  reported_value: 0.5927217743642561
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: withings_s1_log_loss
  reported_value: 0.5059412643362348
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
- raw_path: metrics.json
  metric_key: actigraphy_s3_log_loss
  reported_value: 0.5112450274138282
  tolerance: 0.0
  name: null
  key: null
  expected: null
  actual: null
claims: []
publish_action: bot_pr
risk_tier: tier4-governance
---

# Wave43 Claude campaign stack local OOF projection

- packet: `2026-06-25-wave43-claude-campaign-stack-local-oof-projection`
- generated_by_run: `28153696483-1`
- publish_action: `bot_pr`
- risk_tier: `tier4-governance`
- compiled_packet: [automation/.cache/compiled/2026-06-25-wave43-claude-campaign-stack-local-oof-projection.json](../../automation/.cache/compiled/2026-06-25-wave43-claude-campaign-stack-local-oof-projection.json)
- owner: `chunryongoh`
- status: `submitted`
- task: `dacon-etri-sleep-health-2026`
- dataset: `sleep-lifelog-2024` (`released-package`)
- split: `same-subject-hole-5fold-temporal-by-subject`
- model: `wave43-stacked-ensemble`
- claim_boundary: local same-subject-hole OOF metrics are supported by copied metric snapshots; public leaderboard values are user/Claude-recorded observations or projections unless separately exported.
- claim_status: `supported`
- date: `2026-06-25`
- raw_evidence:
  - `packet.md`
  - `performance.yaml`
  - `metrics.json`
  - `wiki_plan.yaml`
  - `artifact_summary.json`
  - `packet_entity_graph.json`
  - `semantic_lint.json`
  - `question_queue.yaml`
  - `source_artifacts/stack-v2-metrics.json`
  - `source_artifacts/stack-v2-build.py`
  - `source_artifacts/stack-v2-next-steps-post-cap-reset.md`
  - `source_artifacts/withings-metrics.json`
  - `source_artifacts/withings-build.py`
  - `source_artifacts/actigraphy-metrics.json`
  - `source_artifacts/actigraphy-build.py`
  - `source_artifacts/waso-metrics.json`
  - `source_artifacts/transfer-metrics.json`
  - `source_artifacts/deeptab-metrics.json`
  - `source_artifacts/seqbag-metrics.json`
  - `source_artifacts/sliding-window-metrics.json`
  - `source_artifacts/submission-v2-ledger.csv`
- review-required: true

## Summary

Claude 별도 작업으로 수행된 wave43 캠페인 결과를 team LLM wiki에 올리기 위한 성능 packet입니다. 최종 stack-v2는 subject-mean baseline 0.62453 대비 calibrated local OOF macro log-loss 0.58972를 기록했고, projected public은 0.59272로 추정되었습니다. 실제 확인된 public score 0.60761은 Claude 진행 로그 기반 관측치이므로 leaderboard export가 추가되기 전까지는 별도 claim boundary를 유지해야 합니다.

## Packet Synthesis

# Wave43 Claude Campaign Stack Local OOF Projection

## 요약

현재 디렉토리에서 Claude가 별도로 진행한 wave43 캠페인 결과를 team LLM wiki에 연결하기 위한 raw packet이다.
핵심 결론은 `raw/results/2026-06-24-wave43-stack-v2/metrics.json` 기준 최종 `stack-v2`가
same-subject-hole local OOF에서 calibrated macro log-loss `0.5897217743642561`을 기록했다는 점이다.
이 값은 subject-mean baseline `0.6245305092520156` 대비 `-0.0348087348877595` 개선이다.

public leaderboard에 대해서는 claim boundary를 분리한다. Claude 진행 로그에는 public `0.60761`까지의 개선이 기록되어 있고,
최종 calibrated stack의 projected public은 `0.5927217743642561`로 계산되었지만, 이 packet에는 official leaderboard export가 없다.
따라서 wiki에서는 local OOF claim과 public observation/projection claim을 같은 강도로 취급하면 안 된다.

## Claude 작업 흐름

Claude는 2026-06-23부터 2026-06-25까지 wave43 캠페인을 누적 진행했다.
초기에는 targetwise LightGBM/CatBoost baseline과 subject prior, spectral/circadian 계열을 확인했고,
이후 sliding-window, sequence/SSL, deep-tabular, XGB bag, Withings-mat mimic, actigraphy scorer, transfer/domain-shift 계열을 순차적으로 탐색했다.

중요한 전환점은 feature family가 단일 대형 feature set이 아니라 target별 약점을 보완하는 여러 후보 모델군으로 확장된 것이다.
최종 `stack-v2`는 target별 236-238개 후보를 모아 nested same-subject-hole stack과 target별 calibration을 적용했다.

## Preprocessing / Validation

- split: `same-subject-hole-5fold-temporal-by-subject`
- 원칙: 같은 subject의 temporal hole을 fold별로 비워 local OOF를 만들고, test/full-train에서는 subject prior를 fold-safe 방식으로 사용한다.
- leakage boundary: pseudo-labeling은 사용하지 않았고, public/private leaderboard claim과 local OOF claim은 분리한다.
- 불확실성: organizer-official split과 private leaderboard semantics가 공개되면 이 split 정책은 재검토되어야 한다.

## Feature Families

- sliding-window/intraday: 일중 시간대별 aggregation과 window feature로 Q2/Q3 신호를 처음 유의미하게 끌어냈다.
- Withings-mat mimic: 충전/집-정박 상태를 이용해 침대 체류 또는 수면 환경을 간접 추정했고 S1에서 강했다.
- actigraphy scorer: Cole-Kripke/Sadeh 계열 fixed coefficient를 사용해 S3를 크게 개선했다.
- WASO/sleep physiology: S2/S4 보완을 노렸지만 최종 stack을 직접 이기지는 못했다.
- SSL/contrastive/deep-tabular/sequence: standalone로 최종 stack을 대체하지는 못했으나 candidate pool 확장에 쓰였다.
- transfer/domain shift: SLEEPACCEL external LOSO AUC는 높았지만 ETRI final target log-loss 개선으로 직접 연결되지는 않았다.

## Model / Stacking

최종 모델은 단일 모델이 아니라 target별 후보 모델 pool 위의 stacked ensemble이다.
후보에는 LightGBM/CatBoost/XGBoost, subject prior 변형, temporal/window feature 모델, sequence/SSL/deep-tabular 계열, domain-specific sleep feature 모델이 포함된다.
최종 선택은 nested same-subject-hole OOF와 target별 calibration으로 이루어졌다.

Calibration은 Q1/Q2/S3/S4에 temperature, S2에 platt, Q3/S1에는 none으로 기록되어 있다.

## Performance

| Surface | Metric |
| --- | ---: |
| Subject-mean baseline macro | 0.6245305092520156 |
| Equal-all baseline macro | 0.6157419292915838 |
| Stack nested macro | 0.5946367652711365 |
| Calibrated stack macro | 0.5897217743642561 |
| Projected public macro | 0.5927217743642561 |
| Best observed public in Claude log | 0.60761 |

Target-level calibrated log-loss:

| Target | Log-loss | Calibration |
| --- | ---: | --- |
| Q1 | 0.6450606619738299 | temp |
| Q2 | 0.6455155286285766 | temp |
| Q3 | 0.650460985046031 | none |
| S1 | 0.5084141950084338 | none |
| S2 | 0.5561343457335379 | platt |
| S3 | 0.5168327857279124 | temp |
| S4 | 0.6056339184314705 | temp |

## 해석

`0.57`대가 불가능하다는 이전 판단은 아직 완전히 반증된 것은 아니지만, Q-family 신호가 거의 없다는 식의 강한 판단은 superseded로 봐야 한다.
sliding-window와 stack campaign이 Q2/Q3 신호를 일부 끌어냈고, S1/S3는 각각 Withings-mat mimic과 actigraphy scorer가 분명한 후보 방향을 보여줬다.

반면 S4는 여전히 가장 어려운 축이다. WASO와 transfer 방향은 의미 있는 domain hypothesis이지만 final stack을 안정적으로 넘는 성능 증거는 아직 없다.

## Wiki 업데이트 의도

이 packet은 wiki에 raw packet mirror 하나를 만드는 것이 목적이 아니다.
ingest/synthesis는 다음 stable entity들을 갱신해야 한다.

- wave43 campaign performance summary
- same-subject-hole validation policy
- leaderboard claim boundary
- wave43 feature family map
- wave43 stacked ensemble model page
- S1/S3 target insight pages
- Q3/S4 bottleneck pages
- open validation gaps and next actions

## Evidence Gaps

- `0.60761` public score에 대한 official leaderboard export 또는 submission hash가 필요하다.
- `0.59272`는 projected public이며 official public/private result가 아니다.
- OOF prediction arrays와 final submission CSV는 로컬 ETRI raw tree에 남아 있고 packet에는 metric/code snapshot만 복사했다.
- confusion matrix, AUROC, AUPRC는 final stack evidence로 정리되어 있지 않다.
- batch correction/domain adaptation 계열은 partial run이 많아 final claim으로 승격하지 않는다.

## Metrics

raw-evidence-backed metric checks:
- `grouped_macro_log_loss`: reported `0.5897217743642561`, raw_path `metrics.json`, tolerance `0.0`
- `projected_public_macro_log_loss`: reported `0.5927217743642561`, raw_path `metrics.json`, tolerance `0.0`
- `withings_s1_log_loss`: reported `0.5059412643362348`, raw_path `metrics.json`, tolerance `0.0`
- `actigraphy_s3_log_loss`: reported `0.5112450274138282`, raw_path `metrics.json`, tolerance `0.0`
