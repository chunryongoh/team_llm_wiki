import json
from pathlib import Path

from jsonschema import Draft202012Validator
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
        "model": {"family": "not-applicable"},
        "claim_boundary": "Only applies to the dev split.",
        "claim_status": "tentative",
        "summary": "Run summary.",
        "raw_paths": ["result.json"],
        "intended_wiki_targets": ["wiki/experiments/pkt-1.md"],
        "metrics_to_verify": [{"name": "accuracy", "expected": 0.8, "actual": 0.8}],
    }
    data.update(overrides)
    (root / "manifest.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")


def load_manifest_schema() -> dict:
    repo_root = Path(__file__).resolve().parents[2]
    return json.loads((repo_root / "automation" / "schemas" / "wiki-packet-manifest.schema.json").read_text())


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
        type="performance",
        intended_wiki_targets=["wiki/performance/pkt-1.md"],
        raw_paths={"metrics": "metrics/results.yaml", "notes": "notes.md"},
        metrics_to_verify=[{"name": "accuracy", "expected": 0.8, "raw_path": "metrics/results.yaml"}],
    )

    manifest = load_packet_manifest(packet)

    assert manifest.type is PacketType.PERFORMANCE
    assert manifest.raw_paths == ["metrics/results.yaml", "notes.md"]
    assert manifest.raw_path_map == {"metrics": "metrics/results.yaml", "notes": "notes.md"}
    assert manifest.metrics_to_verify[0].raw_path == "metrics/results.yaml"


def test_load_manifest_rejects_conflicting_packet_type_alias(tmp_path):
    packet = tmp_path / "raw" / "users" / "alice" / "pkt-1"
    write_manifest(packet, packet_type="performance", type="reference")

    with pytest.raises(IngestFailure) as exc:
        load_packet_manifest(packet)

    assert exc.value.code is FailureCode.INVALID_MANIFEST


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
        "model",
        "claim_boundary",
        "claim_status",
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


def test_load_manifest_rejects_minimal_legacy_manifest(tmp_path):
    packet = tmp_path / "raw" / "users" / "alice" / "pkt-1"
    write_manifest(packet, id="pkt-1", type="reference")
    (packet / "manifest.yaml").write_text(
        yaml.safe_dump({"id": "pkt-1", "type": "reference", "title": "Legacy minimal"}),
        encoding="utf-8",
    )

    with pytest.raises(IngestFailure) as exc:
        load_packet_manifest(packet)

    assert exc.value.code is FailureCode.INVALID_MANIFEST


