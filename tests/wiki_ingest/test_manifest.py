from pathlib import Path

import pytest
import yaml

from team_llm_wiki.wiki_ingest.manifest import (
    discover_packet_roots,
    load_packet_manifest,
    read_changed_paths_file,
    validate_changed_paths,
)
from team_llm_wiki.wiki_ingest.models import FailureCode, IngestFailure, PacketType


def write_manifest(root: Path, **overrides):
    root.mkdir(parents=True, exist_ok=True)
    data = {
        "id": root.name,
        "packet_type": "experiment",
        "title": "Run title",
        "date": "2026-05-27",
        "owner": "alice",
        "status": "ready",
        "task": "classification",
        "dataset": {"name": "benchmark-set", "version": "v1"},
        "split": {"name": "dev"},
        "claim_boundary": "Only applies to the dev split.",
        "claim_status": "tentative",
        "summary": "Run summary.",
        "raw_paths": ["result.json"],
        "intended_wiki_targets": ["wiki/experiments/pkt-1.md"],
        "metrics_to_verify": [{"name": "accuracy", "expected": 0.8, "actual": 0.8}],
    }
    data.update(overrides)
    (root / "manifest.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")


def test_load_manifest_nested_fields_and_metrics_to_verify(tmp_path):
    packet = tmp_path / "raw" / "users" / "alice" / "pkt-1"
    write_manifest(
        packet,
        packet_type="performance",
        intended_wiki_targets=["wiki/performance/pkt-1.md"],
        claims=[{"status": "supported", "text": "f1 improved"}],
    )

    manifest = load_packet_manifest(packet)

    assert manifest.type is PacketType.PERFORMANCE
    assert manifest.owner == "alice"
    assert manifest.task == "classification"
    assert manifest.dataset.name == "benchmark-set"
    assert manifest.dataset.version == "v1"
    assert manifest.split.name == "dev"
    assert manifest.claim_boundary == "Only applies to the dev split."
    assert manifest.claim_status == "tentative"
    assert manifest.metrics_to_verify[0].name == "accuracy"
    assert manifest.claims[0].status == "supported"
    assert manifest.intended_wiki_targets == ["wiki/performance/pkt-1.md"]


def test_load_manifest_accepts_packet_type_alias_and_raw_path_mapping(tmp_path):
    packet = tmp_path / "raw" / "users" / "alice" / "pkt-1"
    write_manifest(
        packet,
        packet_type="performance",
        type="reference",
        intended_wiki_targets=["wiki/performance/pkt-1.md"],
        raw_paths={"metrics": "metrics/results.yaml", "notes": "notes.md"},
        metrics_to_verify=[{"name": "accuracy", "expected": 0.8, "raw_path": "metrics/results.yaml"}],
    )

    manifest = load_packet_manifest(packet)

    assert manifest.type is PacketType.PERFORMANCE
    assert manifest.raw_paths == ["metrics/results.yaml", "notes.md"]
    assert manifest.raw_path_map == {"metrics": "metrics/results.yaml", "notes": "notes.md"}
    assert manifest.metrics_to_verify[0].raw_path == "metrics/results.yaml"


@pytest.mark.parametrize(
    "field",
    [
        "id",
        "packet_type",
        "title",
        "date",
        "owner",
        "status",
        "task",
        "dataset",
        "split",
        "claim_boundary",
        "summary",
        "raw_paths",
        "intended_wiki_targets",
    ],
)
def test_load_manifest_requires_full_shape_fields_for_new_manifests(tmp_path, field):
    packet = tmp_path / "raw" / "users" / "alice" / "pkt-1"
    write_manifest(packet)
    manifest_path = packet / "manifest.yaml"
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    data.pop(field)
    manifest_path.write_text(yaml.safe_dump(data), encoding="utf-8")

    with pytest.raises(IngestFailure) as exc:
        load_packet_manifest(packet)

    assert exc.value.code is FailureCode.INVALID_MANIFEST


@pytest.mark.parametrize(
    "manifest_overrides",
    [
        {"id": "Bad_ID"},
        {"id": "bad/id"},
        {"id": "bad\nid"},
        {"claims": [{"status": "proven", "text": "unsupported status"}]},
        {"claims": ["not-a-mapping"]},
        {"metrics_to_verify": [{"name": "accuracy", "expected": "high"}]},
        {"metrics_to_verify": ["not-a-mapping"]},
        {"raw_paths": {"metrics": "../escape.json"}},
    ],
)
def test_load_manifest_rejects_invalid_shapes(tmp_path, manifest_overrides):
    packet = tmp_path / "raw" / "users" / "alice" / "pkt-1"
    write_manifest(packet, **manifest_overrides)

    with pytest.raises(IngestFailure) as exc:
        load_packet_manifest(packet)

    assert exc.value.code is FailureCode.INVALID_MANIFEST


def test_validate_changed_paths_rejects_absolute_and_parent_escape(tmp_path):
    with pytest.raises(IngestFailure) as exc:
        validate_changed_paths(tmp_path, ["/tmp/x", "../outside"])

    assert exc.value.code is FailureCode.INVALID_CHANGED_PATH


@pytest.mark.parametrize("changed", ["", "raw\\users\\a\\p\\manifest.yaml", "raw//users/a/p/manifest.yaml"])
def test_validate_changed_paths_rejects_empty_malformed_and_non_manifest(changed, tmp_path):
    with pytest.raises(IngestFailure) as exc:
        validate_changed_paths(tmp_path, [changed])

    assert exc.value.code is FailureCode.INVALID_CHANGED_PATH


def test_changed_path_file_parses_blank_lines_and_comments(tmp_path):
    file = tmp_path / "changed.txt"
    file.write_text("\n# ignored\nraw/users/a/p/manifest.yaml\n", encoding="utf-8")

    assert read_changed_paths_file(file) == ["raw/users/a/p/manifest.yaml"]


def test_discover_packet_roots_dedupes_ancestor_manifest(tmp_path):
    packet = tmp_path / "raw" / "users" / "alice" / "pkt-1"
    write_manifest(packet)
    (packet / "result.json").write_text('{"accuracy": 0.8}', encoding="utf-8")
    changed = [
        "raw/users/alice/pkt-1/manifest.yaml",
        "README.md",
    ]

    roots = discover_packet_roots(tmp_path, changed)

    assert roots == [packet]


def test_discover_packet_roots_accepts_changed_packet_file_under_raw_users(tmp_path):
    packet = tmp_path / "raw" / "users" / "alice" / "pkt-1"
    write_manifest(packet)
    (packet / "result.json").write_text('{"accuracy": 0.8}', encoding="utf-8")

    roots = discover_packet_roots(tmp_path, ["raw/users/alice/pkt-1/result.json"])

    assert roots == [packet]


def test_discover_packet_roots_only_accepts_raw_user_manifest_changes(tmp_path):
    packet = tmp_path / "raw" / "users" / "alice" / "pkt-1"
    write_manifest(packet)
    (packet / "result.json").write_text('{"accuracy": 0.8}', encoding="utf-8")
    other = tmp_path / "raw" / "shared" / "template"
    write_manifest(other)

    roots = discover_packet_roots(
        tmp_path,
        [
            "raw/users/alice/pkt-1/result.json",
            "raw/shared/template/manifest.yaml",
            "raw/users/alice/pkt-1/manifest.yaml",
        ],
    )

    assert roots == [packet]
