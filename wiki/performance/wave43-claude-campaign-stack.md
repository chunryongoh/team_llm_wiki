# Wave43 Claude Campaign Stack

## GitHub Models Deterministic Page Scaffold

- fallback_merge_policy: deterministic_new_page_scaffold
- fallback_compact_body_applied: false
- note: GitHub Models fallback identified this page as required, but compact model prose was not applied because metric provenance must come from raw packet evidence.

## Source Packets

### 2026-06-25-wave43-claude-campaign-stack-local-oof-projection

- packet_type: `performance`
- title: Wave43 Claude campaign stack local OOF projection
- date: `2026-06-25`
- owner: `chunryongoh`
- dataset: `sleep-lifelog-2024` (`released-package`)
- split: `same-subject-hole-5fold-temporal-by-subject`
- model: `wave43-stacked-ensemble`
- claim_boundary: `local same-subject-hole OOF metrics are supported by copied metric snapshots; public leaderboard values are user/Claude-recorded observations or projections unless separately exported.`
- claim_status: `supported`
- summary: Claude 별도 작업으로 수행된 wave43 캠페인 결과를 team LLM wiki에 올리기 위한 성능 packet입니다. 최종 stack-v2는 subject-mean baseline 0.62453 대비 calibrated local OOF macro log-loss 0.58972를 기록했고, projected public은 0.59272로 추정되었습니다. 실제 확인된 public score 0.60761은 Claude 진행 로그 기반 관측치이므로 leaderboard export가 추가되기 전까지는 별도 claim boundary를 유지해야 합니다.

#### Raw-backed Metrics

- `grouped_macro_log_loss`: `0.5897217743642561` (raw_path: `metrics.json`)
- `projected_public_macro_log_loss`: `0.5927217743642561` (raw_path: `metrics.json`)
- `withings_s1_log_loss`: `0.5059412643362348` (raw_path: `metrics.json`)
- `actigraphy_s3_log_loss`: `0.5112450274138282` (raw_path: `metrics.json`)

## Review Boundary

- Local OOF, notebook output, DACON public/private leaderboard, and organizer-official validation remain separate evidence surfaces.
- Do not treat this scaffold as a claim promotion; update it with primary LLM synthesis or human review when stronger evidence is available.

## Raw Evidence

raw_evidence:
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/manifest.yaml
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/packet.md
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/performance.yaml
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/metrics.json
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/wiki_plan.yaml
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/artifact_summary.json
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/packet_entity_graph.json
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/semantic_lint.json
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/question_queue.yaml
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/source_artifacts/stack-v2-metrics.json
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/source_artifacts/stack-v2-build.py
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/source_artifacts/stack-v2-next-steps-post-cap-reset.md
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/source_artifacts/withings-metrics.json
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/source_artifacts/withings-build.py
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/source_artifacts/actigraphy-metrics.json
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/source_artifacts/actigraphy-build.py
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/source_artifacts/waso-metrics.json
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/source_artifacts/transfer-metrics.json
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/source_artifacts/deeptab-metrics.json
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/source_artifacts/seqbag-metrics.json
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/source_artifacts/sliding-window-metrics.json
- raw/users/chunryongoh/performance/2026-06-25-wave43-claude-campaign-stack-local-oof-projection/source_artifacts/submission-v2-ledger.csv
