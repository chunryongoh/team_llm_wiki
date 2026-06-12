from pathlib import Path

import yaml

from team_llm_wiki.wiki_ingest.wiki_plan import load_wiki_plan


def test_wiki_plan_accepts_canonical_pages(tmp_path):
    packet_root = tmp_path / "raw" / "users" / "alice" / "performance" / "2026-06-12-run"
    packet_root.mkdir(parents=True)
    (packet_root / "wiki_plan.yaml").write_text(
        yaml.safe_dump(
            {
                "stable_entities": [
                    {
                        "id": "performance:dacon-public-05917",
                        "kind": "performance",
                        "page": "wiki/performance/dacon-public-05917-lgbm-xgb-anchor-reference.md",
                        "page_role": "leaf",
                    }
                ],
                "affected_pages": [{"path": "wiki/claims/current-supported-claims.md", "role": "registry"}],
            }
        ),
        encoding="utf-8",
    )

    result = load_wiki_plan(packet_root, repo_root=Path("."))

    assert result.ok
    assert result.safe_paths == [
        "wiki/performance/dacon-public-05917-lgbm-xgb-anchor-reference.md",
        "wiki/claims/current-supported-claims.md",
    ]


def test_wiki_plan_rejects_deprecated_pages_outside_migration_mode(tmp_path):
    packet_root = tmp_path / "raw" / "users" / "alice" / "performance" / "2026-06-12-run"
    packet_root.mkdir(parents=True)
    (packet_root / "wiki_plan.yaml").write_text(
        yaml.safe_dump(
            {"affected_pages": [{"path": "wiki/questions/sleep-lifelog-open-questions.md", "role": "hub"}]}
        ),
        encoding="utf-8",
    )

    result = load_wiki_plan(packet_root, repo_root=Path("."))

    assert not result.safe_paths
    assert any("not an allowed synthesis wiki path" in warning for warning in result.warnings)


def test_wiki_plan_allows_deprecated_pages_in_migration_mode(tmp_path):
    packet_root = tmp_path / "raw" / "users" / "alice" / "performance" / "2026-06-12-run"
    packet_root.mkdir(parents=True)
    (packet_root / "wiki_plan.yaml").write_text(
        yaml.safe_dump(
            {
                "affected_pages": [
                    {
                        "path": "wiki/questions/sleep-lifelog-open-questions.md",
                        "role": "hub",
                        "migration_compatibility": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = load_wiki_plan(packet_root, repo_root=Path("."), migration_mode=True)

    assert result.safe_paths == ["wiki/questions/sleep-lifelog-open-questions.md"]
