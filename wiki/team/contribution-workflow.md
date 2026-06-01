# Contribution Workflow

1. Create a packet under `raw/users/<user>/<packet-id>/`.
2. Add `manifest.yaml` and raw evidence files inside the packet root. The manifest must include `id`, `packet_type`, `title`, `date`, `owner`, `status`, `task`, `dataset`, `split`, `model`, `claim_boundary`, `claim_status`, `summary`, `raw_paths`, and `intended_wiki_targets`.
3. Run `plan-wiki-main-ingest` with the changed packet paths.
4. Let the workflow run `run-wiki-main-ingest` on merge-time changes.
5. Review bot PRs for high-risk packet types and governance-tier claims.

Do not edit generated wiki pages to hide failed evidence. Add a new packet that supersedes or disputes the older claim.

Metric claims must be backed by raw YAML or JSON evidence in the packet. Put each metric in `metrics_to_verify` with `raw_path`, `metric_key`, `reported_value`, and optional `tolerance`; the runner reads the raw file and rejects mismatches.

For grouped splits, set `split.group_key` and `split.fold_file`. The fold file must stay inside the packet root, include the group key column, and include `split` or `role` values that distinguish train from validation rows. An optional `fold` column separates multiple folds; without it, the guard treats rows as fold `0`.

Pull requests that change `raw/users/**` get a preview comment from `preview-wiki-ingest`. Main-branch ingest direct commits use `[wiki-bot] ingest wiki packets`; reviewed bot PRs use `[wiki-bot][review-required] ingest wiki packets`. These prefixes prevent bot loops. Default `GITHUB_TOKEN` bot commits may suppress follow-up workflows, so use a PAT or GitHub App token if the team requires follow-up workflow execution from bot output.

Preview comments are Korean-first and include a packet lifecycle summary. Reviewers should check the displayed `packet skill compatibility`, `claim_boundary`, claim status, risk tier, affected wiki pages, and the "merge 후 다음 단계" line before merging.

The packet skill compatibility result is an adoption signal, not a second manifest validator. `warning` means the packet can still be useful but the reviewer should inspect shape or evidence quality, such as a legacy packet root, missing `packet.md`, or performance packet without `metrics_to_verify`.

Supported packet types are `reference`, `meeting`, `experiment`, `feature`, `model`, `performance`, `preprocessing`, `augmentation`, `dataset`, and `benchmark`. Dataset packets define modalities, splits, package files, and leakage risks; benchmark packets define target taxonomy, primary metric, and evaluation policy. Both require packet-specific YAML labeled as `dataset` or `benchmark` in `raw_paths`, route to `wiki/datasets/` and `wiki/benchmarks/` respectively, render to stable entity pages, and go through bot PR review.

Use `packet.md` for the human-readable synthesis narrative that should be promoted into the target wiki page. The manifest and packet-specific YAML provide machine-checkable fields; `packet.md` provides the explanatory context that teammates and agents should read.

## Packet Skill Domain Context

The contributor-side packet skill is expected to read this repository before drafting any packet. For ETRI/DACON sleep-health work, it should also load its bundled `references/etri-dacon-sleep-health-context.md` primer. That primer is only an interview accelerator; this repository remains canonical.

Canonical ETRI/DACON entrypoints:

- `wiki/latest-context.md`
- `wiki/overview.md`
- `wiki/datasets/sleep-lifelog-2024.md`
- `wiki/benchmarks/sleep-health-hackathon-v0.md`
- `wiki/performance/2026-06-01-lgb-cb-reproduction-local-oof-diagnostic.md`
- `wiki/features/sleep-lifelog-feature-landscape.md`
- `wiki/decisions/sleep-lifelog-evaluation-protocol.md`
- `wiki/questions/sleep-lifelog-open-questions.md`

When a packet skill primer conflicts with any of the pages above, reviewers should require the packet to follow the wiki page and record the conflict as an evidence gap or semantic lint item. The primer must not promote local OOF diagnostics to DACON leaderboard claims, must not call LightGBM + CatBoost globally best without the exact supported boundary, and must not conflate different GroupKFold fold counts as the same split.

Bot PRs include an `자동 검증 결과` section. Do not merge a bot PR if self-validation failed or if validation evidence is missing without a clear reason in the workflow summary.
