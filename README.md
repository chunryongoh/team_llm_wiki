# Team LLM Wiki

Merge-time LLM wiki ingest automation for team ML research memory.

## Install

```bash
python -m pip install -e .[test]
```

The CLI is available as either:

```bash
team-llm-wiki --help
PYTHONPATH=src python -m team_llm_wiki.cli --help
```

## Usage

Plan an ingest from changed packet manifests:

```bash
PYTHONPATH=src python -m team_llm_wiki.cli plan-wiki-main-ingest \
  --repo-root . \
  --changed-path raw/users/alice/example-packet/manifest.yaml
```

Run ingest and write an append-only report:

```bash
PYTHONPATH=src python -m team_llm_wiki.cli run-wiki-main-ingest \
  --repo-root . \
  --changed-path-file changed-paths.txt \
  --run-id local-run
```

Check full wiki health:

```bash
PYTHONPATH=src python -m team_llm_wiki.cli check-wiki-health --repo-root .
```

Packets live under `raw/users/<user>/<packet-id>/manifest.yaml`. Use `packet_type` for new manifests; the legacy `type` field remains supported for compatibility.

Required manifest fields are `id`, `packet_type` or legacy `type`, `title`, `date`, `owner`, `status`, `task`, `dataset`, `split`, `model`, `claim_boundary`, `claim_status`, `summary`, `raw_paths`, and `intended_wiki_targets`.

Shared examples in `raw/shared/templates/wiki-packet/` are manifest-shaped templates. When copying one into a packet root, also create every packet-specific file referenced by `raw_paths` such as `notes.md`, `performance.yaml`, or `folds/example.txt`, or intentionally split the template content between `manifest.yaml` and those raw files before running ingest.

Useful maintenance commands:

```bash
PYTHONPATH=src python -m team_llm_wiki.cli preview-wiki-ingest --repo-root . --changed-path-file changed-paths.txt
PYTHONPATH=src python -m team_llm_wiki.cli generate-wiki-brief --repo-root . --date "$(date -u +%F)"
PYTHONPATH=src python -m team_llm_wiki.cli generate-wiki-weekly-brief --repo-root . --date "$(date -u +%F)"
```

Daily brief generation writes `wiki/briefs/<date>-daily.md` and keeps `wiki/briefs/latest.md` as a pointer to the newest brief. Weekly brief generation writes `wiki/briefs/<YYYY-Www>-weekly.md` with the required weekly sections, a contradiction scan, and `wiki/briefs/<date>-stale-claims.md` for tentative claims older than 14 days; it also refreshes the latest pointer. Generated brief pages are excluded from wiki health link, orphan, claim, and metric checks.

Merge-time ingest writes generated wiki pages and `automation/.cache/compiled/<packet-id>.json`; each rendered packet page links to its compiled packet JSON. Direct bot commits and bot PR titles use the `[wiki-bot] ingest wiki packets` prefix so the ingest workflow can skip its own output without disabling normal CI.
