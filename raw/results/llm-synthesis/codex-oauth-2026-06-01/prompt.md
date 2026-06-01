You are running inside the team_llm_wiki repository.

Goal: perform high-quality LLM wiki synthesis using GPT-5.5 and the current Codex OAuth session.

You must read and obey:
- AGENTS.md
- CLAUDE.md
- wiki/latest-context.md
- wiki/team/llm-synthesis-policy.md
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/manifest.yaml
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/dataset.yaml
- raw/users/chunryongoh/datasets/2026-05-29-sleep-lifelog-2024/packet.md
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/manifest.yaml
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/benchmark.yaml
- raw/users/chunryongoh/benchmarks/2026-05-29-sleep-health-hackathon-v0/packet.md
- wiki/datasets/sleep-lifelog-2024.md
- wiki/benchmarks/sleep-health-hackathon-v0.md

Return replacement pages only for these two exact paths:
- wiki/datasets/sleep-lifelog-2024.md
- wiki/benchmarks/sleep-health-hackathon-v0.md

Rules:
- Preserve frontmatter with packet ids, publish_action, risk_tier, claim_status, generated_by_run if present.
- Preserve claim statuses as tentative unless raw evidence proves otherwise.
- Do not add unsupported metric, leaderboard, model-ranking, or performance claims.
- Synthesize, deduplicate, and improve the narrative beyond deterministic packet mirroring.
- Keep Korean prose where useful, but stable field names and filenames must remain machine-friendly.
- Include explicit provenance to raw packet files and packet ids.
- Include open questions/conflicts/supersession notes where relevant.
- Do not write files. Return JSON only according to the output schema.
