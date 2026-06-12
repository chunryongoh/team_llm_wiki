import os
from pathlib import Path

import pytest
import yaml

from team_llm_wiki.wiki_ingest.manifest import load_packet_manifest
from team_llm_wiki.wiki_ingest.packet_skill_compatibility import evaluate_packet_skill_compatibility


ROUTE_CONTRACT = Path("automation/contracts/wiki-route-contract.v1.yaml")
PACKET_SKILL_CONTRACT = Path("references/wiki-route-contract.v1.yaml")


def seed_route_contract(root: Path) -> None:
    target = root / ROUTE_CONTRACT
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(ROUTE_CONTRACT.read_text(encoding="utf-8"), encoding="utf-8")


def write_packet(
    root: Path,
    packet_root: Path,
    *,
    packet_type: str = "performance",
    metrics_to_verify: list[dict] | None = None,
    packet_md: bool = True,
    wiki_plan: dict | None = None,
) -> Path:
    seed_route_contract(root)
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
        "intended_wiki_targets": [f"wiki/reports/{packet_root.name}.md"],
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


def test_packet_skill_contract_parity_with_source_repo():
    candidates = [
        os.environ.get("TEAM_LLM_WIKI_PACKET_SKILL_REPO"),
        "/home/chunoh/.config/superpowers/worktrees/team-llm-wiki-packet-skill/wiki-policy-structure-renovation",
        "/home/chunoh/ETRI/team-llm-wiki-packet-skill",
    ]
    skill_repo = next((Path(path) for path in candidates if path and (Path(path) / PACKET_SKILL_CONTRACT).exists()), None)
    if skill_repo is None:
        pytest.skip("team-llm-wiki-packet-skill checkout is not available for local parity check")

    source_contract = Path("automation/contracts/wiki-route-contract.v1.yaml").read_text(encoding="utf-8")
    skill_contract = (skill_repo / PACKET_SKILL_CONTRACT).read_text(encoding="utf-8")

    assert skill_contract == source_contract


def test_packet_skill_compatibility_passes_skill_shaped_packet(tmp_path):
    packet_root = write_packet(
        tmp_path,
        tmp_path / "raw" / "users" / "alice" / "performance" / "2026-06-01-lgb-cb-oof",
        metrics_to_verify=[
            {"raw_path": "result.json", "metric_key": "logloss", "reported_value": 0.42}
        ],
        wiki_plan={
            "stable_entities": [
                {
                    "id": "performance:lgb-cb-oof",
                    "kind": "performance",
                    "action": "update",
                    "page": "wiki/performance/2026-06-01-lgb-cb-oof.md",
                    "page_role": "leaf",
                    "promotion_reason": ["independent_claim_status_needed"],
                }
            ],
            "affected_pages": [
                {
                    "path": "wiki/claims/current-supported-claims.md",
                    "role": "registry",
                    "expected_change": "preserve local OOF claim boundary",
                }
            ],
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
            "stable_entities": [
                {
                    "id": "model:section07-mix-lgbm-catboost",
                    "kind": "model",
                    "action": "update",
                    "page": "wiki/models/section07-mix-lgbm-catboost.md",
                    "page_role": "leaf",
                    "promotion_reason": ["adoption_guidance_needed"],
                },
                {
                    "id": "feature:section07-feature-policy",
                    "kind": "feature",
                    "action": "update",
                    "page": "wiki/features/section07-feature-policy.md",
                    "page_role": "leaf",
                    "promotion_reason": ["target_specific_ablation_needed"],
                },
                ],
                "affected_pages": [
                    {
                        "path": "wiki/targets/section07-followup-backlog.md",
                        "role": "hub",
                        "expected_change": "update closeable follow-up question",
                    }
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


def test_packet_skill_compatibility_warns_for_string_only_wiki_plan(tmp_path):
    packet_root = write_packet(
        tmp_path,
        tmp_path / "raw" / "users" / "alice" / "performance" / "2026-06-01-string-plan",
        metrics_to_verify=[
            {"raw_path": "result.json", "metric_key": "logloss", "reported_value": 0.42}
        ],
        wiki_plan={
            "stable_entities": ["performance:string-plan"],
            "affected_pages": ["wiki/performance/2026-06-01-string-plan.md"],
            "semantic_lint": ["String-only plan should warn."],
        },
    )
    manifest = load_packet_manifest(packet_root)

    result = evaluate_packet_skill_compatibility(
        tmp_path,
        changed_paths=[str(packet_root.relative_to(tmp_path) / "manifest.yaml")],
        packet_roots=[packet_root],
        manifests_by_root={packet_root: manifest},
    )

    entity_check = next(check for check in result["checks"] if check["id"] == "entity_coverage")
    assert entity_check["status"] == "warning"
    assert any("stable_entities should name" in warning or "page_role" in warning for warning in entity_check["warnings"])


def test_packet_skill_compatibility_warns_on_deprecated_wiki_plan_path(tmp_path):
    packet_root = write_packet(
        tmp_path,
        tmp_path / "raw" / "users" / "alice" / "performance" / "2026-06-12-old-route",
        metrics_to_verify=[
            {"raw_path": "result.json", "metric_key": "logloss", "reported_value": 0.42}
        ],
        wiki_plan={
            "stable_entities": [
                {
                    "id": "performance:old-route",
                    "kind": "performance",
                    "action": "update",
                    "page": "wiki/benchmarks/old-route.md",
                    "page_role": "leaf",
                    "promotion_reason": ["deprecated_route_check"],
                }
            ],
            "affected_pages": [
                {
                    "path": "wiki/performance/current-results.md",
                    "role": "hub",
                    "expected_change": "keep canonical hub updated",
                }
            ],
            "semantic_lint": ["Old route should be rejected."],
        },
    )
    manifest = load_packet_manifest(packet_root)

    result = evaluate_packet_skill_compatibility(
        tmp_path,
        changed_paths=[str(packet_root.relative_to(tmp_path) / "manifest.yaml")],
        packet_roots=[packet_root],
        manifests_by_root={packet_root: manifest},
    )

    entity_check = next(check for check in result["checks"] if check["id"] == "entity_coverage")
    assert entity_check["status"] == "warning"
    assert any("deprecated" in warning.lower() for warning in entity_check["warnings"])
