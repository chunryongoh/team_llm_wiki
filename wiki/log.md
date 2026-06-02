# Team LLM Wiki Log

Append-only ingest and maintenance events belong here.

## [2026-06-02] audit | team-packet-entity-coverage

- target: `wiki/reports/2026-06-02-team-packet-entity-coverage-audit.md`
- finding: current entity-first structure works for Section07/current claims, but 문형도, 구나영, 조혜원 attachment bundles are not yet packet-local raw evidence or wiki entities.

## [2026-06-02] governance | entity-first-claim-gated-wiki

- Added ML/AI hackathon entity model and packet quality standard.
- Added required claim, submission, preprocessing, model, feature, decision, and section07 backlog pages.
- Strengthened health, preview, and LLM synthesis rules so packet ingest updates stable wiki entities rather than only experiment mirrors.

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

## [2026-05-28] design | packet-skill-markdown-safety-gate

- Added a v1 markdown safety gate for markdown-first packet creation.
- Hard blocks cover secret-like content, PII-like content, model weight references, unsafe local paths, prompt-injection text, and oversized markdown.
- Warnings cover unsupported performance claims, meeting opinions stated as facts, missing claim boundaries, large embedded logs, and unchecked external references.

## [2026-05-28] design | packet-skill-fixture-self-tests

- Added fixture-based self-tests to the standalone packet skill v1 scope.
- Required tests cover markdown-first rendering, structured performance rendering, markdown safety blocks/warnings, path containment, staging safety, PR failure recovery, and optional target repo CLI validation.
- Clarified that these tests live in the separate skill repository, not in `team_llm_wiki`.

## [2026-05-28] plan | packet-skill-implementation

- Added an implementation plan for the standalone `team-llm-wiki-packet` skill source repo.
- Planned local skill installation under `~/.codex/skills/team-llm-wiki-packet`.
- Required a fresh subagent smoke test that installs the skill, creates a real raw packet PR against `team_llm_wiki`, validates it, and closes the smoke PR without merge.

## [2026-05-28] implementation | packet-skill-smoke-verified

- Implemented the standalone `team-llm-wiki-packet` skill in `chunryongoh/team-llm-wiki-packet-skill`.
- Installed the skill under `/home/chunoh/.codex/skills/team-llm-wiki-packet`.
- Verified a fresh subagent smoke PR against `team_llm_wiki`: `https://github.com/chunryongoh/team_llm_wiki/pull/2`.
- Smoke PR validation passed for both `wiki-pr-validate / preview` and `tests / pytest`, then the PR was closed without merge and its branch deleted.
- Recorded implementation evidence in `wiki/reports/2026-05-28-packet-skill-implementation.md`.

## [2026-05-29] ingest | 2026-05-29-sleep-health-hackathon-v0

- target: `wiki/benchmarks/sleep-health-hackathon-v0.md`
- run: `26628582638-1`

## [2026-05-29] ingest | 2026-05-29-sleep-lifelog-2024

- target: `wiki/datasets/sleep-lifelog-2024.md`
- run: `26628582638-1`

## [2026-05-29] implementation | gpt-5-5-llm-synthesis

- Added `run-llm-wiki-synthesis` as the actual GPT-5.5 synthesis path.
- The runner reads `AGENTS.md`, `CLAUDE.md`, `wiki/latest-context.md`, raw packet files, and current target wiki pages before calling OpenAI Responses API.
- Added `.github/workflows/wiki-llm-synthesis.yml` to create review-required bot PRs after deterministic ingest reports reach `main`.
- Local and repository `OPENAI_API_KEY` were missing during implementation, so the live GPT-5.5 call remains pending secret configuration.

## [2026-06-01] implementation | llm-wiki-integration-scope

- Expanded `wiki-llm-synthesis` from entity-page rewrite to multi-page wiki integration.
- Required GPT-5.5 output to cover stable entity pages, feature landscape, evaluation decision, open questions, synthesis report, overview, latest context, index, and log.
- Added structured integration metadata to the LLM report and bot PR body.

## [2026-06-01] ingest | 2026-06-01-dacon-leaderboard-claim-boundary

- target: `wiki/sources/2026-06-01-dacon-leaderboard-claim-boundary.md`
- run: `26740055632-1`

## [2026-06-01] ingest | 2026-06-01-lgb-cb-reproduction-local-oof-diagnostic

- target: `wiki/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic.md`
- run: `26741704818-1`

## [2026-06-01] synthesis | sleep-lifelog-packet-integration

- `2026-06-01-lgb-cb-reproduction-local-oof-diagnostic` packet을 packet mirror가 아니라 안정 wiki memory로 통합했다.
- updated: `wiki/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic.md`, `wiki/overview.md`, `wiki/latest-context.md`, `wiki/index.md`, `wiki/log.md`
- created: `wiki/features/sleep-lifelog-feature-landscape.md`, `wiki/decisions/sleep-lifelog-evaluation-protocol.md`, `wiki/questions/sleep-lifelog-open-questions.md`, `wiki/reports/2026-06-01-sleep-lifelog-packet-synthesis.md`
- 보존한 claim boundary: `local_oof_diagnostic_only`
- 보존한 claim_status: `supported`
- 핵심 supported metric: `targetwise_reblend_macro_log_loss` `0.6198365213240887`, `baseline_wave41_macro_log_loss` `0.6198684545582471`, `delta_vs_wave41` `-3.19332341584e-05`
- review-required: true

## [2026-06-01] ingest | 2026-06-01-lifelog-section07-working-notes

- target: `wiki/experiments/2026-06-01-lifelog-section07-working-notes.md`
- run: `local-run-section07`

## [2026-06-01] ingest | 2026-06-01-lifelog-section07-notebook-overview

- target: `wiki/experiments/2026-06-01-lifelog-section07-notebook-overview.md`
- run: `local-run-section07-notebook`

## [2026-06-01] ingest | 2026-06-01-app-context-feature-engineering-20260601

- target: `wiki/performance/2026-06-01-app-context-feature-engineering-20260601.md`
- run: `26806097236-1`

## [2026-05-29] ingest | 2026-05-29-labelwise-weekly-progress-target-bottlenecks

- target: `wiki/experiments/2026-05-29-labelwise-weekly-progress-target-bottlenecks.md`
- run: `26806097236-1`

## [2026-05-28] ingest | 2026-05-28-1875-feature-domain-ablation-and-dedup

- target: `wiki/features/2026-05-28-1875-feature-domain-ablation-and-dedup.md`
- run: `26806097236-1`

## [2026-05-29] ingest | 2026-05-29-v200-v209-sparse-splice-review

- target: `wiki/experiments/2026-05-29-v200-v209-sparse-splice-review.md`
- run: `26806097236-1`

## [2026-05-29] ingest | 2026-05-29-v186-shap-leaderboard-analysis

- target: `wiki/performance/2026-05-29-v186-shap-leaderboard-analysis.md`
- run: `26806097236-1`
