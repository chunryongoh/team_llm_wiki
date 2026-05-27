from __future__ import annotations

from datetime import date
import json
from pathlib import Path
import re

from .links import lint_wiki_links
from .models import FailureCode, HealthError, HealthReport, as_jsonable
from .render import INDEX_END, INDEX_START, LATEST_END, LATEST_START

REQUIRED_LATEST_LINKS = {"[[index]]", "[[overview]]", "[[log]]"}
ORPHAN_AND_CLAIM_CHECK_EXCLUDES = {
    "wiki/index.md",
    "wiki/log.md",
    "wiki/latest-context.md",
    "wiki/overview.md",
}
METRIC_LINE_RE = re.compile(r"(?im)^\s*[-*]?\s*[A-Za-z][A-Za-z0-9_. -]{1,40}\s*[:=]\s*\d+(?:\.\d+)?\s*%?\b")


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


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    end_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break
    if end_index is None:
        return {}, text

    frontmatter: dict[str, str] = {}
    current_key: str | None = None
    for line in lines[1:end_index]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith((" ", "\t")) and ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip()
            if current_key:
                frontmatter[current_key] = value.strip().strip("\"'")
            continue
        if current_key and line.startswith((" ", "\t")):
            frontmatter[current_key] = (frontmatter[current_key] + "\n" + line.strip()).strip()
    body = "\n".join(lines[end_index + 1 :])
    if text.endswith("\n"):
        body += "\n"
    return frontmatter, body


def _is_orphan_claim_excluded(rel_path: str) -> bool:
    return rel_path in ORPHAN_AND_CLAIM_CHECK_EXCLUDES or rel_path.startswith("wiki/team/")


def _has_raw_evidence(frontmatter: dict[str, str], text: str) -> bool:
    return "raw_evidence:" in text or "related_raw" in frontmatter


def _is_indexed(index_text: str, rel_path: str) -> bool:
    wiki_rel = rel_path.removeprefix("wiki/")
    wiki_link = f"[[{wiki_rel.removesuffix('.md')}]]"
    return rel_path in index_text or wiki_rel in index_text or wiki_link in index_text


def _claim_errors(rel_path: str, frontmatter: dict[str, str], text: str) -> list[HealthError]:
    claim_status = frontmatter.get("claim_status", "").strip()
    errors: list[HealthError] = []
    if claim_status == "supported" and not _has_raw_evidence(frontmatter, text):
        errors.append(
            HealthError(
                "supported_claim_missing_raw",
                f"{rel_path} has claim_status supported without raw evidence",
                rel_path,
            )
        )
    if claim_status == "tentative":
        try:
            claim_date = date.fromisoformat(frontmatter.get("date", "").strip())
        except ValueError:
            claim_date = None
        if claim_date and (date.today() - claim_date).days > 14:
            errors.append(
                HealthError(
                    "stale_tentative_claim",
                    f"{rel_path} has a tentative claim older than 14 days",
                    rel_path,
                )
            )
    return errors


def _has_performance_metric_content(text: str) -> bool:
    return "## Metrics" in text or bool(METRIC_LINE_RE.search(text))


def _has_metric_verification(frontmatter: dict[str, str], text: str) -> bool:
    return _has_raw_evidence(frontmatter, text) or "raw-evidence-backed metric" in text or "metrics_to_verify" in text


def _performance_metric_errors(rel_path: str, frontmatter: dict[str, str], text: str) -> list[HealthError]:
    page_type = frontmatter.get("type", "").strip()
    is_performance_page = rel_path.startswith("wiki/performance/") or page_type == "performance"
    if is_performance_page and _has_performance_metric_content(text) and not _has_metric_verification(frontmatter, text):
        return [
            HealthError(
                "performance_metric_unverified",
                f"{rel_path} has performance metrics without raw evidence or metric verification",
                rel_path,
            )
        ]
    return []


def _expanded_health_errors(repo_root: Path) -> list[HealthError]:
    wiki_root = repo_root / "wiki"
    if not wiki_root.exists():
        return []
    index_text = (wiki_root / "index.md").read_text(encoding="utf-8") if (wiki_root / "index.md").exists() else ""
    errors: list[HealthError] = []
    for path in sorted(wiki_root.rglob("*.md")):
        rel_path = path.relative_to(repo_root).as_posix()
        text = path.read_text(encoding="utf-8")
        frontmatter, _body = _parse_frontmatter(text)
        if not _is_orphan_claim_excluded(rel_path):
            if not _is_indexed(index_text, rel_path):
                errors.append(HealthError("orphan_wiki_page", f"{rel_path} is missing from wiki/index.md", rel_path))
            errors.extend(_claim_errors(rel_path, frontmatter, text))
        errors.extend(_performance_metric_errors(rel_path, frontmatter, text))
    return errors


def check_wiki_health(repo_root: Path, report_path: Path | None = None) -> HealthReport:
    checked = [path.relative_to(repo_root).as_posix() for path in (repo_root / "wiki").rglob("*.md")] if (repo_root / "wiki").exists() else []
    errors = [
        *lint_wiki_links(repo_root),
        *_generated_block_errors(repo_root),
        *_latest_context_errors(repo_root),
        *_expanded_health_errors(repo_root),
    ]
    report = HealthReport(ok=not errors, errors=errors, checked_paths=sorted(checked))
    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(as_jsonable(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report
