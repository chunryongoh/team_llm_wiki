from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
import re
from typing import Any

from .links import lint_wiki_links
from .route_contract import WikiRouteContract, load_route_contract

MD_LINK_RE = re.compile(r"(\[[^\]]+\]\()([^)]+)(\))")
WIKI_LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def plan_route_migration(repo_root: Path, *, run_id: str, report_path: Path | None = None) -> dict[str, Any]:
    contract = load_route_contract(repo_root)
    report = _build_report(repo_root, contract, run_id=run_id)
    _set_plan_status(report)
    _write_report(repo_root, report, report_path)
    return report


def run_route_migration(
    repo_root: Path,
    *,
    run_id: str,
    report_path: Path | None = None,
    migration_mode: bool = False,
) -> dict[str, Any]:
    contract = load_route_contract(repo_root)
    if not migration_mode:
        report = _build_report(repo_root, contract, run_id=run_id)
        report["status"] = "blocked"
        report["errors"].append(
            {
                "code": "migration_mode_required",
                "message": "run-wiki-route-migration requires explicit migration mode",
            }
        )
        _write_report(repo_root, report, report_path)
        return report

    report = _build_report(repo_root, contract, run_id=run_id)
    if report["errors"]:
        report["status"] = "failed"
        _write_report(repo_root, report, report_path)
        return report
    for item in report["planned_moves"]:
        source = repo_root / item["source"]
        target = repo_root / item["target"]
        if not source.exists():
            report["errors"].append({"code": "migration_source_missing", "path": item["source"]})
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            _append_migrated_notes(target, source)
            source.write_text(_tombstone(item["target"]), encoding="utf-8")
            report["merged"].append(item)
        else:
            shutil.copy2(source, target)
            source.write_text(_tombstone(item["target"]), encoding="utf-8")
            report["moved"].append(item)
    report["link_rewrites"] = _rewrite_links(repo_root, contract.migration_map)
    report["broken_links"] = [error.__dict__ for error in lint_wiki_links(repo_root)]
    report["status"] = "failed" if report["errors"] or report["broken_links"] else "migrated"
    _write_report(repo_root, report, report_path)
    return report


def _build_report(repo_root: Path, contract: WikiRouteContract, *, run_id: str) -> dict[str, Any]:
    inventory: list[str] = []
    already_migrated: list[str] = []
    wiki_root = repo_root / "wiki"
    if wiki_root.exists():
        for path in sorted(wiki_root.rglob("*.md")):
            rel = path.relative_to(repo_root).as_posix()
            if contract.deprecated_namespace_for_path(rel):
                inventory.append(rel)
                if _is_valid_tombstone(contract, rel, path):
                    already_migrated.append(rel)
    planned_moves = [
        {"source": source, "target": target}
        for source, target in sorted(contract.migration_map.items())
        if (repo_root / source).exists() and source not in already_migrated
    ]
    classified = {move["source"] for move in planned_moves}
    generated = [path for path in inventory if contract.is_generated_compatibility_path(path)]
    deferred = [
        {"path": path, "reason": "no migration_map entry yet"}
        for path in inventory
        if path not in classified and path not in generated and path not in already_migrated
    ]
    errors = []
    if deferred:
        errors.append({"code": "migration_inventory_incomplete", "paths": [item["path"] for item in deferred]})
    return {
        "run_id": run_id,
        "status": "planned",
        "contract_version": contract.version,
        "contract_path": contract.source_path,
        "inventory": inventory,
        "planned_moves": planned_moves,
        "moved": [],
        "merged": [],
        "already_migrated": already_migrated,
        "generated_compatibility": generated,
        "deferred_with_reason": deferred,
        "link_rewrites": [],
        "broken_links": [],
        "errors": errors,
    }


def _set_plan_status(report: dict[str, Any]) -> None:
    if report["errors"]:
        report["status"] = "failed"
    elif report["planned_moves"]:
        report["status"] = "planned"
    else:
        report["status"] = "clean"


