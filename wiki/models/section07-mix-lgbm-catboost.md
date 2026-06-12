---
id: section07-mix-lgbm-catboost
type: model
title: Section07 Mix LGBM CatBoost
status: active-review-required
date: 2026-06-02
dataset: sleep-lifelog-2024
claim_status: tentative
summary: Section07 notebook/working notes의 model path는 per-label LightGBM/CatBoost probability mean blend와 seed ensemble candidate로 기록되지만 재실행 evidence는 없다.
raw_evidence:
- raw/users/hyeonseokrock/experiments/2026-06-01-lifelog-section07-working-notes/source/03_model.md
- raw/users/hyeonseokrock/experiments/2026-06-01-lifelog-section07-notebook-overview/source/notebook-outline.md
- raw/users/hyeonseokrock/experiments/2026-06-01-lifelog-section07-notebook-overview/source/notebook-output-summary.md
---

# Section07 Mix LGBM CatBoost

이 페이지는 Section07 model architecture를 실험 page에서 분리해 관리한다.

## Documented Structure

- family: `mix_lgbm_catboost`
- per-label training: LightGBM and CatBoost packs
- internal blend: `probability_mean`
- candidate blend: `logit_mean`
- seed offsets: `0`, `20000`, `40000`
- n_trials in notebook output: `50`
- labels: `Q1`, `Q2`, `Q3`, `S1`, `S2`, `S3`, `S4`

## Current Boundary

이 모델 page는 model structure memory다. 성능 claim은 [DACON Leaderboard History](../performance/dacon-leaderboard-history.md) 또는 verified performance packet이 들어오기 전까지 tentative로 유지한다.

## Excluded Paths

Working notes는 XGBoost, CNN, LSTM, attention models를 Section07 current optimization path 밖으로 기록한다. 후속 실험으로 재도입하면 별도 model page 또는 decision update가 필요하다.

## Next Evidence Needed

- raw training config
- per-label metric JSON
- fold or validation protocol
- submission lineage if leaderboard claim is desired
- forbidden input audit and feature hash evidence
