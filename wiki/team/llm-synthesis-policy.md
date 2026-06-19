# LLM Synthesis Policy

This repository uses deterministic ingest as the default merge-time path. LLM-assisted synthesis is allowed only as a review-required integration pass that creates or updates a bot PR.

## Default Model

- Provider: OpenAI
- Model: `gpt-5.5`
- Rationale: wiki synthesis requires long-context reasoning over `AGENTS.md`, `CLAUDE.md`, `wiki/latest-context.md`, packet manifests, packet-specific YAML, and packet narratives. Current OpenAI documentation marks GPT-5.5 as the latest flagship model for complex reasoning and coding.
- Primary lane mode: when the OpenAI primary path is available, `run-llm-wiki-synthesis` runs three `gpt-5.5` specialist lanes before final page generation: `entity-graph`, `evidence-claims`, and `wiki-routing`.
- GitHub-native fallback: GitHub Models through `GITHUB_TOKEN`, default model `openai/gpt-4.1`. The fallback exists so packet merge -> ingest -> synthesis remains fully executable inside GitHub Actions when OpenAI quota or billing fails.
- Repo/org owners can set Actions variable `GITHUB_MODELS_MODEL` to a stronger allowed GitHub Models model without changing workflow code.

## Operating Rules

- Merge-time `wiki-main-ingest` must not require an LLM API key.
- `run-llm-wiki-synthesis` is the actual LLM synthesis path. It tries OpenAI Responses API with `gpt-5.5` and `reasoning.effort=high` first, then falls back to GitHub Models for recoverable provider failures such as missing OpenAI key, HTTP 429 quota/rate errors, timeout, or transient server errors.
- On the OpenAI primary path, specialist lanes do not directly write wiki files. They produce bounded JSON findings for entity mapping, evidence/claim audit, and wiki routing; the final `gpt-5.5` integrator owns page generation and the existing validator still rejects missing, duplicate, noncanonical, or out-of-scope pages.
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
- The workflow must not depend on `OPENAI_API_KEY` alone. It grants `models: read`, passes `GITHUB_TOKEN`, and should still create a synthesis bot PR through GitHub Models when OpenAI is unavailable.
- If fallback is used, the synthesis report and bot PR body must record the actual model and include a review note that the primary provider failed recoverably.
- If the primary specialist lanes run, the synthesis report and bot PR body must record the lane ids and concise summaries so reviewers can see how the work was divided.

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
- GitHub Models fallback default: `openai/gpt-4.1`
- Primary specialist lanes: `entity-graph`, `evidence-claims`, `wiki-routing`
- Reasoning default: `high`
- Allowed write surface: stable entity pages plus deterministic integration pages computed from the changed packets
- Report path: `raw/results/llm-synthesis/<run-id>/report.json`
