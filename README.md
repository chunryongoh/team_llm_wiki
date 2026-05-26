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
