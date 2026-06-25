# Team LLM Wiki Overview

## Current Focus

The current focus is the sleep-lifelog DACON/ETRI hackathon wiki. The latest integrated wave is `2026-06-25-wave43-claude-campaign-stack-local-oof-projection`.

## Current Best Evidence

- Best supported local OOF line: [Wave43 Claude Campaign Stack](performance/wave43-claude-campaign-stack.md), calibrated macro log-loss `0.5897217743642561`.
- Validation surface: [Same Subject Hole CV](preprocessing/same-subject-hole-cv.md), local five-fold `subject_id` temporal-hole policy.
- Model shape: [Wave43 Stacked Ensemble](models/wave43-stacked-ensemble.md), targetwise candidate stack over 236-238 candidate models per target.
- Feature shape: [Wave43 Feature Families](features/wave43-feature-families.md), with S1/Withings mimic and S3/actigraphy as the clearest target insights.

## Evidence Boundary

Local OOF, notebook output, DACON public score, DACON private score, projected public, and organizer-official validation are separate surfaces. The supported wave43 claim is local OOF only. Public `0.60761` and projected public `0.59272` remain tentative until raw leaderboard/submission lineage is attached.

## Review Queue

- Close [Wave43 Open Validation Gaps](targets/wave43-open-validation-gaps.md).
- Add official leaderboard export or submission hash for the wave43 public observation.
- Attach fold assignment/row membership evidence for same-subject-hole CV.
- Continue S4-specific work; S4 remains the main unresolved target.
