from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import FailureCode, IngestFailure, PacketManifest, PacketType


PACKET_SCHEMA_LABELS: dict[PacketType, str] = {
    PacketType.PREPROCESSING: "preprocessing",
    PacketType.FEATURE: "features",
    PacketType.MODEL: "model",
    PacketType.PERFORMANCE: "performance",
    PacketType.AUGMENTATION: "augmentation",
}

PACKET_REQUIRED_KEYS: dict[PacketType, tuple[str, ...]] = {
    PacketType.PREPROCESSING: (
        "input_sources",
        "row_identity",
        "target_scope",
        "split_strategy",
        "fold_assignment",
        "leakage_guards",
        "normalization",
        "feature_window_policy",
        "imputation",
        "code_entrypoint",
    ),
    PacketType.FEATURE: ("feature_families",),
    PacketType.MODEL: (
        "family",
        "library_versions",
        "objective",
        "target_handling",
        "hyperparameters",
        "training_strategy",
        "validation_strategy",
        "calibration",
        "ensembling",
        "hardware",
        "inference_contract",
        "weights_policy",
    ),
    PacketType.PERFORMANCE: (
        "primary_metric",
        "metric_definitions",
        "targets",
        "split_id",
        "overall_metrics",
        "target_metrics",
        "baseline_comparison",
        "claim_status",
    ),
    PacketType.AUGMENTATION: (
        "source_data_scope",
        "generator",
        "prompt_or_recipe",
        "privacy_guard",
        "label_policy",
        "validation_policy",
        "failure_modes",
    ),
}

FEATURE_FAMILY_REQUIRED_KEYS = (
    "name",
    "owner",
    "source_modalities",
    "feature_prefixes",
    "anchor",
    "window",
    "formula",
    "expected_dtype",
    "missing_policy",
    "leakage_risk",
    "target_hypothesis",
    "evidence",
    "compute_cost",
    "dependencies",
)


def validate_packet_specific_schema(packet_root: Path, manifest: PacketManifest) -> None:
    packet_type = manifest.type
    if not isinstance(packet_type, PacketType) or packet_type not in PACKET_SCHEMA_LABELS:
        return

    label = PACKET_SCHEMA_LABELS[packet_type]
    raw_path = manifest.raw_path_map.get(label)
    if raw_path is None:
        raise IngestFailure(
            FailureCode.INVALID_MANIFEST,
            f"raw_paths missing required packet-specific entry: {label}",
            {"label": label},
        )
    if not isinstance(raw_path, str):
        raise IngestFailure(
            FailureCode.INVALID_MANIFEST,
            f"raw_paths packet-specific entry must be a string: {label}",
            {"label": label},
        )

    source = _resolve_packet_raw_path(packet_root, raw_path)
    data = _load_mapping(source, raw_path)
    _require_keys(data, PACKET_REQUIRED_KEYS[packet_type], label)

    if packet_type is PacketType.FEATURE:
        _validate_feature_families(data["feature_families"], label)


def _resolve_packet_raw_path(packet_root: Path, raw_path: str) -> Path:
    if not isinstance(raw_path, str):
        raise IngestFailure(
            FailureCode.INVALID_MANIFEST,
            "packet-specific raw path must be a string",
            {"path": str(raw_path)},
        )
    path = Path(raw_path)
    source = (packet_root / path).resolve()
    try:
        source.relative_to(packet_root.resolve())
    except ValueError as exc:
        raise IngestFailure(FailureCode.PATH_ESCAPE, "packet-specific raw path escapes packet root", {"path": raw_path}) from exc
    if not source.exists():
        raise IngestFailure(FailureCode.MISSING_RAW_FILE, "packet-specific raw file is missing", {"path": raw_path})
    return source


def _load_mapping(source: Path, display_path: str) -> dict[str, Any]:
    try:
        data = yaml.safe_load(source.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise IngestFailure(FailureCode.INVALID_MANIFEST, f"invalid packet-specific YAML: {display_path}") from exc
    if not isinstance(data, dict):
        raise IngestFailure(FailureCode.INVALID_MANIFEST, f"packet-specific YAML must be a mapping: {display_path}")
    return data


def _require_keys(data: dict[str, Any], required_keys: tuple[str, ...], label: str) -> None:
    missing = [key for key in required_keys if key not in data]
    if missing:
        raise IngestFailure(
            FailureCode.INVALID_MANIFEST,
            f"{label} packet YAML missing fields: {', '.join(missing)}",
            {"missing": missing},
        )


def _validate_feature_families(value: Any, label: str) -> None:
    if not isinstance(value, list):
        raise IngestFailure(FailureCode.INVALID_MANIFEST, f"{label}.feature_families must be a list")
    for index, family in enumerate(value):
        if not isinstance(family, dict):
            raise IngestFailure(
                FailureCode.INVALID_MANIFEST,
                f"{label}.feature_families[{index}] must be a mapping",
            )
        missing = [key for key in FEATURE_FAMILY_REQUIRED_KEYS if key not in family]
        if missing:
            raise IngestFailure(
                FailureCode.INVALID_MANIFEST,
                f"{label}.feature_families[{index}] missing fields: {', '.join(missing)}",
                {"index": index, "missing": missing},
            )
