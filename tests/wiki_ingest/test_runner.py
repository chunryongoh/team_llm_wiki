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
        "status": "submitted",
        "task": "classification",
        "dataset": {"name": "benchmark-set", "version": "v1"},
        "split": {"name": "dev"},
        "model": {"family": "not-applicable"},
        "claim_boundary": "Only applies to the dev split.",
        "claim_status": "tentative",
        "summary": "Run summary.",
        "raw_paths": ["result.json"],
        "intended_wiki_targets": [f"{ROUTES[packet_type]}/{packet_id}.md"],
        "metrics_to_verify": [
            {"raw_path": "result.json", "metric_key": "accuracy", "reported_value": metric_expected}
        ],
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
    assert "automation/.cache/compiled/ref-1.json" in payload["generated_paths"]
    assert "automation/.cache/compiled/ref-1.json" in payload["changed_paths"]
    assert payload["report_path"] == "raw/results/wiki-ingest/run-1/report.json"
    assert payload["timing_ms"] >= 0
    compiled = tmp_path / "automation" / ".cache" / "compiled" / "ref-1.json"
    assert compiled.exists()
    compiled_payload = json.loads(compiled.read_text(encoding="utf-8"))
    assert compiled_payload["id"] == "ref-1"
    assert compiled_payload["packet_type"] == "reference"
    assert compiled_payload["packet_root"] == "raw/users/alice/ref-1"
    assert compiled_payload["publish_action"] == "direct_commit"
    assert compiled_payload["risk_tier"] == "tier0-catalog"
    assert payload["packets"][0]["publish_action"] == "direct_commit"
    assert payload["packets"][0]["risk_tier"] == "tier0-catalog"
    assert payload["packets"][0]["claim_boundary"] == "Only applies to the dev split."
    assert payload["packet_skill_compatibility"]["status"] == "warning"
    assert any(
        check["id"] == "packet_root_shape" and check["status"] == "warning"
        for check in payload["packet_skill_compatibility"]["checks"]
    )
    assert payload["risk_tier"] == "tier0-catalog"


def test_runner_top_level_risk_tier_uses_governance_label(tmp_path):
    seed_repo(tmp_path)
    packet_root = packet_with_manifest(
        tmp_path,
        "ref-supported",
        {
            "id": "ref-supported",
            "packet_type": "reference",
            "title": "Supported Claim",
            "date": "2026-05-27",
            "owner": "alice",
            "status": "submitted",
            "task": "source-ingest",
            "dataset": {"name": "benchmark-set", "version": "v1"},
            "split": {"name": "none"},
            "model": {"family": "not-applicable"},
            "claim_boundary": "Only applies to this source packet.",
            "claim_status": "supported",
            "summary": "Run summary.",
            "raw_paths": ["result.json"],
            "intended_wiki_targets": ["wiki/sources/ref-supported.md"],
        },
        {"result.json": '{"accuracy": 0.8}'},
    )

    report_path = tmp_path / "raw" / "results" / "wiki-ingest" / "risk-label" / "report.json"
    report = run_wiki_main_ingest(
        tmp_path,
        changed_paths=[str(packet_root.relative_to(tmp_path) / "manifest.yaml")],
        report_path=report_path,
        run_id="risk-label",
    )

    assert report.status == "bot_pr"
    assert report.packets[0]["risk_tier"] == "tier4-governance"
    assert report.risk_tier == "tier4-governance"
    compiled_payload = json.loads((tmp_path / "automation" / ".cache" / "compiled" / "ref-supported.json").read_text())
    rendered_text = (tmp_path / "wiki" / "sources" / "ref-supported.md").read_text(encoding="utf-8")
    assert compiled_payload["publish_action"] == "bot_pr"
    assert compiled_payload["risk_tier"] == "tier4-governance"
    assert "publish_action: bot_pr" in rendered_text
    assert "risk_tier: tier4-governance" in rendered_text


def test_runner_compiled_payload_preserves_labeled_raw_paths(tmp_path):
    seed_repo(tmp_path)
    packet_root = packet_with_manifest(
        tmp_path,
        "ref-labeled",
        {
            "id": "ref-labeled",
            "packet_type": "reference",
            "title": "ref-labeled",
            "date": "2026-05-27",
            "owner": "alice",
            "status": "submitted",
            "task": "source-ingest",
            "dataset": {"name": "benchmark-set", "version": "v1"},
            "split": {"name": "none"},
            "model": {"family": "not-applicable"},
            "claim_boundary": "Only applies to this source packet.",
            "claim_status": "tentative",
            "summary": "Run summary.",
            "raw_paths": {"metrics": "metrics.json", "split": "folds.csv"},
            "intended_wiki_targets": ["wiki/sources/ref-labeled.md"],
            "metrics_to_verify": [
                {"raw_path": "metrics.json", "metric_key": "accuracy", "reported_value": 0.8}
            ],
        },
        {"metrics.json": '{"accuracy": 0.8}', "folds.csv": "fold,id\n0,1\n"},
    )

    report = run_wiki_main_ingest(
        tmp_path,
        changed_paths=[str(packet_root.relative_to(tmp_path) / "manifest.yaml")],
        report_path=tmp_path / "raw" / "results" / "wiki-ingest" / "run-labeled" / "report.json",
        run_id="run-labeled",
    )

    assert report.status == "direct_commit"
    compiled = tmp_path / "automation" / ".cache" / "compiled" / "ref-labeled.json"
    compiled_payload = json.loads(compiled.read_text(encoding="utf-8"))
    assert compiled_payload["raw_paths"] == {"metrics": "metrics.json", "split": "folds.csv"}


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


