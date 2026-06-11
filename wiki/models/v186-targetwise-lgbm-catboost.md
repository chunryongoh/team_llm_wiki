---
id: v186-targetwise-lgbm-catboost
type: model-entity
page_role: leaf
claim_status: tentative
status: active
title: v186 Targetwise LGBM CatBoost
raw_evidence:
- raw/users/moon-hyungdo/performance/2026-05-29-v186-shap-leaderboard-analysis/manifest.yaml
- raw/users/moon-hyungdo/performance/2026-05-29-v186-shap-leaderboard-analysis/packet.md
- raw/users/moon-hyungdo/performance/2026-05-29-v186-shap-leaderboard-analysis/performance.yaml
- raw/users/moon-hyungdo/performance/2026-05-29-v186-shap-leaderboard-analysis/metrics.json
---

# v186 Targetwise LGBM CatBoost

v186 is the currently important targetwise LightGBM/CatBoost candidate associated with reported public LB `0.5922831771` and SHAP analysis. The score is not yet a verified leaderboard claim because submission id, leaderboard export, and CSV lineage are missing.

## Current interpretation

- Treat v186 as a high-value candidate and SHAP interpretation source.
- Do not state that v186 is the verified best model.
- SHAP target drivers are feature-importance evidence, not causal feature proof.
- Q targets appear tied to routine proxies; S targets appear tied to sleep episode or transition proxies.

## Adoption rule

Use v186 insights for hypothesis generation and target-specific ablation design. Promote score claims only after leaderboard provenance and run mapping are supplied.

## Required evidence

- DACON submission id and leaderboard export
- submission CSV lineage
- local run config and feature hash
- target-level metrics and SHAP artifact mapping

## Related pages

- [DACON Leaderboard History](../submissions/dacon-leaderboard-history.md)
- [Current Supported Claims](../claims/current-supported-claims.md)
- [Sleep Lifelog Feature Landscape](../features/sleep-lifelog-feature-landscape.md)
