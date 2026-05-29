@AGENTS.md

## Claude Code

At session start, read `wiki/latest-context.md` when it exists, then follow links to task-relevant wiki pages only.
Treat `raw/` as immutable source evidence and `wiki/` as maintained memory.
Do not promote performance claims without raw evidence and split/metric validation.
Dataset and benchmark wiki pages are stable entity pages, not dated packet mirrors.
If asked to run LLM-assisted synthesis, treat `gpt-5.5` as the default model policy and keep the result as a review-required wiki update.
