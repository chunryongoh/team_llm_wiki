# Test Plan

Focused pytest coverage includes:

- Model defaults, enum coercion, named manifest errors, metric consistency, and JSON conversion.
- Full manifest required fields, nested `dataset`/`split`/`model` fields, `metrics_to_verify`, changed path validation, changed path files, and packet discovery dedupe.
- Packet-specific YAML required fields for preprocessing, feature, model, performance, and augmentation packets.
- Policy loading, missing `AGENTS.md`, and Claude import warnings.
- Guards for path escapes, missing raw files, secret content, forbidden secret filenames, model-weight suffixes, raw-only metric mismatch, route validation, grouped split overlap, and packet limits.
- Risk classification for low-risk, high-risk, failures, and governance-tier claims.
- Rendering of canonical routes, source pages, managed index, append-only log, bounded latest context, previous generated entry preservation, required links, review notes, lineage frontmatter, and compiled packet JSON cache files.
- Runner behavior for direct commit, bot PR, hard fail without wiki mutation, skipped zero-packet runs, metric mismatch failure, and changed-page-only link lint.
- CLI JSON output for plan, preview, run, expected errors, report path writes, high-risk output, health check nonzero failures, and daily brief generation.
- GitHub Actions helper behavior, including `[wiki-bot]` loop skips, PR preview comments, and workflow output files.
- Full-wiki health checks for clean wiki, broken links, unbalanced generated blocks, incomplete latest context, and JSON report serialization.

Final verification for spec-complete changes runs:

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q`
- `python -m pip install -e . --dry-run`
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m team_llm_wiki.cli check-wiki-health --repo-root . --report-path /tmp/team-llm-wiki-health-spec-complete.json`
- PyYAML parsing for all `.github/workflows/*.yml`
- `git diff --check`