def test_runner_invalid_changed_path_writes_hard_fail_report(tmp_path):
    seed_repo(tmp_path)
    report_path = tmp_path / "raw" / "results" / "wiki-ingest" / "bad-path" / "report.json"

    report = run_wiki_main_ingest(
        tmp_path,
        changed_paths=["/tmp/bad"],
        report_path=report_path,
        run_id="bad-path",
    )

    assert report.status == "hard_fail"
    assert report_path.exists()
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["status"] == "hard_fail"
    assert payload["failures"][0]["code"] == "invalid_changed_path"


def test_runner_conflict_markers_hard_fail_without_mutation(tmp_path):
    seed_repo(tmp_path)
    packet_root = packet_with_manifest(
        tmp_path,
        "ref-conflict",
        {
            "id": "ref-conflict",
            "packet_type": "reference",
            "title": "Conflict",
            "date": "2026-05-27",
            "owner": "alice",
            "status": "submitted",
            "task": "source-ingest",
            "dataset": {"name": "benchmark-set", "version": "v1"},
            "split": {"name": "none"},
            "model": {"family": "not-applicable"},
            "claim_boundary": "Only applies to this source packet.",
            "claim_status": "tentative",
            "summary": "Run summary.",
            "raw_paths": ["result.json"],
            "intended_wiki_targets": ["wiki/sources/ref-conflict.md"],
            "claims": [{"status": "tentative", "text": "<<<<<<< HEAD\nleft\n=======\nright\n>>>>>>> branch"}],
        },
        {"result.json": '{"accuracy": 0.8}'},
    )
    before_index = (tmp_path / "wiki" / "index.md").read_text(encoding="utf-8")

    report = run_wiki_main_ingest(
        tmp_path,
        changed_paths=[str(packet_root.relative_to(tmp_path) / "manifest.yaml")],
        report_path=tmp_path / "raw" / "results" / "wiki-ingest" / "conflict" / "report.json",
        run_id="conflict",
    )

    assert report.status == "hard_fail"
    assert any(error["code"] == "unbalanced_generated_block" for error in report.link_lint_errors)
    assert (tmp_path / "wiki" / "index.md").read_text(encoding="utf-8") == before_index
    assert not (tmp_path / "wiki" / "sources" / "ref-conflict.md").exists()


def test_plan_hard_fail_does_not_predict_generated_paths(tmp_path):
    seed_repo(tmp_path)
    packet_root = packet(tmp_path, "exp-preview-fail", "experiment", metric_expected=0.9)

    report = plan_wiki_main_ingest(
        tmp_path,
        [str(packet_root.relative_to(tmp_path) / "manifest.yaml")],
        "preview-fail",
    )

    assert report.status == "hard_fail"
    assert report.generated_paths == []
    assert report.changed_paths == []
    assert not (tmp_path / "wiki" / "experiments" / "exp-preview-fail.md").exists()


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
            "status": "submitted",
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
    assert report.risk_tier == "tier4-governance"
    assert report.link_lint_errors
    assert (tmp_path / "wiki" / "index.md").read_text(encoding="utf-8") == before_index
    assert not (tmp_path / "wiki" / "sources" / "ref-bad-link.md").exists()
    assert not (tmp_path / "automation" / ".cache" / "compiled" / "ref-bad-link.json").exists()


def test_runner_missing_manifest_under_raw_users_hard_fails(tmp_path):
    seed_repo(tmp_path)
    packet_root = tmp_path / "raw" / "users" / "alice" / "missing-manifest"
    packet_root.mkdir(parents=True)
    (packet_root / "result.json").write_text('{"accuracy": 0.8}', encoding="utf-8")
    report_path = tmp_path / "raw" / "results" / "wiki-ingest" / "missing" / "report.json"

    report = run_wiki_main_ingest(
        tmp_path,
        changed_paths=[str(packet_root.relative_to(tmp_path) / "result.json")],
        report_path=report_path,
        run_id="missing",
    )

    assert report.status == "hard_fail"
    assert report.risk_tier == "tier4-governance"
    assert report_path.exists()
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["packet_roots"] == ["raw/users/alice/missing-manifest"]
    assert payload["failures"][0]["code"] == "invalid_manifest"


