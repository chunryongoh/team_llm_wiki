from __future__ import annotations

from datetime import date
import json
from pathlib import Path
import re

from .links import lint_wiki_links
from .models import FailureCode, HealthError, HealthReport, as_jsonable
from .render import INDEX_END, INDEX_START, LATEST_END, LATEST_START

REQUIRED_LATEST_LINKS = {"[[index]]", "[[overview]]", "[[log]]"}
REQUIRED_LATEST_OPERATING_SECTIONS = {
    "## Current Best",
    "## Active Risks",
    "## Next Actions",
}
REQUIRED_ENTITY_MODEL_PAGES = {
    "wiki/team/ml-ai-hackathon-entity-model.md",
    "wiki/team/packet-quality-standard.md",
    "wiki/team/page-taxonomy.md",
    "wiki/team/llm-wiki-operating-harness.md",
    "wiki/claims/current-supported-claims.md",
    "wiki/preprocessing/canonical-split-and-leakage-policy.md",
    "wiki/submissions/dacon-leaderboard-history.md",
}
ORPHAN_AND_CLAIM_CHECK_EXCLUDES = {
    "wiki/index.md",
    "wiki/log.md",
    "wiki/latest-context.md",
    "wiki/overview.md",
}
METRIC_LINE_RE = re.compile(r"(?im)^\s*[-*]?\s*[A-Za-z][A-Za-z0-9_. -]{1,40}\s*[:=]\s*\d+(?:\.\d+)?\s*%?\b")
HUB_PAGE_HINTS = ("landscape", "history", "open-questions", "current-supported-claims", "policy", "overview")
LATEST_CONTEXT_SOFT_CHAR_LIMIT = 9000
HUB_SOFT_CHAR_LIMIT = 14000
HUB_SOFT_HEADING_LIMIT = 24


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
    errors = [
        HealthError(
            FailureCode.MISSING_REQUIRED_LATEST_LINK.value,
            f"latest-context missing required link {link}",
            "wiki/latest-context.md",
        )
        for link in sorted(REQUIRED_LATEST_LINKS)
        if link not in text
    ]
    errors.extend(
        HealthError(
            "missing_latest_operating_section",
            f"latest-context missing operating section {section}",
            "wiki/latest-context.md",
        )
        for section in sorted(REQUIRED_LATEST_OPERATING_SECTIONS)
        if section not in text
    )
    return errors


def _entity_model_page_errors(repo_root: Path) -> list[HealthError]:
    return [
        HealthError(
            "missing_entity_model_page",
            f"required ML/AI hackathon entity page is missing: {rel_path}",
            rel_path,
        )
        for rel_path in sorted(REQUIRED_ENTITY_MODEL_PAGES)
        if not (repo_root / rel_path).exists()
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
    return (
        rel_path in ORPHAN_AND_CLAIM_CHECK_EXCLUDES
        or rel_path in REQUIRED_ENTITY_MODEL_PAGES
        or rel_path.startswith("wiki/briefs/")
        or rel_path.startswith("wiki/team/")
        or rel_path.startswith("wiki/") and rel_path.endswith("/README.md")
    )


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
    return _has_raw_evidence(frontmatter, text) or "raw-evidence-backed metric" in text


def _performance_metric_errors(rel_path: str, frontmatter: dict[str, str], text: str) -> list[HealthError]:
    if _has_performance_metric_content(text) and not _has_metric_verification(frontmatter, text):
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
            is_indexed = _is_indexed(index_text, rel_path)
            if not is_indexed:
                errors.append(HealthError("orphan_wiki_page", f"{rel_path} is missing from wiki/index.md", rel_path))
            errors.extend(_claim_errors(rel_path, frontmatter, text))
            if is_indexed:
                errors.extend(_performance_metric_errors(rel_path, frontmatter, text))
    return errors


def _entity_graph_health(repo_root: Path) -> tuple[dict[str, object], list[HealthError]]:
    wiki_root = repo_root / "wiki"
    if not wiki_root.exists():
        return {"status": "skipped", "warnings": 0}, []
    warnings: list[HealthError] = []
    checked_hubs = 0
    leaf_pages = 0
    indexed_pages = 0
    latest = wiki_root / "latest-context.md"
    if latest.exists():
        text = latest.read_text(encoding="utf-8")
        if len(text) > LATEST_CONTEXT_SOFT_CHAR_LIMIT:
            warnings.append(
                HealthError(
                    "latest_context_overloaded",
                    "wiki/latest-context.md is too long for an entrypoint; move details to hub/leaf pages",
                    "wiki/latest-context.md",
                )
            )
        if text.lower().count("raw/users/") > 12:
            warnings.append(
                HealthError(
                    "latest_context_packet_history_dump",
                    "wiki/latest-context.md references many raw packets; keep it as routing context, not packet history",
                    "wiki/latest-context.md",
                )
            )
    for path in sorted(wiki_root.rglob("*.md")):
        rel_path = path.relative_to(repo_root).as_posix()
        text = path.read_text(encoding="utf-8")
        frontmatter, _body = _parse_frontmatter(text)
        page_role = frontmatter.get("page_role") or frontmatter.get("role")
        if page_role == "leaf":
            leaf_pages += 1
        if not _is_orphan_claim_excluded(rel_path):
            indexed_pages += 1
        if _is_hub_like(rel_path, frontmatter):
            checked_hubs += 1
            heading_count = len(re.findall(r"(?m)^#{2,6}\s+", text))
            leaf_link_count = len(re.findall(r"\[\[(?:features|models|targets|preprocessing|submissions)/[^]\n]+]]", text))
            md_leaf_link_count = len(
                re.findall(r"\]\((?:features|models|targets|preprocessing|submissions)/[^)\n]+\.md\)", text)
            )
            if (
                len(text) > HUB_SOFT_CHAR_LIMIT or heading_count > HUB_SOFT_HEADING_LIMIT
            ) and leaf_link_count + md_leaf_link_count < 3:
                warnings.append(
                    HealthError(
                        "hub_without_leaf_routes",
                        f"{rel_path} looks like a large hub but has few leaf routes",
                        rel_path,
                    )
                )
    status = "warning" if warnings else "pass"
    return {
        "status": status,
        "warnings": len(warnings),
        "checked_hubs": checked_hubs,
        "leaf_pages": leaf_pages,
        "indexed_entity_pages": indexed_pages,
    }, warnings


def _is_hub_like(rel_path: str, frontmatter: dict[str, str]) -> bool:
    role = (frontmatter.get("page_role") or frontmatter.get("role") or "").strip()
    if role in {"hub", "registry", "entrypoint"}:
        return True
    return any(hint in rel_path for hint in HUB_PAGE_HINTS)


def check_wiki_health(repo_root: Path, report_path: Path | None = None) -> HealthReport:
    checked = [path.relative_to(repo_root).as_posix() for path in (repo_root / "wiki").rglob("*.md")] if (repo_root / "wiki").exists() else []
    link_checked = [path for path in checked if not path.startswith("wiki/briefs/")]
    entity_graph_health, warnings = _entity_graph_health(repo_root)
    errors = [
        *lint_wiki_links(repo_root, paths=link_checked),
        *_generated_block_errors(repo_root),
        *_latest_context_errors(repo_root),
        *_entity_model_page_errors(repo_root),
        *_expanded_health_errors(repo_root),
    ]
    report = HealthReport(
        ok=not errors,
        errors=errors,
        warnings=warnings,
        checked_paths=sorted(checked),
        entity_graph_health=entity_graph_health,
    )
    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(as_jsonable(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report
