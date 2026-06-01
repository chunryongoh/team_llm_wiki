# Full Chain Actions Smoke Packet Notes

This packet exists to verify the GitHub Actions chain for Team LLM Wiki automation.

It is intentionally small and does not make a dataset, model, feature, benchmark, or performance claim.

Expected chain:

1. A packet PR adds files under `raw/users/**`.
2. `wiki-pr-validate` previews deterministic wiki ingest.
3. After merge to `main`, `wiki-main-ingest` generates deterministic wiki pages and a report under `raw/results/wiki-ingest/**`.
4. The ingest report triggers `wiki-llm-synthesis`.
5. GPT-5.5 synthesis opens a review-required bot PR when synthesis changes are produced.
