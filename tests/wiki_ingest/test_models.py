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


def test_manifest_defaults_and_packet_type_coercion():
    manifest = PacketManifest(id="pkt-1", type="reference", title="A source")

    assert manifest.type is PacketType.REFERENCE
    assert manifest.status == "draft"
    assert manifest.raw_paths == []
    assert manifest.metrics_to_verify == []
    assert manifest.claims == []


def test_manifest_rejects_unknown_packet_type():
    with pytest.raises(IngestFailure) as exc:
        PacketManifest(id="pkt-1", type="other", title="Bad")

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
        "metric": {"name": "f1", "expected": 0.5, "actual": 0.5, "tolerance": 0.0},
    }
