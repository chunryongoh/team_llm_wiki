from __future__ import annotations

import json
from pathlib import Path

from .links import lint_wiki_links
from .models import FailureCode, HealthError, HealthReport, as_jsonable
from .render import INDEX_END, INDEX_START

REQUIRED_LATEST_LINKS = {"[[index]]", "[[overview]]", "[[log]]"}


def _generated_block_errors(repo_root: Path) -> list[HealthError]:
    index = repo_root / "wiki" / "index.md"
    if not index.exists():
        return [HealthError(FailureCode.UNBALANCED_GENERATED_BLOCK.value, "wiki/index.md is missing", "wiki/index.md")]
    text = index.read_text(encoding="utf-8")
    if text.count(INDEX_START) != 1 or text.count(INDEX_END) != 1 or text.index(INDEX_START) > text.index(INDEX_END):
        return [
            HealthError(
                FailureCode.UNBALANCED_GENERATED_BLOCK.value,
                "wiki/index.md generated block markers must be balanced",
                "wiki/index.md",
            )
        ]
    return []


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
