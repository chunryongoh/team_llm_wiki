---
project: team-llm-wiki
status: active
---

# Team LLM Wiki Agent Rules

- Treat `raw/` as append-only source evidence.
- Treat `wiki/` as generated and reviewed team memory.
- Do not promote performance, model, feature, or supported claims without raw evidence and metric validation.
- Use ASCII kebab-case filenames and stable machine-readable fields.
- Keep `wiki/latest-context.md` bounded and use it as an agent session entrypoint, not as a wiki dump.
- Render `wiki/` as synthesized memory, not raw packet mirroring. Dataset and benchmark pages should use stable entity filenames such as `wiki/datasets/<dataset-name>.md` and `wiki/benchmarks/<benchmark-name>.md`; packet ids belong in provenance.
- When LLM-assisted synthesis is enabled, use `gpt-5.5` as the default high-accuracy model and keep all LLM output review-required. Merge-time ingest must still be reproducible without an API key.
- Do not add automation-only smoke-test packets to `raw/` or `wiki/`. End-to-end workflow tests that intentionally enter team memory must use DACON/ETRI sleep-health domain content; pure workflow evidence belongs in PR comments, run summaries, or engineering docs outside the research wiki.
