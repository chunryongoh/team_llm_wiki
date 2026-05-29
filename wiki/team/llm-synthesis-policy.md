# LLM Synthesis Policy

This repository uses deterministic ingest as the default merge-time path. LLM-assisted synthesis is allowed only as a review-required enhancement that creates or updates a bot PR.

## Default Model

- Provider: OpenAI
- Model: `gpt-5.5`
- Rationale: wiki synthesis requires long-context reasoning over `AGENTS.md`, `CLAUDE.md`, `wiki/latest-context.md`, packet manifests, packet-specific YAML, and packet narratives. Current OpenAI documentation marks GPT-5.5 as the latest flagship model for complex reasoning and coding.
- Fallbacks: `gpt-5.4` for lower cost with strong quality, `gpt-5.4-mini` only for low-risk summarization or lint-style checks.

## Operating Rules

- Merge-time `wiki-main-ingest` must not require an LLM API key.
- LLM output must never mutate `raw/`.
- LLM output that changes `wiki/` must be review-required unless the change is only a low-risk summary with no claim promotion.
- The LLM must read `AGENTS.md`, `CLAUDE.md`, `wiki/latest-context.md`, target packet manifests, packet-specific YAML, and packet narratives before writing synthesis.
- The LLM must preserve claim statuses and must not promote `tentative` to `supported` without raw evidence and metric/split validation.
- The LLM must output a bounded diff or replacement page, not free-form repository edits.

## Prompt Contract

The synthesis prompt should ask for:

- stable entity page updates rather than dated packet mirrors
- explicit provenance back to packet ids and raw evidence
- conflicts, supersession, and open questions
- reviewer checklist items for risky interpretation
- no unsupported metric, leaderboard, or model-ranking claims
