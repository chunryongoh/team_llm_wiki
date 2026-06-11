---
project: team-llm-wiki
status: active
---

# Team LLM Wiki Agent Rules

This repository is a Karpathy-style LLM wiki for ETRI/DACON sleep-health research. The agent is a wiki maintainer, not a generic chatbot and not a packet mirror formatter.

## Layer Contract

- `raw/` is append-only source evidence. Read it, cite it, and never rewrite it unless the user explicitly asks to add source material.
- `wiki/` is LLM-maintained team memory. It should contain synthesized, interlinked markdown pages that compound over time.
- `automation/.cache/compiled/` is generated structured cache. Use it for stable machine-readable packet facts.
- `AGENTS.md`, `CLAUDE.md`, and `wiki/team/llm-wiki-operating-harness.md` are the operating schema. Update them when the maintainer workflow changes.

## Session Start

When answering or editing in this repo:

1. Read `wiki/latest-context.md`.
2. Read `wiki/index.md`.
3. Follow only the task-relevant hub, registry, and leaf pages.
4. Drop to `raw/` only when the wiki is insufficient, provenance is disputed, or a claim status may change.

`wiki/latest-context.md` is an entrypoint. Keep it bounded; move detail into hub, registry, leaf, question, decision, or report pages.

## Ingest Loop

When new source material appears under `raw/users/**`:

1. Identify source type, owner, claim boundary, evidence surface, and target entities.
2. Preserve packet-specific context in packet review pages or compiled JSON.
3. Update stable entity pages, not dated packet mirrors, whenever the source affects reusable knowledge.
4. Update relevant hub/registry pages with short routing summaries and links to leaf pages.
5. Update claim registry, leaderboard history, split/leakage policy, decisions, and open questions when affected.
6. Update `wiki/index.md`.
7. Append `wiki/log.md`.

A single meaningful source may touch 10-15 wiki pages. That is expected when it changes durable team memory.

## Query Loop

When answering a question:

1. Answer from `wiki/` first.
2. Cite wiki pages and raw evidence when provenance matters.
3. Separate supported, tentative, disputed, and superseded claims.
4. If the answer creates durable value, crystallize it back into `wiki/reports/`, `wiki/questions/`, `wiki/decisions/`, or the relevant leaf entity page.

Do not leave important analysis only in chat.

## Crystallize-Back Rule

Create or update a wiki page when a conversation produces any of the following:

- a reusable feature/model/preprocessing/target interpretation
- a decision or rejected alternative
- a contradiction or supersession
- a new open question with close condition
- a benchmark or leaderboard provenance rule
- a briefing that future agents should read

## Page Roles

Use `page_role` in frontmatter when practical:

- `entrypoint`: `latest-context`, `overview`, `index`
- `registry`: claim, submission, benchmark, or entity catalog
- `hub`: topic routing page
- `leaf`: one durable entity or concept
- `packet_review`: source-specific packet interpretation
- `report`: time-bounded synthesis
- `policy`: operating rules

One durable entity should have one stable page. Repeated concepts, target bottlenecks, model variants, feature families, and claim boundaries should be promoted to leaf pages.

## Claim and Evidence Rules

- Do not promote performance, model, feature, or supported claims without raw evidence and metric validation.
- Local OOF, notebook output, user-reported public score, DACON public leaderboard, DACON private leaderboard, and organizer-official validation are separate evidence surfaces.
- Dataset and benchmark pages use stable entity filenames such as `wiki/datasets/<dataset-name>.md` and `wiki/benchmarks/<benchmark-name>.md`; packet ids belong in provenance.
- SHAP or feature importance is interpretation evidence, not causal proof.

## Lint Loop

Periodically check for:

- contradictions between pages
- stale tentative claims
- orphan pages with no index or inbound links
- repeated concepts lacking a leaf page
- missing cross-links between raw evidence, claims, decisions, and questions
- metrics without evidence
- `latest-context` turning into a dump

Use `PYTHONPATH=src python -m team_llm_wiki.cli check-wiki-health --repo-root .` for machine checks, then perform semantic review for contradictions and missing entity pages.

## Automation Policy

- When LLM-assisted synthesis is enabled, use `gpt-5.5` as the default high-accuracy model and keep all LLM output review-required.
- Merge-time ingest must remain reproducible without an API key.
- Do not add automation-only smoke-test packets to `raw/` or `wiki/`. End-to-end workflow tests that intentionally enter team memory must use DACON/ETRI sleep-health domain content; pure workflow evidence belongs in PR comments, run summaries, or engineering docs outside the research wiki.
