---
claim_boundary: DOCX-reported feature engineering and public LB observation only; raw metric JSON, submission id, leaderboard export, private score, and same-split local OOF evidence are not included.
claim_status: tentative
date: "2026-06-01"
mode: structured
owner: cho-hyewon
packet_type: performance
route: wiki/performance
title: app context feature engineering 20260601
---

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
