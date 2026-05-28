# Packet Skill Design Summary

**Date** 2026-05-28
**Status** design captured

## Summary

The team decided to scope the next AI-assistant workflow as a packet creation skill, not a team-member profile system. The skill should help teammates create evidence-backed raw packets through an ML/DL expert interview, preview the generated packet, obtain explicit approval, validate locally, and upload the approved packet to GitHub under `raw/users/...`.

## Key Direction

- Skill name: `team-llm-wiki-packet`
- Primary outcome: approved raw packet committed and pushed to GitHub
- Non-goal: direct edits to generated `wiki/` synthesis pages
- Interaction style: one-question-at-a-time interview inspired by `superpowers:brainstorming` and `gstack-office-hours`
- Expert stance: challenge weak ML/DL claims, leakage risks, missing baseline evidence, and unsupported performance claims

## Design Spec

- [Team LLM Wiki Packet Skill Design](../../docs/superpowers/specs/2026-05-28-team-llm-wiki-packet-skill-design.md)

## Next Action

Turn the design into an implementation plan for a reusable skill package.
