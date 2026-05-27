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
