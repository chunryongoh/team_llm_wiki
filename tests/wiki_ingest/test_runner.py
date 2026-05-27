import json
from pathlib import Path

import yaml

from team_llm_wiki.wiki_ingest.runner import plan_wiki_main_ingest, run_wiki_main_ingest


ROUTES = {
    "reference": "wiki/sources",
    "experiment": "wiki/experiments",
}


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
        "intended_wiki_targets": [f"{ROUTES[packet_type]}/{packet_id}.md"],
        "metrics_to_verify": [{"name": "accuracy", "expected": metric_expected, "actual": 0.8}],
    }
    (packet_root / "manifest.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")
    return packet_root


def packet_with_manifest(root: Path, packet_id: str, manifest: dict, files: dict[str, str]):
    packet_root = root / "raw" / "users" / "alice" / packet_id
    packet_root.mkdir(parents=True)
    for rel, content in files.items():
        path = packet_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
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
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["status"] == "direct_commit"
    assert payload["input_changed_paths"] == ["raw/users/alice/ref-1/manifest.yaml"]
    assert "wiki/sources/ref-1.md" in payload["generated_paths"]
    assert payload["report_path"] == "raw/results/wiki-ingest/run-1/report.json"
    assert payload["timing_ms"] >= 0


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


def test_runner_generated_link_hard_fail_does_not_mutate_wiki(tmp_path):
    seed_repo(tmp_path)
    packet_root = packet_with_manifest(
        tmp_path,
        "ref-bad-link",
        {
            "id": "ref-bad-link",
            "packet_type": "reference",
            "title": "Bad Link",
            "date": "2026-05-27",
            "owner": "alice",
            "status": "ready",
            "task": "source-ingest",
            "dataset": {"name": "benchmark-set", "version": "v1"},
            "split": {"name": "none"},
            "model": {"family": "not-applicable"},
            "claim_boundary": "Only applies to this source packet.",
            "claim_status": "tentative",
            "summary": "Generated page has [[missing-generated-link]].",
            "raw_paths": ["result.json"],
            "intended_wiki_targets": ["wiki/sources/ref-bad-link.md"],
        },
        {"result.json": '{"accuracy": 0.8}'},
    )
    before_index = (tmp_path / "wiki" / "index.md").read_text(encoding="utf-8")

    report = run_wiki_main_ingest(
        tmp_path,
        changed_paths=[str(packet_root.relative_to(tmp_path) / "manifest.yaml")],
        report_path=tmp_path / "raw" / "results" / "wiki-ingest" / "run-link" / "report.json",
        run_id="run-link",
    )

    assert report.status == "hard_fail"
    assert report.link_lint_errors
    assert (tmp_path / "wiki" / "index.md").read_text(encoding="utf-8") == before_index
    assert not (tmp_path / "wiki" / "sources" / "ref-bad-link.md").exists()


def test_runner_invalid_manifest_writes_hard_fail_report_without_mutation(tmp_path):
    seed_repo(tmp_path)
    packet_root = tmp_path / "raw" / "users" / "alice" / "bad-packet"
    packet_root.mkdir(parents=True)
    (packet_root / "manifest.yaml").write_text(
        yaml.safe_dump({"id": "bad-packet", "packet_type": "reference"}),
        encoding="utf-8",
    )
    before_index = (tmp_path / "wiki" / "index.md").read_text(encoding="utf-8")
    report_path = tmp_path / "raw" / "results" / "wiki-ingest" / "bad" / "report.json"

    report = run_wiki_main_ingest(
        tmp_path,
        changed_paths=[str(packet_root.relative_to(tmp_path) / "manifest.yaml")],
        report_path=report_path,
        run_id="bad",
    )

    assert report.status == "hard_fail"
    assert report_path.exists()
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["failures"][0]["code"] == "invalid_manifest"
    assert (tmp_path / "wiki" / "index.md").read_text(encoding="utf-8") == before_index


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
