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
        "metrics_to_verify": [{"raw_path": "result.json", "metric_key": "accuracy", "reported_value": 0.82}],
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


def test_guard_surfaces_malformed_direct_manifest_raw_path_entry(tmp_path):
    packet, manifest = make_packet(tmp_path)
    manifest.raw_paths = ["result.json", ["nested-result.json"]]

    result = run_guard_checks(tmp_path, packet, manifest, policy())

    assert any(
        failure.code is FailureCode.INVALID_MANIFEST and "raw_paths" in failure.message
        for failure in result.failures
    )


def test_guard_blocks_secret_content_metric_mismatch_and_wrong_route(tmp_path):
    packet, manifest = make_packet(
        tmp_path,
        intended_wiki_targets=["wiki/models/pkt-1.md"],
        metrics_to_verify=[{"raw_path": "result.json", "metric_key": "accuracy", "reported_value": 0.9}],
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
        metrics_to_verify=[
            {
                "raw_path": "result.json",
                "metric_key": "accuracy",
                "reported_value": 0.9,
                "actual": 0.9,
            }
        ],
    )
    (packet / "result.json").write_text(json.dumps({"accuracy": 0.82}), encoding="utf-8")

    result = run_guard_checks(tmp_path, packet, manifest, policy())

    assert FailureCode.METRIC_MISMATCH in [failure.code for failure in result.failures]


def test_guard_verifies_metric_against_raw_yaml_dotted_key(tmp_path):
    packet, manifest = make_packet(
        tmp_path,
        raw_paths=["metrics.yaml"],
        metrics_to_verify=[{"raw_path": "metrics.yaml", "metric_key": "scores.accuracy", "reported_value": 0.82}],
    )
    (packet / "metrics.yaml").write_text("scores:\n  accuracy: 0.82\n", encoding="utf-8")

    result = run_guard_checks(tmp_path, packet, manifest, policy())

    assert result.failures == []


def test_manifest_rejects_metric_actual_without_raw_path(tmp_path):
    with pytest.raises(IngestFailure) as exc_info:
        make_packet(
            tmp_path,
            metrics_to_verify=[{"name": "accuracy", "expected": 0.82, "actual": 0.82}],
        )

    assert exc_info.value.code is FailureCode.INVALID_MANIFEST


def test_guard_allows_legacy_metric_names_only_with_raw_path(tmp_path):
    packet, manifest = make_packet(
        tmp_path,
        metrics_to_verify=[{"raw_path": "result.json", "name": "accuracy", "expected": 0.82}],
    )

    result = run_guard_checks(tmp_path, packet, manifest, policy())

    assert result.failures == []


def test_guard_reports_grouped_split_overlap(tmp_path):
    packet, manifest = make_packet(
        tmp_path,
        raw_paths=["result.json", "folds.csv"],
        split={"name": "dev", "fold_file": "folds.csv", "group_key": "patient_id"},
    )
    (packet / "folds.csv").write_text(
        "fold,split,patient_id\n0,train,p1\n0,valid,p1\n0,train,p2\n1,valid,p2\n",
        encoding="utf-8",
    )

    result = run_guard_checks(tmp_path, packet, manifest, policy())

    assert FailureCode.SPLIT_GROUP_OVERLAP in [failure.code for failure in result.failures]


def test_guard_allows_grouped_split_non_overlap(tmp_path):
    packet, manifest = make_packet(
        tmp_path,
        raw_paths=["result.json", "folds.csv"],
        split={"name": "dev", "fold_file": "folds.csv", "group_key": "patient_id"},
    )
    (packet / "folds.csv").write_text(
        "split,patient_id\ntrain,p1\ntrain,p2\nvalidation,p3\nval,p4\n",
        encoding="utf-8",
    )

    result = run_guard_checks(tmp_path, packet, manifest, policy())

    assert result.failures == []


