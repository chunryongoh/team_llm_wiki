# Implementation Plan

1. Define dataclass models, enums, JSON serialization helpers, and named ingest failures.
2. Load manifests with `yaml.safe_load`, validate changed paths, and discover packet roots by ancestor `manifest.yaml`.
3. Load `AGENTS.md` and `CLAUDE.md`, warning when Claude rules do not import `@AGENTS.md`.
4. Run guard checks before rendering and classify packet risk.
5. Render packet pages, managed index entries, append-only log entries, and bounded latest context.
6. Implement planning and running entrypoints. Hard-fail and skipped runs do not mutate `wiki/`; reports are JSON and append under `raw/results/wiki-ingest/<run-id>/report.json` by default.
7. Add CLI commands for plan, run, and full wiki health checks.
8. Add GitHub Actions helpers and workflows for merge-time ingest and scheduled health checks.
9. Cover critical paths with deterministic pytest tests.
10. Add `run-llm-wiki-synthesis` as the review-required GPT-5.5 path. It reads policy, latest context, raw packet files, and existing wiki pages; calls OpenAI Responses API; validates that the model only returns approved `wiki/` page replacements; writes an LLM report; and drives a separate bot PR through `.github/workflows/wiki-llm-synthesis.yml`.
