# Team LLM Wiki Overview

이 wiki는 team LLM experiments, sources, model notes, feature work, benchmark outcomes를 위한 유지보수형 synthesis layer입니다. Raw evidence는 `raw/` 아래에 append-only source로 남고, `wiki/`는 review-aware automation과 LLM-assisted synthesis를 거쳐 팀이 읽을 수 있는 stable memory로 정리됩니다.

## Current Sleep Lifelog Knowledge Map

2026-05-29 packet integration 이후 sleep-lifelog 관련 지식은 날짜별 packet mirror가 아니라 다음 안정 페이지로 관리합니다.

- [Sleep Lifelog 2024 Dataset](datasets/sleep-lifelog-2024.md): released package, modalities, labels, split policy, leakage risks.
- [Sleep Health Hackathon Benchmark v0](benchmarks/sleep-health-hackathon-v0.md): seven targets, `grouped_macro_logloss`, Track A/Track B, allowed claim boundaries.
- [Sleep Lifelog Feature Landscape](features/sleep-lifelog-feature-landscape.md): modality feature surface, aggregation requirements, leakage checklist.
- [Sleep Lifelog Evaluation Protocol](decisions/sleep-lifelog-evaluation-protocol.md): provisional local sprint-1 `GroupKFold` by `subject_id` 3-fold OOF decision.
- [Sleep Lifelog Open Questions](questions/sleep-lifelog-open-questions.md): official split, schema gaps, aggregation windows, DACON evidence questions.
- [Sleep Lifelog Benchmark Synthesis Report](reports/2026-05-29-sleep-lifelog-benchmark-synthesis.md): integration summary and reviewer checklist.

## Evidence and Claim Discipline

현재 sleep-lifelog pages는 dataset/benchmark definition claims만 포함합니다. 모든 raw packet claims는 `claim_status: tentative`로 유지됩니다. Numeric performance, model ranking, feature importance, leaderboard superiority는 raw metric/split evidence와 `metrics_to_verify` 검증 없이는 wiki claim으로 승격하지 않습니다.

## Review Posture

LLM-assisted synthesis output은 review-required입니다. 다음 에이전트는 [Latest Context](latest-context.md)에서 시작한 뒤 task-relevant page만 따라가면 됩니다.

## Raw Evidence

raw_evidence:
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/manifest.yaml
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/benchmark.yaml
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/packet.md
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/manifest.yaml
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/dataset.yaml
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/packet.md
