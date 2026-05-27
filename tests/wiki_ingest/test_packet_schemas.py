from pathlib import Path

import pytest
import yaml

from team_llm_wiki.wiki_ingest.manifest import load_packet_manifest
from team_llm_wiki.wiki_ingest.models import FailureCode, IngestFailure
from team_llm_wiki.wiki_ingest.packet_schemas import validate_packet_specific_schema


def write_manifest(root: Path, packet_type: str, raw_paths: dict[str, str]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    data = {
        "id": "pkt-1",
        "packet_type": packet_type,
        "title": "Packet",
        "date": "2026-05-27",
        "owner": "alice",
        "status": "ready",
        "task": "classification",
        "dataset": {"name": "benchmark-set", "version": "v1"},
        "split": {"name": "dev"},
        "model": {"family": "not-applicable"},
        "claim_boundary": "Only applies to this packet.",
        "claim_status": "tentative",
        "summary": "Packet summary.",
        "raw_paths": raw_paths,
        "intended_wiki_targets": [f"wiki/{'performance' if packet_type == 'performance' else packet_type + 's'}/pkt-1.md"],
        "metrics_to_verify": [],
    }
    if packet_type in {"preprocessing", "augmentation"}:
        data["intended_wiki_targets"] = ["wiki/datasets/pkt-1.md"]
    (root / "manifest.yaml").write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def feature_payload(**family_overrides):
    family = {
        "name": "lag-counts",
        "owner": "alice",
        "source_modalities": ["tabular"],
        "feature_prefixes": ["lag_"],
        "anchor": "event_time",
        "window": "previous 7 days",
        "formula": "count(events)",
        "expected_dtype": "float32",
        "missing_policy": "fill with zero",
        "leakage_risk": "low",
        "target_hypothesis": "Recent activity predicts label.",
        "evidence": "raw/results/feature-ablation.yaml",
        "compute_cost": "low",
        "dependencies": ["event_time"],
    }
    family.update(family_overrides)
    return {"feature_families": [family]}


def test_feature_missing_source_modalities_fails(tmp_path):
    packet = tmp_path / "packet"
    write_manifest(packet, "feature", {"features": "features.yaml"})
    payload = feature_payload()
    payload["feature_families"][0].pop("source_modalities")
    (packet / "features.yaml").write_text(yaml.safe_dump(payload), encoding="utf-8")
    manifest = load_packet_manifest(packet)

    with pytest.raises(IngestFailure) as exc:
        validate_packet_specific_schema(packet, manifest)

    assert exc.value.code is FailureCode.INVALID_MANIFEST
    assert "source_modalities" in exc.value.message


def test_complete_feature_family_passes(tmp_path):
    packet = tmp_path / "packet"
    write_manifest(packet, "feature", {"features": "features.yaml"})
    (packet / "features.yaml").write_text(yaml.safe_dump(feature_payload()), encoding="utf-8")
    manifest = load_packet_manifest(packet)

    validate_packet_specific_schema(packet, manifest)


def test_performance_missing_overall_metrics_fails(tmp_path):
    packet = tmp_path / "packet"
    write_manifest(packet, "performance", {"performance": "performance.yaml"})
    (packet / "performance.yaml").write_text(
        yaml.safe_dump(
            {
                "primary_metric": "accuracy",
                "metric_definitions": {"accuracy": "correct / total"},
                "targets": ["overall"],
                "split_id": "dev",
                "target_metrics": {},
                "baseline_comparison": "not compared",
                "claim_status": "tentative",
            }
        ),
        encoding="utf-8",
    )
    manifest = load_packet_manifest(packet)

    with pytest.raises(IngestFailure) as exc:
        validate_packet_specific_schema(packet, manifest)

    assert exc.value.code is FailureCode.INVALID_MANIFEST
    assert "overall_metrics" in exc.value.message


def test_packet_specific_schema_rejects_missing_raw_path_label(tmp_path):
    packet = tmp_path / "packet"
    write_manifest(packet, "performance", {"metrics": "performance.yaml"})
    (packet / "performance.yaml").write_text("overall_metrics: {}\n", encoding="utf-8")
    manifest = load_packet_manifest(packet)

    with pytest.raises(IngestFailure) as exc:
        validate_packet_specific_schema(packet, manifest)

    assert exc.value.code is FailureCode.INVALID_MANIFEST
    assert "performance" in exc.value.message


def test_packet_templates_validate_against_packet_specific_schemas(tmp_path):
    repo_root = Path(__file__).resolve().parents[2]
    template_dir = repo_root / "raw" / "shared" / "templates" / "wiki-packet"

    for template_name in ["preprocessing.yaml", "features.yaml", "model.yaml", "performance.yaml"]:
        packet = tmp_path / template_name.removesuffix(".yaml")
        packet.mkdir()
        template_text = (template_dir / template_name).read_text(encoding="utf-8")
        (packet / "manifest.yaml").write_text(template_text, encoding="utf-8")
        (packet / template_name).write_text(template_text, encoding="utf-8")
        manifest = load_packet_manifest(packet)

        validate_packet_specific_schema(packet, manifest)
