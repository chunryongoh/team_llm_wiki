import json
import subprocess
import sys
from pathlib import Path

import yaml

from team_llm_wiki.wiki_ingest.route_contract import DEFAULT_CONTRACT_PATH


ROUTES = {
    "reference": "wiki/reports",
    "experiment": "wiki/reports",
}


def seed_repo(root: Path, packet_type="reference", metric_expected=0.8):
    (root / "AGENTS.md").write_text("rules", encoding="utf-8")
    (root / "CLAUDE.md").write_text("@AGENTS.md", encoding="utf-8")
    contract_target = root / DEFAULT_CONTRACT_PATH
    contract_target.parent.mkdir(parents=True, exist_ok=True)
    contract_target.write_text(Path(DEFAULT_CONTRACT_PATH).read_text(encoding="utf-8"), encoding="utf-8")
    (root / "wiki").mkdir()
    (root / "wiki" / "index.md").write_text("# Index\n", encoding="utf-8")
    (root / "wiki" / "overview.md").write_text("# Overview\n", encoding="utf-8")
    (root / "wiki" / "log.md").write_text("# Log\n", encoding="utf-8")
    packet = root / "raw" / "users" / "alice" / "pkt-1"
    packet.mkdir(parents=True)
    (packet / "result.json").write_text('{"accuracy": 0.8}', encoding="utf-8")
    (packet / "manifest.yaml").write_text(
        yaml.safe_dump(
            {
                "id": "pkt-1",
                "type": packet_type,
                "title": "Packet",
                "date": "2026-05-27",
                "owner": "alice",
                "status": "submitted",
                "task": "classification",
                "dataset": {"name": "benchmark-set", "version": "v1"},
                "split": {"name": "dev"},
                "model": {"family": "not-applicable"},
                "claim_boundary": "Only applies to the dev split.",
                "claim_status": "tentative",
                "summary": "Run summary.",
                "raw_paths": ["result.json"],
                "intended_wiki_targets": [f"{ROUTES[packet_type]}/pkt-1.md"],
                "metrics_to_verify": [
                    {"raw_path": "result.json", "metric_key": "accuracy", "reported_value": metric_expected}
                ],
            }
        ),
        encoding="utf-8",
    )
    return packet


