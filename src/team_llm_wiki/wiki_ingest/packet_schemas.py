from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import CLAIM_STATUS_VALUES, FailureCode, IngestFailure, PacketManifest, PacketType


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
        "confusion_matrices",
        "oof_predictions",
        "submission_predictions",
        "baseline_comparison",
        "uncertainty",
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

FEATURE_LEAKAGE_RISK_VALUES = {"low", "medium", "high"}
MODEL_WEIGHTS_POLICY_VALUES = {"not_in_repo", "small_in_repo", "external_uri"}


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
    elif packet_type is PacketType.MODEL:
        _validate_model_packet(data, label)
    elif packet_type is PacketType.PERFORMANCE:
        _validate_performance_packet(data, manifest, label)


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
    if not source.is_file():
        raise IngestFailure(
            FailureCode.INVALID_MANIFEST,
            "packet-specific raw path must be a file",
            {"path": raw_path},
        )
    return source


def _load_mapping(source: Path, display_path: str) -> dict[str, Any]:
    try:
        source_text = source.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise IngestFailure(
            FailureCode.INVALID_MANIFEST,
            f"packet-specific YAML could not be read as UTF-8: {display_path}",
        ) from exc
    try:
        data = yaml.safe_load(source_text)
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
    if not value:
        raise IngestFailure(FailureCode.INVALID_MANIFEST, f"{label}.feature_families must not be empty")
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
        leakage_risk = family["leakage_risk"]
        if not isinstance(leakage_risk, str) or leakage_risk not in FEATURE_LEAKAGE_RISK_VALUES:
            raise IngestFailure(
                FailureCode.INVALID_MANIFEST,
                f"{label}.feature_families[{index}].leakage_risk must be one of: "
                f"{', '.join(sorted(FEATURE_LEAKAGE_RISK_VALUES))}",
                {"index": index, "value": str(leakage_risk)},
            )


def _validate_model_packet(data: dict[str, Any], label: str) -> None:
    weights_policy = data["weights_policy"]
    if not isinstance(weights_policy, str) or weights_policy not in MODEL_WEIGHTS_POLICY_VALUES:
        raise IngestFailure(
            FailureCode.INVALID_MANIFEST,
            f"{label}.weights_policy must be one of: {', '.join(sorted(MODEL_WEIGHTS_POLICY_VALUES))}",
            {"value": str(weights_policy)},
        )


def _validate_performance_packet(data: dict[str, Any], manifest: PacketManifest, label: str) -> None:
    claim_status = data["claim_status"]
    if not isinstance(claim_status, str) or claim_status not in CLAIM_STATUS_VALUES:
        raise IngestFailure(
            FailureCode.INVALID_MANIFEST,
            f"{label}.claim_status must be one of: {', '.join(sorted(CLAIM_STATUS_VALUES))}",
            {"value": str(claim_status)},
        )
    if claim_status != manifest.claim_status:
        raise IngestFailure(
            FailureCode.INVALID_MANIFEST,
            f"{label}.claim_status must match manifest claim_status",
            {"manifest": manifest.claim_status, "performance": claim_status},
        )
