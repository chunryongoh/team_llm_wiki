# Wiki Packet Template

Copy this directory under `raw/users/<user>/<packet-id>/` and keep all evidence files inside that packet root.

The ingest runner treats `raw/` as append-only evidence and promotes only synthesized markdown into `wiki/`.

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
