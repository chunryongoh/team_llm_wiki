from pathlib import Path

import yaml

from team_llm_wiki.wiki_ingest.manifest import load_packet_manifest
from team_llm_wiki.wiki_ingest.packet_skill_compatibility import evaluate_packet_skill_compatibility


def write_packet(
    root: Path,
    packet_root: Path,
    *,
    packet_type: str = "performance",
    metrics_to_verify: list[dict] | None = None,
    packet_md: bool = True,
    wiki_plan: dict | None = None,
) -> Path:
    packet_root.mkdir(parents=True)
    manifest = {
        "id": packet_root.name,
        "packet_type": packet_type,
        "title": packet_root.name,
        "date": "2026-06-01",
        "owner": "alice",
        "status": "submitted",
        "task": "packet-skill-fixture",
        "dataset": {"name": "sleep-lifelog-2024", "version": "v0"},
        "split": {"name": "groupkfold-subject-3fold-oof"},
        "model": {"family": "lightgbm-catboost"},
        "claim_boundary": "local_oof_diagnostic_only",
        "claim_status": "tentative",
        "summary": "Packet skill compatibility fixture.",
        "raw_paths": ["result.json"],
        "intended_wiki_targets": [f"wiki/experiments/{packet_root.name}.md"],
    }
    if metrics_to_verify is not None:
        manifest["metrics_to_verify"] = metrics_to_verify
    (packet_root / "manifest.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")
    (packet_root / "result.json").write_text('{"logloss": 0.42}', encoding="utf-8")
    if packet_md:
        (packet_root / "packet.md").write_text("# Packet\n\nEvidence summary.\n", encoding="utf-8")
    if wiki_plan is not None:
        (packet_root / "wiki_plan.yaml").write_text(yaml.safe_dump(wiki_plan), encoding="utf-8")
    return packet_root


def test_packet_skill_compatibility_passes_skill_shaped_packet(tmp_path):
    packet_root = write_packet(
        tmp_path,
        tmp_path / "raw" / "users" / "alice" / "performance" / "2026-06-01-lgb-cb-oof",
        metrics_to_verify=[
            {"raw_path": "result.json", "metric_key": "logloss", "reported_value": 0.42}
        ],
        wiki_plan={
            "stable_entities": ["performance:lgb-cb-oof"],
            "affected_pages": ["wiki/performance/2026-06-01-lgb-cb-oof.md"],
            "semantic_lint": ["Keep this as local OOF only."],
        },
    )
    manifest = load_packet_manifest(packet_root)

    result = evaluate_packet_skill_compatibility(
        tmp_path,
        changed_paths=[str(packet_root.relative_to(tmp_path) / "manifest.yaml")],
        packet_roots=[packet_root],
        manifests_by_root={packet_root: manifest},
    )

    assert result["status"] == "pass"
    assert {check["id"] for check in result["checks"]} >= {
        "changed_scope",
        "packet_root_shape",
        "packet_markdown",
        "metric_claim_evidence",
    }


def test_packet_skill_compatibility_warns_for_legacy_root_and_missing_metrics(tmp_path):
    packet_root = write_packet(tmp_path, tmp_path / "raw" / "users" / "alice" / "legacy-packet")
    manifest = load_packet_manifest(packet_root)

    result = evaluate_packet_skill_compatibility(
        tmp_path,
        changed_paths=[str(packet_root.relative_to(tmp_path) / "manifest.yaml"), "README.md"],
        packet_roots=[packet_root],
        manifests_by_root={packet_root: manifest},
    )

    assert result["status"] == "warning"
    warning_ids = {check["id"] for check in result["checks"] if check["status"] == "warning"}
    assert "changed_scope" in warning_ids
    assert "packet_root_shape" in warning_ids
    assert "metric_claim_evidence" in warning_ids


def test_packet_skill_compatibility_fails_missing_manifest(tmp_path):
    packet_root = tmp_path / "raw" / "users" / "alice" / "performance" / "2026-06-01-missing"
    packet_root.mkdir(parents=True)

    result = evaluate_packet_skill_compatibility(
        tmp_path,
        changed_paths=[str(packet_root.relative_to(tmp_path) / "result.json")],
        packet_roots=[packet_root],
        manifests_by_root={},
    )

    assert result["status"] == "fail"
    assert any(check["id"] == "manifest" and check["status"] == "fail" for check in result["checks"])


def test_packet_skill_compatibility_warns_when_entity_bearing_packet_lacks_wiki_plan(tmp_path):
    packet_root = write_packet(
        tmp_path,
        tmp_path / "raw" / "users" / "alice" / "experiments" / "2026-06-01-section07",
        packet_type="experiment",
        metrics_to_verify=[],
    )
    manifest = load_packet_manifest(packet_root)

    result = evaluate_packet_skill_compatibility(
        tmp_path,
        changed_paths=[str(packet_root.relative_to(tmp_path) / "manifest.yaml")],
        packet_roots=[packet_root],
        manifests_by_root={packet_root: manifest},
    )

    assert result["status"] == "warning"
    assert any(check["id"] == "entity_coverage" and check["status"] == "warning" for check in result["checks"])


def test_packet_skill_compatibility_passes_entity_coverage_with_wiki_plan(tmp_path):
    packet_root = write_packet(
        tmp_path,
        tmp_path / "raw" / "users" / "alice" / "experiments" / "2026-06-01-section07",
        packet_type="experiment",
        metrics_to_verify=[],
        wiki_plan={
            "stable_entities": ["model:section07-mix-lgbm-catboost", "feature:section07-feature-policy"],
            "affected_pages": [
                "wiki/models/section07-mix-lgbm-catboost.md",
                "wiki/features/section07-feature-policy.md",
            ],
            "claim_registry_updates": [
                {"status": "tentative", "text": "Notebook-output observation only."}
            ],
            "semantic_lint": ["Do not promote notebook-output scores to leaderboard claims."],
        },
    )
    manifest = load_packet_manifest(packet_root)

    result = evaluate_packet_skill_compatibility(
        tmp_path,
        changed_paths=[str(packet_root.relative_to(tmp_path) / "manifest.yaml")],
        packet_roots=[packet_root],
        manifests_by_root={packet_root: manifest},
    )

    assert result["status"] == "warning"  # experiment metrics still lack metrics_to_verify
    assert any(check["id"] == "entity_coverage" and check["status"] == "pass" for check in result["checks"])
