from __future__ import annotations

import json
from pathlib import Path

from .links import lint_wiki_links
from .models import FailureCode, HealthError, HealthReport, as_jsonable
from .render import INDEX_END, INDEX_START, LATEST_END, LATEST_START

REQUIRED_LATEST_LINKS = {"[[index]]", "[[overview]]", "[[log]]"}


def _generated_block_errors(repo_root: Path) -> list[HealthError]:
    checks = [
        ("wiki/index.md", INDEX_START, INDEX_END),
        ("wiki/latest-context.md", LATEST_START, LATEST_END),
    ]
    errors: list[HealthError] = []
    for rel, start, end in checks:
        path = repo_root / rel
        if not path.exists():
            errors.append(HealthError(FailureCode.UNBALANCED_GENERATED_BLOCK.value, f"{rel} is missing", rel))
            continue
        text = path.read_text(encoding="utf-8")
        if text.count(start) != 1 or text.count(end) != 1 or text.index(start) > text.index(end):
            errors.append(
                HealthError(
                    FailureCode.UNBALANCED_GENERATED_BLOCK.value,
                    f"{rel} generated block markers must be balanced",
                    rel,
                )
            )
    return errors


def _latest_context_errors(repo_root: Path) -> list[HealthError]:
    latest = repo_root / "wiki" / "latest-context.md"
    if not latest.exists():
        return [
            HealthError(
                FailureCode.MISSING_REQUIRED_LATEST_LINK.value,
                "wiki/latest-context.md is missing",
                "wiki/latest-context.md",
            )
        ]
    text = latest.read_text(encoding="utf-8")
    return [
        HealthError(
            FailureCode.MISSING_REQUIRED_LATEST_LINK.value,
            f"latest-context missing required link {link}",
            "wiki/latest-context.md",
        )
        for link in sorted(REQUIRED_LATEST_LINKS)
        if link not in text
    ]


def check_wiki_health(repo_root: Path, report_path: Path | None = None) -> HealthReport:
    checked = [path.relative_to(repo_root).as_posix() for path in (repo_root / "wiki").rglob("*.md")] if (repo_root / "wiki").exists() else []
    errors = [*lint_wiki_links(repo_root), *_generated_block_errors(repo_root), *_latest_context_errors(repo_root)]
    report = HealthReport(ok=not errors, errors=errors, checked_paths=sorted(checked))
    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(as_jsonable(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report
