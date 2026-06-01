---
type: open-questions
title: Sleep Lifelog Open Questions
claim_status: tentative
review_required: true
source_packets:
  - 2026-05-29-sleep-lifelog-2024
  - 2026-05-29-sleep-health-hackathon-v0
related_pages:
  - wiki/datasets/sleep-lifelog-2024.md
  - wiki/benchmarks/sleep-health-hackathon-v0.md
  - wiki/features/sleep-lifelog-feature-landscape.md
  - wiki/decisions/sleep-lifelog-evaluation-protocol.md
raw_evidence:
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/manifest.yaml
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/benchmark.yaml
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/packet.md
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/manifest.yaml
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/dataset.yaml
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/packet.md
---

# Sleep Lifelog Open Questions

This page tracks unresolved questions raised by the current tentative dataset and benchmark packets. Closing any question requires raw evidence in a future packet or reviewed wiki update.

| id | status | question | why it matters | related page |
| --- | --- | --- | --- | --- |
| OQ-SL-001 | open | Has an organizer-official validation or split protocol been published? | The current `GroupKFold` policy is local sprint-1 semantics, not organizer-official validation semantics. | [Evaluation protocol](../decisions/sleep-lifelog-evaluation-protocol.md) |
| OQ-SL-002 | open | Where is the durable fold assignment artifact for the canonical 3-fold split? | Same-split comparisons need exact fold reproducibility, not just a policy description. | [Benchmark](../benchmarks/sleep-health-hackathon-v0.md) |
| OQ-SL-003 | open | Are sleep-sensor schemas available beyond the packet placeholder? | The dataset packet references sleep-sensor data but does not schema-map it. | [Dataset](../datasets/sleep-lifelog-2024.md) |
| OQ-SL-004 | open | What is the complete self-report schema, including bedtime questionnaire fields? | Self-report fields may be useful but could leak subjective Q-family labels. | [Feature landscape](../features/sleep-lifelog-feature-landscape.md) |
| OQ-SL-005 | open | What aggregation recipes should be used for nested and minute-level modality streams? | Feature packets need reproducible row-grain alignment before tabular modeling. | [Feature landscape](../features/sleep-lifelog-feature-landscape.md) |
| OQ-SL-006 | open | Which source introduced the six-target framing, and has it been reviewed against the released package? | Current packets say the released package includes seven targets including `S4`, superseding older six-target summaries. | [Dataset](../datasets/sleep-lifelog-2024.md) |
| OQ-SL-007 | open | Should future result reports require Q-family and S-family metric breakdowns? | The benchmark primary metric macro-averages all targets, but interpretation risk differs by family. | [Benchmark](../benchmarks/sleep-health-hackathon-v0.md) |
| OQ-SL-008 | open | Which DACON submission ids correspond to any public leaderboard observations? | Public leaderboard claims require submission-specific raw evidence. | [Evaluation protocol](../decisions/sleep-lifelog-evaluation-protocol.md) |
| OQ-SL-009 | open | How should Track B same-subject temporal forecasting be reported if used? | Track B may answer a useful temporal question but must not be conflated with unseen-subject generalization. | [Benchmark](../benchmarks/sleep-health-hackathon-v0.md) |

## Current contradiction watchlist

- Six-target historical summaries versus seven released target columns.
- Track A unseen-subject generalization versus Track B same-subject temporal forecasting.
- Local OOF diagnostics versus DACON public leaderboard observations.
- Placeholder modality references versus complete schema availability.
