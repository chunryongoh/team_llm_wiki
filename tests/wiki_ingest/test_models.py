from pathlib import Path

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


def test_manifest_full_shape_and_packet_type_coercion():
    manifest = PacketManifest(
        id="pkt-1",
        type="experiment",
        title="A run",
        date="2026-05-27",
        owner="alice",
        status="ready",
        task="classification",
        dataset={"name": "benchmark-set", "version": "v1", "hash": "sha256:abc"},
        split={"name": "dev", "group_key": "team", "fold_file": "folds/dev.txt"},
        model={"family": "llama"},
        claim_boundary="Only applies to the dev split.",
        summary="Run summary.",
        raw_paths=["result.json"],
        intended_wiki_targets=["wiki/experiments/pkt-1.md"],
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
        PacketManifest(id="pkt-1", type="other", title="Bad")

    assert exc.value.code is FailureCode.INVALID_MANIFEST


@pytest.mark.parametrize(
    "overrides",
    [
        {"owner": "   "},
        {"task": "   "},
        {"claim_boundary": "   "},
    ],
)
def test_manifest_rejects_whitespace_owner_task_and_claim_boundary(overrides):
    data = {
        "id": "pkt-1",
        "type": "experiment",
        "title": "A run",
        "owner": "alice",
        "task": "classification",
        "dataset": {"name": "benchmark-set", "version": "v1"},
        "split": {"name": "dev"},
        "claim_boundary": "Only applies to the dev split.",
    }
    data.update(overrides)

    with pytest.raises(IngestFailure) as exc:
        PacketManifest(**data)

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
    data = {
        "id": "pkt-1",
        "type": "experiment",
        "title": "A run",
        "owner": "alice",
        "task": "classification",
        "dataset": {"name": "benchmark-set", "version": "v1"},
        "split": {"name": "dev"},
        "claim_boundary": "Only applies to the dev split.",
    }
    data.update(overrides)

    with pytest.raises(IngestFailure) as exc:
        PacketManifest(**data)

    assert exc.value.code is FailureCode.INVALID_MANIFEST


def test_metric_check_uses_absolute_tolerance():
    assert MetricCheck(name="accuracy", expected=0.9, actual=0.9004, tolerance=0.001).is_consistent()
    assert not MetricCheck(name="accuracy", expected=0.9, actual=0.92, tolerance=0.001).is_consistent()


def test_as_jsonable_converts_enums_paths_and_dataclasses():
    payload = {
        "tier": RiskTier.BOT_PR,
        "path": Path("wiki/index.md"),
        "metric": MetricCheck(name="f1", expected=0.5, actual=0.5),
    }

    assert as_jsonable(payload) == {
        "tier": "bot_pr",
        "path": "wiki/index.md",
        "metric": {"name": "f1", "expected": 0.5, "actual": 0.5, "tolerance": 0.0, "raw_path": None, "key": None},
    }
