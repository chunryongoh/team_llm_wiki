import json
import subprocess
import sys
from pathlib import Path

import yaml


def seed_repo(root: Path, packet_type="reference", metric_expected=0.8):
    (root / "AGENTS.md").write_text("rules", encoding="utf-8")
    (root / "CLAUDE.md").write_text("@AGENTS.md", encoding="utf-8")
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
                "raw_paths": ["result.json"],
                "metrics_to_verify": [{"name": "accuracy", "expected": metric_expected, "actual": 0.8}],
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
    assert json.loads(result.stdout)["status"] == "direct_commit"
    assert report_path.exists()


def test_cli_expected_error_is_machine_readable_json(tmp_path):
    result = run_cli(["plan-wiki-main-ingest", "--repo-root", str(tmp_path), "--changed-path", "/abs"], cwd=Path.cwd())

    assert result.returncode == 1
    payload = json.loads(result.stderr)
    assert payload["error"]["code"] == "invalid_changed_path"


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
