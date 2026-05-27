import json
from pathlib import Path

import pytest
import yaml

from team_llm_wiki.wiki_ingest.guards import run_guard_checks
from team_llm_wiki.wiki_ingest.manifest import load_packet_manifest
from team_llm_wiki.wiki_ingest.models import FailureCode, IngestFailure
from team_llm_wiki.wiki_ingest.policy import IngestPolicy


def make_packet(tmp_path: Path, **manifest_overrides):
    packet = tmp_path / "raw" / "users" / "alice" / "pkt-1"
    packet.mkdir(parents=True)
    (packet / "result.json").write_text(json.dumps({"accuracy": 0.82}), encoding="utf-8")
    data = {
        "id": "pkt-1",
        "type": "experiment",
        "title": "Run",
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
        "metrics_to_verify": [{"name": "accuracy", "expected": 0.82, "actual": 0.82}],
    }
    data.update(manifest_overrides)
    (packet / "manifest.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")
    return packet, load_packet_manifest(packet)


def policy(**overrides):
    data = {"agents_text": "rules", "claude_text": "@AGENTS.md", "warnings": []}
    data.update(overrides)
    return IngestPolicy(**data)


def test_guard_allows_valid_packet(tmp_path):
    packet, manifest = make_packet(tmp_path)

    result = run_guard_checks(tmp_path, packet, manifest, policy())

    assert result.failures == []


@pytest.mark.parametrize(
    "filename,code",
    [
        (".env", FailureCode.FORBIDDEN_SECRET_FILE),
        ("secret.pem", FailureCode.FORBIDDEN_SECRET_FILE),
        ("weights.safetensors", FailureCode.MODEL_WEIGHT_FILE),
    ],
)
def test_guard_blocks_forbidden_files_anywhere_under_packet(tmp_path, filename, code):
    packet, manifest = make_packet(tmp_path)
    nested = packet / "nested"
    nested.mkdir()
    (nested / filename).write_text("x", encoding="utf-8")

    result = run_guard_checks(tmp_path, packet, manifest, policy())

    assert code in [failure.code for failure in result.failures]


def test_guard_blocks_missing_raw_file(tmp_path):
    packet, manifest = make_packet(tmp_path, raw_paths=["missing.json"])

    result = run_guard_checks(tmp_path, packet, manifest, policy())

    codes = [failure.code for failure in result.failures]
    assert FailureCode.MISSING_RAW_FILE in codes


def test_guard_blocks_secret_content_metric_mismatch_and_wrong_route(tmp_path):
    packet, manifest = make_packet(
        tmp_path,
        intended_wiki_targets=["wiki/models/pkt-1.md"],
        metrics_to_verify=[{"name": "accuracy", "expected": 0.9, "actual": 0.82}],
    )
    (packet / "notes.txt").write_text("OPENAI_API_KEY=sk-testsecret", encoding="utf-8")

    result = run_guard_checks(tmp_path, packet, manifest, policy())

    codes = [failure.code for failure in result.failures]
    assert FailureCode.SECRET_CONTENT in codes
    assert FailureCode.METRIC_MISMATCH in codes
    assert FailureCode.INVALID_TARGET_ROUTE in codes


def test_guard_verifies_metric_against_raw_json_not_manifest_actual(tmp_path):
    packet, manifest = make_packet(
        tmp_path,
        raw_paths=["result.json"],
        metrics_to_verify=[{"name": "accuracy", "expected": 0.9, "actual": 0.9, "raw_path": "result.json"}],
    )
    (packet / "result.json").write_text(json.dumps({"accuracy": 0.82}), encoding="utf-8")

    result = run_guard_checks(tmp_path, packet, manifest, policy())

    assert FailureCode.METRIC_MISMATCH in [failure.code for failure in result.failures]


def test_guard_verifies_metric_against_raw_yaml_dotted_key(tmp_path):
    packet, manifest = make_packet(
        tmp_path,
        raw_paths=["metrics.yaml"],
        metrics_to_verify=[{"name": "accuracy", "expected": 0.82, "raw_path": "metrics.yaml", "key": "scores.accuracy"}],
    )
    (packet / "metrics.yaml").write_text("scores:\n  accuracy: 0.82\n", encoding="utf-8")

    result = run_guard_checks(tmp_path, packet, manifest, policy())

    assert result.failures == []


def test_guard_surfaces_packet_specific_schema_failure(tmp_path):
    packet, manifest = make_packet(
        tmp_path,
        type="performance",
        raw_paths={"performance": "performance.yaml"},
        intended_wiki_targets=["wiki/performance/pkt-1.md"],
        metrics_to_verify=[],
    )
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

    result = run_guard_checks(tmp_path, packet, manifest, policy())

    assert any(
        failure.code is FailureCode.INVALID_MANIFEST and "overall_metrics" in failure.message
        for failure in result.failures
    )


def test_guard_enforces_packet_limits(tmp_path):
    packet, manifest = make_packet(tmp_path)
    (packet / "extra.txt").write_text("123456", encoding="utf-8")

    result = run_guard_checks(tmp_path, packet, manifest, policy(max_packet_files=1, max_packet_text_bytes=5))

    codes = [failure.code for failure in result.failures]
    assert FailureCode.PACKET_TOO_LARGE in codes
