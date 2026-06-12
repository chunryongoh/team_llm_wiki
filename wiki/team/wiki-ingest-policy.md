# Wiki Ingest Policy

The ingest runner accepts packet manifests under changed raw packet roots and writes deterministic synthesis pages under `wiki/`. `wiki/` pages are maintained team memory, not raw packet mirrors. Packet ids stay in provenance; stable entities such as datasets and benchmarks use stable page ids.

This policy is subordinate to the maintainer loop in [LLM Wiki Operating Harness](llm-wiki-operating-harness.md) and the page roles in [Page Taxonomy](page-taxonomy.md). Ingest should preserve raw evidence, but LLM synthesis should integrate durable knowledge into registry, hub, and leaf pages.

Route policy source of truth: `automation/contracts/wiki-route-contract.v1.yaml`.

Automation must read the contract through `src/team_llm_wiki/wiki_ingest/route_contract.py`; packet skill must vendor the same contract under `references/wiki-route-contract.v1.yaml`.

Low-risk reference and meeting packets may be direct-commit candidates. Experiment, performance, model, feature, augmentation, dataset, benchmark, supported, disputed, and superseded claims require bot PR review. Guard failures hard-fail and must not mutate `wiki/`.

Packets must keep raw evidence local to the packet root. Secret-like content, secret filenames, model weight files, path escapes, missing raw evidence, metric mismatches, wrong target routes, and packet size limit violations are blocked.

Full manifests require these fields: `id`, `packet_type` or legacy `type`, `title`, `date`, `owner`, `status`, `task`, `dataset`, `split`, `model`, `claim_boundary`, `claim_status`, `summary`, `raw_paths`, and `intended_wiki_targets`. `dataset` requires `name` and `version`; `split` requires `name`; `model` requires `family`.

Packet-specific YAML is required for preprocessing, feature, model, performance, augmentation, dataset, and benchmark packets through labeled entries in `raw_paths`. Required labels are `preprocessing`, `features`, `model`, `performance`, `augmentation`, `dataset`, and `benchmark` respectively. The required packet YAML fields are enforced by the ingest guard before any wiki mutation. Dataset, split, leakage, and fit-scope knowledge routes to `wiki/preprocessing/`; metric, evaluation, leaderboard, and submission knowledge routes to `wiki/performance/`. Dataset and benchmark packets mirror `claim_status` between the manifest and the packet-specific YAML, and render to canonical entity pages under those contract routes.

When `packet.md` exists in a packet root, ingest promotes the approved packet narrative into the rendered wiki page after stripping packet-local frontmatter and duplicate H1 headings. Packet-specific YAML renders into structured entity sections before that narrative so downstream agents can scan stable fields quickly.

LLM-assisted synthesis is optional and review-required. The default model policy is `gpt-5.5` for high-accuracy synthesis, but merge-time ingest must remain deterministic and pass without an API key. The actual LLM path is `run-llm-wiki-synthesis` and `.github/workflows/wiki-llm-synthesis.yml`, which call OpenAI Responses API, read `AGENTS.md`, `CLAUDE.md`, `wiki/latest-context.md`, raw packet files, and the current target wiki pages, then open a separate review-required bot PR. See `wiki/team/llm-synthesis-policy.md`.

Metrics are raw-only evidence checks. `metrics_to_verify` entries must point to YAML or JSON in the packet with `raw_path`, identify a value by `metric_key`, and declare the manifest-side `reported_value`; optional `tolerance` controls numeric comparison.

Grouped split checks use `split.group_key` and `split.fold_file`. The fold file must be local to the packet, must include the group key column, and must include `split` or `role`; `fold` is optional and defaults to `0`.

Successful ingest also writes compiled packet JSON under `automation/.cache/compiled/<packet-id>.json`. The cache is generated output and is included in direct commits or bot PRs with the corresponding wiki pages. Rendered packet wiki pages include a Markdown link to the compiled JSON cache entry.

