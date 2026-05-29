# Wiki Ingest Policy

The ingest runner accepts packet manifests under changed raw packet roots and writes deterministic synthesis pages under `wiki/`. `wiki/` pages are maintained team memory, not raw packet mirrors. Packet ids stay in provenance; stable entities such as datasets and benchmarks use stable page ids.

Low-risk reference and meeting packets may be direct-commit candidates. Experiment, performance, model, feature, augmentation, dataset, benchmark, supported, disputed, and superseded claims require bot PR review. Guard failures hard-fail and must not mutate `wiki/`.

Packets must keep raw evidence local to the packet root. Secret-like content, secret filenames, model weight files, path escapes, missing raw evidence, metric mismatches, wrong target routes, and packet size limit violations are blocked.

Full manifests require these fields: `id`, `packet_type` or legacy `type`, `title`, `date`, `owner`, `status`, `task`, `dataset`, `split`, `model`, `claim_boundary`, `claim_status`, `summary`, `raw_paths`, and `intended_wiki_targets`. `dataset` requires `name` and `version`; `split` requires `name`; `model` requires `family`.

Packet-specific YAML is required for preprocessing, feature, model, performance, augmentation, dataset, and benchmark packets through labeled entries in `raw_paths`. Required labels are `preprocessing`, `features`, `model`, `performance`, `augmentation`, `dataset`, and `benchmark` respectively. The required packet YAML fields are enforced by the ingest guard before any wiki mutation. Dataset and benchmark packets route to `wiki/datasets/` and `wiki/benchmarks/`, mirror `claim_status` between the manifest and the packet-specific YAML, and render to canonical entity pages such as `wiki/datasets/<dataset-name>.md` and `wiki/benchmarks/<benchmark-name>.md`.

When `packet.md` exists in a packet root, ingest promotes the approved packet narrative into the rendered wiki page after stripping packet-local frontmatter and duplicate H1 headings. Packet-specific YAML renders into structured entity sections before that narrative so downstream agents can scan stable fields quickly.

LLM-assisted synthesis is optional and review-required. The default model policy is `gpt-5.5` for high-accuracy synthesis, but merge-time ingest must remain deterministic and pass without an API key. The actual LLM path is `run-llm-wiki-synthesis` and `.github/workflows/wiki-llm-synthesis.yml`, which call OpenAI Responses API, read `AGENTS.md`, `CLAUDE.md`, `wiki/latest-context.md`, raw packet files, and the current target wiki pages, then open a separate review-required bot PR. See `wiki/team/llm-synthesis-policy.md`.

Metrics are raw-only evidence checks. `metrics_to_verify` entries must point to YAML or JSON in the packet with `raw_path`, identify a value by `metric_key`, and declare the manifest-side `reported_value`; optional `tolerance` controls numeric comparison.

Grouped split checks use `split.group_key` and `split.fold_file`. The fold file must be local to the packet, must include the group key column, and must include `split` or `role`; `fold` is optional and defaults to `0`.

Successful ingest also writes compiled packet JSON under `automation/.cache/compiled/<packet-id>.json`. The cache is generated output and is included in direct commits or bot PRs with the corresponding wiki pages. Rendered packet wiki pages include a Markdown link to the compiled JSON cache entry.

PR preview runs on packet PRs and comments a bounded summary of status, failures, packet roots, and generated paths. Health checks run from `check-wiki-health`; scheduled and manual health workflows also generate daily and weekly briefs under `wiki/briefs/` and upload the health report plus brief artifacts. Daily brief generation writes `<date>-daily.md` and refreshes `latest.md`. Weekly generation writes `<date>-weekly.md` with the required weekly sections, a contradiction scan, and `<date>-stale-claims.md` for stale tentative claims, then refreshes `latest.md` to the weekly brief.

Main ingest direct commits use `[wiki-bot] ingest wiki packets`; reviewed bot PRs use `[wiki-bot][review-required] ingest wiki packets`. The main ingest workflow skips only changes matching those bot-loop conventions. It does not use `[skip ci]`, but default `GITHUB_TOKEN` bot commits may still suppress follow-up workflows under GitHub's event rules; use a PAT or GitHub App token when follow-up workflows must run from bot output.