def run_cli(args, cwd):
    return subprocess.run(
        [sys.executable, "-m", "team_llm_wiki.cli", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def test_cli_plan_run_and_high_risk_json(tmp_path):
    packet = seed_repo(tmp_path, packet_type="experiment")
    changed_file = tmp_path / "changed.txt"
    changed_file.write_text(str(packet.relative_to(tmp_path) / "manifest.yaml"), encoding="utf-8")

    result = run_cli(["plan-wiki-main-ingest", "--repo-root", str(tmp_path), "--changed-path-file", str(changed_file)], cwd=Path.cwd())

    assert result.returncode == 0
    assert json.loads(result.stdout)["status"] == "bot_pr"


def test_cli_run_writes_report_path(tmp_path):
    packet = seed_repo(tmp_path)
    report_path = tmp_path / "custom-report.json"

    result = run_cli(
        [
            "run-wiki-main-ingest",
            "--repo-root",
            str(tmp_path),
            "--changed-path",
            str(packet.relative_to(tmp_path) / "manifest.yaml"),
            "--report-path",
            str(report_path),
            "--run-id",
            "cli-run",
        ],
        cwd=Path.cwd(),
    )

    assert result.returncode == 0
    assert json.loads(result.stdout)["status"] == "bot_pr"
    assert report_path.exists()


def test_cli_expected_error_is_machine_readable_json(tmp_path):
    result = run_cli(["plan-wiki-main-ingest", "--repo-root", str(tmp_path), "--changed-path", "/abs"], cwd=Path.cwd())

    assert result.returncode == 1
    payload = json.loads(result.stderr)
    assert payload["error"]["code"] == "invalid_changed_path"


def test_cli_run_llm_wiki_synthesis_requires_api_key(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    packet = seed_repo(tmp_path)

    result = run_cli(
        [
            "run-llm-wiki-synthesis",
            "--repo-root",
            str(tmp_path),
            "--changed-path",
            str(packet.relative_to(tmp_path) / "manifest.yaml"),
            "--run-id",
            "llm-cli",
        ],
        cwd=Path.cwd(),
    )

    assert result.returncode == 1
    payload = json.loads(result.stderr)
    assert payload["error"]["code"] == "missing_api_key"


def test_cli_check_wiki_health_nonzero_on_failure(tmp_path):
    (tmp_path / "wiki").mkdir()
    (tmp_path / "wiki" / "index.md").write_text("[[missing]]", encoding="utf-8")
    report_path = tmp_path / "health.json"

    result = run_cli(
        ["check-wiki-health", "--repo-root", str(tmp_path), "--report-path", str(report_path)],
        cwd=Path.cwd(),
    )

    assert result.returncode == 1
    assert json.loads(report_path.read_text(encoding="utf-8"))["ok"] is False


def test_cli_generate_wiki_brief_writes_files_and_json(tmp_path):
    (tmp_path / "wiki").mkdir()
    (tmp_path / "wiki" / "log.md").write_text(
        "# Log\n\n"
        "## [2026-05-27] ingest | pkt-1\n\n"
        "- target: `wiki/reports/pkt-1.md`\n",
        encoding="utf-8",
    )

    result = run_cli(
        ["generate-wiki-brief", "--repo-root", str(tmp_path), "--date", "2026-05-27"],
        cwd=Path.cwd(),
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload == {"generated_paths": ["wiki/briefs/2026-05-27-daily.md", "wiki/briefs/latest.md"]}
    assert (tmp_path / "wiki" / "briefs" / "2026-05-27-daily.md").exists()
    assert (tmp_path / "wiki" / "briefs" / "latest.md").exists()
    latest = (tmp_path / "wiki" / "briefs" / "latest.md").read_text(encoding="utf-8")
    assert latest.splitlines()[0] == "[[2026-05-27-daily]]"
    assert "<!-- wiki-brief:generated -->" in latest


def test_cli_generate_wiki_weekly_brief_writes_weekly_and_stale_reports(tmp_path):
    (tmp_path / "wiki").mkdir()
    (tmp_path / "wiki" / "log.md").write_text(
        "# Log\n\n"
        "## [2026-05-27] ingest | pkt-1\n\n"
        "- target: `wiki/reports/pkt-1.md`\n",
        encoding="utf-8",
    )
    (tmp_path / "wiki" / "targets").mkdir()
    (tmp_path / "wiki" / "targets" / "old.md").write_text(
        "---\nclaim_status: tentative\ndate: 2026-05-01\n---\n# Old\n",
        encoding="utf-8",
    )

    result = run_cli(
        ["generate-wiki-weekly-brief", "--repo-root", str(tmp_path), "--date", "2026-05-27"],
        cwd=Path.cwd(),
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload == {
        "generated_paths": [
            "wiki/briefs/2026-05-27-weekly.md",
            "wiki/briefs/2026-05-27-stale-claims.md",
            "wiki/briefs/latest.md",
        ]
    }
    assert (tmp_path / "wiki" / "briefs" / "2026-05-27-weekly.md").exists()
    assert (tmp_path / "wiki" / "briefs" / "2026-05-27-stale-claims.md").exists()
    latest = (tmp_path / "wiki" / "briefs" / "latest.md").read_text(encoding="utf-8")
    assert latest.splitlines()[0] == "[[2026-05-27-weekly]]"
    assert "<!-- wiki-brief:generated -->" in latest


def test_cli_plan_wiki_route_migration_writes_report(tmp_path):
    seed_repo(tmp_path)
    report_path = tmp_path / "raw" / "results" / "wiki-renovation" / "cli" / "report.json"

    result = run_cli(
        [
            "plan-wiki-route-migration",
            "--repo-root",
            str(tmp_path),
            "--run-id",
            "cli",
            "--report-path",
            str(report_path),
        ],
        cwd=Path.cwd(),
    )

    assert result.returncode == 0
    assert json.loads(result.stdout)["status"] in {"planned", "clean"}
    assert report_path.exists()


def test_cli_run_wiki_route_migration_requires_flag(tmp_path):
    seed_repo(tmp_path)

    result = run_cli(
        ["run-wiki-route-migration", "--repo-root", str(tmp_path), "--run-id", "blocked"],
        cwd=Path.cwd(),
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"


def test_cli_plan_wiki_route_migration_fails_on_unmapped_deprecated_inventory(tmp_path):
    seed_repo(tmp_path)
    deprecated = tmp_path / "wiki" / "datasets" / "new-unmapped-page.md"
    deprecated.parent.mkdir()
    deprecated.write_text("# New Unmapped Page\n\n## Metrics\n\n- public_lb: 0.59\n", encoding="utf-8")

    result = run_cli(
        ["plan-wiki-route-migration", "--repo-root", str(tmp_path), "--run-id", "unmapped"],
        cwd=Path.cwd(),
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "failed"
    assert any(error["code"] == "migration_inventory_incomplete" for error in payload["errors"])


def test_cli_run_exits_nonzero_on_hard_fail_and_writes_report(tmp_path):
    packet = seed_repo(tmp_path, packet_type="experiment", metric_expected=0.9)
    report_path = tmp_path / "hard-fail-report.json"

    result = run_cli(
        [
            "run-wiki-main-ingest",
            "--repo-root",
            str(tmp_path),
            "--changed-path",
            str(packet.relative_to(tmp_path) / "manifest.yaml"),
            "--report-path",
            str(report_path),
            "--run-id",
            "hard-fail",
        ],
        cwd=Path.cwd(),
    )

    assert result.returncode == 1
    assert json.loads(result.stdout)["status"] == "hard_fail"
    assert json.loads(report_path.read_text(encoding="utf-8"))["status"] == "hard_fail"