PR preview runs on packet PRs and comments a bounded summary of status, failures, packet roots, and generated paths. Health checks run from `check-wiki-health`; scheduled and manual health workflows may write generated compatibility brief mirrors under `wiki/briefs/` and upload the health report plus brief artifacts. Durable briefing conclusions belong in canonical report, decision, target, claim, or leaf pages.

PR preview also reports `packet_skill_compatibility`. This check is scoped to the standalone packet skill contract: packet root shape, `packet.md`, claim boundary, metric evidence for metric-bearing packets, and strong-claim evidence. It should not duplicate manifest validation or guard checks. Compatibility warnings are review signals; manifest, security, leakage, link, metric mismatch, and policy failures remain the hard-fail mechanisms.

Entity-bearing packet types (`experiment`, `feature`, `model`, `performance`, `preprocessing`, `augmentation`) are expected to include `wiki_plan.yaml`. Preview reports an `entity_coverage` check that looks for `stable_entities`, `affected_pages`, and `semantic_lint`. A warning is not a hard fail, but reviewers should not let important work remain only as an experiment mirror when it should update feature, model, preprocessing, performance, decision, target, claim, or leaderboard pages.

Modern `wiki_plan.yaml` entries should include page roles and promotion reasons. `stable_entities[].page` and `affected_pages[].path` can propose safe synthesis targets under canonical namespaces: `wiki/preprocessing/`, `wiki/features/`, `wiki/models/`, `wiki/performance/`, `wiki/claims/`, `wiki/targets/`, `wiki/decisions/`, or `wiki/reports/`. The synthesis workflow may update those pages if the paths pass repo-side validation. Deprecated namespaces such as `wiki/datasets/`, `wiki/benchmarks/`, `wiki/questions/`, `wiki/submissions/`, `wiki/experiments/`, and `wiki/sources/` are compatibility-only and must not receive substantive new packet output.

Example:

```yaml
stable_entities:
  - id: feature:app-context-windows
    kind: feature
    action: update
    page: wiki/features/app-context-windows.md
    page_role: leaf
    promotion_reason:
      - repeated_across_packets
      - adoption_guidance_needed
affected_pages:
  - path: wiki/features/sleep-lifelog-feature-landscape.md
    role: hub
    expected_change: add_or_update_registry_entry
```

Main ingest direct commits use `[wiki-bot] ingest wiki packets`; reviewed bot PRs use `[wiki-bot][review-required] ingest wiki packets`. The main ingest workflow skips only changes matching those bot-loop conventions. It does not use `[skip ci]`, but default `GITHUB_TOKEN` bot commits may still suppress follow-up workflows under GitHub's event rules; use a PAT or GitHub App token when follow-up workflows must run from bot output.

Before direct commit or bot PR publication, ingest workflows must self-validate generated output. Required checks are `check-wiki-health` and a targeted pytest suite for the touched automation path. The validation payload is rendered into bot PR bodies so reviewers can evaluate bot-created branches even when GitHub does not attach downstream pull request checks.

`check-wiki-health` also enforces the ML/AI hackathon entity scaffold: `wiki/claims/current-supported-claims.md`, `wiki/performance/dacon-leaderboard-history.md`, `wiki/preprocessing/canonical-split-and-leakage-policy.md`, `wiki/team/ml-ai-hackathon-entity-model.md`, `wiki/team/page-taxonomy.md`, `wiki/team/llm-wiki-operating-harness.md`, and `wiki/team/packet-quality-standard.md` must exist. `wiki/latest-context.md` must keep `Current Best`, `Active Risks`, and `Next Actions` sections so a new AI session can quickly understand what is currently believed, what is risky, and what to do next.

LLM synthesis `open_questions` must be structured backlog entries, not free-form strings. Each entry needs `id`, `question`, `priority`, `owner_role`, `merge_blocker`, `needed_evidence`, and `close_condition`; this makes generated questions actionable and reviewable.
