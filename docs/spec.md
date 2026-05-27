# Team LLM Wiki Ingest MVP Spec

This repository implements a standalone Python ingest tool for merge-time wiki maintenance.

The source of truth is packet evidence under `raw/users/<user>/<packet-id>/`. Each packet contains a `manifest.yaml` and local raw files. New manifests use `packet_type`; the legacy `type` field remains accepted for compatibility. The maintained memory layer is `wiki/`, where generated packet pages, index entries, log entries, and latest context are updated deterministically.

Manifest contract:

- Full manifests require `id`, `packet_type` or legacy `type`, `title`, `date`, `owner`, `status`, `task`, `dataset`, `split`, `model`, `claim_boundary`, `claim_status`, `summary`, `raw_paths`, and `intended_wiki_targets`.
- `dataset` requires `name` and `version`; optional `hash` is preserved.
- `split` requires `name`; optional `group_key` and `fold_file` activate grouped split guards.
- `model` requires `family`; optional `weights_in_repo` must be boolean.
- `claim_status` and individual claim statuses must be one of `tentative`, `supported`, `disputed`, or `superseded`.
- `raw_paths` may be a list or label-to-path mapping. Labeled mappings are required for packet-specific YAML checks.
- `metrics_to_verify` is optional, but each entry must include raw-file evidence via `raw_path`, identify a numeric value through `metric_key`, and include `reported_value`; `tolerance` is optional.

Packet-specific YAML contract:

- `preprocessing` packets require a `raw_paths.preprocessing` YAML file with `input_sources`, `row_identity`, `target_scope`, `split_strategy`, `fold_assignment`, `leakage_guards`, `normalization`, `feature_window_policy`, `imputation`, and `code_entrypoint`.
- `feature` packets require `raw_paths.features` with `feature_families`. Each family requires `name`, `owner`, `source_modalities`, `feature_prefixes`, `anchor`, `window`, `formula`, `expected_dtype`, `missing_policy`, `leakage_risk`, `target_hypothesis`, `evidence`, `compute_cost`, and `dependencies`.
- `model` packets require `raw_paths.model` with `family`, `library_versions`, `objective`, `target_handling`, `hyperparameters`, `training_strategy`, `validation_strategy`, `calibration`, `ensembling`, `hardware`, `inference_contract`, and `weights_policy`.
- `performance` packets require `raw_paths.performance` with `primary_metric`, `metric_definitions`, `targets`, `split_id`, `overall_metrics`, `target_metrics`, `baseline_comparison`, and `claim_status`.
- `augmentation` packets require `raw_paths.augmentation` with `source_data_scope`, `generator`, `prompt_or_recipe`, `privacy_guard`, `label_policy`, `validation_policy`, and `failure_modes`.

Risk policy:

- `reference` and `meeting` packets can be `direct_commit` when guards pass.
- `performance`, `experiment`, `model`, `feature`, and `augmentation` packets are `bot_pr`.
- High-risk wiki paths under `wiki/performance`, `wiki/models`, `wiki/features`, and `wiki/experiments` are `bot_pr`.
- `supported`, `disputed`, and `superseded` claims are governance-tier and require `bot_pr`.
- Any guard failure is `hard_fail`.

Guard policy:

- Raw paths must stay inside the changed packet root and exist.
- Changed paths and intended wiki targets must not escape the repository.
- Secret-like content, forbidden secret filenames, and model-weight suffixes are blocked.
- Intended wiki targets must match the packet type route.
- Metrics in `metrics_to_verify` must match raw YAML/JSON evidence via `raw_path` and `metric_key`. Metric evidence is raw-only; manifest-side values are reports to verify, not source evidence.
- Grouped split validation reads `split.fold_file` when `split.group_key` is set. The CSV must stay inside the packet root, include the group key, include `split` or `role`, and keep each group out of both train and validation within the same `fold` value.
- Policy conflicts in `CLAUDE.md` around raw immutability, secret handling, protected paths, or claim promotion hard-fail.
- Packet file count and text byte limits are enforced.

Renderer policy:

- Routes are deterministic by packet type.
- `wiki/index.md` has an idempotent managed block.
- `wiki/log.md` is append-only and idempotent per packet heading.
- `wiki/latest-context.md` preserves previous generated entries, includes `[[index]]`, `[[overview]]`, and `[[log]]`, and is bounded by entry count.
- Candidate wiki mutations are rendered in staging first. They are copied to the real repo only after guard checks and generated-link lint pass.
- Ingest writes compiled packet JSON cache entries under `automation/.cache/compiled/<packet-id>.json` and includes them in generated paths.

Workflow policy:

- `.github/workflows/wiki-main-ingest.yml` runs on main-branch packet changes and manual dispatch. It uses concurrency group `wiki-ingest-${{ github.ref }}` with `cancel-in-progress: false`.
- Direct bot commits and bot PR titles use `[wiki-bot] ingest wiki packets`. The main ingest workflow skips only that bot-loop convention, and does not add `[skip ci]`.
- Manual `workflow_dispatch` accepts optional newline-separated `changed_paths`. When omitted, the helper falls back to tracked `raw/users/**/manifest.yaml` files, then filesystem glob discovery. The caveat is that a manual dispatch without input can intentionally scan more packets than a push event.
- `.github/workflows/wiki-pr-validate.yml` runs `preview-wiki-ingest` on packet PRs and updates a single marked preview comment with status, failures, packet roots, and generated paths.
- `.github/workflows/wiki-health-check.yml` runs scheduled/manual health checks, writes a JSON report, generates a daily brief, and uploads both as artifacts.
