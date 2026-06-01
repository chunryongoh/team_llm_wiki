# Workflow Run Chain Smoke Packet Notes

This packet verifies the GitHub Actions chain after adding the `workflow_run` trigger to `wiki-llm-synthesis`.

Expected result:

1. Merge this packet into `main`.
2. `wiki-main-ingest` runs from the `raw/users/**` push.
3. `wiki-main-ingest` commits deterministic wiki output and an ingest report.
4. The completed `wiki-main-ingest` run triggers `wiki-llm-synthesis`.
5. `wiki-llm-synthesis` uses GPT-5.5 and opens a review-required bot PR when synthesis output exists.

This is not evidence for a sleep-health modeling claim.
