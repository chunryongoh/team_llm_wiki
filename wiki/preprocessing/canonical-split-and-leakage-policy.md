---
id: canonical-split-and-leakage-policy
type: preprocessing-policy
title: Canonical Split And Leakage Policy
status: active
date: 2026-06-02
dataset: sleep-lifelog-2024
benchmark: sleep-health-hackathon-v0
summary: split, fold count, fit scope, feature-generation cutoff, leakage risks를 성능 claim 옆에 붙이기 위한 canonical policy.
raw_evidence:
- raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/leakage_audit.json
- raw/users/hyeonseokrock/experiments/2026-06-01-lifelog-section07-working-notes/source/01_preprocessing.md
- raw/users/hyeonseokrock/experiments/2026-06-01-lifelog-section07-notebook-overview/source/notebook-outline.md
---

# Canonical Split And Leakage Policy

이 페이지는 sleep-lifelog 작업에서 성능 claim이 어떤 split과 leakage boundary 위에 있는지 관리한다.

## Known Split Surfaces

| split surface | fold count | group key | evidence class | note |
| --- | ---: | --- | --- | --- |
| `groupkfold-subject-3fold-oof` | 3 | `subject_id` | local canonical sprint-1 definition | dataset/benchmark definition에 기록된 초기 기준 |
| `local-groupkfold-subject-5fold-oof` | 5 | `subject_id` | local OOF diagnostic | LGB/CB reproduction local OOF page의 기준 |
| `local-working-notes-mixed-validation-protocols` | mixed | `subject_id` | working notes only | section07 notes에 기록된 validation probes |
| `existing-notebook-local-validation-probes` | mixed | `subject_id` | notebook-output observation only | section07 notebook overview 기준 |

서로 다른 split surface는 같은 split claim으로 비교하지 않는다.

## Fit Scope Rules

- imputation, normalization, target encoding은 fold-safe claim을 하려면 train-fold-only fit이어야 한다.
- grouped OOF 전에 global train median imputer를 fit하면 fold-safe supported claim으로 승격하지 않는다.
- subject target encoding feature는 train-fold mean policy가 raw evidence로 없으면 leakage risk로 유지한다.
- train/test transductive feature statistics는 leaderboard 또는 official validation claim으로 승격할 때 blocker다.

## Feature Cutoff Rules

- `sleep_date`와 `lifelog_date` anchor를 구분한다.
- target 이후 정보가 window aggregation에 들어가면 performance claim을 지원하지 않는다.
- rolling/date feature는 fold boundary와 target boundary audit가 필요하다.

## Current Known Risks

- LGB/CB reproduction: train/test transductive statistics, global imputer, subject encoding, date/rolling manual review risk
- section07: allowed input audit file and feature-policy hashes are referenced but not yet packet-local evidence
- notebook-output summary: raw fold files and rerun logs are missing

## Promotion Gate

성능 claim을 `supported`로 승격하려면 split surface, fit scope, baseline, raw metric, leakage audit가 같은 packet 또는 명시된 provenance chain으로 연결되어야 한다.
