---
id: 2026-06-01-dacon-leaderboard-claim-boundary
packet_type: reference
type: reference
title: DACON Leaderboard and Local OOF Claim Boundary
date: '2026-06-01'
owner: chunryongoh
status: submitted
task: dacon-sleep-health-reporting-policy
dataset:
  name: sleep-lifelog-2024
  version: released-package
  hash: null
split:
  name: local-groupkfold-subject-3fold-oof-vs-dacon-public-private
  group_key: subject_id
  fold_file: null
model:
  family: not-applicable
  weights_in_repo: false
claim_boundary: Team reporting convention for the DACON/ETRI sleep-health hackathon;
  not organizer-official split evidence.
claim_status: tentative
summary: Records how to separate local OOF evidence from DACON public/private leaderboard
  evidence when reporting sleep-health hackathon results.
raw_paths:
- notes.md
intended_wiki_targets:
- wiki/sources/2026-06-01-dacon-leaderboard-claim-boundary.md
metrics_to_verify: []
claims:
- status: tentative
  text: Local GroupKFold OOF metrics and DACON public/private leaderboard results
    should be recorded as separate evidence classes.
- status: tentative
  text: DACON public leaderboard feedback should not automatically supersede local
    validation conclusions without matching submission metadata and private leaderboard
    evidence.
publish_action: direct_commit
risk_tier: tier0-catalog
---

# DACON Leaderboard and Local OOF Claim Boundary

- packet: `2026-06-01-dacon-leaderboard-claim-boundary`
- generated_by_run: `26740055632-1`
- publish_action: `direct_commit`
- risk_tier: `tier0-catalog`
- compiled_packet: [automation/.cache/compiled/2026-06-01-dacon-leaderboard-claim-boundary.json](../../automation/.cache/compiled/2026-06-01-dacon-leaderboard-claim-boundary.json)
- owner: `chunryongoh`
- status: `submitted`
- task: `dacon-sleep-health-reporting-policy`
- dataset: `sleep-lifelog-2024` (`released-package`)
- split: `local-groupkfold-subject-3fold-oof-vs-dacon-public-private`
- model: `not-applicable`
- claim_boundary: Team reporting convention for the DACON/ETRI sleep-health hackathon; not organizer-official split evidence.
- claim_status: `tentative`
- date: `2026-06-01`
- raw_evidence:
  - `notes.md`

## Summary

Records how to separate local OOF evidence from DACON public/private leaderboard evidence when reporting sleep-health hackathon results.

## Packet Synthesis

# DACON Leaderboard Claim Boundary Packet

Use this packet to verify the end-to-end wiki automation chain with DACON/ETRI domain content.

The durable research value is the claim boundary: local validation metrics, DACON public leaderboard feedback, and DACON private leaderboard results must be recorded separately unless raw submission evidence links them.

This packet should remain tentative until organizer-official validation and leaderboard interpretation rules are confirmed.

## Claims

- tentative: Local GroupKFold OOF metrics and DACON public/private leaderboard results should be recorded as separate evidence classes.
- tentative: DACON public leaderboard feedback should not automatically supersede local validation conclusions without matching submission metadata and private leaderboard evidence.
