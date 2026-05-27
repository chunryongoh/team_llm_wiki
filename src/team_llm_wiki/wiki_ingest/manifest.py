from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import FailureCode, IngestFailure, PacketManifest


def _repo_relative(repo_root: Path, path: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def validate_changed_paths(repo_root: Path, changed_paths: list[str]) -> list[str]:
    validated: list[str] = []
    root = repo_root.resolve()
    for raw in changed_paths:
        if not raw or "\\" in raw or "//" in raw:
            raise IngestFailure(FailureCode.INVALID_CHANGED_PATH, f"invalid changed path: {raw!r}")
        path = Path(raw)
        if path.is_absolute() or ".." in path.parts:
            raise IngestFailure(FailureCode.INVALID_CHANGED_PATH, f"changed path escapes repo: {raw}")
        resolved = (root / path).resolve()
        try:
            rel = resolved.relative_to(root)
        except ValueError as exc:
            raise IngestFailure(FailureCode.INVALID_CHANGED_PATH, f"changed path escapes repo: {raw}") from exc
        rel_text = rel.as_posix()
        validated.append(rel_text)
    return validated


def read_changed_paths_file(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]


def load_packet_manifest(packet_root: Path) -> PacketManifest:
    manifest_path = packet_root / "manifest.yaml"
    if not manifest_path.exists():
        raise IngestFailure(FailureCode.INVALID_MANIFEST, f"missing manifest: {manifest_path}")
    raw: Any = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise IngestFailure(FailureCode.INVALID_MANIFEST, "manifest must be a mapping")
    if "packet_type" in raw:
        raw["type"] = raw["packet_type"]
    known = {
        "id",
        "type",
        "packet_type",
        "title",
        "date",
        "owner",
        "status",
        "task",
        "dataset",
        "split",
        "model",
        "claim_boundary",
        "claim_status",
        "summary",
        "raw_paths",
        "raw_path_map",
        "intended_wiki_targets",
        "metrics_to_verify",
        "claims",
    }
    missing = _missing_required_fields(raw)
    if missing:
        raise IngestFailure(FailureCode.INVALID_MANIFEST, f"manifest missing fields: {', '.join(missing)}")
    for key in ["owner", "task", "claim_boundary"]:
        if not isinstance(raw.get(key), str) or not raw[key].strip():
            raise IngestFailure(FailureCode.INVALID_MANIFEST, f"manifest field must be a non-empty string: {key}")
    if not isinstance(raw.get("model"), dict):
        raise IngestFailure(FailureCode.INVALID_MANIFEST, "manifest model must be a mapping")
    payload = {key: raw[key] for key in known if key in raw and key != "packet_type"}
    payload["extra"] = {key: value for key, value in raw.items() if key not in known}
    return PacketManifest(**payload)


FULL_MANIFEST_REQUIRED = [
    "id",
    "type",
    "title",
    "date",
    "owner",
    "status",
    "task",
    "dataset",
    "split",
    "model",
    "claim_boundary",
    "claim_status",
    "summary",
    "raw_paths",
    "intended_wiki_targets",
]


def _missing_required_fields(raw: dict[str, Any]) -> list[str]:
    return [key for key in FULL_MANIFEST_REQUIRED if key not in raw]


def discover_packet_roots(repo_root: Path, changed_paths: list[str]) -> list[Path]:
    validated = validate_changed_paths(repo_root, changed_paths)
    roots: list[Path] = []
    seen: set[Path] = set()
    repo = repo_root.resolve()
    for changed in validated:
        if not changed.startswith("raw/users/"):
            continue
        changed_rel = Path(changed)
        current = repo / changed_rel
        if current.is_file() or changed_rel.name == "manifest.yaml" or changed_rel.suffix:
            current = current.parent
        for candidate in [current, *current.parents]:
            if candidate == repo.parent:
                break
            if (candidate / "manifest.yaml").exists():
                rel_candidate = candidate.relative_to(repo)
                is_packet_root = (
                    len(rel_candidate.parts) >= 4
                    and rel_candidate.parts[0] == "raw"
                    and rel_candidate.parts[1] == "users"
                )
                if is_packet_root and candidate not in seen:
                    roots.append(candidate)
                    seen.add(candidate)
                break
            if candidate == repo:
                break
    return roots
