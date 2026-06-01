---
claim_boundary: local_oof_diagnostic_only
claim_status: supported
date: "2026-06-01"
mode: structured
owner: chunryongoh
packet_type: performance
route: wiki/performance
title: LGB CB Reproduction Local OOF Diagnostic
---

# LGB/CB reproduction local OOF diagnostic

## 관측된 사실

- 이 packet은 DACON sleep-lifelog 2024 작업 중 `2026-05-26-lgb-cb-reproduction-audit-v1` 결과를 팀 위키에 올리기 위한 local OOF diagnostic이다.
- audit은 LightGBM, CatBoost, fixed 0.5 LGB/CB blend, 그리고 Wave41 maintained local OOF line과의 targetwise reblend를 비교했다.
- 최종 targetwise reblend macro log-loss는 local GroupKFold subject OOF에서 `0.6198365213240887`이다.
- 비교 기준인 Wave41 macro log-loss는 `0.6198684545582471`이며, delta는 `-0.0000319332341584`이다. Log-loss 기준으로 낮을수록 좋다.
- Standalone LightGBM은 `0.6657586405095428`, standalone CatBoost는 `0.6538557592728997`, fixed LGB/CB blend는 `0.6536839393073466`으로 Wave41 line보다 약했다.
- 최종 reblend에서 LGB/CB fixed blend는 Q2에만 `0.1` 가중치로 들어갔고, 나머지 target은 Wave41 line을 유지했다.

## 해석

핵심은 "LGB/CB가 전체적으로 가장 강하다"가 아니다. 현재 evidence로 지원되는 claim은 더 좁다. 재현된 fixed LGB/CB blend는 단독 성능으로 Wave41 line을 이기지 못했지만, Q2에서 source diversity를 아주 작게 보강해 maintained Wave41 local OOF line을 미세하게 개선했다.

## claim boundary와 위험

이 packet의 claim boundary는 `local_oof_diagnostic_only`이다. DACON public leaderboard, private leaderboard, organizer-official validation claim으로 승격하지 않는다.

leakage audit에는 다음 위험이 기록되어 있다.

- notebook reproduction 과정의 train+test transductive feature statistics
- grouped OOF 전에 적용된 global train median imputer
- subject identity 및 target encoding 계열 feature
- date/rolling alignment의 manual review 필요성

이 위험들은 local diagnostic 기록 자체를 폐기하는 근거는 아니지만, public/private leaderboard나 official validation claim으로 확장하는 것을 막는다.

## 다음 액션

Q2 중심 후속 검증을 우선한다. subject stats, target encodings, imputer scope를 fold-safe하게 ablation하고, per-target LGB/CB blend-weight search를 별도로 수행한다. SHAP/manual feature selection은 fold-scope audit 이후에 진행한다.
