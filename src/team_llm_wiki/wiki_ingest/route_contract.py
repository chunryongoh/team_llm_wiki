from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .models import FailureCode, HealthError, IngestFailure, PacketType


DEFAULT_CONTRACT_PATH = Path("automation/contracts/wiki-route-contract.v1.yaml")
SUPPORTED_VERSION = 1
TOMBSTONE_HEADING = "# Deprecated Compatibility Page"
SUBSTANTIVE_TOMBSTONE_MARKERS = (
    "## Raw Evidence",
    "raw_evidence:",
    "## Metrics",
    "## Claim",
    "## Claims",
    "## Open Questions",
    "## Questions",
    "| metric |",
    "claim_status:",
    "claim_boundary:",
    "metrics_to_verify:",
    "public_lb:",
    "local_oof:",
)


@dataclass(frozen=True)
class NamespaceRoute:
    name: str
    path: str
    required: bool = False


@dataclass(frozen=True)
class DeprecatedNamespace:
    name: str
    path: str
    replacement: str
    allowed_mode: str


@dataclass(frozen=True)
class WikiRouteContract:
    version: int
    canonical_namespaces: dict[str, NamespaceRoute]
    deprecated_namespaces: dict[str, DeprecatedNamespace]
    packet_routes: dict[str, str]
    allowed_page_roles: set[str]
    required_entrypoints: tuple[str, ...]
    required_pages: tuple[str, ...]
    migration_map: dict[str, str]
    source_path: str

    @property
    def canonical_paths(self) -> tuple[str, ...]:
        return tuple(route.path for route in self.canonical_namespaces.values())

    @property
    def deprecated_paths(self) -> tuple[str, ...]:
        return tuple(route.path for route in self.deprecated_namespaces.values())

    def packet_route(self, packet_type: PacketType | str) -> str:
        key = packet_type.value if isinstance(packet_type, PacketType) else str(packet_type)
        try:
            return self.packet_routes[key]
        except KeyError as exc:
            raise IngestFailure(FailureCode.POLICY_CONFLICT, f"missing packet route: {key}") from exc

    def is_canonical_path(self, rel_path: str) -> bool:
        return any(rel_path == prefix or rel_path.startswith(prefix + "/") for prefix in self.canonical_paths)

    def deprecated_namespace_for_path(self, rel_path: str) -> DeprecatedNamespace | None:
        for namespace in self.deprecated_namespaces.values():
            if rel_path == namespace.path or rel_path.startswith(namespace.path + "/"):
                return namespace
        return None

    def is_allowed_synthesis_path(self, rel_path: str, *, migration_mode: bool = False) -> bool:
        path = Path(rel_path)
        parts = path.parts
        if path.is_absolute() or ".." in parts:
            return False
        if len(parts) < 3 or parts[0] != "wiki" or not rel_path.endswith(".md"):
            return False
        if self.is_canonical_path(rel_path):
            return True
        return migration_mode and self.deprecated_namespace_for_path(rel_path) is not None

    def is_generated_compatibility_path(self, rel_path: str) -> bool:
        namespace = self.deprecated_namespace_for_path(rel_path)
        return namespace is not None and namespace.allowed_mode == "generated_compatibility_only"

    def validate_tombstone(self, rel_path: str, text: str) -> list[HealthError]:
        errors: list[HealthError] = []
        namespace = self.deprecated_namespace_for_path(rel_path)
        if namespace is None:
            return errors
        if namespace.allowed_mode == "generated_compatibility_only":
            return errors
        if "page_role: compatibility" not in text:
            errors.append(
                HealthError("invalid_deprecated_tombstone", "tombstone missing page_role: compatibility", rel_path)
            )
        if "status: deprecated" not in text:
            errors.append(HealthError("invalid_deprecated_tombstone", "tombstone missing status: deprecated", rel_path))
        if "canonical_target:" not in text:
            errors.append(HealthError("invalid_deprecated_tombstone", "tombstone missing canonical_target", rel_path))
        headings = [line.strip() for line in text.splitlines() if line.startswith("#")]
        if headings != [TOMBSTONE_HEADING]:
            errors.append(
                HealthError(
                    "invalid_deprecated_tombstone",
                    "tombstone must contain only the deprecated compatibility heading",
                    rel_path,
                )
            )
        for marker in SUBSTANTIVE_TOMBSTONE_MARKERS:
            if marker in text:
                errors.append(
                    HealthError(
                        "deprecated_tombstone_substantive_content",
                        f"tombstone contains substantive marker: {marker}",
                        rel_path,
                    )
                )
        return errors


def load_route_contract(repo_root: Path, contract_path: Path | None = None) -> WikiRouteContract:
    rel_path = contract_path or DEFAULT_CONTRACT_PATH
    path = rel_path if rel_path.is_absolute() else repo_root / rel_path
    if not path.exists():
        raise IngestFailure(FailureCode.POLICY_MISSING, f"route contract is missing: {rel_path}")
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise IngestFailure(FailureCode.POLICY_CONFLICT, f"route contract could not be parsed: {exc}") from exc
    if not isinstance(payload, dict):
        raise IngestFailure(FailureCode.POLICY_CONFLICT, "route contract must be a mapping")
    version = payload.get("version")
    if version != SUPPORTED_VERSION:
        raise IngestFailure(FailureCode.POLICY_CONFLICT, f"unsupported route contract version: {version}")

    canonical = _canonical_namespaces(payload.get("canonical_namespaces"))
    deprecated = _deprecated_namespaces(payload.get("deprecated_namespaces"))
    packet_routes = _packet_routes(payload.get("packet_routes"), canonical)
    allowed_roles = _string_set(payload.get("allowed_page_roles"), "allowed_page_roles")
    required_entrypoints = tuple(_string_list(payload.get("required_entrypoints"), "required_entrypoints"))
    required_pages = tuple(_string_list(payload.get("required_pages"), "required_pages"))
    migration_map = _migration_map(payload.get("migration_map"), deprecated)
    _validate_replacements(deprecated, canonical)
    return WikiRouteContract(
        version=version,
        canonical_namespaces=canonical,
        deprecated_namespaces=deprecated,
        packet_routes=packet_routes,
        allowed_page_roles=allowed_roles,
        required_entrypoints=required_entrypoints,
        required_pages=required_pages,
        migration_map=migration_map,
        source_path=path.as_posix(),
    )


