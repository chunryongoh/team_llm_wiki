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

## [2026-05-28] design | packet-skill-hybrid-mode-review

- Updated the packet skill design after CEO review to use markdown-first hybrid mode.
- Clarified that default packets create `packet.md` plus helper-generated `manifest.yaml`, while structured YAML/evidence is reserved for performance, experiment, metric, split-sensitive, or strong claims.
- Set PR-first upload as the default path and deferred markdown-to-structured promotion from v1.

## [2026-05-28] design | packet-skill-standalone-boundary

- Clarified that `team-llm-wiki-packet` is a standalone skill package, not an implementation subdirectory of `team_llm_wiki`.
- Defined `team_llm_wiki` as the target repository that the skill reads from and writes raw packets into.
- Kept helper scripts inside the standalone skill bundle for v1.

## [2026-05-28] design | packet-skill-helper-failure-contract

- Added a named JSON success/failure contract for standalone packet skill helper scripts.
- Defined failure codes and recovery actions for draft creation, packet rendering, preview generation, and PR upload helpers.
- Required helper failures to stop the skill unless the recovery path is explicit.

## [2026-05-28] design | packet-skill-separate-repo

- Chose a separate GitHub repository as the source of truth for the standalone `team-llm-wiki-packet` skill.
- Clarified that local `~/.codex/skills/...` directories are installation targets, not the canonical source.
- Kept `team_llm_wiki` as the packet target repository only.

## [2026-05-28] design | packet-skill-repo-name

- Set the standalone packet skill source repository to `chunryongoh/team-llm-wiki-packet-skill`.
- Kept `~/.codex/skills/team-llm-wiki-packet/` as the local install/use location.
