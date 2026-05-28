# Packet Skill Design Summary

**Date** 2026-05-28
**Status** design captured

## Summary

The team decided to scope the next AI-assistant workflow as a packet creation skill, not a team-member profile system. The skill should help teammates create evidence-backed raw packets through an ML/DL expert interview, preview the generated packet, obtain explicit approval, validate locally, and upload the approved packet to GitHub under `raw/users/...`.

After CEO review, the v1 direction is markdown-first hybrid mode: the user-facing artifact is `packet.md`, and a helper-generated minimal `manifest.yaml` keeps the packet compatible with the existing ingest pipeline. Structured YAML and raw metric evidence are required only for performance, experiment, metric, split-sensitive, or strong claims.

The skill itself must be standalone. `team_llm_wiki` is the target repo the skill reads from and writes packets into, not the location where the skill package is implemented.

## Key Direction

- Skill name: `team-llm-wiki-packet`
- Primary outcome: approved raw packet committed to a packet branch and opened as a GitHub pull request
- Non-goal: direct edits to generated `wiki/` synthesis pages
- Interaction style: one-question-at-a-time interview inspired by `superpowers:brainstorming` and `gstack-office-hours`
- Expert stance: challenge weak ML/DL claims, leakage risks, missing baseline evidence, and unsupported performance claims
- Default artifact: `packet.md` plus ingest-compatible `manifest.yaml`
- Structured path: type-specific YAML/evidence only when the claim requires validation
- Packaging boundary: standalone skill package, not a subdirectory of `team_llm_wiki`

## Design Spec

- [Team LLM Wiki Packet Skill Design](../../docs/superpowers/specs/2026-05-28-team-llm-wiki-packet-skill-design.md)

## Next Action

Turn the design into an implementation plan for a standalone reusable skill package.
