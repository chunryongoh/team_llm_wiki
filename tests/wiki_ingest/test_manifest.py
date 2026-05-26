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
        "type": "experiment",
        "title": "Run title",
        "raw_paths": ["result.json"],
        "metrics_to_verify": [{"name": "accuracy", "expected": 0.8, "actual": 0.8}],
    }
    data.update(overrides)
    (root / "manifest.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")


def test_load_manifest_nested_fields_and_metrics_to_verify(tmp_path):
    packet = tmp_path / "raw" / "users" / "alice" / "pkt-1"
    write_manifest(
        packet,
        type="performance",
        claims=[{"status": "supported", "text": "f1 improved"}],
        intended_wiki_targets=["wiki/performance/pkt-1.md"],
    )

    manifest = load_packet_manifest(packet)

    assert manifest.type is PacketType.PERFORMANCE
    assert manifest.metrics_to_verify[0].name == "accuracy"
    assert manifest.claims[0].status == "supported"
    assert manifest.intended_wiki_targets == ["wiki/performance/pkt-1.md"]


def test_validate_changed_paths_rejects_absolute_and_parent_escape(tmp_path):
    with pytest.raises(IngestFailure) as exc:
        validate_changed_paths(tmp_path, ["/tmp/x", "../outside"])

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
        "raw/users/alice/pkt-1/result.json",
        "README.md",
    ]

    roots = discover_packet_roots(tmp_path, changed)

    assert roots == [packet]
