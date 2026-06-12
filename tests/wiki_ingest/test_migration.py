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
    (wiki / "datasets" / "sleep-lifelog-2024.md").write_text(
        "---\nclaim_status: tentative\n---\n# Sleep Lifelog 2024\n\n## Split Policy\n\n- GroupKFold by subject.\n",
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
    assert json.loads(report_path.read_text(encoding="utf-8"))["status"] == "migrated"


def test_run_route_migration_requires_explicit_migration_mode(tmp_path):
    seed_deprecated_page(tmp_path)

    report = run_route_migration(tmp_path, run_id="blocked", migration_mode=False)

    assert report["status"] == "blocked"
    assert any(error["code"] == "migration_mode_required" for error in report["errors"])
