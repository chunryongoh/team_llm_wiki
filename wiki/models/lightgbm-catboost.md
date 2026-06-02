---
id: lightgbm-catboost
type: model
title: LightGBM CatBoost
status: active
date: 2026-06-02
dataset: sleep-lifelog-2024
claim_status: supported
summary: LightGBM + CatBoost는 현재 standalone winner가 아니라 Q2 targetwise reblend source-diversity로 지원된다.
raw_evidence:
- raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/metrics.json
- raw/users/chunryongoh/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic/blend_weights.json
---

# LightGBM CatBoost

이 페이지는 sleep-lifelog 작업에서 LightGBM + CatBoost family의 지원되는 claim과 제한을 관리한다.

## Current Boundary

- supported boundary: `local_oof_diagnostic_only`
- supported role: Q2 source-diversity component in targetwise reblend
- unsupported wording: "LGB/CB is globally best standalone model"

## Current Evidence

- standalone LightGBM macro log-loss: `0.6657586405095428`
- standalone CatBoost macro log-loss: `0.6538557592728997`
- fixed LGB/CB blend macro log-loss: `0.6536839393073466`
- final targetwise reblend macro log-loss: `0.6198365213240887`
- Wave41 baseline macro log-loss: `0.6198684545582471`
- selected use: fixed LGB/CB blend weight `0.1` for Q2 only

## Interpretation

LightGBM + CatBoost는 current raw evidence에서 standalone best가 아니다. 의미 있는 기록은 Q2 targetwise reblend에 작은 source-diversity signal을 제공했다는 점이다.

## Required Follow-Up

- Q2 weight selection을 nested 또는 fold-safe procedure로 재검증한다.
- same-split, same-feature, same-baseline 조건에서 standalone LGB/CB와 current line을 다시 비교한다.
- leaderboard claim은 [DACON Leaderboard History](../submissions/dacon-leaderboard-history.md) evidence 없이는 만들지 않는다.
