import json
from pathlib import Path
import shutil

from team_llm_wiki.wiki_ingest.migration import plan_route_migration, run_route_migration
from team_llm_wiki.wiki_ingest.route_contract import DEFAULT_CONTRACT_PATH


REPO_ROOT = Path(__file__).resolve().parents[2]


def seed_deprecated_page(root: Path) -> None:
    contract_target = root / DEFAULT_CONTRACT_PATH
    contract_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(REPO_ROOT / DEFAULT_CONTRACT_PATH, contract_target)

    wiki = root / "wiki"
    (wiki / "datasets").mkdir(parents=True)
    (wiki / "preprocessing").mkdir(parents=True)
    (wiki / "index.md").write_text(
        "- [Sleep Lifelog](datasets/sleep-lifelog-2024.md)\n",
        encoding="utf-8",
    )
    (wiki / "overview.md").write_text(
        "# Overview\n\n[Dataset](wiki/datasets/sleep-lifelog-2024.md)\n\n[[datasets/sleep-lifelog-2024|Sleep Lifelog]]\n",
        encoding="utf-8",
    )
    (wiki / "datasets" / "sleep-lifelog-2024.md").write_text(
        "---\nclaim_status: tentative\n---\n# Sleep Lifelog 2024\n\n## Split Policy\n\n- GroupKFold by subject.\n",
        encoding="utf-8",
    )
    (wiki / "models").mkdir()
    (wiki / "models" / "lgbm-catboost.md").write_text(
        "# LGBM CatBoost\n\n[Dataset](../datasets/sleep-lifelog-2024.md)\n",
        encoding="utf-8",
    )


def test_plan_route_migration_is_dry_run(tmp_path):
    seed_deprecated_page(tmp_path)
    report_path = tmp_path / "raw" / "results" / "wiki-renovation" / "dry" / "report.json"

    report = plan_route_migration(tmp_path, run_id="dry", report_path=report_path)

    assert report["status"] == "planned"
    assert "wiki/datasets/sleep-lifelog-2024.md" in report["inventory"]
    assert report["planned_moves"][0]["source"] == "wiki/datasets/sleep-lifelog-2024.md"
    assert report_path.exists()
    assert (tmp_path / "wiki" / "datasets" / "sleep-lifelog-2024.md").read_text(encoding="utf-8").startswith(
        "---"
    )


def test_run_route_migration_moves_page_leaves_tombstone_and_rewrites_links(tmp_path):
    seed_deprecated_page(tmp_path)
    report_path = tmp_path / "raw" / "results" / "wiki-renovation" / "run" / "report.json"

    report = run_route_migration(tmp_path, run_id="run", report_path=report_path, migration_mode=True)

    assert report["status"] == "migrated"
    assert (tmp_path / "wiki" / "preprocessing" / "sleep-lifelog-2024.md").exists()
    tombstone = (tmp_path / "wiki" / "datasets" / "sleep-lifelog-2024.md").read_text(encoding="utf-8")
    assert "page_role: compatibility" in tombstone
    assert "canonical_target: wiki/preprocessing/sleep-lifelog-2024.md" in tombstone
    assert "preprocessing/sleep-lifelog-2024.md" in (tmp_path / "wiki" / "index.md").read_text(
        encoding="utf-8"
    )
    model_page = (tmp_path / "wiki" / "models" / "lgbm-catboost.md").read_text(encoding="utf-8")
    assert "../preprocessing/sleep-lifelog-2024.md" in model_page
    assert "../datasets/sleep-lifelog-2024.md" not in model_page
    overview = (tmp_path / "wiki" / "overview.md").read_text(encoding="utf-8")
    assert "preprocessing/sleep-lifelog-2024.md" in overview
    assert "[[preprocessing/sleep-lifelog-2024|Sleep Lifelog]]" in overview
    assert json.loads(report_path.read_text(encoding="utf-8"))["status"] == "migrated"


def test_run_route_migration_is_idempotent_after_tombstone(tmp_path):
    seed_deprecated_page(tmp_path)

    first = run_route_migration(tmp_path, run_id="first", migration_mode=True)
    canonical = tmp_path / "wiki" / "preprocessing" / "sleep-lifelog-2024.md"
    before = canonical.read_text(encoding="utf-8")
    second = run_route_migration(tmp_path, run_id="second", migration_mode=True)

    assert first["status"] == "migrated"
    assert second["status"] == "migrated"
    assert second["planned_moves"] == []
    assert "wiki/datasets/sleep-lifelog-2024.md" in second["already_migrated"]
    assert canonical.read_text(encoding="utf-8") == before
    assert "Deprecated Compatibility Page" not in canonical.read_text(encoding="utf-8")


def test_plan_route_migration_fails_on_unmapped_deprecated_inventory(tmp_path):
    seed_deprecated_page(tmp_path)
    unmapped = tmp_path / "wiki" / "datasets" / "new-unmapped-page.md"
    unmapped.write_text("# New Unmapped Page\n\n## Metrics\n\n- public_lb: 0.59\n", encoding="utf-8")

    report = plan_route_migration(tmp_path, run_id="unmapped")

    assert report["status"] == "failed"
    assert any(error["code"] == "migration_inventory_incomplete" for error in report["errors"])


def test_run_route_migration_requires_explicit_migration_mode(tmp_path):
    seed_deprecated_page(tmp_path)

    report = run_route_migration(tmp_path, run_id="blocked", migration_mode=False)

    assert report["status"] == "blocked"
    assert any(error["code"] == "migration_mode_required" for error in report["errors"])
