import json
from pathlib import Path

import yaml

from team_llm_wiki.wiki_ingest.runner import plan_wiki_main_ingest, run_wiki_main_ingest


def seed_repo(root: Path):
    (root / "AGENTS.md").write_text("rules", encoding="utf-8")
    (root / "CLAUDE.md").write_text("@AGENTS.md", encoding="utf-8")
    (root / "wiki").mkdir()
    (root / "wiki" / "index.md").write_text("# Index\n", encoding="utf-8")
    (root / "wiki" / "overview.md").write_text("# Overview\n", encoding="utf-8")
    (root / "wiki" / "log.md").write_text("# Log\n", encoding="utf-8")
    (root / "wiki" / "old.md").write_text("[[missing-old]]\n", encoding="utf-8")


def packet(root: Path, packet_id: str, packet_type: str, metric_expected=0.8):
    packet_root = root / "raw" / "users" / "alice" / packet_id
    packet_root.mkdir(parents=True)
    (packet_root / "result.json").write_text(json.dumps({"accuracy": 0.8}), encoding="utf-8")
    manifest = {
        "id": packet_id,
        "type": packet_type,
        "title": packet_id,
        "raw_paths": ["result.json"],
        "metrics_to_verify": [{"name": "accuracy", "expected": metric_expected, "actual": 0.8}],
    }
    (packet_root / "manifest.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")
    return packet_root


def test_runner_low_risk_direct_commit_and_report(tmp_path):
    seed_repo(tmp_path)
    packet_root = packet(tmp_path, "ref-1", "reference")
    report_path = tmp_path / "raw" / "results" / "wiki-ingest" / "run-1" / "report.json"

    report = run_wiki_main_ingest(
        tmp_path,
        changed_paths=[str(packet_root.relative_to(tmp_path) / "manifest.yaml")],
        report_path=report_path,
        run_id="run-1",
    )

    assert report.status == "direct_commit"
    assert (tmp_path / "wiki" / "sources" / "ref-1.md").exists()
    assert report_path.exists()
    assert json.loads(report_path.read_text(encoding="utf-8"))["status"] == "direct_commit"


def test_runner_hard_fail_does_not_mutate_wiki(tmp_path):
    seed_repo(tmp_path)
    packet_root = packet(tmp_path, "exp-1", "experiment", metric_expected=0.9)
    before = (tmp_path / "wiki" / "index.md").read_text(encoding="utf-8")

    report = run_wiki_main_ingest(
        tmp_path,
        changed_paths=[str(packet_root.relative_to(tmp_path) / "manifest.yaml")],
        report_path=tmp_path / "raw" / "results" / "wiki-ingest" / "run-2" / "report.json",
        run_id="run-2",
    )

    assert report.status == "hard_fail"
    assert (tmp_path / "wiki" / "index.md").read_text(encoding="utf-8") == before
    assert not (tmp_path / "wiki" / "experiments" / "exp-1.md").exists()


def test_runner_zero_packet_skipped_no_mutation(tmp_path):
    seed_repo(tmp_path)
    before = (tmp_path / "wiki" / "index.md").read_text(encoding="utf-8")

    report = run_wiki_main_ingest(tmp_path, changed_paths=["README.md"], run_id="run-3")

    assert report.status == "skipped"
    assert (tmp_path / "wiki" / "index.md").read_text(encoding="utf-8") == before


def test_plan_high_risk_bot_pr_and_old_broken_link_ignored(tmp_path):
    seed_repo(tmp_path)
    packet_root = packet(tmp_path, "exp-2", "experiment")

    report = plan_wiki_main_ingest(tmp_path, [str(packet_root.relative_to(tmp_path) / "manifest.yaml")], "run-4")

    assert report.status == "bot_pr"
    assert report.link_lint_errors == []