def _canonical_namespaces(value: Any) -> dict[str, NamespaceRoute]:
    if not isinstance(value, dict) or not value:
        raise IngestFailure(FailureCode.POLICY_CONFLICT, "canonical_namespaces must be a non-empty mapping")
    result: dict[str, NamespaceRoute] = {}
    seen_paths: set[str] = set()
    for name, data in value.items():
        if not isinstance(data, dict):
            raise IngestFailure(FailureCode.POLICY_CONFLICT, f"canonical namespace must be a mapping: {name}")
        path = _wiki_dir(data.get("path"), f"canonical namespace {name}")
        if path in seen_paths:
            raise IngestFailure(FailureCode.POLICY_CONFLICT, f"duplicate namespace path: {path}")
        seen_paths.add(path)
        result[str(name)] = NamespaceRoute(str(name), path, bool(data.get("required")))
    return result


def _deprecated_namespaces(value: Any) -> dict[str, DeprecatedNamespace]:
    if not isinstance(value, dict):
        raise IngestFailure(FailureCode.POLICY_CONFLICT, "deprecated_namespaces must be a mapping")
    result: dict[str, DeprecatedNamespace] = {}
    seen_paths: set[str] = set()
    for name, data in value.items():
        if not isinstance(data, dict):
            raise IngestFailure(FailureCode.POLICY_CONFLICT, f"deprecated namespace must be a mapping: {name}")
        path = _wiki_dir(data.get("path"), f"deprecated namespace {name}")
        replacement = _wiki_dir(data.get("replacement"), f"deprecated namespace {name} replacement")
        allowed_mode = str(data.get("allowed_mode", "")).strip()
        if allowed_mode not in {"tombstone_only", "generated_compatibility_only"}:
            raise IngestFailure(FailureCode.POLICY_CONFLICT, f"invalid deprecated namespace mode: {name}")
        if path in seen_paths:
            raise IngestFailure(FailureCode.POLICY_CONFLICT, f"duplicate deprecated namespace path: {path}")
        seen_paths.add(path)
        result[str(name)] = DeprecatedNamespace(str(name), path, replacement, allowed_mode)
    return result


def _packet_routes(value: Any, canonical: dict[str, NamespaceRoute]) -> dict[str, str]:
    if not isinstance(value, dict):
        raise IngestFailure(FailureCode.POLICY_CONFLICT, "packet_routes must be a mapping")
    required = {packet_type.value for packet_type in PacketType}
    missing = sorted(required - set(value))
    if missing:
        raise IngestFailure(FailureCode.POLICY_CONFLICT, f"missing packet route: {missing[0]}")
    canonical_paths = {route.path for route in canonical.values()}
    routes: dict[str, str] = {}
    for key, raw_path in value.items():
        path = _wiki_dir(raw_path, f"packet route {key}")
        if path not in canonical_paths:
            raise IngestFailure(
                FailureCode.POLICY_CONFLICT, f"packet route must target canonical namespace: {key} -> {path}"
            )
        routes[str(key)] = path
    return routes


def _migration_map(value: Any, deprecated: dict[str, DeprecatedNamespace]) -> dict[str, str]:
    if not isinstance(value, dict):
        raise IngestFailure(FailureCode.POLICY_CONFLICT, "migration_map must be a mapping")
    result: dict[str, str] = {}
    for source, target in value.items():
        source_path = _wiki_file(source, f"migration source {source}")
        target_path = _wiki_file(target, f"migration target {source}")
        if not any(source_path == route.path or source_path.startswith(route.path + "/") for route in deprecated.values()):
            raise IngestFailure(FailureCode.POLICY_CONFLICT, f"migration source is not deprecated: {source_path}")
        result[source_path] = target_path
    return result


def _validate_replacements(
    deprecated: dict[str, DeprecatedNamespace], canonical: dict[str, NamespaceRoute]
) -> None:
    canonical_paths = {route.path for route in canonical.values()}
    for namespace in deprecated.values():
        if namespace.replacement not in canonical_paths:
            raise IngestFailure(
                FailureCode.POLICY_CONFLICT, f"deprecated namespace replacement is not canonical: {namespace.name}"
            )


def _wiki_dir(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.startswith("wiki/") or value.endswith(".md") or ".." in Path(value).parts:
        raise IngestFailure(FailureCode.POLICY_CONFLICT, f"{label} must be a relative wiki directory")
    return value.rstrip("/")


def _wiki_file(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.startswith("wiki/") or not value.endswith(".md") or ".." in Path(value).parts:
        raise IngestFailure(FailureCode.POLICY_CONFLICT, f"{label} must be a relative wiki markdown file")
    return value


def _string_list(value: Any, label: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise IngestFailure(FailureCode.POLICY_CONFLICT, f"{label} must be a list of strings")
    return [item.strip() for item in value]


def _string_set(value: Any, label: str) -> set[str]:
    return set(_string_list(value, label))
