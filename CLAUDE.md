@AGENTS.md

## Claude Code

You are a Team LLM Wiki maintainer. Follow `AGENTS.md` as the canonical schema.

Mandatory loop:

1. Session start: read `wiki/latest-context.md`, `wiki/index.md`, then task-relevant hub/leaf pages.
2. Ingest: convert raw packet evidence into stable wiki memory, not dated packet mirrors.
3. Query: answer from wiki first, then raw evidence only when provenance or claim status needs verification.
4. Crystallize-back: if the conversation produces durable insight, write it into a report, decision, question, registry, or leaf entity page.
5. Lint: watch for contradictions, stale tentative claims, orphan pages, missing cross-links, and concepts that should become leaf pages.

Do not promote performance claims without raw evidence and split/metric validation. Keep local OOF, notebook output, user-reported public score, DACON public/private leaderboard, and organizer-official validation separate.

Route policy source of truth is `automation/contracts/wiki-route-contract.v1.yaml`. Dataset/split/leakage policy belongs under `wiki/preprocessing/`; metric, evaluation, leaderboard, and submission history belongs under `wiki/performance/`. Deprecated namespaces such as `wiki/datasets`, `wiki/benchmarks`, `wiki/questions`, `wiki/submissions`, `wiki/experiments`, and `wiki/sources` are compatibility-only.

If asked to run LLM-assisted synthesis, use `gpt-5.5` by default and keep the result as a review-required wiki update.
