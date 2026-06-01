---
id: 2026-06-01-full-chain-smoke-packet
packet_type: reference
type: reference
title: Full Chain Actions Smoke Packet
date: '2026-06-01'
owner: chunryongoh
status: submitted
task: full-chain-actions-smoke-test
dataset:
  name: team-llm-wiki-actions
  version: full-chain-smoke
  hash: null
split:
  name: none
  group_key: none
  fold_file: null
model:
  family: not-applicable
  weights_in_repo: false
claim_boundary: This packet only verifies the GitHub Actions automation chain from
  packet PR merge to deterministic ingest and GPT-5.5 synthesis.
claim_status: tentative
summary: Smoke-test packet used to verify the full wiki-main-ingest to wiki-llm-synthesis
  automation chain after packet lifecycle workflow changes.
raw_paths:
- notes.md
intended_wiki_targets:
- wiki/sources/2026-06-01-full-chain-smoke-packet.md
metrics_to_verify: []
claims:
- status: tentative
  text: This packet verifies whether the full GitHub Actions chain runs after a packet
    PR is merged.
publish_action: direct_commit
risk_tier: tier0-catalog
---

# Full Chain Actions Smoke Packet

- packet: `2026-06-01-full-chain-smoke-packet`
- generated_by_run: `26739124273-1`
- publish_action: `direct_commit`
- risk_tier: `tier0-catalog`
- compiled_packet: [automation/.cache/compiled/2026-06-01-full-chain-smoke-packet.json](../../automation/.cache/compiled/2026-06-01-full-chain-smoke-packet.json)
- owner: `chunryongoh`
- status: `submitted`
- task: `full-chain-actions-smoke-test`
- dataset: `team-llm-wiki-actions` (`full-chain-smoke`)
- split: `none`
- model: `not-applicable`
- claim_boundary: This packet only verifies the GitHub Actions automation chain from packet PR merge to deterministic ingest and GPT-5.5 synthesis.
- claim_status: `tentative`
- date: `2026-06-01`
- raw_evidence:
  - `notes.md`

## Summary

Smoke-test packet used to verify the full wiki-main-ingest to wiki-llm-synthesis automation chain after packet lifecycle workflow changes.

## Packet Synthesis

This packet verifies the end-to-end automation path for packet skill output.

The packet should cause the PR preview workflow to show packet compatibility, then after merge should cause deterministic ingest and GPT-5.5 synthesis automation to run according to repository policy.

This packet is not evidence for any sleep-health research claim.

## Claims

- tentative: This packet verifies whether the full GitHub Actions chain runs after a packet PR is merged.