def test_load_manifest_rejects_partial_full_manifest_without_core_fields(tmp_path):
    packet = tmp_path / "raw" / "users" / "alice" / "pkt-1"
    packet.mkdir(parents=True)
    (packet / "manifest.yaml").write_text(
        yaml.safe_dump(
            {
                "id": "pkt-1",
                "packet_type": "reference",
                "title": "Partial",
                "date": "2026-05-27",
                "status": "ready",
                "summary": "Missing core manifest fields.",
                "raw_paths": ["result.json"],
                "intended_wiki_targets": ["wiki/sources/pkt-1.md"],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(IngestFailure) as exc:
        load_packet_manifest(packet)

    assert exc.value.code is FailureCode.INVALID_MANIFEST


@pytest.mark.parametrize("field", ["owner", "task", "claim_boundary"])
def test_load_manifest_rejects_empty_required_text_fields(tmp_path, field):
    packet = tmp_path / "raw" / "users" / "alice" / "pkt-1"
    write_manifest(packet, **{field: ""})

    with pytest.raises(IngestFailure) as exc:
        load_packet_manifest(packet)

    assert exc.value.code is FailureCode.INVALID_MANIFEST


@pytest.mark.parametrize(
    "manifest_overrides",
    [
        {"owner": "   "},
        {"task": "   "},
        {"claim_boundary": "   "},
        {"dataset": {"name": "   ", "version": "v1"}},
        {"dataset": {"name": "benchmark-set", "version": "   "}},
        {"split": {"name": "   "}},
        {"model": {"family": "   "}},
    ],
)
def test_load_manifest_rejects_whitespace_required_text_fields(tmp_path, manifest_overrides):
    packet = tmp_path / "raw" / "users" / "alice" / "pkt-1"
    write_manifest(packet, **manifest_overrides)

    with pytest.raises(IngestFailure) as exc:
        load_packet_manifest(packet)

    assert exc.value.code is FailureCode.INVALID_MANIFEST


def test_shared_manifest_templates_validate_against_schema():
    repo_root = Path(__file__).resolve().parents[2]
    schema = load_manifest_schema()
    template_paths = sorted((repo_root / "raw" / "shared" / "templates" / "wiki-packet").glob("*.yaml"))

    assert template_paths
    for path in template_paths:
        manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
        Draft202012Validator(schema).validate(manifest)


@pytest.mark.parametrize(
    "field,value",
    [
        ("dataset", {"name": "benchmark-set", "version": "v1", "unexpected": "extra"}),
        ("split", {"name": "dev", "unexpected": "extra"}),
        ("model", {"family": "not-applicable", "unexpected": "extra"}),
    ],
)
def test_manifest_schema_rejects_nested_extras(field, value, tmp_path):
    packet = tmp_path / "raw" / "users" / "alice" / "pkt-1"
    write_manifest(packet, **{field: value})
    manifest = yaml.safe_load((packet / "manifest.yaml").read_text(encoding="utf-8"))

    errors = list(Draft202012Validator(load_manifest_schema()).iter_errors(manifest))

    assert errors


def test_manifest_schema_rejects_conflicting_packet_type_alias(tmp_path):
    packet = tmp_path / "raw" / "users" / "alice" / "pkt-1"
    write_manifest(packet, packet_type="performance", type="reference")
    manifest = yaml.safe_load((packet / "manifest.yaml").read_text(encoding="utf-8"))

    errors = list(Draft202012Validator(load_manifest_schema()).iter_errors(manifest))

    assert errors


def test_manifest_schema_rejects_metric_without_actual_or_raw_path(tmp_path):
    packet = tmp_path / "raw" / "users" / "alice" / "pkt-1"
    write_manifest(packet, metrics_to_verify=[{"name": "accuracy", "expected": 0.8}])
    manifest = yaml.safe_load((packet / "manifest.yaml").read_text(encoding="utf-8"))

    errors = list(Draft202012Validator(load_manifest_schema()).iter_errors(manifest))

    assert errors


@pytest.mark.parametrize(
    "raw_path",
    [
        "",
        "   ",
        "../metrics.json",
        "/metrics.json",
        "nested//metrics.json",
    ],
)
def test_manifest_schema_rejects_unsafe_metric_raw_path(raw_path, tmp_path):
    packet = tmp_path / "raw" / "users" / "alice" / "pkt-1"
    write_manifest(packet, metrics_to_verify=[{"name": "accuracy", "expected": 0.8, "raw_path": raw_path}])
    manifest = yaml.safe_load((packet / "manifest.yaml").read_text(encoding="utf-8"))

    errors = list(Draft202012Validator(load_manifest_schema()).iter_errors(manifest))

    assert errors


@pytest.mark.parametrize(
    "raw_paths",
    [
        ["../escape.json"],
        ["/abs.json"],
        ["nested//result.json"],
        {"metrics": "../escape.json"},
        {"metrics": "/abs.json"},
        {"metrics": "nested//result.json"},
    ],
)
def test_manifest_schema_rejects_unsafe_raw_paths(raw_paths, tmp_path):
    packet = tmp_path / "raw" / "users" / "alice" / "pkt-1"
    write_manifest(packet, raw_paths=raw_paths)
    manifest = yaml.safe_load((packet / "manifest.yaml").read_text(encoding="utf-8"))

    errors = list(Draft202012Validator(load_manifest_schema()).iter_errors(manifest))

    assert errors


@pytest.mark.parametrize(
    "manifest_overrides",
    [
        {"metrics_to_verify": [{"name": "accuracy", "expected": 0.8, "actual": 0.8, "unexpected": "extra"}]},
        {"claims": [{"status": "tentative", "text": "claim", "unexpected": "extra"}]},
    ],
)
def test_manifest_schema_rejects_metric_and_claim_extras(manifest_overrides, tmp_path):
    packet = tmp_path / "raw" / "users" / "alice" / "pkt-1"
    write_manifest(packet, **manifest_overrides)
    manifest = yaml.safe_load((packet / "manifest.yaml").read_text(encoding="utf-8"))

    errors = list(Draft202012Validator(load_manifest_schema()).iter_errors(manifest))

    assert errors


@pytest.mark.parametrize(
    "target",
    [
        "../wiki/experiments/pkt-1.md",
        "/wiki/experiments/pkt-1.md",
        "wiki//experiments/pkt-1.md",
    ],
)
def test_manifest_schema_rejects_unsafe_intended_wiki_targets(target, tmp_path):
    packet = tmp_path / "raw" / "users" / "alice" / "pkt-1"
    write_manifest(packet, intended_wiki_targets=[target])
    manifest = yaml.safe_load((packet / "manifest.yaml").read_text(encoding="utf-8"))

    errors = list(Draft202012Validator(load_manifest_schema()).iter_errors(manifest))

    assert errors


@pytest.mark.parametrize(
    "manifest_overrides",
    [
        {"owner": "   "},
        {"task": "   "},
        {"claim_boundary": "   "},
        {"dataset": {"name": "   ", "version": "v1"}},
        {"dataset": {"name": "benchmark-set", "version": "   "}},
        {"split": {"name": "   "}},
        {"model": {"family": "   "}},
    ],
)
def test_manifest_schema_rejects_whitespace_required_text_fields(tmp_path, manifest_overrides):
    packet = tmp_path / "raw" / "users" / "alice" / "pkt-1"
    write_manifest(packet, **manifest_overrides)
    manifest = yaml.safe_load((packet / "manifest.yaml").read_text(encoding="utf-8"))

    errors = list(Draft202012Validator(load_manifest_schema()).iter_errors(manifest))

    assert errors


@pytest.mark.parametrize(
    "manifest_overrides",
    [
        {"owner": "ali\x01ce"},
        {"task": "class\x01ification"},
        {"claim_boundary": "dev\x01split"},
        {"dataset": {"name": "bench\x01mark", "version": "v1"}},
        {"dataset": {"name": "benchmark-set", "version": "v\x011"}},
        {"split": {"name": "dev\x01"}},
        {"model": {"family": "not\x01applicable"}},
        {"metrics_to_verify": [{"name": "acc\x01uracy", "expected": 0.8, "actual": 0.8}]},
        {"raw_paths": ["res\x01ult.json"]},
        {"intended_wiki_targets": ["wiki/experiments/pkt\x01-1.md"]},
        {"metrics_to_verify": [{"name": "accuracy", "expected": 0.8, "raw_path": "metrics\x01.json"}]},
    ],
)
def test_manifest_schema_rejects_control_character_fields(tmp_path, manifest_overrides):
    packet = tmp_path / "raw" / "users" / "alice" / "pkt-1"
    write_manifest(packet, **manifest_overrides)
    manifest = yaml.safe_load((packet / "manifest.yaml").read_text(encoding="utf-8"))

    errors = list(Draft202012Validator(load_manifest_schema()).iter_errors(manifest))

    assert errors


@pytest.mark.parametrize(
    "manifest_overrides",
    [
        {"id": "Bad_ID"},
        {"id": "bad/id"},
        {"id": "bad\nid"},
        {"claims": [{"status": "proven", "text": "unsupported status"}]},
        {"claims": [{"status": "tentative", "text": "claim", "unexpected": "extra"}]},
        {"claims": ["not-a-mapping"]},
        {"metrics_to_verify": [{"name": "accuracy", "expected": "high"}]},
        {"metrics_to_verify": [{"name": "accuracy", "expected": 0.8}]},
        {"metrics_to_verify": [{"name": "accuracy", "expected": 0.8, "actual": 0.8, "unexpected": "extra"}]},
        {"metrics_to_verify": [{"name": "   ", "expected": 0.8, "actual": 0.8}]},
        {"metrics_to_verify": [{"name": "acc\x01uracy", "expected": 0.8, "actual": 0.8}]},
        {"metrics_to_verify": [{"name": "accuracy", "expected": 0.8, "raw_path": ""}]},
        {"metrics_to_verify": [{"name": "accuracy", "expected": 0.8, "raw_path": "   "}]},
        {"metrics_to_verify": [{"name": "accuracy", "expected": 0.8, "raw_path": "../metrics.json"}]},
        {"metrics_to_verify": [{"name": "accuracy", "expected": 0.8, "raw_path": "/metrics.json"}]},
        {"metrics_to_verify": [{"name": "accuracy", "expected": 0.8, "raw_path": "metrics\x01.json"}]},
        {"metrics_to_verify": ["not-a-mapping"]},
        {"raw_paths": {"metrics": "../escape.json"}},
        {"raw_paths": ["../escape.json"]},
        {"raw_paths": ["/abs.json"]},
        {"raw_paths": ["   "]},
        {"raw_paths": ["res\x01ult.json"]},
        {"intended_wiki_targets": ["../wiki/experiments/pkt-1.md"]},
        {"intended_wiki_targets": ["/wiki/experiments/pkt-1.md"]},
        {"intended_wiki_targets": ["   "]},
        {"intended_wiki_targets": ["wiki/experiments/pkt\x01-1.md"]},
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
