from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from .links import lint_wiki_links
from .route_contract import WikiRouteContract, load_route_contract


def plan_route_migration(repo_root: Path, *, run_id: str, report_path: Path | None = None) -> dict[str, Any]:
    contract = load_route_contract(repo_root)
    report = _build_report(repo_root, contract, run_id=run_id)
    report["status"] = "clean" if not report["inventory"] else "planned"
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
    wiki_root = repo_root / "wiki"
    if wiki_root.exists():
        for path in sorted(wiki_root.rglob("*.md")):
            rel = path.relative_to(repo_root).as_posix()
            if contract.deprecated_namespace_for_path(rel):
                inventory.append(rel)
    planned_moves = [
        {"source": source, "target": target}
        for source, target in sorted(contract.migration_map.items())
        if (repo_root / source).exists()
    ]
    classified = {move["source"] for move in planned_moves}
    generated = [path for path in inventory if contract.is_generated_compatibility_path(path)]
    deferred = [
        {"path": path, "reason": "no migration_map entry yet"}
        for path in inventory
        if path not in classified and path not in generated
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
        "generated_compatibility": generated,
        "deferred_with_reason": deferred,
        "link_rewrites": [],
        "broken_links": [],
        "errors": errors,
    }


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
    replacements = _link_replacements(migration_map)
    for path in sorted(wiki_root.rglob("*.md")):
        rel = path.relative_to(repo_root).as_posix()
        if rel == "wiki/log.md":
            continue
        text = path.read_text(encoding="utf-8")
        updated = text
        for old, new in replacements.items():
            updated = updated.replace(old, new)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            rewrites.append({"path": rel, "status": "rewritten"})
    return rewrites


def _link_replacements(migration_map: dict[str, str]) -> dict[str, str]:
    replacements: dict[str, str] = {}
    for old, new in migration_map.items():
        old_rel = old.removeprefix("wiki/")
        new_rel = new.removeprefix("wiki/")
        replacements[f"]({old_rel})"] = f"]({new_rel})"
        replacements[f"]({old})"] = f"]({new})"
        replacements[f"[[{old_rel.removesuffix('.md')}]]"] = f"[[{new_rel.removesuffix('.md')}]]"
        replacements[f"[[{old.removesuffix('.md')}]]"] = f"[[{new.removesuffix('.md')}]]"
    return replacements


def _write_report(repo_root: Path, report: dict[str, Any], report_path: Path | None) -> None:
    if report_path is None:
        return
    target = report_path if report_path.is_absolute() else repo_root / report_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
