# Team LLM Wiki Ingest MVP Spec

This repository implements a standalone Python ingest tool for merge-time wiki maintenance.

The source of truth is packet evidence under `raw/users/<user>/<packet-id>/`. Each packet contains a `manifest.yaml` and local raw files. New manifests use `packet_type`; the legacy `type` field remains accepted for compatibility. The maintained memory layer is `wiki/`, where generated packet pages, index entries, log entries, and latest context are updated deterministically.

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
- Metrics in `metrics_to_verify` must match raw YAML/JSON evidence via `raw_path` and optional dotted `key`; legacy manifest-only `actual` values remain accepted for older packets.
- Policy conflicts in `CLAUDE.md` around raw immutability, secret handling, protected paths, or claim promotion hard-fail.
- Packet file count and text byte limits are enforced.

Renderer policy:

- Routes are deterministic by packet type.
- `wiki/index.md` has an idempotent managed block.
- `wiki/log.md` is append-only and idempotent per packet heading.
- `wiki/latest-context.md` preserves previous generated entries, includes `[[index]]`, `[[overview]]`, and `[[log]]`, and is bounded by entry count.
- Candidate wiki mutations are rendered in staging first. They are copied to the real repo only after guard checks and generated-link lint pass.
