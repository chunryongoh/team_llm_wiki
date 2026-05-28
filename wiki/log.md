# Team LLM Wiki Log

Append-only ingest and maintenance events belong here.

## [2026-05-28] docs | korean-readme-usage-policy

- Rewrote `README.md` in Korean around setup, packet authoring, ingest commands, GitHub Actions triggers, review policy, guard policy, and local verification.
- Clarified that `wiki-pr-validate` remains empty until a pull request triggers it.
- Documented the distinction between `publish_action` and semantic `risk_tier`.

## [2026-05-28] design | packet-skill-interview-flow

- Added a design spec for `team-llm-wiki-packet`, an interview-driven skill for creating and uploading raw wiki packets.
- Scoped v1 away from team-member profile generation and toward approved packet creation, local validation, commit, and GitHub push.
- Filed a wiki report linking the durable design summary.
