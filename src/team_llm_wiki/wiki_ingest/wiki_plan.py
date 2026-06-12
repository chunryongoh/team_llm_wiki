from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .models import IngestFailure
from .route_contract import load_route_contract


@dataclass
class WikiPlanPage:
    path: str
    role: str | None = None
    source: str = "unknown"
    entity_id: str | None = None
    promotion_reason: list[str] = field(default_factory=list)
    expected_change: str | None = None
    migration_compatibility: bool = False


@dataclass
class WikiPlanParseResult:
    path: str
    repo_root: Path = field(default_factory=lambda: Path("."))
    migration_mode: bool = False
    payload: dict[str, Any] = field(default_factory=dict)
    pages: list[WikiPlanPage] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    @property
    def has_leaf(self) -> bool:
        return any(page.role == "leaf" for page in self.pages)

    @property
    def has_hub_or_registry(self) -> bool:
        return any(page.role in {"hub", "registry"} for page in self.pages)

    @property
    def safe_paths(self) -> list[str]:
        paths = [
            page.path
            for page in self.pages
            if _is_safe_synthesis_path(
                page.path,
                repo_root=self.repo_root,
                migration_mode=self.migration_mode and page.migration_compatibility,
            )
        ]
        return list(dict.fromkeys(paths))


def load_wiki_plan(
    packet_root: Path, *, repo_root: Path | None = None, migration_mode: bool = False
) -> WikiPlanParseResult:
    plan_path = packet_root / "wiki_plan.yaml"
    rel = plan_path.as_posix()
    root = repo_root or Path(".")
    if not plan_path.exists():
        return WikiPlanParseResult(path=rel, repo_root=root, migration_mode=migration_mode, warnings=["wiki_plan.yaml is missing"])
    try:
        payload = yaml.safe_load(plan_path.read_text(encoding="utf-8")) or {}
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        return WikiPlanParseResult(
            path=rel,
            repo_root=root,
            migration_mode=migration_mode,
            warnings=[f"wiki_plan.yaml could not be parsed: {exc}"],
        )
    if not isinstance(payload, dict):
        return WikiPlanParseResult(
            path=rel, repo_root=root, migration_mode=migration_mode, warnings=["wiki_plan.yaml must be a mapping"]
        )
    result = WikiPlanParseResult(path=rel, repo_root=root, migration_mode=migration_mode, payload=payload)
    result.pages.extend(_stable_entity_pages(payload.get("stable_entities")))
    result.pages.extend(_affected_pages(payload.get("affected_pages")))
    result.pages = _dedupe_pages(result.pages)
    _validate_page_roles(result)
    _validate_page_paths(result)
    return result


def proposed_synthesis_paths(
    packet_roots: list[Path], *, repo_root: Path | None = None, migration_mode: bool = False
) -> list[str]:
    paths: list[str] = []
    for packet_root in packet_roots:
        result = load_wiki_plan(packet_root, repo_root=repo_root, migration_mode=migration_mode)
        paths.extend(result.safe_paths)
    return list(dict.fromkeys(paths))


def _stable_entity_pages(value: Any) -> list[WikiPlanPage]:
    pages: list[WikiPlanPage] = []
    if not isinstance(value, list):
        return pages
    for item in value:
        if isinstance(item, dict):
            path = item.get("page") or item.get("path")
            if path:
                pages.append(
                    WikiPlanPage(
                        path=str(path),
                        role=_clean_role(item.get("page_role") or item.get("role")),
                        source="stable_entities",
                        entity_id=str(item.get("id", "") or "") or None,
                        promotion_reason=_as_string_list(item.get("promotion_reason")),
                        expected_change=str(item.get("action", "") or "") or None,
                        migration_compatibility=bool(item.get("migration_compatibility")),
                    )
                )
            continue
        if isinstance(item, str):
            path = _path_from_string_hint(item)
            if path:
                pages.append(WikiPlanPage(path=path, source="stable_entities"))
    return pages


def _affected_pages(value: Any) -> list[WikiPlanPage]:
    pages: list[WikiPlanPage] = []
    if not isinstance(value, list):
        return pages
    for item in value:
        if isinstance(item, dict):
            path = item.get("path") or item.get("page")
            if path:
                pages.append(
                    WikiPlanPage(
                        path=str(path),
                        role=_clean_role(item.get("role") or item.get("page_role")),
                        source="affected_pages",
                        promotion_reason=_as_string_list(item.get("promotion_reason")),
                        expected_change=str(item.get("expected_change", "") or "") or None,
                        migration_compatibility=bool(item.get("migration_compatibility")),
                    )
                )
            continue
        if isinstance(item, str):
            path = _path_from_string_hint(item)
            if path:
                pages.append(WikiPlanPage(path=path, source="affected_pages"))
    return pages


def _dedupe_pages(pages: list[WikiPlanPage]) -> list[WikiPlanPage]:
    merged: dict[str, WikiPlanPage] = {}
    for page in pages:
        existing = merged.get(page.path)
        if not existing:
            merged[page.path] = page
            continue
        existing.role = existing.role or page.role
        existing.entity_id = existing.entity_id or page.entity_id
        existing.expected_change = existing.expected_change or page.expected_change
        existing.migration_compatibility = existing.migration_compatibility or page.migration_compatibility
        existing.promotion_reason = list(dict.fromkeys([*existing.promotion_reason, *page.promotion_reason]))
        if page.source not in existing.source.split("+"):
            existing.source = existing.source + "+" + page.source
    return list(merged.values())


def _validate_page_roles(result: WikiPlanParseResult) -> None:
    try:
        allowed_page_roles = load_route_contract(result.repo_root).allowed_page_roles
    except IngestFailure as exc:
        result.warnings.append(exc.message)
        return
    for page in result.pages:
        if not page.role:
            result.warnings.append(f"{page.path} is missing page_role/role")
        elif page.role not in allowed_page_roles:
            result.warnings.append(f"{page.path} has unknown page_role: {page.role}")


def _validate_page_paths(result: WikiPlanParseResult) -> None:
    for page in result.pages:
        if not _is_safe_synthesis_path(
            page.path,
            repo_root=result.repo_root,
            migration_mode=result.migration_mode and page.migration_compatibility,
        ):
            result.warnings.append(f"{page.path} is not an allowed synthesis wiki path")


def _is_safe_synthesis_path(value: str, *, repo_root: Path | None = None, migration_mode: bool = False) -> bool:
    try:
        contract = load_route_contract(repo_root or Path("."))
    except IngestFailure:
        return False
    return contract.is_allowed_synthesis_path(str(value), migration_mode=migration_mode)


def _path_from_string_hint(value: str) -> str | None:
    stripped = value.strip()
    if stripped.startswith("wiki/") and stripped.endswith(".md"):
        return stripped
    return None


def _clean_role(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    role = value.strip().lower().replace("-", "_")
    return role or None


def _as_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)] if str(value).strip() else []