def _is_valid_tombstone(contract: WikiRouteContract, rel_path: str, path: Path) -> bool:
    namespace = contract.deprecated_namespace_for_path(rel_path)
    if namespace is None or namespace.allowed_mode == "generated_compatibility_only":
        return False
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return False
    return contract.validate_tombstone(rel_path, text) == []


def _append_migrated_notes(target: Path, source: Path) -> None:
    source_text = source.read_text(encoding="utf-8").strip()
    target_text = target.read_text(encoding="utf-8").rstrip()
    if source_text and source_text not in target_text:
        target.write_text(target_text + "\n\n## Migrated Notes\n\n" + source_text + "\n", encoding="utf-8")


def _tombstone(canonical_target: str) -> str:
    wiki_link = canonical_target.removeprefix("wiki/").removesuffix(".md")
    return (
        "---\n"
        "page_role: compatibility\n"
        "status: deprecated\n"
        f"canonical_target: {canonical_target}\n"
        "---\n"
        "# Deprecated Compatibility Page\n\n"
        f"This page has moved to [[{wiki_link}]].\n\n"
        "Do not add new substantive content here. This file exists to preserve historical links and provenance.\n"
    )


def _rewrite_links(repo_root: Path, migration_map: dict[str, str]) -> list[dict[str, str]]:
    rewrites: list[dict[str, str]] = []
    wiki_root = repo_root / "wiki"
    if not wiki_root.exists():
        return rewrites
    for path in sorted(wiki_root.rglob("*.md")):
        rel = path.relative_to(repo_root).as_posix()
        if rel == "wiki/log.md":
            continue
        text = path.read_text(encoding="utf-8")
        updated = _rewrite_markdown_links(repo_root, path, text, migration_map)
        updated = _rewrite_wiki_links(updated, migration_map)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            rewrites.append({"path": rel, "status": "rewritten"})
    return rewrites


def _rewrite_markdown_links(repo_root: Path, source: Path, text: str, migration_map: dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        href = match.group(2)
        if href.startswith(("http://", "https://", "#", "mailto:")):
            return match.group(0)
        clean_href, fragment = _split_fragment(href)
        if not clean_href:
            return match.group(0)
        target = (repo_root / clean_href).resolve() if clean_href.startswith("wiki/") else (source.parent / clean_href).resolve()
        try:
            rel_target = target.relative_to(repo_root.resolve()).as_posix()
        except ValueError:
            return match.group(0)
        canonical = migration_map.get(rel_target)
        if not canonical:
            return match.group(0)
        canonical_path = repo_root / canonical
        new_href = os.path.relpath(canonical_path, source.parent).replace(os.sep, "/")
        return f"{match.group(1)}{new_href}{fragment}{match.group(3)}"

    return MD_LINK_RE.sub(replace, text)


def _rewrite_wiki_links(text: str, migration_map: dict[str, str]) -> str:
    wiki_replacements: dict[str, str] = {}
    for old, new in migration_map.items():
        old_rel = old.removeprefix("wiki/")
        new_rel = new.removeprefix("wiki/")
        wiki_replacements[old_rel.removesuffix(".md")] = new_rel.removesuffix(".md")
        wiki_replacements[old_rel] = new_rel
        wiki_replacements[old.removesuffix(".md")] = new.removesuffix(".md")
        wiki_replacements[old] = new

    def replace(match: re.Match[str]) -> str:
        label = match.group(1)
        target, sep, alias = label.partition("|")
        replacement = wiki_replacements.get(target.strip())
        if not replacement:
            return match.group(0)
        return f"[[{replacement}{sep}{alias}]]"

    return WIKI_LINK_RE.sub(replace, text)


def _split_fragment(href: str) -> tuple[str, str]:
    if "#" not in href:
        return href, ""
    clean, fragment = href.split("#", 1)
    return clean, f"#{fragment}"


def _write_report(repo_root: Path, report: dict[str, Any], report_path: Path | None) -> None:
    if report_path is None:
        return
    target = report_path if report_path.is_absolute() else repo_root / report_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
