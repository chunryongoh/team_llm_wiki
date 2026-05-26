# Contribution Workflow

1. Create a packet under `raw/users/<user>/<packet-id>/`.
2. Add `manifest.yaml` and raw evidence files inside the packet root.
3. Run `plan-wiki-main-ingest` with the changed packet paths.
4. Let the workflow run `run-wiki-main-ingest` on merge-time changes.
5. Review bot PRs for high-risk packet types and governance-tier claims.

Do not edit generated wiki pages to hide failed evidence. Add a new packet that supersedes or disputes the older claim.
