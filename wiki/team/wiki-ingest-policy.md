# Wiki Ingest Policy

The ingest runner accepts packet manifests under changed raw packet roots and writes deterministic synthesis pages under `wiki/`.

Low-risk reference and meeting packets may be direct-commit candidates. Experiment, performance, model, feature, augmentation, supported, disputed, and superseded claims require bot PR review. Guard failures hard-fail and must not mutate `wiki/`.

Packets must keep raw evidence local to the packet root. Secret-like content, secret filenames, model weight files, path escapes, missing raw evidence, metric mismatches, wrong target routes, and packet size limit violations are blocked.

Full manifests require these fields: `id`, `packet_type` or legacy `type`, `title`, `date`, `owner`, `status`, `task`, `dataset`, `split`, `model`, `claim_boundary`, `claim_status`, `summary`, `raw_paths`, and `intended_wiki_targets`. `dataset` requires `name` and `version`; `split` requires `name`; `model` requires `family`.

Packet-specific YAML is required for preprocessing, feature, model, performance, and augmentation packets through labeled entries in `raw_paths`. Required labels are `preprocessing`, `features`, `model`, `performance`, and `augmentation` respectively. The required packet YAML fields are enforced by the ingest guard before any wiki mutation.

Metrics are raw-only evidence checks. `metrics_to_verify` entries must point to YAML or JSON in the packet with `raw_path`, identify a value by `metric_key`, and declare the manifest-side `reported_value`; optional `tolerance` controls numeric comparison.

Grouped split checks use `split.group_key` and `split.fold_file`. The fold file must be local to the packet, must include the group key column, and must include `split` or `role`; `fold` is optional and defaults to `0`.

Successful ingest also writes compiled packet JSON under `automation/.cache/compiled/<packet-id>.json`. The cache is generated output and is included in direct commits or bot PRs with the corresponding wiki pages. Rendered packet wiki pages include a Markdown link to the compiled JSON cache entry.

PR preview runs on packet PRs and comments a bounded summary of status, failures, packet roots, and generated paths. Health checks run from `check-wiki-health`; scheduled and manual health workflows also generate daily and weekly briefs under `wiki/briefs/` and upload the health report plus brief artifacts. Daily brief generation writes `<date>-daily.md` and refreshes `latest.md`. Weekly generation writes `<YYYY-Www>-weekly.md` with the required weekly sections, a contradiction scan, and `<date>-stale-claims.md` for stale tentative claims, then refreshes `latest.md` to the weekly brief.

Main ingest direct commits and bot PR titles use `[wiki-bot] ingest wiki packets`. The main ingest workflow skips only changes matching that bot-loop convention. It does not use `[skip ci]`, so normal CI remains eligible to run on bot output and human changes.
