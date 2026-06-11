# LLM Synthesis Policy

This repository uses deterministic ingest as the default merge-time path. LLM-assisted synthesis is allowed only as a review-required integration pass that creates or updates a bot PR.

## Default Model

- Provider: OpenAI
- Model: `gpt-5.5`
- Rationale: wiki synthesis requires long-context reasoning over `AGENTS.md`, `CLAUDE.md`, `wiki/latest-context.md`, packet manifests, packet-specific YAML, and packet narratives. Current OpenAI documentation marks GPT-5.5 as the latest flagship model for complex reasoning and coding.
- Fallbacks: `gpt-5.4` for lower cost with strong quality, `gpt-5.4-mini` only for low-risk summarization or lint-style checks.

## Operating Rules

- Merge-time `wiki-main-ingest` must not require an LLM API key.
- `run-llm-wiki-synthesis` is the actual LLM synthesis path. It calls OpenAI Responses API with `gpt-5.5` and `reasoning.effort=high`.
- `.github/workflows/wiki-llm-synthesis.yml` runs after `raw/results/wiki-ingest/**` reaches `main`, reads the ingest report, and creates a review-required bot PR with the rewritten wiki pages.
- LLM output must never mutate `raw/`.
- LLM output that changes `wiki/` must be review-required unless the change is only a low-risk summary with no claim promotion.
- The LLM must read `AGENTS.md`, `CLAUDE.md`, `wiki/latest-context.md`, target packet manifests, packet-specific YAML, and packet narratives before writing synthesis.
- The LLM must run a wiki integration pass, not a two-page formatter pass. A source can update stable entity pages plus feature, decision, question, report, overview, latest-context, index, and log pages.
- The LLM must follow [LLM Wiki Operating Harness](llm-wiki-operating-harness.md) and [Page Taxonomy](page-taxonomy.md). Chat-only insight should be crystallized back into wiki pages when durable.
- Hub and registry pages summarize and route; leaf pages own reusable entity memory. Do not let `sleep-lifelog-feature-landscape.md` absorb every feature, target, and model detail.
- The LLM must preserve the entity graph. It should consider claim registry, DACON leaderboard history, submission history, and preprocessing/split policy pages on every synthesis pass, even when the conclusion is "no change".
- `wiki/latest-context.md` must expose `Current Best`, `Active Risks`, and `Next Actions`.
- Local OOF, notebook-output, user-reported public score, DACON public leaderboard, DACON private leaderboard, and organizer-official validation are separate evidence surfaces and must not be merged into one claim.
- The LLM must preserve claim statuses and must not promote `tentative` to `supported` without raw evidence and metric/split validation.
- The LLM must output structured JSON containing only allowed replacement wiki pages, not free-form repository edits.
- The workflow requires `OPENAI_API_KEY`. If the secret is missing, the workflow must skip without breaking deterministic ingest.

## Prompt Contract

The synthesis prompt should ask for:

- stable entity page updates rather than dated packet mirrors
- page-role aware routing: entrypoint, registry, hub, leaf, packet review, report, policy
- proposed leaf pages from `wiki_plan.yaml` when path validation allows them
- compounding topic pages when a packet creates durable cross-cutting knowledge
- explicit provenance back to packet ids and raw evidence
- conflicts, supersession, and open questions
- reviewer checklist items for risky interpretation
- no unsupported metric, leaderboard, or model-ranking claims

## Current Automation

- CLI: `python -m team_llm_wiki.cli run-llm-wiki-synthesis`
- Model default: `gpt-5.5`
- Reasoning default: `high`
- Allowed write surface: stable entity pages plus deterministic integration pages computed from the changed packets
- Report path: `raw/results/llm-synthesis/<run-id>/report.json`