def test_guard_rejects_malformed_grouped_split_fold_file(tmp_path):
    packet, manifest = make_packet(
        tmp_path,
        raw_paths=["result.json", "folds.csv"],
        split={"name": "dev", "fold_file": "folds.csv", "group_key": "patient_id"},
    )
    (packet / "folds.csv").write_text('fold,split,patient_id\n0,train,"p1\n0,valid,p2\n', encoding="utf-8")

    result = run_guard_checks(tmp_path, packet, manifest, policy())

    assert any(
        failure.code is FailureCode.INVALID_MANIFEST
        and "split fold_file could not be read" in failure.message
        and failure.path == "folds.csv"
        for failure in result.failures
    )


def test_guard_rejects_grouped_split_fold_file_missing_group_key_column(tmp_path):
    packet, manifest = make_packet(
        tmp_path,
        raw_paths=["result.json", "folds.csv"],
        split={"name": "dev", "fold_file": "folds.csv", "group_key": "patient_id"},
    )
    (packet / "folds.csv").write_text("split,subject_id\ntrain,p1\nvalid,p2\n", encoding="utf-8")

    result = run_guard_checks(tmp_path, packet, manifest, policy())

    assert any(
        failure.code is FailureCode.INVALID_MANIFEST and "patient_id" in failure.message
        for failure in result.failures
    )


def test_guard_rejects_grouped_split_fold_file_missing_split_or_role_column(tmp_path):
    packet, manifest = make_packet(
        tmp_path,
        raw_paths=["result.json", "folds.csv"],
        split={"name": "dev", "fold_file": "folds.csv", "group_key": "patient_id"},
    )
    (packet / "folds.csv").write_text("fold,patient_id\n0,p1\n0,p2\n", encoding="utf-8")

    result = run_guard_checks(tmp_path, packet, manifest, policy())

    assert any(
        failure.code is FailureCode.INVALID_MANIFEST and "split or role" in failure.message
        for failure in result.failures
    )


def test_guard_reports_missing_split_fold_file(tmp_path):
    packet, manifest = make_packet(
        tmp_path,
        raw_paths=["result.json", "folds.csv"],
        split={"name": "dev", "fold_file": "folds.csv", "group_key": "patient_id"},
    )

    result = run_guard_checks(tmp_path, packet, manifest, policy())

    assert FailureCode.MISSING_RAW_FILE in [failure.code for failure in result.failures]


def test_guard_reports_escaped_split_fold_file(tmp_path):
    packet, manifest = make_packet(tmp_path)
    manifest.split.fold_file = "../folds.csv"
    manifest.split.group_key = "patient_id"

    result = run_guard_checks(tmp_path, packet, manifest, policy())

    assert FailureCode.PATH_ESCAPE in [failure.code for failure in result.failures]


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


def test_guard_surfaces_non_string_packet_specific_raw_path(tmp_path):
    packet, manifest = make_packet(
        tmp_path,
        type="augmentation",
        raw_paths={"augmentation": "augmentation.yaml"},
        intended_wiki_targets=["wiki/datasets/pkt-1.md"],
        metrics_to_verify=[],
    )
    (packet / "augmentation.yaml").write_text(
        yaml.safe_dump(
            {
                "source_data_scope": "train split only",
                "generator": "rule based",
                "prompt_or_recipe": "replace approved synonyms",
                "privacy_guard": "no direct identifiers",
                "label_policy": "preserve labels",
                "validation_policy": "spot check",
                "failure_modes": ["semantic drift"],
            }
        ),
        encoding="utf-8",
    )
    manifest.raw_path_map["augmentation"] = ["augmentation.yaml"]

    result = run_guard_checks(tmp_path, packet, manifest, policy())

    assert any(
        failure.code is FailureCode.INVALID_MANIFEST and "augmentation" in failure.message
        for failure in result.failures
    )


def test_guard_enforces_packet_limits(tmp_path):
    packet, manifest = make_packet(tmp_path)
    (packet / "extra.txt").write_text("123456", encoding="utf-8")

    result = run_guard_checks(tmp_path, packet, manifest, policy(max_packet_files=1, max_packet_text_bytes=5))

    codes = [failure.code for failure in result.failures]
    assert FailureCode.PACKET_TOO_LARGE in codes
