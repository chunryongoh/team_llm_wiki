# Wiki Packet Template

Copy this directory under `raw/users/<user>/<packet-id>/` and keep all evidence files inside that packet root.

The ingest runner treats `raw/` as append-only evidence and promotes only synthesized markdown into `wiki/`.

For team contributors, the recommended path is to use
`chunryongoh/team-llm-wiki-packet-skill` rather than copying this template
manually. The skill performs graph-first artifact intake, asks evidence-gap
questions, renders packet files, and opens a PR that only touches
`raw/users/<owner>/<category>/<date-slug>/`.

## Packet types

- `reference`, `meeting` -> `wiki/sources/`.
- `experiment` -> `wiki/experiments/`.
- `feature` -> `wiki/features/`.
- `model` -> `wiki/models/`.
- `performance` -> `wiki/performance/`.
- `preprocessing`, `augmentation` -> `wiki/datasets/`.
- `dataset` -> `wiki/datasets/`; route for first-class dataset definitions (modalities, splits, leakage risks).
- `benchmark` -> `wiki/benchmarks/`; route for target taxonomy and metric definitions.

Use `dataset.yaml` and `benchmark.yaml` in this directory as the packet-specific raw evidence for the new types. The ingest runner mirrors `claim_status` from the manifest into the packet-specific YAML and requires the listed fields.

## Graph-first packet files

Entity-bearing packets should include enough information for repo-side ingest
and GPT synthesis to update durable wiki pages instead of creating only a dated
mirror page.

Recommended packet-local files:

- `manifest.yaml`: packet id, owner, packet type, claim status, claim boundary,
  raw paths, and intended wiki targets.
- `packet.md`: human-readable source summary and provenance notes.
- packet-specific YAML such as `performance.yaml`, `model.yaml`,
  `features.yaml`, `preprocessing.yaml`, `augmentation.yaml`, `dataset.yaml`, or
  `benchmark.yaml`.
- `metrics.json`, `*.csv`, notebook/code/report excerpts, or other raw evidence
  referenced by `manifest.yaml`.
- `wiki_plan.yaml`: advisory stable entities, affected hub/leaf pages, claim
  registry updates, conflicts/supersessions, open questions, and semantic lint.

The packet skill may create intermediate graph artifacts such as
`packet_scan_manifest.json`, `packet_entity_graph.json`, `semantic_lint.json`,
and `question_queue.yaml` under a scratch directory like
`/tmp/team-llm-wiki-packet-work/<packet-id>/`. These scratch artifacts guide the
interview and draft, but they do not need to be committed unless they are
explicit raw evidence for the packet.

## Claim boundary reminder

Do not collapse separate evidence surfaces into one claim. Local OOF, notebook
output, user-reported DACON public score, DACON private score, and
organizer-official validation are separate surfaces. If a packet lacks
submission id, exported prediction file, CSV hash, private score, or team
reproduction evidence, leaderboard observations should normally remain
`tentative`.
