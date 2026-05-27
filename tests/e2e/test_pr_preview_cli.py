import json
import subprocess
import sys
from pathlib import Path

import yaml


def seed_repo(root: Path):
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
                "packet_type": "reference",
                "title": "Packet",
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
                "intended_wiki_targets": ["wiki/sources/pkt-1.md"],
                "metrics_to_verify": [
                    {"raw_path": "result.json", "metric_key": "accuracy", "reported_value": 0.8}
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


def test_preview_wiki_ingest_outputs_json_without_mutating_wiki(tmp_path):
    packet = seed_repo(tmp_path)
    changed_file = tmp_path / "changed.txt"
    changed_file.write_text(str(packet.relative_to(tmp_path) / "manifest.yaml"), encoding="utf-8")
    before_index = (tmp_path / "wiki" / "index.md").read_text(encoding="utf-8")

    result = run_cli(
        [
            "preview-wiki-ingest",
            "--repo-root",
            str(tmp_path),
            "--changed-path-file",
            str(changed_file),
            "--run-id",
            "preview",
        ],
        cwd=Path.cwd(),
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "direct_commit"
    assert payload["run_id"] == "preview"
    assert payload["packet_roots"] == ["raw/users/alice/pkt-1"]
    assert "wiki/sources/pkt-1.md" in payload["generated_paths"]
    assert "automation/.cache/compiled/pkt-1.json" in payload["generated_paths"]
    assert "wiki/sources/pkt-1.md" in payload["changed_paths"]
    assert "automation/.cache/compiled/pkt-1.json" in payload["changed_paths"]
    assert (tmp_path / "wiki" / "index.md").read_text(encoding="utf-8") == before_index
    assert not (tmp_path / "wiki" / "sources" / "pkt-1.md").exists()
    assert not (tmp_path / "automation" / ".cache" / "compiled" / "pkt-1.json").exists()
    assert not (tmp_path / "raw" / "results" / "wiki-ingest" / "preview" / "report.json").exists()


def test_preview_wiki_ingest_exits_nonzero_on_hard_fail(tmp_path):
    packet = seed_repo(tmp_path)
    (packet / "result.json").unlink()
    changed_file = tmp_path / "changed.txt"
    changed_file.write_text(str(packet.relative_to(tmp_path) / "manifest.yaml"), encoding="utf-8")

    result = run_cli(
        [
            "preview-wiki-ingest",
            "--repo-root",
            str(tmp_path),
            "--changed-path-file",
            str(changed_file),
            "--run-id",
            "preview",
        ],
        cwd=Path.cwd(),
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "hard_fail"
    assert payload["failures"]


def test_preview_wiki_ingest_reports_invalid_utf8_manifest_as_hard_fail(tmp_path):
    packet = seed_repo(tmp_path)
    (packet / "manifest.yaml").write_bytes(b"id: pkt-1\nsummary: \xff\n")
    changed_file = tmp_path / "changed.txt"
    changed_file.write_text(str(packet.relative_to(tmp_path) / "manifest.yaml"), encoding="utf-8")

    result = run_cli(
        [
            "preview-wiki-ingest",
            "--repo-root",
            str(tmp_path),
            "--changed-path-file",
            str(changed_file),
            "--run-id",
            "preview",
        ],
        cwd=Path.cwd(),
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "hard_fail"
    assert payload["failures"][0]["code"] == "invalid_manifest"
    assert "could not be read as UTF-8" in payload["failures"][0]["message"]
    assert "Traceback" not in result.stderr


def test_wiki_pr_validate_workflow_yaml_parses():
    workflow = Path(".github/workflows/wiki-pr-validate.yml")

    assert yaml.safe_load(workflow.read_text(encoding="utf-8"))["name"] == "wiki-pr-validate"