def test_runner_dataset_and_benchmark_ingest_use_canonical_entity_pages(tmp_path):
    seed_repo(tmp_path)
    dataset_manifest = {
        "id": "2026-05-29-sleep-lifelog-2024",
        "packet_type": "dataset",
        "title": "Sleep Lifelog 2024 Dataset Definition",
        "date": "2026-05-29",
        "owner": "alice",
        "status": "submitted",
        "task": "dataset-definition",
        "dataset": {"name": "sleep-lifelog-2024", "version": "v0"},
        "split": {"name": "groupkfold-subject-3fold-oof"},
        "model": {"family": "not-applicable"},
        "claim_boundary": "dataset definition only",
        "claim_status": "tentative",
        "summary": "Dataset summary.",
        "raw_paths": {"dataset": "dataset.yaml"},
        "intended_wiki_targets": ["wiki/datasets/2026-05-29-sleep-lifelog-2024.md"],
    }
    benchmark_manifest = {
        "id": "2026-05-29-sleep-health-hackathon-v0",
        "packet_type": "benchmark",
        "title": "Sleep Health Hackathon Benchmark v0 Definition",
        "date": "2026-05-29",
        "owner": "alice",
        "status": "submitted",
        "task": "benchmark-definition",
        "dataset": {"name": "sleep-lifelog-2024", "version": "v0"},
        "split": {"name": "groupkfold-subject-3fold-oof"},
        "model": {"family": "not-applicable"},
        "claim_boundary": "benchmark definition only",
        "claim_status": "tentative",
        "summary": "Benchmark summary.",
        "raw_paths": {"benchmark": "benchmark.yaml"},
        "intended_wiki_targets": ["wiki/benchmarks/2026-05-29-sleep-health-hackathon-v0.md"],
    }
    dataset_root = packet_with_manifest(
        tmp_path,
        "datasets/2026-05-29-sleep-lifelog-2024",
        dataset_manifest,
        {
            "dataset.yaml": (
                "name: sleep-lifelog-2024\n"
                "version: v0\n"
                "modalities: [smartphone:mActivity]\n"
                "package_files: [ch2026_metrics_train.csv]\n"
                "splits: {policy: groupkfold-subject}\n"
                "leakage_risks: [q-family-identity-leakage]\n"
                "provenance: {source_type: released-package}\n"
                "claim_status: tentative\n"
            ),
            "packet.md": "# Dataset\n\n## Working Implications\n\n- Use grouped subject splits.\n",
        },
    )
    benchmark_root = packet_with_manifest(
        tmp_path,
        "benchmarks/2026-05-29-sleep-health-hackathon-v0",
        benchmark_manifest,
        {
            "benchmark.yaml": (
                "name: sleep-health-hackathon-v0\n"
                "dataset_ref: sleep-lifelog-2024\n"
                "task_family: sleep-health-prediction\n"
                "targets:\n"
                "  - id: Q1\n"
                "    kind: subjective-binary\n"
                "    description: perceived sleep quality\n"
                "primary_metric: {name: grouped_macro_logloss}\n"
                "evaluation_policy: {split: groupkfold-subject}\n"
                "claim_boundaries: [local_oof_diagnostic_only]\n"
                "claim_status: tentative\n"
            ),
            "packet.md": (
                "# Benchmark\n\n"
                "This uses [[datasets/2026-05-29-sleep-lifelog-2024]].\n"
            ),
        },
    )

    report = run_wiki_main_ingest(
        tmp_path,
        changed_paths=[
            str(dataset_root.relative_to(tmp_path) / "manifest.yaml"),
            str(benchmark_root.relative_to(tmp_path) / "manifest.yaml"),
        ],
        report_path=tmp_path / "raw" / "results" / "wiki-ingest" / "canonical" / "report.json",
        run_id="canonical",
    )

    assert report.status == "bot_pr"
    assert "wiki/datasets/sleep-lifelog-2024.md" in report.generated_paths
    assert "wiki/benchmarks/sleep-health-hackathon-v0.md" in report.generated_paths
    assert "wiki/datasets/2026-05-29-sleep-lifelog-2024.md" not in report.generated_paths
    assert (tmp_path / "wiki" / "datasets" / "sleep-lifelog-2024.md").exists()
    benchmark_text = (tmp_path / "wiki" / "benchmarks" / "sleep-health-hackathon-v0.md").read_text(encoding="utf-8")
    assert "## Benchmark Entity" in benchmark_text
    assert "[[datasets/sleep-lifelog-2024]]" in benchmark_text


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
    assert report.risk_tier == "tier4-governance"
    assert report_path.exists()
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["risk_tier"] == "tier4-governance"
    assert payload["failures"][0]["code"] == "invalid_manifest"
    assert (tmp_path / "wiki" / "index.md").read_text(encoding="utf-8") == before_index


def test_runner_policy_conflict_hard_fail_uses_governance_risk(tmp_path):
    seed_repo(tmp_path)
    (tmp_path / "CLAUDE.md").write_text("@AGENTS.md\nrewrite raw files\n", encoding="utf-8")
    packet_root = packet(tmp_path, "ref-policy-conflict", "reference")

    report = run_wiki_main_ingest(
        tmp_path,
        changed_paths=[str(packet_root.relative_to(tmp_path) / "manifest.yaml")],
        report_path=tmp_path / "raw" / "results" / "wiki-ingest" / "policy" / "report.json",
        run_id="policy",
    )

    assert report.status == "hard_fail"
    assert report.risk_tier == "tier4-governance"
    assert any(failure["code"] == "policy_conflict" for failure in report.failures)


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
