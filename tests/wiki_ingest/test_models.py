from pathlib import Path
import math

import pytest

from team_llm_wiki.wiki_ingest.models import (
    FailureCode,
    IngestFailure,
    MetricCheck,
    PacketManifest,
    PacketType,
    RiskTier,
    as_jsonable,
)


def manifest_data(**overrides):
    data = {
        "id": "pkt-1",
        "type": "experiment",
        "title": "A run",
        "date": "2026-05-27",
        "owner": "alice",
        "status": "submitted",
        "task": "classification",
        "dataset": {"name": "benchmark-set", "version": "v1"},
        "split": {"name": "dev"},
        "model": {"family": "llama"},
        "claim_boundary": "Only applies to the dev split.",
        "claim_status": "tentative",
        "summary": "Run summary.",
        "raw_paths": ["result.json"],
        "intended_wiki_targets": ["wiki/experiments/pkt-1.md"],
    }
    data.update(overrides)
    return data


def test_manifest_full_shape_and_packet_type_coercion():
    manifest = PacketManifest(
        **manifest_data(
            dataset={"name": "benchmark-set", "version": "v1", "hash": "sha256:abc"},
            split={"name": "dev", "group_key": "team", "fold_file": "folds/dev.txt"},
        )
    )

    assert manifest.type is PacketType.EXPERIMENT
    assert manifest.owner == "alice"
    assert manifest.task == "classification"
    assert manifest.dataset.name == "benchmark-set"
    assert manifest.dataset.version == "v1"
    assert manifest.dataset.hash == "sha256:abc"
    assert manifest.split.name == "dev"
    assert manifest.split.group_key == "team"
    assert manifest.split.fold_file == "folds/dev.txt"
    assert manifest.model.family == "llama"
    assert manifest.model.weights_in_repo is False
    assert manifest.claim_boundary == "Only applies to the dev split."
    assert manifest.claim_status == "tentative"
    assert manifest.metrics_to_verify == []
    assert manifest.claims == []


def test_manifest_rejects_unknown_packet_type():
    with pytest.raises(IngestFailure) as exc:
        PacketManifest(**manifest_data(type="other", title="Bad"))

    assert exc.value.code is FailureCode.INVALID_MANIFEST


def test_manifest_minimal_direct_construction_fails():
    with pytest.raises(TypeError):
        PacketManifest(id="pkt-1", type="experiment", title="A run")


def test_manifest_rejects_none_model():
    with pytest.raises(IngestFailure) as exc:
        PacketManifest(**manifest_data(model=None))

    assert exc.value.code is FailureCode.INVALID_MANIFEST


@pytest.mark.parametrize(
    "overrides",
    [
        {"owner": "   "},
        {"task": "   "},
        {"claim_boundary": "   "},
        {"date": "   "},
        {"status": "   "},
        {"summary": "   "},
    ],
)
def test_manifest_rejects_whitespace_required_text_fields(overrides):
    with pytest.raises(IngestFailure) as exc:
        PacketManifest(**manifest_data(**overrides))

    assert exc.value.code is FailureCode.INVALID_MANIFEST


@pytest.mark.parametrize(
    "overrides",
    [
        {"claim_status": "proven"},
        {"split": {"name": "dev", "fold_file": "../folds.txt"}},
        {"dataset": {"name": "benchmark-set"}},
        {"split": {"group_key": "team"}},
        {"model": {"weights_in_repo": True}},
    ],
)
def test_manifest_rejects_invalid_full_shape_fields(overrides):
    with pytest.raises(IngestFailure) as exc:
        PacketManifest(**manifest_data(**overrides))

    assert exc.value.code is FailureCode.INVALID_MANIFEST


@pytest.mark.parametrize(
    "overrides",
    [
        {"id": "pkt-1-"},
        {"id": "a" * 121},
        {"claim_status": ["tentative"]},
        {"claims": [{"status": ["tentative"], "text": "claim"}]},
    ],
)
def test_manifest_rejects_runtime_schema_drift_shapes(overrides):
    with pytest.raises(IngestFailure) as exc:
        PacketManifest(**manifest_data(**overrides))

    assert exc.value.code is FailureCode.INVALID_MANIFEST


@pytest.mark.parametrize(
    "raw_paths",
    [
        {"metrics": ["result.json"]},
        [["result.json"]],
    ],
)
def test_manifest_rejects_non_string_raw_path_entries(raw_paths):
    with pytest.raises(IngestFailure) as exc:
        PacketManifest(**manifest_data(raw_paths=raw_paths))

    assert exc.value.code is FailureCode.INVALID_MANIFEST


def test_metric_check_uses_absolute_tolerance():
    assert MetricCheck(
        raw_path="result.json", metric_key="accuracy", reported_value=0.9, actual=0.9004, tolerance=0.001
    ).is_consistent()
    assert not MetricCheck(
        raw_path="result.json", metric_key="accuracy", reported_value=0.9, actual=0.92, tolerance=0.001
    ).is_consistent()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"raw_path": "result.json", "metric_key": "accuracy", "reported_value": math.nan},
        {"raw_path": "result.json", "metric_key": "accuracy", "reported_value": math.inf},
        {"raw_path": "result.json", "metric_key": "accuracy", "reported_value": 0.9, "tolerance": math.nan},
        {"raw_path": "result.json", "metric_key": "accuracy", "reported_value": 0.9, "expected": math.nan},
        {"raw_path": "result.json", "metric_key": "accuracy", "reported_value": 0.9, "actual": math.inf},
        {"raw_path": "result.json", "name": "accuracy", "expected": math.nan},
    ],
)
def test_metric_check_rejects_non_finite_numeric_values(kwargs):
    with pytest.raises(IngestFailure) as exc:
        MetricCheck(**kwargs)

    assert exc.value.code is FailureCode.INVALID_MANIFEST


def test_as_jsonable_converts_enums_paths_and_dataclasses():
    payload = {
        "tier": RiskTier.BOT_PR,
        "path": Path("wiki/index.md"),
        "metric": MetricCheck(raw_path="result.json", metric_key="f1", reported_value=0.5),
    }

    assert as_jsonable(payload) == {
        "tier": "bot_pr",
        "path": "wiki/index.md",
        "metric": {
            "raw_path": "result.json",
            "metric_key": "f1",
            "reported_value": 0.5,
            "tolerance": 0.0,
            "name": None,
            "key": None,
            "expected": None,
            "actual": None,
        },
    }
