from __future__ import annotations

from datetime import date
import json
from pathlib import Path
import posixpath
import re

from .brief import GENERATED_BRIEF_MARKER
from .links import lint_wiki_links
from .models import FailureCode, HealthError, HealthReport, IngestFailure, as_jsonable
from .render import INDEX_END, INDEX_START, LATEST_END, LATEST_START
from .route_contract import DEFAULT_CONTRACT_PATH, WikiRouteContract, load_route_contract

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
    "wiki/performance/dacon-leaderboard-history.md",
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
STALE_TENTATIVE_CLAIM_CODE = "stale_tentative_claim"
STALE_TENTATIVE_MODES = {"error", "warning"}
STALE_TENTATIVE_REGISTRY_PATH = "wiki/claims/stale-tentative-claims.md"


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


def _load_health_contract(repo_root: Path) -> tuple[WikiRouteContract | None, list[HealthError]]:
    try:
        return load_route_contract(repo_root), []
    except IngestFailure as exc:
        return None, [HealthError(exc.code.value, exc.message, DEFAULT_CONTRACT_PATH.as_posix())]


def _required_entity_pages(contract: WikiRouteContract | None) -> set[str]:
    if contract is None:
        return set(REQUIRED_ENTITY_MODEL_PAGES)
    return set(contract.required_pages)


def _entity_model_page_errors(repo_root: Path, required_pages: set[str]) -> list[HealthError]:
    return [
        HealthError(
            "missing_entity_model_page",
            f"required ML/AI hackathon entity page is missing: {rel_path}",
            rel_path,
        )
        for rel_path in sorted(required_pages)
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


def _is_orphan_claim_excluded(
    rel_path: str,
    *,
    required_pages: set[str],
    contract: WikiRouteContract | None,
) -> bool:
    return (
        rel_path in ORPHAN_AND_CLAIM_CHECK_EXCLUDES
        or rel_path in required_pages
        or (contract is not None and contract.deprecated_namespace_for_path(rel_path) is not None)
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
                    STALE_TENTATIVE_CLAIM_CODE,
                    f"{rel_path} has a tentative claim older than 14 days",
                    rel_path,
                )
            )
    return errors


def _tracked_stale_tentative_paths(repo_root: Path) -> set[str]:
    registry = repo_root / STALE_TENTATIVE_REGISTRY_PATH
    if not registry.exists():
        return set()
    text = registry.read_text(encoding="utf-8")
    paths: set[str] = set()
    base = posixpath.dirname(STALE_TENTATIVE_REGISTRY_PATH)
    for target in re.findall(r"\]\(([^)\n#]+\.md)(?:#[^)\n]*)?\)", text):
        normalized = posixpath.normpath(target if target.startswith("wiki/") else posixpath.join(base, target))
        if normalized.startswith("wiki/"):
            paths.add(normalized)
    for target in re.findall(r"\[\[([^]\n#]+)(?:#[^]\n]*)?]]", text):
        normalized = posixpath.normpath(target if target.startswith("wiki/") else posixpath.join("wiki", target))
        if normalized.startswith("wiki/"):
            paths.add(normalized if normalized.endswith(".md") else f"{normalized}.md")
    return paths


def _partition_stale_tentative_claims(
    errors: list[HealthError],
    *,
    tracked_paths: set[str] | None = None,
) -> tuple[list[HealthError], list[HealthError]]:
    remaining: list[HealthError] = []
    stale_tentative_claims: list[HealthError] = []
    for error in errors:
        if error.code == STALE_TENTATIVE_CLAIM_CODE and (tracked_paths is None or error.path in tracked_paths):
            stale_tentative_claims.append(error)
        else:
            remaining.append(error)
    return remaining, stale_tentative_claims


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


def _expanded_health_errors(
    repo_root: Path,
    *,
    contract: WikiRouteContract | None,
    required_pages: set[str],
) -> list[HealthError]:
    wiki_root = repo_root / "wiki"
    if not wiki_root.exists():
        return []
    index_text = (wiki_root / "index.md").read_text(encoding="utf-8") if (wiki_root / "index.md").exists() else ""
    errors: list[HealthError] = []
    for path in sorted(wiki_root.rglob("*.md")):
        rel_path = path.relative_to(repo_root).as_posix()
        text = path.read_text(encoding="utf-8")
        frontmatter, _body = _parse_frontmatter(text)
        if not _is_orphan_claim_excluded(rel_path, required_pages=required_pages, contract=contract):
            is_indexed = _is_indexed(index_text, rel_path)
            if not is_indexed:
                errors.append(HealthError("orphan_wiki_page", f"{rel_path} is missing from wiki/index.md", rel_path))
            errors.extend(_claim_errors(rel_path, frontmatter, text))
            if is_indexed:
                errors.extend(_performance_metric_errors(rel_path, frontmatter, text))
    return errors


