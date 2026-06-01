# GPT-5.5 LLM Synthesis Implementation

Status: implemented, live Codex OAuth verification completed, GitHub-hosted API key path pending secret configuration

## Summary

The repository now has a real LLM-assisted synthesis path separate from deterministic merge-time ingest.

`run-llm-wiki-synthesis` reads:

- `AGENTS.md`
- `CLAUDE.md`
- `wiki/latest-context.md`
- `wiki/team/llm-synthesis-policy.md`
- packet manifests
- packet-specific YAML
- `packet.md`
- current target wiki pages

It then calls OpenAI Responses API with `gpt-5.5` and `reasoning.effort=high`, requests structured JSON output, validates that the model only writes approved target `wiki/` pages, and writes a synthesis report under `raw/results/llm-synthesis/<run-id>/report.json`.

## Automation

`.github/workflows/wiki-llm-synthesis.yml` runs after deterministic ingest reports under `raw/results/wiki-ingest/**` reach `main`, or by manual dispatch. The workflow creates a review-required PR with the GPT-5.5 rewritten wiki pages.

## Guardrails

- `raw/` writes from the model are rejected.
- Unapproved wiki paths are rejected.
- Generated link and wiki health checks run in staging before any wiki page is copied back.
- Failed LLM output produces `hard_fail` without mutating wiki pages.
- Deterministic `wiki-main-ingest` still does not require an API key.

## Verification

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q` passed with 317 tests.
- Workflow YAML parsed successfully.
- `git diff --check` passed.
- `check-wiki-health` returned `ok: true`.
- Local missing-key behavior was verified: `run-llm-wiki-synthesis` returns `missing_api_key` when `OPENAI_API_KEY` is absent.

## Open Item

The GitHub-hosted workflow still needs an `OPENAI_API_KEY` repository secret before it can run GPT-5.5 in Actions. Add the repository secret, then dispatch `wiki-llm-synthesis` against `raw/results/wiki-ingest/26628582638-1/report.json` to produce hosted LLM-authored synthesis PRs.

## Codex OAuth Verification

On 2026-06-01, a local `codex exec -m gpt-5.5` run used the existing Codex OAuth session to read the policy files, packet files, and current target wiki pages, then returned structured JSON replacements for:

- `wiki/datasets/sleep-lifelog-2024.md`
- `wiki/benchmarks/sleep-health-hackathon-v0.md`

The audit artifacts are stored under `raw/results/llm-synthesis/codex-oauth-2026-06-01/`. This verifies the OAuth-backed local path, but it does not remove the need for `OPENAI_API_KEY` in GitHub-hosted Actions.
