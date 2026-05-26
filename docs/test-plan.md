# Test Plan

Focused pytest coverage includes:

- Model defaults, enum coercion, named manifest errors, metric consistency, and JSON conversion.
- Manifest nested fields, `metrics_to_verify`, changed path validation, changed path files, and packet discovery dedupe.
- Policy loading, missing `AGENTS.md`, and Claude import warnings.
- Guards for path escapes, missing raw files, secret content, forbidden secret filenames, model-weight suffixes, metric mismatch, route validation, and packet limits.
- Risk classification for low-risk, high-risk, failures, and governance-tier claims.
- Rendering of canonical routes, source pages, managed index, append-only log, bounded latest context, previous generated entry preservation, required links, and review notes.
- Runner behavior for direct commit, bot PR, hard fail without wiki mutation, skipped zero-packet runs, metric mismatch failure, and changed-page-only link lint.
- CLI JSON output for plan, run, expected errors, report path writes, high-risk output, and health check nonzero failures.
- GitHub Actions helper behavior.
- Full-wiki health checks for clean wiki, broken links, unbalanced generated blocks, incomplete latest context, and JSON report serialization.
