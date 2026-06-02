---
claim_boundary: PDF and Slack-reported v186 public leaderboard and SHAP analysis only; DACON leaderboard export, submission id, private score, submission CSV lineage, and ablation evidence are not included.
claim_status: tentative
date: "2026-05-29"
mode: structured
owner: moon-hyungdo
packet_type: performance
route: wiki/performance
title: v186 shap leaderboard analysis
---

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
