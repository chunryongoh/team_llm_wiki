# DACON Code Share 13975 Recheck

source_url: https://dacon.io/en/competitions/official/236690/codeshare/13975?page=1&dtype=recent
source_title: "[Public 0.5917] LGBM+XGB 앵커·Subject-hole CV·안정성 피처선별·블렌드"
source_author: "비비드백"
posted_at: "2026-05-03 13:00"
observed_at: "2026-06-12"

## LightGBM XGBoost Anchor Blend Signal

This source is about an LGBM / XGBoost anchor blend strategy: V152 anchor OOF probabilities are joined as features, and the public-score summary emphasizes LGBM+XGB 7:3 blending.

## Observed Facts

- DACON code share 13975 reports a Public LB log-loss observation of 0.5917.
- The shared strategy is a multi-target binary classification example for Q1, Q2, Q3, S1, S2, S3, and S4.
- The post describes LightGBM, XGBoost, and CatBoost examples, but the final public-score summary emphasizes an LGBM+XGB 7:3 blend.
- The post describes an anchor structure where V152 base-model OOF probabilities are joined as features.
- The validation strategy is described as Subject-hole CV.
- Calendar features, window definitions, and blend search are included.
- Some window-pair feature code is described as skeleton code before full parquet integration.
- The author comments that the anchor CSV contains out-of-fold probabilities aligned by subject_id, sleep_date, and lifelog_date.
- The author comments that the V152 base is not fully included and that identical reproduction is not guaranteed.

## Claim Boundary

This packet only records an external DACON code-share observation. It does not verify a team submission, DACON submission id, leaderboard export, submission CSV hash, private leaderboard score, or same-split local reproduction.

## Wiki Handling

- Keep Public 0.5917 tentative.
- Keep notebook local OOF summaries separate from team canonical local OOF.
- Treat V152 anchor OOF as high leakage risk until the OOF generation recipe and row alignment are provided.
- Update stable pages rather than creating another isolated packet mirror.