def _entity_graph_health(
    repo_root: Path,
    *,
    contract: WikiRouteContract | None,
    required_pages: set[str],
) -> tuple[dict[str, object], list[HealthError]]:
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
        if not _is_orphan_claim_excluded(rel_path, required_pages=required_pages, contract=contract):
            indexed_pages += 1
        if _is_hub_like(rel_path, frontmatter):
            checked_hubs += 1
            heading_count = len(re.findall(r"(?m)^#{2,6}\s+", text))
            leaf_routes = _leaf_route_pattern(contract)
            leaf_link_count = len(re.findall(rf"\[\[(?:{leaf_routes})/[^]\n]+]]", text))
            md_leaf_link_count = len(
                re.findall(rf"\]\((?:{leaf_routes})/[^)\n]+\.md\)", text)
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


def _leaf_route_pattern(contract: WikiRouteContract | None) -> str:
    if contract is None:
        return "features|models|targets|preprocessing|performance"
    leaf_routes = [
        route.path.removeprefix("wiki/")
        for name, route in contract.canonical_namespaces.items()
        if name not in {"claims", "team"}
    ]
    return "|".join(re.escape(route) for route in sorted(leaf_routes))


def _map_tombstone_error(error: HealthError) -> HealthError:
    if error.code == "deprecated_tombstone_substantive_content":
        return HealthError(
            "deprecated_namespace_substantive_content",
            error.message,
            error.path,
        )
    return error


def _deprecated_namespace_findings(
    repo_root: Path,
    contract: WikiRouteContract | None,
    *,
    deprecated_mode: str,
) -> tuple[list[HealthError], list[HealthError]]:
    if contract is None or not (repo_root / "wiki").exists():
        return [], []
    if deprecated_mode not in {"warn_existing", "strict"}:
        return [
            HealthError(
                FailureCode.POLICY_CONFLICT.value,
                f"unsupported deprecated namespace mode: {deprecated_mode}",
                DEFAULT_CONTRACT_PATH.as_posix(),
            )
        ], []

    errors: list[HealthError] = []
    warnings: list[HealthError] = []
    for path in sorted((repo_root / "wiki").rglob("*.md")):
        rel_path = path.relative_to(repo_root).as_posix()
        namespace = contract.deprecated_namespace_for_path(rel_path)
        if namespace is None:
            continue
        text = path.read_text(encoding="utf-8")
        if namespace.allowed_mode == "generated_compatibility_only":
            if GENERATED_BRIEF_MARKER not in text:
                errors.append(
                    HealthError(
                        "invalid_generated_compatibility_page",
                        f"{rel_path} is in generated compatibility namespace without {GENERATED_BRIEF_MARKER}",
                        rel_path,
                    )
                )
            continue
        tombstone_errors = contract.validate_tombstone(rel_path, text)
        if deprecated_mode == "strict":
            errors.extend(_map_tombstone_error(error) for error in tombstone_errors)
            continue
        substantive_errors = [
            _map_tombstone_error(error)
            for error in tombstone_errors
            if error.code == "deprecated_tombstone_substantive_content"
        ]
        if substantive_errors and rel_path in contract.migration_map:
            warnings.append(
                HealthError(
                    "deprecated_namespace_pending_migration",
                    f"{rel_path} contains substantive content but is covered by the route migration map",
                    rel_path,
                )
            )
        else:
            errors.extend(substantive_errors)
    return errors, warnings


def check_wiki_health(
    repo_root: Path,
    report_path: Path | None = None,
    *,
    deprecated_mode: str = "warn_existing",
    stale_tentative_mode: str = "error",
) -> HealthReport:
    checked = [path.relative_to(repo_root).as_posix() for path in (repo_root / "wiki").rglob("*.md")] if (repo_root / "wiki").exists() else []
    contract, contract_errors = _load_health_contract(repo_root)
    required_pages = _required_entity_pages(contract)
    link_checked = [
        path
        for path in checked
        if not (contract is not None and contract.is_generated_compatibility_path(path))
    ]
    entity_graph_health, warnings = _entity_graph_health(
        repo_root,
        contract=contract,
        required_pages=required_pages,
    )
    deprecated_errors, deprecated_warnings = _deprecated_namespace_findings(
        repo_root,
        contract,
        deprecated_mode=deprecated_mode,
    )
    errors = [
        *contract_errors,
        *lint_wiki_links(repo_root, paths=link_checked),
        *_generated_block_errors(repo_root),
        *_latest_context_errors(repo_root),
        *_entity_model_page_errors(repo_root, required_pages),
        *deprecated_errors,
        *_expanded_health_errors(repo_root, contract=contract, required_pages=required_pages),
    ]
    if stale_tentative_mode not in STALE_TENTATIVE_MODES:
        errors.append(
            HealthError(
                FailureCode.POLICY_CONFLICT.value,
                f"unsupported stale tentative claim mode: {stale_tentative_mode}",
                DEFAULT_CONTRACT_PATH.as_posix(),
            )
        )
    if stale_tentative_mode == "warning":
        errors, stale_tentative_warnings = _partition_stale_tentative_claims(errors)
        warnings = [*warnings, *stale_tentative_warnings]
    elif stale_tentative_mode == "error":
        errors, tracked_stale_tentative_warnings = _partition_stale_tentative_claims(
            errors,
            tracked_paths=_tracked_stale_tentative_paths(repo_root),
        )
        warnings = [*warnings, *tracked_stale_tentative_warnings]
    report = HealthReport(
        ok=not errors,
        errors=errors,
        warnings=[*warnings, *deprecated_warnings],
        checked_paths=sorted(checked),
        entity_graph_health=entity_graph_health,
    )
    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(as_jsonable(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report
