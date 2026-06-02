from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import PacketManifest, PacketType


STRONG_CLAIM_STATUSES = {"supported", "disputed", "superseded"}
METRIC_PACKET_TYPES = {PacketType.EXPERIMENT, PacketType.PERFORMANCE}
ENTITY_BEARING_PACKET_TYPES = {
    PacketType.EXPERIMENT,
    PacketType.FEATURE,
    PacketType.MODEL,
    PacketType.PERFORMANCE,
    PacketType.PREPROCESSING,
    PacketType.AUGMENTATION,
}
REQUIRED_WIKI_PLAN_FIELDS = {"stable_entities", "affected_pages", "semantic_lint"}


def evaluate_packet_skill_compatibility(
    repo_root: Path,
    *,
    changed_paths: list[str],
    packet_roots: list[Path],
    manifests_by_root: dict[Path, PacketManifest],
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    manifests = {_key(root): manifest for root, manifest in manifests_by_root.items()}

    if not packet_roots:
        return {"status": "skipped", "checks": []}

    non_packet_paths = [path for path in changed_paths if path and not path.startswith("raw/users/")]
    if non_packet_paths:
        checks.append(
            _check(
                "changed_scope",
                "warning",
                "packet skill PR should normally touch only raw/users/** packet files",
                paths=non_packet_paths[:10],
            )
        )
    else:
        checks.append(_check("changed_scope", "pass", "changed paths are limited to raw/users/**"))

    for packet_root in packet_roots:
        rel_root = _rel(repo_root, packet_root)
        manifest = manifests.get(_key(packet_root))
        if manifest is None:
            checks.append(_check("manifest", "fail", "packet root is missing a valid manifest.yaml", rel_root))
            continue

        checks.append(_check("manifest", "pass", "manifest.yaml loaded", rel_root))
        checks.append(_packet_root_shape_check(rel_root))
        checks.append(
            _check(
                "packet_markdown",
                "pass" if (packet_root / "packet.md").exists() else "warning",
                "packet.md exists" if (packet_root / "packet.md").exists() else "packet.md is missing",
                rel_root,
            )
        )
        checks.append(
            _check(
                "claim_boundary",
                "pass" if manifest.claim_boundary.strip() else "fail",
                "claim_boundary is present" if manifest.claim_boundary.strip() else "claim_boundary is missing",
                rel_root,
            )
        )
        checks.append(_metric_claim_check(manifest, rel_root))
        checks.append(_strong_claim_evidence_check(manifest, rel_root))
        checks.append(_entity_coverage_check(packet_root, manifest, rel_root))

    return {"status": _aggregate_status(checks), "checks": checks}


def _packet_root_shape_check(rel_root: str) -> dict[str, Any]:
    parts = Path(rel_root).parts
    if len(parts) >= 5 and parts[0] == "raw" and parts[1] == "users" and parts[4][:4].isdigit():
        return _check("packet_root_shape", "pass", "packet root follows raw/users/<owner>/<category>/<date-slug>", rel_root)
    if len(parts) == 4 and parts[0] == "raw" and parts[1] == "users":
        return _check("packet_root_shape", "warning", "legacy raw/users/<owner>/<packet-id> root shape", rel_root)
    return _check("packet_root_shape", "fail", "packet root is outside the packet skill upload shape", rel_root)


def _metric_claim_check(manifest: PacketManifest, rel_root: str) -> dict[str, Any]:
    if manifest.type in METRIC_PACKET_TYPES and not manifest.metrics_to_verify:
        return _check("metric_claim_evidence", "warning", "metric-bearing packet has no metrics_to_verify entries", rel_root)
    return _check("metric_claim_evidence", "pass", "metric evidence contract is present or not required", rel_root)


def _strong_claim_evidence_check(manifest: PacketManifest, rel_root: str) -> dict[str, Any]:
    if manifest.claim_status in STRONG_CLAIM_STATUSES and not manifest.raw_paths:
        return _check("strong_claim_evidence", "warning", "strong claim has no raw_paths evidence", rel_root)
    return _check("strong_claim_evidence", "pass", "claim evidence level is compatible with packet skill policy", rel_root)


def _entity_coverage_check(packet_root: Path, manifest: PacketManifest, rel_root: str) -> dict[str, Any]:
    if manifest.type not in ENTITY_BEARING_PACKET_TYPES:
        return _check("entity_coverage", "pass", "stable entity coverage is not required for this packet type", rel_root)
    wiki_plan = packet_root / "wiki_plan.yaml"
    if not wiki_plan.exists():
        return _check(
            "entity_coverage",
            "warning",
            "entity-bearing packet is missing wiki_plan.yaml stable entity coverage hints",
            rel_root,
        )
    try:
        payload = yaml.safe_load(wiki_plan.read_text(encoding="utf-8")) or {}
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        return _check("entity_coverage", "warning", "wiki_plan.yaml could not be parsed", rel_root)
    if not isinstance(payload, dict):
        return _check("entity_coverage", "warning", "wiki_plan.yaml must be a mapping", rel_root)
    missing = sorted(field for field in REQUIRED_WIKI_PLAN_FIELDS if not payload.get(field))
    if missing:
        return _check(
            "entity_coverage",
            "warning",
            "wiki_plan.yaml is missing required entity-first fields",
            rel_root,
            missing_fields=missing,
        )
    return _check(
        "entity_coverage",
        "pass",
        "wiki_plan.yaml includes stable entities, affected pages, and semantic lint",
        rel_root,
    )


def _aggregate_status(checks: list[dict[str, Any]]) -> str:
    statuses = {str(check.get("status", "")) for check in checks}
    if "fail" in statuses:
        return "fail"
    if "warning" in statuses:
        return "warning"
    return "pass"


def _check(check_id: str, status: str, message: str, packet_root: str | None = None, **extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {"id": check_id, "status": status, "message": message}
    if packet_root:
        payload["packet_root"] = packet_root
    payload.update(extra)
    return payload


def _rel(repo_root: Path, path: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def _key(path: Path) -> str:
    return path.resolve().as_posix()
